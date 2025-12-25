"""
GPS Payments CDM - XML Parser
==============================

Parser for XML-based message formats including ISO 20022.
Uses Spark XML for distributed parsing with XPath extraction.
"""

from typing import Any, Dict, List, Optional
import re

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, explode, expr, xpath, xpath_string, xpath_float,
    xpath_int, xpath_boolean, lit, when, coalesce,
    from_json, get_json_object, struct, to_json,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, ArrayType,
    MapType, LongType, DoubleType, BooleanType,
)

from gps_cdm.ingestion.core.models import SourceConfig, ExtractHint
from gps_cdm.ingestion.parsers.base import BaseParser, ParseResult, ExtractionContext


# ISO 20022 namespace mapping
ISO20022_NAMESPACES = {
    "pain.001": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.09",
    "pain.002": "urn:iso:std:iso:20022:tech:xsd:pain.002.001.10",
    "pain.008": "urn:iso:std:iso:20022:tech:xsd:pain.008.001.08",
    "pacs.002": "urn:iso:std:iso:20022:tech:xsd:pacs.002.001.10",
    "pacs.004": "urn:iso:std:iso:20022:tech:xsd:pacs.004.001.09",
    "pacs.008": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08",
    "pacs.009": "urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08",
    "camt.052": "urn:iso:std:iso:20022:tech:xsd:camt.052.001.08",
    "camt.053": "urn:iso:std:iso:20022:tech:xsd:camt.053.001.08",
    "camt.054": "urn:iso:std:iso:20022:tech:xsd:camt.054.001.08",
    "camt.056": "urn:iso:std:iso:20022:tech:xsd:camt.056.001.08",
    "camt.029": "urn:iso:std:iso:20022:tech:xsd:camt.029.001.09",
}

# Common root elements
ISO20022_ROOT_ELEMENTS = {
    "pain.001": "CstmrCdtTrfInitn",
    "pain.002": "CstmrPmtStsRpt",
    "pain.008": "CstmrDrctDbtInitn",
    "pacs.002": "FIToFIPmtStsRpt",
    "pacs.004": "PmtRtr",
    "pacs.008": "FIToFICstmrCdtTrf",
    "pacs.009": "FICdtTrf",
    "camt.052": "BkToCstmrAcctRpt",
    "camt.053": "BkToCstmrStmt",
    "camt.054": "BkToCstmrDbtCdtNtfctn",
    "camt.056": "FIToFIPmtCxlReq",
    "camt.029": "RsltnOfInvstgtn",
}


class XMLParser(BaseParser):
    """
    Generic XML parser using Spark's built-in XML support.

    Extracts values using XPath expressions. Supports:
    - Namespace-aware parsing
    - Nested element extraction
    - Attribute extraction
    - Array/repeating element handling
    """

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self.namespace = config.namespace
        self.root_element = config.root_element
        self._ns_prefix = "ns:"
        self._ns_map = {}

        if self.namespace:
            self._ns_map = {"ns": self.namespace}

    def parse(self, source_df: DataFrame) -> ParseResult:
        """
        Parse XML content from source DataFrame.

        Expects DataFrame with 'content' column containing XML strings.
        """
        # Parse XML using spark-xml or built-in functions
        # For distributed parsing, we use xpath functions

        # Add namespace-aware root path
        root_path = self._get_root_xpath()

        # Create parsed DataFrame with exploded elements if needed
        parsed_df = source_df

        # Add parse metadata
        parsed_df = parsed_df.withColumn(
            "_parse_metadata",
            struct(
                lit(self.config.format.value).alias("format"),
                lit(self.config.parser).alias("parser"),
                lit(self.namespace).alias("namespace"),
            )
        )

        row_count = parsed_df.count()

        return ParseResult(
            data=parsed_df,
            row_count=row_count,
            metadata={
                "namespace": self.namespace,
                "root_element": self.root_element,
            }
        )

    def extract_value(
        self,
        data: Any,
        path: str,
        hint: Optional[ExtractHint] = None
    ) -> Any:
        """
        Extract value using XPath.

        Args:
            data: XML string or parsed element
            path: XPath expression (with or without namespace prefix)
            hint: Extraction type hint
        """
        # Normalize path to include namespace prefix if needed
        xpath_expr = self._normalize_xpath(path)

        if hint == ExtractHint.ATTRIBUTE:
            # Path should be like "element/@attribute"
            if not "@" in xpath_expr:
                xpath_expr = xpath_expr + "/text()"
        elif hint == ExtractHint.TEXT_CONTENT:
            if not xpath_expr.endswith("/text()"):
                xpath_expr = xpath_expr + "/text()"
        elif hint == ExtractHint.FULL_ELEMENT:
            # Keep as is - will extract whole element
            pass
        elif hint == ExtractHint.CHILD_ELEMENTS:
            # Will return array
            pass

        return xpath_expr

    def get_schema(self) -> StructType:
        """Get schema for parsed XML output."""
        return StructType([
            StructField("content", StringType(), True),
            StructField("_parse_metadata", StructType([
                StructField("format", StringType(), True),
                StructField("parser", StringType(), True),
                StructField("namespace", StringType(), True),
            ]), True),
        ])

    def _get_root_xpath(self) -> str:
        """Get XPath to root element with namespace."""
        if self.root_element:
            if self.namespace:
                return f"/{self._ns_prefix}{self.root_element}"
            return f"/{self.root_element}"
        return "/*"

    def _normalize_xpath(self, path: str) -> str:
        """Normalize XPath to include namespace prefixes."""
        if not self.namespace:
            return path

        # Add namespace prefix to element names
        # Matches element names but not attributes (@) or functions
        def add_prefix(match):
            name = match.group(1)
            # Don't prefix if already prefixed, is an attribute, or is a function
            if ":" in name or name.startswith("@"):
                return match.group(0)
            return f"/{self._ns_prefix}{name}"

        normalized = re.sub(r'/([a-zA-Z][a-zA-Z0-9_]*)', add_prefix, path)
        return normalized

    def get_xpath_expr(self, path: str, data_type: str = "string") -> str:
        """
        Generate Spark SQL xpath expression.

        Args:
            path: XPath expression
            data_type: Target data type (string, int, float, boolean)

        Returns:
            Spark SQL expression string
        """
        normalized = self._normalize_xpath(path)

        if data_type == "string":
            return f"xpath_string(content, '{normalized}')"
        elif data_type == "int":
            return f"xpath_int(content, '{normalized}')"
        elif data_type == "float":
            return f"xpath_float(content, '{normalized}')"
        elif data_type == "boolean":
            return f"xpath_boolean(content, '{normalized}')"
        else:
            return f"xpath_string(content, '{normalized}')"


class ISO20022Parser(XMLParser):
    """
    Specialized parser for ISO 20022 XML messages.

    Provides:
    - Auto-detection of message type from namespace
    - Pre-built paths for common elements
    - Entity extraction for repeating structures (transactions, parties)
    """

    # Common paths for ISO 20022 elements
    COMMON_PATHS = {
        # Group Header elements (pain.001, pacs.008)
        "message_id": "GrpHdr/MsgId",
        "creation_datetime": "GrpHdr/CreDtTm",
        "number_of_transactions": "GrpHdr/NbOfTxs",
        "control_sum": "GrpHdr/CtrlSum",
        "initiating_party": "GrpHdr/InitgPty",

        # Payment Information (pain.001)
        "payment_info_id": "PmtInf/PmtInfId",
        "payment_method": "PmtInf/PmtMtd",
        "requested_execution_date": "PmtInf/ReqdExctnDt/Dt",

        # Credit Transfer Transaction (pain.001, pacs.008)
        "end_to_end_id": "CdtTrfTxInf/PmtId/EndToEndId",
        "instruction_id": "CdtTrfTxInf/PmtId/InstrId",
        "uetr": "CdtTrfTxInf/PmtId/UETR",
        "instructed_amount": "CdtTrfTxInf/Amt/InstdAmt",
        "instructed_currency": "CdtTrfTxInf/Amt/InstdAmt/@Ccy",

        # Parties
        "debtor_name": "Dbtr/Nm",
        "debtor_account_iban": "DbtrAcct/Id/IBAN",
        "debtor_agent_bic": "DbtrAgt/FinInstnId/BICFI",
        "creditor_name": "Cdtr/Nm",
        "creditor_account_iban": "CdtrAcct/Id/IBAN",
        "creditor_agent_bic": "CdtrAgt/FinInstnId/BICFI",

        # Remittance
        "remittance_unstructured": "RmtInf/Ustrd",
        "remittance_structured": "RmtInf/Strd",
    }

    def __init__(self, spark: SparkSession, config: SourceConfig):
        # Detect namespace if not provided
        if not config.namespace and config.root_element:
            config.namespace = self._detect_namespace(config.root_element)

        super().__init__(spark, config)

        # Determine message type
        self.message_type = self._detect_message_type()

    def _detect_namespace(self, root_element: str) -> Optional[str]:
        """Detect ISO 20022 namespace from root element."""
        for msg_type, root in ISO20022_ROOT_ELEMENTS.items():
            if root == root_element:
                return ISO20022_NAMESPACES.get(msg_type)
        return None

    def _detect_message_type(self) -> Optional[str]:
        """Detect message type from namespace."""
        if self.namespace:
            for msg_type, ns in ISO20022_NAMESPACES.items():
                if ns == self.namespace:
                    return msg_type
        return None

    def get_common_path(self, element_name: str) -> Optional[str]:
        """Get common XPath for named element."""
        return self.COMMON_PATHS.get(element_name)

    def parse(self, source_df: DataFrame) -> ParseResult:
        """Parse ISO 20022 message with message type detection."""
        result = super().parse(source_df)

        # Add message type to metadata
        result.metadata["message_type"] = self.message_type
        result.metadata["iso20022"] = True

        return result

    def get_transaction_xpath(self) -> str:
        """Get XPath to transaction elements based on message type."""
        if self.message_type in ("pain.001",):
            return "//PmtInf/CdtTrfTxInf"
        elif self.message_type in ("pacs.008", "pacs.009"):
            return "//CdtTrfTxInf"
        elif self.message_type in ("pain.008",):
            return "//PmtInf/DrctDbtTxInf"
        elif self.message_type in ("camt.053", "camt.054"):
            return "//Ntry"
        else:
            return "//*[contains(local-name(), 'TxInf')]"

    def get_party_paths(self, party_type: str) -> Dict[str, str]:
        """Get all paths for a party type (debtor, creditor, etc.)."""
        prefix_map = {
            "debtor": "Dbtr",
            "creditor": "Cdtr",
            "initiating_party": "InitgPty",
            "ultimate_debtor": "UltmtDbtr",
            "ultimate_creditor": "UltmtCdtr",
        }

        prefix = prefix_map.get(party_type, party_type)

        return {
            "name": f"{prefix}/Nm",
            "postal_address_country": f"{prefix}/PstlAdr/Ctry",
            "postal_address_street": f"{prefix}/PstlAdr/StrtNm",
            "postal_address_town": f"{prefix}/PstlAdr/TwnNm",
            "postal_address_postcode": f"{prefix}/PstlAdr/PstCd",
            "org_id_lei": f"{prefix}/Id/OrgId/LEI",
            "org_id_bic": f"{prefix}/Id/OrgId/AnyBIC",
            "org_id_other": f"{prefix}/Id/OrgId/Othr/Id",
            "priv_id_birth_date": f"{prefix}/Id/PrvtId/DtAndPlcOfBirth/BirthDt",
            "priv_id_other": f"{prefix}/Id/PrvtId/Othr/Id",
            "contact_phone": f"{prefix}/CtctDtls/PhneNb",
            "contact_email": f"{prefix}/CtctDtls/EmailAdr",
        }

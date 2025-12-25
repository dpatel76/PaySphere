"""
GPS Payments CDM - SWIFT MT Parser
===================================

Parser for SWIFT MT (Message Type) formatted messages.
Handles field tag extraction and option letter parsing.
"""

from typing import Any, Dict, List, Optional, Tuple
import re

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, lit, regexp_extract, regexp_replace, split,
    struct, when, coalesce, trim, length, substring,
    udf, explode, array,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, ArrayType, MapType,
)

from gps_cdm.ingestion.core.models import SourceConfig, ExtractHint
from gps_cdm.ingestion.parsers.base import BaseParser, ParseResult


# SWIFT MT message type definitions
MT_DEFINITIONS = {
    "MT103": {
        "name": "Single Customer Credit Transfer",
        "category": "1",
        "fields": {
            "20": {"name": "Transaction Reference", "mandatory": True},
            "13C": {"name": "Time Indication", "mandatory": False},
            "23B": {"name": "Bank Operation Code", "mandatory": True},
            "23E": {"name": "Instruction Code", "mandatory": False},
            "26T": {"name": "Transaction Type Code", "mandatory": False},
            "32A": {"name": "Value Date/Currency/Amount", "mandatory": True},
            "33B": {"name": "Currency/Instructed Amount", "mandatory": False},
            "36": {"name": "Exchange Rate", "mandatory": False},
            "50A": {"name": "Ordering Customer (Account)", "mandatory": False},
            "50F": {"name": "Ordering Customer (Party)", "mandatory": False},
            "50K": {"name": "Ordering Customer (Name/Address)", "mandatory": False},
            "51A": {"name": "Sending Institution", "mandatory": False},
            "52A": {"name": "Ordering Institution (BIC)", "mandatory": False},
            "52D": {"name": "Ordering Institution (Name/Address)", "mandatory": False},
            "53A": {"name": "Sender's Correspondent (BIC)", "mandatory": False},
            "53B": {"name": "Sender's Correspondent (Location)", "mandatory": False},
            "54A": {"name": "Receiver's Correspondent (BIC)", "mandatory": False},
            "54D": {"name": "Receiver's Correspondent (Name/Address)", "mandatory": False},
            "55A": {"name": "Third Reimbursement Institution (BIC)", "mandatory": False},
            "56A": {"name": "Intermediary Institution (BIC)", "mandatory": False},
            "56D": {"name": "Intermediary Institution (Name/Address)", "mandatory": False},
            "57A": {"name": "Account With Institution (BIC)", "mandatory": False},
            "57D": {"name": "Account With Institution (Name/Address)", "mandatory": False},
            "59": {"name": "Beneficiary Customer", "mandatory": True},
            "59A": {"name": "Beneficiary Customer (Account)", "mandatory": False},
            "59F": {"name": "Beneficiary Customer (Party)", "mandatory": False},
            "70": {"name": "Remittance Information", "mandatory": False},
            "71A": {"name": "Details of Charges", "mandatory": True},
            "71F": {"name": "Sender's Charges", "mandatory": False},
            "71G": {"name": "Receiver's Charges", "mandatory": False},
            "72": {"name": "Sender to Receiver Information", "mandatory": False},
            "77B": {"name": "Regulatory Reporting", "mandatory": False},
        },
    },
    "MT202": {
        "name": "General Financial Institution Transfer",
        "category": "2",
        "fields": {
            "20": {"name": "Transaction Reference", "mandatory": True},
            "21": {"name": "Related Reference", "mandatory": True},
            "13C": {"name": "Time Indication", "mandatory": False},
            "32A": {"name": "Value Date/Currency/Amount", "mandatory": True},
            "52A": {"name": "Ordering Institution (BIC)", "mandatory": False},
            "53A": {"name": "Sender's Correspondent (BIC)", "mandatory": False},
            "54A": {"name": "Receiver's Correspondent (BIC)", "mandatory": False},
            "56A": {"name": "Intermediary (BIC)", "mandatory": False},
            "57A": {"name": "Account With Institution (BIC)", "mandatory": False},
            "58A": {"name": "Beneficiary Institution (BIC)", "mandatory": True},
            "72": {"name": "Sender to Receiver Information", "mandatory": False},
        },
    },
    "MT202COV": {
        "name": "General Financial Institution Transfer (Cover)",
        "category": "2",
        "fields": {
            # Same as MT202 plus underlying customer details
            "20": {"name": "Transaction Reference", "mandatory": True},
            "21": {"name": "Related Reference", "mandatory": True},
            "32A": {"name": "Value Date/Currency/Amount", "mandatory": True},
            "50A": {"name": "Ordering Customer (Account)", "mandatory": False},
            "50F": {"name": "Ordering Customer (Party)", "mandatory": False},
            "50K": {"name": "Ordering Customer (Name/Address)", "mandatory": False},
            "52A": {"name": "Ordering Institution (BIC)", "mandatory": False},
            "56A": {"name": "Intermediary (BIC)", "mandatory": False},
            "57A": {"name": "Account With Institution (BIC)", "mandatory": False},
            "58A": {"name": "Beneficiary Institution (BIC)", "mandatory": True},
            "59": {"name": "Beneficiary Customer", "mandatory": False},
            "59A": {"name": "Beneficiary Customer (Account)", "mandatory": False},
            "70": {"name": "Remittance Information", "mandatory": False},
            "72": {"name": "Sender to Receiver Information", "mandatory": False},
        },
    },
    "MT940": {
        "name": "Customer Statement Message",
        "category": "9",
        "fields": {
            "20": {"name": "Transaction Reference", "mandatory": True},
            "21": {"name": "Related Reference", "mandatory": False},
            "25": {"name": "Account Identification", "mandatory": True},
            "28C": {"name": "Statement Number", "mandatory": True},
            "60F": {"name": "Opening Balance", "mandatory": True},
            "60M": {"name": "Opening Balance (Interim)", "mandatory": False},
            "61": {"name": "Statement Line", "mandatory": False},
            "62F": {"name": "Closing Balance", "mandatory": True},
            "62M": {"name": "Closing Balance (Interim)", "mandatory": False},
            "64": {"name": "Closing Available Balance", "mandatory": False},
            "86": {"name": "Information to Account Owner", "mandatory": False},
        },
    },
}


class MTParser(BaseParser):
    """
    Generic SWIFT MT message parser.

    Parses MT message structure:
    - Basic Header Block {1:...}
    - Application Header Block {2:...}
    - User Header Block {3:...}
    - Text Block {4:...}
    - Trailer Block {5:...}

    Extracts field tags from text block using :tag:value patterns.
    """

    # MT field tag pattern: :tag:value or :tag:\nvalue (for multiline)
    FIELD_PATTERN = r':(\d{2}[A-Z]?):(.*?)(?=:(\d{2}[A-Z]?):|\Z)'

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self.message_type = config.message_type  # e.g., "MT103"
        self.field_definitions = self._get_field_definitions()

    def _get_field_definitions(self) -> Dict[str, Dict]:
        """Get field definitions for message type."""
        if self.message_type and self.message_type in MT_DEFINITIONS:
            return MT_DEFINITIONS[self.message_type]["fields"]
        return {}

    def parse(self, source_df: DataFrame) -> ParseResult:
        """
        Parse MT message content.

        Expects DataFrame with 'content' column containing MT message strings.
        """
        # Extract blocks
        parsed_df = source_df.withColumn(
            "basic_header",
            regexp_extract(col("content"), r'\{1:([^}]+)\}', 1)
        ).withColumn(
            "application_header",
            regexp_extract(col("content"), r'\{2:([^}]+)\}', 1)
        ).withColumn(
            "user_header",
            regexp_extract(col("content"), r'\{3:([^}]+)\}', 1)
        ).withColumn(
            "text_block",
            regexp_extract(col("content"), r'\{4:\s*(.*?)\s*-\}', 1)
        ).withColumn(
            "trailer",
            regexp_extract(col("content"), r'\{5:([^}]+)\}', 1)
        )

        # Add parse metadata
        parsed_df = parsed_df.withColumn(
            "_parse_metadata",
            struct(
                lit(self.config.format.value).alias("format"),
                lit(self.config.parser).alias("parser"),
                lit(self.message_type).alias("message_type"),
            )
        )

        row_count = parsed_df.count()

        return ParseResult(
            data=parsed_df,
            row_count=row_count,
            metadata={
                "message_type": self.message_type,
            }
        )

    def extract_value(
        self,
        data: Any,
        path: str,
        hint: Optional[ExtractHint] = None
    ) -> Any:
        """
        Extract field value from MT message.

        Path format: field tag (e.g., "32A", "59", "50K")
        Can include subfield: "32A.date", "32A.currency", "32A.amount"
        """
        # Parse field tag and optional subfield
        parts = path.split(".")
        field_tag = parts[0]
        subfield = parts[1] if len(parts) > 1 else None

        # Build regex pattern
        pattern = rf':({field_tag}):(.*?)(?=:\d{{2}}[A-Z]?:|-\}})'

        return (field_tag, subfield, pattern)

    def get_schema(self) -> StructType:
        """Get schema for parsed MT output."""
        return StructType([
            StructField("content", StringType(), True),
            StructField("basic_header", StringType(), True),
            StructField("application_header", StringType(), True),
            StructField("user_header", StringType(), True),
            StructField("text_block", StringType(), True),
            StructField("trailer", StringType(), True),
            StructField("_parse_metadata", StructType([
                StructField("format", StringType(), True),
                StructField("parser", StringType(), True),
                StructField("message_type", StringType(), True),
            ]), True),
        ])

    def get_field_extraction_expr(self, field_tag: str) -> str:
        """
        Get Spark SQL expression to extract a field value.

        Args:
            field_tag: MT field tag (e.g., "32A", "59")

        Returns:
            Spark SQL regexp_extract expression
        """
        # Handle option letters (A, B, C, D, F, K, etc.)
        if len(field_tag) == 3 and field_tag[2].isalpha():
            base_tag = field_tag[:2]
            option = field_tag[2]
            pattern = rf':({field_tag}):(.*?)(?=:\d{{2}}[A-Z]?:|-\}})'
        else:
            pattern = rf':({field_tag}[A-Z]?):(.*?)(?=:\d{{2}}[A-Z]?:|-\}})'

        return f"regexp_extract(text_block, '{pattern}', 2)"


class SWIFTMTParser(MTParser):
    """
    Enhanced SWIFT MT parser with structured field parsing.

    Provides:
    - Automatic subfield parsing for composite fields (32A, 50F, 59F)
    - BIC validation
    - Account format detection (IBAN, BBAN)
    """

    # Composite field parsers
    COMPOSITE_PARSERS = {
        "32A": {
            "subfields": ["date", "currency", "amount"],
            "pattern": r"(\d{6})([A-Z]{3})([\d,\.]+)",
        },
        "33B": {
            "subfields": ["currency", "amount"],
            "pattern": r"([A-Z]{3})([\d,\.]+)",
        },
        "50F": {
            "subfields": ["party_identifier", "name", "address_lines"],
            "parser": "_parse_party_field",
        },
        "59F": {
            "subfields": ["account", "name", "address_lines"],
            "parser": "_parse_party_field",
        },
    }

    def extract_structured_field(self, field_tag: str, value: str) -> Dict[str, Any]:
        """
        Parse composite field into structured components.

        Args:
            field_tag: Field tag (e.g., "32A")
            value: Raw field value

        Returns:
            Dictionary with parsed subfields
        """
        if field_tag not in self.COMPOSITE_PARSERS:
            return {"value": value.strip()}

        parser_config = self.COMPOSITE_PARSERS[field_tag]

        if "parser" in parser_config:
            # Use custom parser method
            parser_method = getattr(self, parser_config["parser"])
            return parser_method(value)
        elif "pattern" in parser_config:
            # Use regex pattern
            import re
            match = re.match(parser_config["pattern"], value.strip())
            if match:
                return dict(zip(parser_config["subfields"], match.groups()))

        return {"value": value.strip()}

    def _parse_party_field(self, value: str) -> Dict[str, Any]:
        """Parse party identification field (50F, 59F format)."""
        result = {
            "party_identifier": None,
            "name": None,
            "address_lines": [],
            "country": None,
        }

        lines = value.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for structured line codes
            if line.startswith("/"):
                # Account or identifier
                result["party_identifier"] = line[1:]
            elif line.startswith("1/"):
                result["name"] = line[2:]
            elif line.startswith("2/"):
                result["address_lines"].append(line[2:])
            elif line.startswith("3/"):
                # Country and town
                parts = line[2:].split("/")
                if len(parts) >= 1:
                    result["country"] = parts[0][:2]
                if len(parts) >= 2:
                    result["address_lines"].append(parts[1])
            else:
                # Unstructured - assume name or address
                if result["name"] is None:
                    result["name"] = line
                else:
                    result["address_lines"].append(line)

        return result

    def get_value_date_expr(self) -> str:
        """Get expression to extract and convert value date from 32A."""
        return """
        to_date(
            concat('20', substring(regexp_extract(text_block, ':32A:(\\d{6})', 1), 1, 6)),
            'yyyyMMdd'
        )
        """

    def get_amount_expr(self) -> str:
        """Get expression to extract amount from 32A."""
        return """
        cast(
            replace(
                regexp_extract(text_block, ':32A:\\d{6}[A-Z]{3}([\\d,\\.]+)', 1),
                ',', '.'
            ) as decimal(18,2)
        )
        """

    def get_currency_expr(self) -> str:
        """Get expression to extract currency from 32A."""
        return "regexp_extract(text_block, ':32A:\\d{6}([A-Z]{3})', 1)"

    def get_bic_validation_expr(self, bic_field: str) -> str:
        """Get expression to validate BIC format."""
        return f"""
        regexp_extract({bic_field}, '^[A-Z]{{4}}[A-Z]{{2}}[A-Z0-9]{{2}}([A-Z0-9]{{3}})?$', 0)
        = {bic_field}
        """

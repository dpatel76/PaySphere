"""
GPS Payments CDM - Fixed-Width Parser
======================================

Parser for fixed-width record formats including Fedwire and ACH.
Extracts fields based on positional specifications.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, lit, substring, trim, struct, when, length,
    regexp_replace, coalesce,
)
from pyspark.sql.types import (
    StructType, StructField, StringType,
)

from gps_cdm.ingestion.core.models import SourceConfig, ExtractHint
from gps_cdm.ingestion.parsers.base import BaseParser, ParseResult


@dataclass
class FieldSpec:
    """Specification for a fixed-width field."""
    name: str
    start: int  # 1-based position
    length: int
    data_type: str = "string"
    padding: str = " "  # Padding character
    alignment: str = "left"  # left or right

    @property
    def end(self) -> int:
        """End position (1-based, inclusive)."""
        return self.start + self.length - 1


# Fedwire message format specifications
FEDWIRE_SPECS = {
    "funds_transfer": {
        "record_length": 500,
        "fields": [
            FieldSpec("record_type", 1, 1),
            FieldSpec("type_subtype", 2, 4),
            FieldSpec("imad", 6, 22),
            FieldSpec("amount", 28, 12, "decimal", "0", "right"),
            FieldSpec("sender_di", 40, 9),
            FieldSpec("receiver_di", 49, 9),
            FieldSpec("business_function", 58, 3),
            FieldSpec("transaction_type", 61, 3),
            FieldSpec("sender_reference", 64, 16),
            FieldSpec("sender_account", 80, 34),
            FieldSpec("beneficiary_account", 114, 34),
            FieldSpec("beneficiary_name", 148, 35),
            FieldSpec("originator_name", 183, 35),
            FieldSpec("originator_address", 218, 105),
            FieldSpec("beneficiary_address", 323, 105),
            FieldSpec("originator_to_beneficiary", 428, 70),
        ],
    },
}

# ACH (NACHA) format specifications
ACH_SPECS = {
    "file_header": {
        "record_length": 94,
        "record_type": "1",
        "fields": [
            FieldSpec("record_type", 1, 1),
            FieldSpec("priority_code", 2, 2),
            FieldSpec("immediate_destination", 4, 10),
            FieldSpec("immediate_origin", 14, 10),
            FieldSpec("file_creation_date", 24, 6),
            FieldSpec("file_creation_time", 30, 4),
            FieldSpec("file_id_modifier", 34, 1),
            FieldSpec("record_size", 35, 3),
            FieldSpec("blocking_factor", 38, 2),
            FieldSpec("format_code", 40, 1),
            FieldSpec("destination_name", 41, 23),
            FieldSpec("origin_name", 64, 23),
            FieldSpec("reference_code", 87, 8),
        ],
    },
    "batch_header": {
        "record_length": 94,
        "record_type": "5",
        "fields": [
            FieldSpec("record_type", 1, 1),
            FieldSpec("service_class_code", 2, 3),
            FieldSpec("company_name", 5, 16),
            FieldSpec("company_discretionary_data", 21, 20),
            FieldSpec("company_identification", 41, 10),
            FieldSpec("standard_entry_class", 51, 3),
            FieldSpec("company_entry_description", 54, 10),
            FieldSpec("company_descriptive_date", 64, 6),
            FieldSpec("effective_entry_date", 70, 6),
            FieldSpec("settlement_date", 76, 3),
            FieldSpec("originator_status", 79, 1),
            FieldSpec("odfi_identification", 80, 8),
            FieldSpec("batch_number", 88, 7),
        ],
    },
    "entry_detail": {
        "record_length": 94,
        "record_type": "6",
        "fields": [
            FieldSpec("record_type", 1, 1),
            FieldSpec("transaction_code", 2, 2),
            FieldSpec("rdfi_identification", 4, 8),
            FieldSpec("check_digit", 12, 1),
            FieldSpec("dfi_account_number", 13, 17),
            FieldSpec("amount", 30, 10, "decimal", "0", "right"),
            FieldSpec("individual_identification", 40, 15),
            FieldSpec("individual_name", 55, 22),
            FieldSpec("discretionary_data", 77, 2),
            FieldSpec("addenda_indicator", 79, 1),
            FieldSpec("trace_number", 80, 15),
        ],
    },
    "batch_control": {
        "record_length": 94,
        "record_type": "8",
        "fields": [
            FieldSpec("record_type", 1, 1),
            FieldSpec("service_class_code", 2, 3),
            FieldSpec("entry_addenda_count", 5, 6),
            FieldSpec("entry_hash", 11, 10),
            FieldSpec("total_debit_amount", 21, 12, "decimal", "0", "right"),
            FieldSpec("total_credit_amount", 33, 12, "decimal", "0", "right"),
            FieldSpec("company_identification", 45, 10),
            FieldSpec("message_authentication_code", 55, 19),
            FieldSpec("reserved", 74, 6),
            FieldSpec("odfi_identification", 80, 8),
            FieldSpec("batch_number", 88, 7),
        ],
    },
    "file_control": {
        "record_length": 94,
        "record_type": "9",
        "fields": [
            FieldSpec("record_type", 1, 1),
            FieldSpec("batch_count", 2, 6),
            FieldSpec("block_count", 8, 6),
            FieldSpec("entry_addenda_count", 14, 8),
            FieldSpec("entry_hash", 22, 10),
            FieldSpec("total_debit_amount", 32, 12, "decimal", "0", "right"),
            FieldSpec("total_credit_amount", 44, 12, "decimal", "0", "right"),
            FieldSpec("reserved", 56, 39),
        ],
    },
}


class FixedWidthParser(BaseParser):
    """
    Parser for fixed-width record formats.

    Supports:
    - Positional field extraction
    - Multiple record types in same file
    - Numeric field parsing (removing padding)
    - Field-level type conversion
    """

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self.record_length = config.record_length
        self.field_specs: List[FieldSpec] = []
        self._record_type_position: Optional[Tuple[int, int]] = None

    def set_field_specs(self, specs: List[FieldSpec]) -> None:
        """Set field specifications for parsing."""
        self.field_specs = specs

    def set_record_type_position(self, start: int, length: int) -> None:
        """Set position of record type indicator."""
        self._record_type_position = (start, length)

    def parse(self, source_df: DataFrame) -> ParseResult:
        """
        Parse fixed-width content from source DataFrame.

        Expects DataFrame with 'content' column containing fixed-width records.
        """
        # Validate record length if specified
        if self.record_length:
            # Filter records with correct length
            parsed_df = source_df.filter(
                length(col("content")) >= self.record_length
            )
        else:
            parsed_df = source_df

        # Extract fields based on specifications
        for spec in self.field_specs:
            parsed_df = parsed_df.withColumn(
                spec.name,
                self._extract_field(col("content"), spec)
            )

        # Add parse metadata
        parsed_df = parsed_df.withColumn(
            "_parse_metadata",
            struct(
                lit(self.config.format.value).alias("format"),
                lit(self.config.parser).alias("parser"),
                lit(self.record_length).alias("record_length"),
            )
        )

        row_count = parsed_df.count()

        return ParseResult(
            data=parsed_df,
            row_count=row_count,
            metadata={
                "record_length": self.record_length,
                "field_count": len(self.field_specs),
            }
        )

    def _extract_field(self, content_col, spec: FieldSpec):
        """Extract and convert a field from content."""
        # Extract substring (Spark substring is 1-based)
        extracted = substring(content_col, spec.start, spec.length)

        # Trim padding
        if spec.alignment == "right" and spec.padding != " ":
            # Right-aligned, left-padded (typically numeric)
            extracted = regexp_replace(extracted, f"^{spec.padding}+", "")
        elif spec.alignment == "left":
            # Left-aligned, right-padded
            extracted = trim(extracted)

        return extracted

    def extract_value(
        self,
        data: Any,
        path: str,
        hint: Optional[ExtractHint] = None
    ) -> Any:
        """
        Extract value by field name or position range.

        Args:
            data: Record string
            path: Field name or "start:length" (e.g., "28:12")

        Returns:
            Field specification or position tuple
        """
        # Check if position range format
        if ":" in path:
            parts = path.split(":")
            start = int(parts[0])
            length = int(parts[1])
            return (start, length)

        # Otherwise, field name - look up in specs
        for spec in self.field_specs:
            if spec.name == path:
                return spec

        return path

    def get_schema(self) -> StructType:
        """Get schema for parsed output."""
        fields = []
        for spec in self.field_specs:
            fields.append(StructField(spec.name, StringType(), True))

        fields.append(
            StructField("_parse_metadata", StructType([
                StructField("format", StringType(), True),
                StructField("parser", StringType(), True),
                StructField("record_length", StringType(), True),
            ]), True)
        )

        return StructType(fields)

    def get_extraction_expr(
        self,
        path: str,
        data_type: str = "string"
    ) -> str:
        """
        Get Spark SQL expression for field extraction.

        Args:
            path: Field name or "start:length"
            data_type: Target data type

        Returns:
            Spark SQL expression
        """
        # Parse position
        if ":" in path:
            parts = path.split(":")
            start = int(parts[0])
            length = int(parts[1])
        else:
            # Look up field spec
            spec = None
            for s in self.field_specs:
                if s.name == path:
                    spec = s
                    break

            if spec:
                start = spec.start
                length = spec.length
            else:
                return f"`{path}`"  # Assume column name

        base_expr = f"TRIM(SUBSTRING(content, {start}, {length}))"

        # Add type casting
        if data_type == "int" or data_type == "integer":
            return f"CAST({base_expr} AS INT)"
        elif data_type == "decimal":
            # Handle implied decimal (e.g., last 2 digits are cents)
            return f"CAST({base_expr} AS DECIMAL(18,2)) / 100"
        elif data_type == "date":
            return f"TO_DATE({base_expr}, 'yyMMdd')"
        elif data_type == "datetime":
            return f"TO_TIMESTAMP({base_expr})"
        else:
            return base_expr


class FedwireParser(FixedWidthParser):
    """
    Specialized parser for Fedwire funds transfer messages.

    Reference: Federal Reserve Bank Fedwire Funds Service Format
    """

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)

        # Set Fedwire specifications
        fedwire_config = FEDWIRE_SPECS.get("funds_transfer", {})
        self.record_length = fedwire_config.get("record_length", 500)
        self.set_field_specs(fedwire_config.get("fields", []))

    def get_imad(self) -> str:
        """Get expression for Input Message Accountability Data."""
        return "TRIM(SUBSTRING(content, 6, 22))"

    def get_amount_expr(self) -> str:
        """Get expression for transaction amount (implied 2 decimals)."""
        return "CAST(TRIM(SUBSTRING(content, 28, 12)) AS DECIMAL(18,2)) / 100"


class ACHParser(FixedWidthParser):
    """
    Specialized parser for ACH (NACHA) format files.

    Reference: NACHA Operating Rules and Guidelines
    """

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self.record_length = 94  # Standard NACHA record length

    def parse(self, source_df: DataFrame) -> ParseResult:
        """
        Parse ACH file with multiple record types.

        Detects record type from first character and applies
        appropriate field specifications.
        """
        # Add record type column
        typed_df = source_df.withColumn(
            "record_type",
            substring(col("content"), 1, 1)
        )

        # Parse each record type separately
        parsed_dfs = []

        for record_type, spec in ACH_SPECS.items():
            rt_code = spec["record_type"]
            rt_df = typed_df.filter(col("record_type") == rt_code)

            if rt_df.count() > 0:
                self.set_field_specs(spec["fields"])
                for field_spec in spec["fields"]:
                    rt_df = rt_df.withColumn(
                        field_spec.name,
                        self._extract_field(col("content"), field_spec)
                    )
                rt_df = rt_df.withColumn(
                    "_record_type_name",
                    lit(record_type)
                )
                parsed_dfs.append(rt_df)

        # Union all record types
        if parsed_dfs:
            result_df = parsed_dfs[0]
            for df in parsed_dfs[1:]:
                # Align columns before union
                result_df = result_df.unionByName(df, allowMissingColumns=True)
        else:
            result_df = typed_df

        # Add parse metadata
        result_df = result_df.withColumn(
            "_parse_metadata",
            struct(
                lit(self.config.format.value).alias("format"),
                lit(self.config.parser).alias("parser"),
                lit(self.record_length).alias("record_length"),
            )
        )

        row_count = result_df.count()

        return ParseResult(
            data=result_df,
            row_count=row_count,
            metadata={
                "record_length": self.record_length,
                "record_types_found": [
                    spec["record_type"] for spec in ACH_SPECS.values()
                ],
            }
        )

    def get_entry_details_df(self, parsed_df: DataFrame) -> DataFrame:
        """Filter to entry detail records only."""
        return parsed_df.filter(col("record_type") == "6")

    def get_batch_headers_df(self, parsed_df: DataFrame) -> DataFrame:
        """Filter to batch header records only."""
        return parsed_df.filter(col("record_type") == "5")

    def get_sec_code_expr(self) -> str:
        """Get expression for Standard Entry Class code."""
        return "TRIM(SUBSTRING(content, 51, 3))"

    def get_entry_amount_expr(self) -> str:
        """Get expression for entry amount (implied 2 decimals)."""
        return "CAST(TRIM(SUBSTRING(content, 30, 10)) AS DECIMAL(18,2)) / 100"

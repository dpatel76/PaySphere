"""
GPS Payments CDM - CSV Parser
==============================

Parser for CSV and delimited file formats.
Supports header detection, custom delimiters, and encoding options.
"""

from typing import Any, Dict, List, Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, lit, split, struct, when, coalesce,
    trim, regexp_replace, element_at,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, ArrayType,
)

from gps_cdm.ingestion.core.models import SourceConfig, ExtractHint
from gps_cdm.ingestion.parsers.base import BaseParser, ParseResult


class CSVParser(BaseParser):
    """
    Parser for CSV and delimited file formats.

    Supports:
    - Custom delimiters (comma, tab, pipe, etc.)
    - Header row detection
    - Quote handling
    - Encoding options
    - Column name mapping
    """

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self.delimiter = config.delimiter or ","
        self.has_header = config.header if config.header is not None else True
        self.encoding = config.encoding or "utf-8"
        self._column_names: List[str] = []
        self._column_map: Dict[str, int] = {}

    def parse(self, source_df: DataFrame) -> ParseResult:
        """
        Parse CSV content from source DataFrame.

        Expects DataFrame with 'content' column containing CSV data
        OR a DataFrame already parsed by Spark's CSV reader.
        """
        # Check if already parsed (has multiple columns)
        if len(source_df.columns) > 2:
            # Assume already parsed by Spark CSV reader
            parsed_df = source_df
            self._column_names = source_df.columns
        else:
            # Parse from content column
            parsed_df = self._parse_csv_content(source_df)

        # Build column map
        self._column_map = {
            name: idx for idx, name in enumerate(self._column_names)
        }

        # Add parse metadata
        parsed_df = parsed_df.withColumn(
            "_parse_metadata",
            struct(
                lit(self.config.format.value).alias("format"),
                lit(self.config.parser).alias("parser"),
                lit(self.delimiter).alias("delimiter"),
                lit(self.has_header).alias("has_header"),
            )
        )

        row_count = parsed_df.count()

        return ParseResult(
            data=parsed_df,
            row_count=row_count,
            metadata={
                "delimiter": self.delimiter,
                "has_header": self.has_header,
                "column_count": len(self._column_names),
                "columns": self._column_names,
            }
        )

    def _parse_csv_content(self, source_df: DataFrame) -> DataFrame:
        """Parse CSV content string into columns."""
        # Split content by delimiter
        # Note: This is a simple implementation - for production,
        # consider proper CSV parsing with quote handling

        # Escape special regex characters in delimiter
        escaped_delim = self.delimiter
        if escaped_delim in r"\.^$*+?{}[]|()":
            escaped_delim = "\\" + escaped_delim

        # Split into array
        split_df = source_df.withColumn(
            "_fields",
            split(col("content"), escaped_delim)
        )

        # If has header, extract column names from first row
        if self.has_header:
            first_row = split_df.first()
            if first_row and first_row._fields:
                self._column_names = [
                    self._clean_column_name(f)
                    for f in first_row._fields
                ]
                # Skip header row
                split_df = split_df.filter(
                    col("content") != first_row.content
                )
            else:
                # Generate column names
                self._column_names = [f"col_{i}" for i in range(10)]
        else:
            # Detect number of columns
            first_row = split_df.first()
            if first_row and first_row._fields:
                num_cols = len(first_row._fields)
                self._column_names = [f"col_{i}" for i in range(num_cols)]

        # Expand array to columns
        for i, col_name in enumerate(self._column_names):
            split_df = split_df.withColumn(
                col_name,
                trim(element_at(col("_fields"), i + 1))
            )

        # Drop intermediate columns
        split_df = split_df.drop("_fields")

        return split_df

    def _clean_column_name(self, name: str) -> str:
        """Clean column name for use in DataFrame."""
        # Remove quotes, whitespace, special characters
        cleaned = name.strip().strip('"\'')
        cleaned = cleaned.replace(" ", "_").replace("-", "_")
        # Remove non-alphanumeric except underscore
        cleaned = "".join(c if c.isalnum() or c == "_" else "" for c in cleaned)
        return cleaned.lower() or "unnamed"

    def extract_value(
        self,
        data: Any,
        path: str,
        hint: Optional[ExtractHint] = None
    ) -> Any:
        """
        Extract value by column name or index.

        Args:
            data: Row data
            path: Column name or index (e.g., "amount" or "3")

        Returns:
            Column reference
        """
        # Check if numeric index
        if path.isdigit():
            return int(path)

        # Otherwise, column name
        return path

    def get_schema(self) -> StructType:
        """Get schema for parsed CSV output."""
        fields = [
            StructField(name, StringType(), True)
            for name in self._column_names
        ]
        fields.append(
            StructField("_parse_metadata", StructType([
                StructField("format", StringType(), True),
                StructField("parser", StringType(), True),
                StructField("delimiter", StringType(), True),
                StructField("has_header", StringType(), True),
            ]), True)
        )
        return StructType(fields)

    def get_column_expr(self, column_ref: str, data_type: str = "string") -> str:
        """
        Get Spark expression for column extraction.

        Args:
            column_ref: Column name or index
            data_type: Target data type

        Returns:
            Spark SQL expression
        """
        # Determine column name
        if column_ref.isdigit():
            idx = int(column_ref)
            if idx < len(self._column_names):
                col_name = self._column_names[idx]
            else:
                col_name = f"col_{idx}"
        else:
            col_name = column_ref

        base_expr = f"`{col_name}`"

        # Add type casting
        if data_type == "int" or data_type == "integer":
            return f"CAST({base_expr} AS INT)"
        elif data_type == "decimal":
            return f"CAST({base_expr} AS DECIMAL(18,4))"
        elif data_type == "boolean":
            return f"CAST({base_expr} AS BOOLEAN)"
        elif data_type == "date":
            return f"TO_DATE({base_expr})"
        elif data_type == "datetime":
            return f"TO_TIMESTAMP({base_expr})"
        else:
            return base_expr

    def get_column_names(self) -> List[str]:
        """Get list of column names."""
        return self._column_names.copy()

    def get_column_index(self, name: str) -> Optional[int]:
        """Get index of column by name."""
        return self._column_map.get(name.lower())


class BatchFileParser(CSVParser):
    """
    Specialized parser for batch payment files.

    Handles common batch file patterns:
    - Header/detail/trailer records
    - Record type indicators
    - Control totals
    """

    RECORD_TYPES = {
        "header": ["H", "01", "HDR", "HEADER"],
        "detail": ["D", "02", "DTL", "DETAIL"],
        "trailer": ["T", "99", "TRL", "TRAILER"],
    }

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self.record_type_column: Optional[str] = None
        self.record_type_position: int = 0

    def detect_record_type_column(self, df: DataFrame) -> Optional[str]:
        """Detect which column contains record type indicator."""
        # Check first few columns for record type patterns
        for col_name in self._column_names[:3]:
            sample = df.select(col_name).distinct().collect()
            values = [row[0] for row in sample if row[0]]

            # Check if values match record type patterns
            all_patterns = (
                self.RECORD_TYPES["header"] +
                self.RECORD_TYPES["detail"] +
                self.RECORD_TYPES["trailer"]
            )
            if any(v in all_patterns for v in values):
                return col_name

        return None

    def parse(self, source_df: DataFrame) -> ParseResult:
        """Parse batch file with record type detection."""
        result = super().parse(source_df)

        # Detect record type column
        self.record_type_column = self.detect_record_type_column(result.data)

        result.metadata["record_type_column"] = self.record_type_column

        return result

    def get_detail_records_expr(self) -> str:
        """Get expression to filter detail records only."""
        if self.record_type_column:
            patterns = self.RECORD_TYPES["detail"]
            conditions = " OR ".join(
                f"`{self.record_type_column}` = '{p}'"
                for p in patterns
            )
            return f"({conditions})"
        return "TRUE"

    def get_header_record_expr(self) -> str:
        """Get expression to filter header record."""
        if self.record_type_column:
            patterns = self.RECORD_TYPES["header"]
            conditions = " OR ".join(
                f"`{self.record_type_column}` = '{p}'"
                for p in patterns
            )
            return f"({conditions})"
        return "FALSE"

"""
GPS Payments CDM - JSON Parser
===============================

Parser for JSON-based message formats including API payloads.
Uses Spark's native JSON support with JSONPath extraction.
"""

from typing import Any, Dict, List, Optional
import json

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, lit, from_json, get_json_object, json_tuple,
    struct, explode, explode_outer, when, coalesce,
    schema_of_json, to_json,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, ArrayType,
    MapType, LongType, DoubleType, BooleanType,
)

from gps_cdm.ingestion.core.models import SourceConfig, ExtractHint
from gps_cdm.ingestion.parsers.base import BaseParser, ParseResult


class JSONParser(BaseParser):
    """
    Parser for JSON message formats.

    Supports:
    - JSONPath extraction
    - Schema inference
    - Nested object/array handling
    - Streaming JSON (newline-delimited)
    """

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self._inferred_schema: Optional[StructType] = None

    def parse(self, source_df: DataFrame) -> ParseResult:
        """
        Parse JSON content from source DataFrame.

        Expects DataFrame with 'content' column containing JSON strings.
        """
        # Infer schema from sample if needed
        if self._inferred_schema is None:
            self._infer_schema(source_df)

        # Parse JSON into structured columns
        if self._inferred_schema:
            parsed_df = source_df.withColumn(
                "parsed",
                from_json(col("content"), self._inferred_schema)
            )
        else:
            # Keep as string, use get_json_object for extraction
            parsed_df = source_df

        # Add parse metadata
        parsed_df = parsed_df.withColumn(
            "_parse_metadata",
            struct(
                lit(self.config.format.value).alias("format"),
                lit(self.config.parser).alias("parser"),
            )
        )

        row_count = parsed_df.count()

        return ParseResult(
            data=parsed_df,
            row_count=row_count,
            metadata={
                "schema_inferred": self._inferred_schema is not None,
            }
        )

    def _infer_schema(self, source_df: DataFrame) -> None:
        """Infer JSON schema from sample data."""
        try:
            # Get sample JSON
            sample_row = source_df.select("content").first()
            if sample_row and sample_row.content:
                sample_json = sample_row.content
                # Use Spark's schema inference
                schema_json = self.spark.range(1).select(
                    schema_of_json(lit(sample_json))
                ).first()[0]
                # Parse schema string to StructType
                self._inferred_schema = StructType.fromJson(json.loads(schema_json))
        except Exception:
            # Schema inference failed, will use string extraction
            self._inferred_schema = None

    def extract_value(
        self,
        data: Any,
        path: str,
        hint: Optional[ExtractHint] = None
    ) -> Any:
        """
        Extract value using JSONPath.

        Args:
            data: JSON string or parsed object
            path: JSONPath expression (e.g., "$.payment.amount")
            hint: Extraction hint

        Returns:
            JSONPath expression for Spark
        """
        # Normalize path to JSONPath format
        if not path.startswith("$"):
            path = f"$.{path}"

        return path

    def get_schema(self) -> StructType:
        """Get schema for parsed JSON output."""
        if self._inferred_schema:
            return StructType([
                StructField("content", StringType(), True),
                StructField("parsed", self._inferred_schema, True),
                StructField("_parse_metadata", StructType([
                    StructField("format", StringType(), True),
                    StructField("parser", StringType(), True),
                ]), True),
            ])

        return StructType([
            StructField("content", StringType(), True),
            StructField("_parse_metadata", StructType([
                StructField("format", StringType(), True),
                StructField("parser", StringType(), True),
            ]), True),
        ])

    def get_extraction_expr(self, path: str, data_type: str = "string") -> str:
        """
        Generate Spark SQL expression for JSON extraction.

        Args:
            path: JSONPath (e.g., "$.payment.amount" or "payment.amount")
            data_type: Target data type

        Returns:
            Spark SQL expression string
        """
        # Normalize path
        if not path.startswith("$"):
            json_path = f"$.{path}"
        else:
            json_path = path

        base_expr = f"get_json_object(content, '{json_path}')"

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

    def get_array_extraction_expr(self, array_path: str, element_path: str = None) -> str:
        """
        Generate expression to extract array elements.

        Args:
            array_path: Path to array (e.g., "$.transactions")
            element_path: Optional path within each element

        Returns:
            Spark SQL expression for array extraction
        """
        if not array_path.startswith("$"):
            array_path = f"$.{array_path}"

        if element_path:
            # Extract specific field from each element
            return f"""
            transform(
                from_json(get_json_object(content, '{array_path}'), 'array<string>'),
                x -> get_json_object(x, '$.{element_path}')
            )
            """
        else:
            # Return full array
            return f"from_json(get_json_object(content, '{array_path}'), 'array<string>')"


class APIPayloadParser(JSONParser):
    """
    Specialized parser for REST API JSON payloads.

    Handles common API patterns:
    - Envelope wrapping (data, meta, errors)
    - Pagination
    - HATEOAS links
    """

    # Common API envelope patterns
    ENVELOPE_PATTERNS = {
        "data": ["data", "result", "results", "payload", "response"],
        "meta": ["meta", "metadata", "_meta"],
        "pagination": ["pagination", "paging", "page_info"],
        "errors": ["errors", "error", "error_messages"],
    }

    def __init__(self, spark: SparkSession, config: SourceConfig):
        super().__init__(spark, config)
        self.envelope_path: Optional[str] = None

    def detect_envelope(self, sample_json: str) -> Optional[str]:
        """Detect API envelope pattern and return path to data."""
        try:
            data = json.loads(sample_json)
            if isinstance(data, dict):
                for pattern in self.ENVELOPE_PATTERNS["data"]:
                    if pattern in data:
                        return f"$.{pattern}"
        except Exception:
            pass
        return None

    def parse(self, source_df: DataFrame) -> ParseResult:
        """Parse API payload, unwrapping envelope if present."""
        # Detect envelope from sample
        sample_row = source_df.select("content").first()
        if sample_row and sample_row.content:
            self.envelope_path = self.detect_envelope(sample_row.content)

        result = super().parse(source_df)

        # Add envelope info to metadata
        result.metadata["envelope_detected"] = self.envelope_path is not None
        result.metadata["envelope_path"] = self.envelope_path

        return result

    def get_data_extraction_expr(self) -> str:
        """Get expression to extract data from envelope."""
        if self.envelope_path:
            return f"get_json_object(content, '{self.envelope_path}')"
        return "content"

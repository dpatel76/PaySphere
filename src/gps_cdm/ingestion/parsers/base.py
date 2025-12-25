"""
GPS Payments CDM - Base Parser Interface
=========================================

Abstract base class for all format-specific parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from gps_cdm.ingestion.core.models import SourceConfig, ExtractHint


@dataclass
class ParseResult:
    """Result of parsing source data."""
    data: DataFrame
    row_count: int
    parse_errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        return len(self.parse_errors) > 0

    @property
    def error_count(self) -> int:
        return len(self.parse_errors)


@dataclass
class ExtractionContext:
    """Context for value extraction from parsed data."""
    root_element: Optional[str] = None
    namespace: Optional[str] = None
    current_path: str = ""
    parent_data: Optional[Dict] = None


class BaseParser(ABC):
    """
    Abstract base class for source format parsers.

    Each parser implementation handles a specific format:
    - XMLParser: ISO 20022, regional XML formats
    - MTParser: SWIFT MT messages
    - JSONParser: API payloads
    - CSVParser: Batch files
    - FixedWidthParser: Fedwire, ACH formats
    """

    def __init__(self, spark: SparkSession, config: SourceConfig):
        self.spark = spark
        self.config = config

    @abstractmethod
    def parse(self, source_df: DataFrame) -> ParseResult:
        """
        Parse source DataFrame into structured format.

        Args:
            source_df: DataFrame with raw message data (typically a 'content' column)

        Returns:
            ParseResult with parsed DataFrame
        """
        pass

    @abstractmethod
    def extract_value(
        self,
        data: Any,
        path: str,
        hint: Optional[ExtractHint] = None
    ) -> Any:
        """
        Extract a value from parsed data using the specified path.

        Args:
            data: Parsed data structure (element, dict, etc.)
            path: Path to the value (XPath, JSONPath, field name)
            hint: Extraction hint for ambiguous cases

        Returns:
            Extracted value or None if not found
        """
        pass

    @abstractmethod
    def get_schema(self) -> StructType:
        """
        Get the Spark schema for parsed output.

        Returns:
            StructType for the parsed DataFrame
        """
        pass

    def validate_config(self) -> List[str]:
        """
        Validate parser configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        return []

    def get_parser_info(self) -> Dict[str, Any]:
        """Get parser metadata."""
        return {
            "parser_type": self.__class__.__name__,
            "format": self.config.format.value,
            "parser_name": self.config.parser,
        }

"""
GPS Payments CDM - Parser Registry
===================================

Registry for format-specific parsers.
Supports dynamic parser registration and lookup.
"""

from typing import Dict, Type, Optional, List
from pyspark.sql import SparkSession

from gps_cdm.ingestion.core.models import SourceConfig, SourceFormat
from gps_cdm.ingestion.parsers.base import BaseParser


class ParserRegistry:
    """
    Registry for message format parsers.

    Manages registration and instantiation of parsers for different
    source formats (XML, SWIFT MT, JSON, CSV, etc.).

    Usage:
        registry = ParserRegistry(spark)

        # Register custom parser
        registry.register("xml", "iso20022", ISO20022Parser)

        # Get parser for config
        parser = registry.get_parser(source_config)
    """

    # Default parser mappings
    # Format -> {parser_name -> parser_class}
    _parsers: Dict[SourceFormat, Dict[str, Type[BaseParser]]] = {}

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self._initialize_default_parsers()

    def _initialize_default_parsers(self) -> None:
        """Register default parsers for all supported formats."""
        # Import here to avoid circular imports
        from gps_cdm.ingestion.parsers.xml_parser import XMLParser, ISO20022Parser
        from gps_cdm.ingestion.parsers.mt_parser import MTParser, SWIFTMTParser
        from gps_cdm.ingestion.parsers.json_parser import JSONParser
        from gps_cdm.ingestion.parsers.csv_parser import CSVParser
        from gps_cdm.ingestion.parsers.fixed_width_parser import FixedWidthParser

        # XML parsers
        self.register(SourceFormat.XML, "generic", XMLParser)
        self.register(SourceFormat.XML, "iso20022", ISO20022Parser)
        self.register(SourceFormat.XML, "pain", ISO20022Parser)
        self.register(SourceFormat.XML, "pacs", ISO20022Parser)
        self.register(SourceFormat.XML, "camt", ISO20022Parser)

        # SWIFT MT parsers
        self.register(SourceFormat.SWIFT_MT, "generic", MTParser)
        self.register(SourceFormat.SWIFT_MT, "swift", SWIFTMTParser)

        # JSON parsers
        self.register(SourceFormat.JSON, "generic", JSONParser)
        self.register(SourceFormat.JSON, "api", JSONParser)

        # CSV parsers
        self.register(SourceFormat.CSV, "generic", CSVParser)
        self.register(SourceFormat.CSV, "batch", CSVParser)

        # Fixed-width parsers
        self.register(SourceFormat.FIXED_WIDTH, "generic", FixedWidthParser)
        self.register(SourceFormat.FIXED_WIDTH, "fedwire", FixedWidthParser)
        self.register(SourceFormat.FIXED_WIDTH, "ach", FixedWidthParser)

    def register(
        self,
        format_type: SourceFormat,
        parser_name: str,
        parser_class: Type[BaseParser]
    ) -> None:
        """
        Register a parser for a format and name combination.

        Args:
            format_type: Source format (XML, SWIFT_MT, etc.)
            parser_name: Parser identifier
            parser_class: Parser class to instantiate
        """
        if format_type not in self._parsers:
            self._parsers[format_type] = {}

        self._parsers[format_type][parser_name.lower()] = parser_class

    def get_parser(self, config: SourceConfig) -> BaseParser:
        """
        Get parser instance for the given configuration.

        Args:
            config: Source configuration with format and parser name

        Returns:
            Instantiated parser

        Raises:
            ValueError if no parser found for config
        """
        format_type = config.format
        parser_name = config.parser.lower()

        if format_type not in self._parsers:
            raise ValueError(f"No parsers registered for format: {format_type.value}")

        format_parsers = self._parsers[format_type]

        if parser_name not in format_parsers:
            # Try generic parser
            if "generic" in format_parsers:
                parser_class = format_parsers["generic"]
            else:
                available = list(format_parsers.keys())
                raise ValueError(
                    f"No parser '{parser_name}' for format {format_type.value}. "
                    f"Available: {available}"
                )
        else:
            parser_class = format_parsers[parser_name]

        return parser_class(self.spark, config)

    def list_parsers(self) -> Dict[str, List[str]]:
        """List all registered parsers by format."""
        return {
            fmt.value: list(parsers.keys())
            for fmt, parsers in self._parsers.items()
        }

    def has_parser(self, format_type: SourceFormat, parser_name: str) -> bool:
        """Check if a parser is registered."""
        if format_type not in self._parsers:
            return False
        return parser_name.lower() in self._parsers[format_type]

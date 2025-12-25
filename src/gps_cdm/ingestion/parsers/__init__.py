"""Parser implementations for various source formats."""

from gps_cdm.ingestion.parsers.registry import ParserRegistry
from gps_cdm.ingestion.parsers.base import BaseParser, ParseResult
from gps_cdm.ingestion.parsers.xml_parser import XMLParser, ISO20022Parser
from gps_cdm.ingestion.parsers.mt_parser import MTParser, SWIFTMTParser
from gps_cdm.ingestion.parsers.json_parser import JSONParser
from gps_cdm.ingestion.parsers.csv_parser import CSVParser
from gps_cdm.ingestion.parsers.fixed_width_parser import FixedWidthParser

__all__ = [
    "ParserRegistry",
    "BaseParser",
    "ParseResult",
    "XMLParser",
    "ISO20022Parser",
    "MTParser",
    "SWIFTMTParser",
    "JSONParser",
    "CSVParser",
    "FixedWidthParser",
]

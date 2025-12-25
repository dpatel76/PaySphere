"""
GPS Payments CDM - Transformation Layer
=======================================

Provides transformation capabilities from source formats to CDM,
and from CDM to regulatory report formats.

Key Components:
- mappings: Machine-readable mapping registry referencing /documents/mappings/
- parsers: Source format parsers (ISO 20022 XML, SWIFT MT, regional formats)
- generators: Regulatory report generators (FinCEN, AUSTRAC, FINTRAC, etc.)

Reference Documents:
- /documents/mappings/standards/ - Payment standard mappings (69 standards)
- /documents/mappings/reports/ - Regulatory report mappings (32+ reports)
"""

from gps_cdm.transformations.registry import MappingRegistry
from gps_cdm.transformations.engine import TransformationEngine

__all__ = [
    "MappingRegistry",
    "TransformationEngine",
]

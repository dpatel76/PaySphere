"""
GPS Payments CDM - Configuration-Driven Ingestion Framework
============================================================

A declarative, YAML-based framework for transforming payment messages
from any source format to the GPS Payments CDM.

Key Principles:
- Configuration over code: Add new standards via YAML, not Python
- Single execution engine: One optimized engine for all mappings
- Full traceability: Every field transformation is auditable
- Performance first: Generates native Spark SQL where possible

Components:
- MappingCompiler: Compiles YAML to executable plans
- ParserRegistry: Format-specific parsers (XML, MT, JSON, CSV)
- TransformLibrary: 50+ reusable transform functions
- ExecutionEngine: Spark-based execution with optimization
- ValidationEngine: Declarative validation rules

Usage:
    from gps_cdm.ingestion import ConfigDrivenIngestion

    ingestion = ConfigDrivenIngestion(spark)

    # Process with a single mapping
    result = ingestion.process(
        source_df=raw_messages,
        mapping_path="/mappings/standards/pain_001.yaml"
    )

    # Or process all mappings for a message type
    result = ingestion.process_by_type(
        source_df=raw_messages,
        message_type="pain.001"
    )

Mapping Reference:
    YAML mappings: /mappings/standards/, /mappings/reports/
    Detailed docs: /documents/mappings/
"""

from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion
from gps_cdm.ingestion.core.compiler import MappingCompiler, CompiledMapping
from gps_cdm.ingestion.core.models import (
    MappingConfig,
    FieldMapping,
    SourceConfig,
    TransformConfig,
    ValidationRule,
)
from gps_cdm.ingestion.parsers.registry import ParserRegistry
from gps_cdm.ingestion.transforms.library import TransformLibrary

__all__ = [
    "ConfigDrivenIngestion",
    "MappingCompiler",
    "CompiledMapping",
    "MappingConfig",
    "FieldMapping",
    "SourceConfig",
    "TransformConfig",
    "ValidationRule",
    "ParserRegistry",
    "TransformLibrary",
]

__version__ = "1.0.0"

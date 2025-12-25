"""Core ingestion framework components."""

from gps_cdm.ingestion.core.models import (
    MappingConfig,
    FieldMapping,
    SourceConfig,
    TransformConfig,
    ValidationRule,
    EntityExtraction,
    QualityConfig,
    OptimizationConfig,
)
from gps_cdm.ingestion.core.compiler import MappingCompiler, CompiledMapping
from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion, IngestionResult

__all__ = [
    "MappingConfig",
    "FieldMapping",
    "SourceConfig",
    "TransformConfig",
    "ValidationRule",
    "EntityExtraction",
    "QualityConfig",
    "OptimizationConfig",
    "MappingCompiler",
    "CompiledMapping",
    "ConfigDrivenIngestion",
    "IngestionResult",
]

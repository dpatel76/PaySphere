"""
GPS CDM - Ingestion Orchestration Framework
============================================

This module provides the production-grade orchestration layer for the
GPS CDM ingestion pipeline, implementing:

- Medallion Architecture (Bronze → Silver → Gold)
- Delta Lake persistence
- Checkpoint/restart capability for large feeds
- Lineage tracking and persistence
- Error handling with dead-letter tables
- Batch tracking and observability

Architecture:
    Source Files → Auto Loader → Bronze (Raw) → Silver (CDM) → Gold (Analytics)
                                     ↓              ↓             ↓
                              Lineage Table   Lineage Table   Lineage Table
                                     ↓              ↓             ↓
                              Error Table    Error Table    Error Table
"""

from gps_cdm.ingestion.orchestration.medallion import MedallionOrchestrator
from gps_cdm.ingestion.orchestration.batch_tracker import BatchTracker, BatchStatus
from gps_cdm.ingestion.orchestration.lineage_manager import LineageManager
from gps_cdm.ingestion.orchestration.error_handler import ErrorHandler

__all__ = [
    "MedallionOrchestrator",
    "BatchTracker",
    "BatchStatus",
    "LineageManager",
    "ErrorHandler",
]

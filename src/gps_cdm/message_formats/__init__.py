"""
GPS CDM Message Format Extractors

This module provides extractor classes for each supported payment message format.
Each message format has its own subpackage with extractors for:
- Bronze layer: Raw message ingestion
- Silver layer: Parsed field extraction
- Gold layer: CDM entity extraction

Folder Structure:
    message_formats/
    ├── base/           # Base classes and registry
    ├── pain001/        # ISO 20022 pain.001 (Customer Credit Transfer Initiation)
    ├── mt103/          # SWIFT MT103 (Single Customer Credit Transfer)
    ├── pacs008/        # ISO 20022 pacs.008 (FI to FI Credit Transfer)
    ├── fedwire/        # Fedwire (US RTGS)
    └── ... (60+ additional formats)

Usage:
    from gps_cdm.message_formats import get_extractor
    from gps_cdm.message_formats.pain001 import Pain001Extractor

    extractor = get_extractor('pain.001')
    silver_record = extractor.extract_silver(msg_content, raw_id, stg_id, batch_id)
"""

from .base import BaseExtractor, ExtractorRegistry

__all__ = [
    'BaseExtractor',
    'ExtractorRegistry',
    'get_extractor',
    'list_extractors',
]


def get_extractor(message_type: str) -> BaseExtractor:
    """Get the extractor for a message type.

    Args:
        message_type: Message type identifier (e.g., 'pain.001', 'MT103')

    Returns:
        Extractor instance for the message type

    Raises:
        ValueError: If no extractor is registered for the message type
    """
    extractor = ExtractorRegistry.get(message_type)
    if not extractor:
        raise ValueError(f"No extractor registered for message type: {message_type}")
    return extractor


def list_extractors() -> list:
    """List all registered message type extractors."""
    return ExtractorRegistry.list_types()

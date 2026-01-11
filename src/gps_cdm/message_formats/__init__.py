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
    ├── pacs008/        # ISO 20022 pacs.008 (FI to FI Credit Transfer)
    ├── camt053/        # ISO 20022 camt.053 (Bank to Customer Statement)
    ├── fedwire/        # Fedwire (US RTGS)
    ├── fednow/         # FedNow (US Instant)
    ├── ach/            # NACHA ACH
    ├── chips/          # CHIPS (US Large Value)
    ├── sepa/           # SEPA Credit Transfer
    ├── rtp/            # TCH RTP (US Real-Time Payments)
    ├── chaps/          # UK CHAPS
    ├── bacs/           # UK BACS
    ├── fps/            # UK Faster Payments Service
    ├── target2/        # Eurozone TARGET2
    ├── npp/            # Australia NPP
    ├── upi/            # India UPI
    ├── pix/            # Brazil PIX
    ├── rtgs_hk/        # Hong Kong RTGS (CHATS)
    ├── meps_plus/      # Singapore MEPS+
    ├── bojnet/         # Japan BOJ-NET
    ├── kftc/           # Korea KFTC
    ├── cnaps/          # China CNAPS
    ├── sarie/          # Saudi Arabia SARIE
    ├── uaefts/         # UAE Funds Transfer System
    ├── promptpay/      # Thailand PromptPay
    ├── paynow/         # Singapore PayNow
    ├── instapay/       # Philippines InstaPay
    └── ... (additional formats)

Usage:
    from gps_cdm.message_formats import get_extractor
    from gps_cdm.message_formats.pain001 import Pain001Extractor

    extractor = get_extractor('pain.001')
    silver_record = extractor.extract_silver(msg_content, raw_id, stg_id, batch_id)
"""

from .base import BaseExtractor, ExtractorRegistry

# Import all extractors to trigger registration
# ISO 20022 Payment Messages
from . import pain001
from . import pacs008

# ISO 20022 Statement Messages
from . import camt053

# NOTE: All SWIFT MT messages decommissioned by SWIFT in November 2025
# Use ISO 20022 equivalents: MT103→pacs.008, MT202→pacs.009, MT940/MT950→camt.053

# US Payment Schemes
from . import fedwire
from . import fednow
from . import ach
from . import chips
from . import rtp

# EU/UK Payment Schemes
from . import sepa
from . import chaps
from . import bacs
from . import fps
from . import target2

# APAC Payment Schemes
from . import npp
from . import upi
from . import rtgs_hk
from . import meps_plus
from . import bojnet
from . import kftc
from . import cnaps

# Middle East Payment Schemes
from . import sarie
from . import uaefts

# LatAm Payment Schemes
from . import pix

# Southeast Asia Payment Schemes
from . import promptpay
from . import paynow
from . import instapay

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

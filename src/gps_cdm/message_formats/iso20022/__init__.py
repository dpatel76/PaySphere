"""ISO 20022 Base Classes for Payment Message Processing.

This package provides the foundational classes for parsing and extracting
ISO 20022 compliant payment messages. The architecture mirrors the actual
ISO 20022 standard hierarchy:

Layer 1: BaseISO20022Parser - Common XML parsing utilities
Layer 2: Message-type specific parsers (Pacs008Parser, Pacs009Parser, etc.)
Layer 3: System-specific parsers (FedwirePacs008Parser, ChapsPacs008Parser, etc.)

Usage Guidelines:
- FEDWIRE, CHIPS, CHAPS, FPS, FEDNOW, RTP, NPP, etc. use pacs.008
- TARGET2 uses pacs.009 for FI transfers
- pacs.002 for payment status reports (all systems)
- pacs.004 for payment returns (all systems)
- SEPA uses pain.001 for credit initiations, pain.008 for direct debit
- Statement formats use camt.053

IMPORTANT: Each payment system implements their own usage guidelines on top
of the base ISO 20022 schema. System-specific parsers/extractors inherit from
message-type base classes and apply system-specific rules.
"""

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor
from .pacs008 import Pacs008Parser, Pacs008Extractor
from .pacs009 import Pacs009Parser, Pacs009Extractor
from .pacs002 import Pacs002Parser, Pacs002Extractor
from .pacs004 import Pacs004Parser, Pacs004Extractor
from .pain001 import Pain001Parser, Pain001Extractor
from .pain008 import Pain008Parser, Pain008Extractor
from .camt053 import Camt053Parser, Camt053Extractor

__all__ = [
    # Base classes
    'BaseISO20022Parser',
    'BaseISO20022Extractor',
    # pacs.008 (FI to FI Customer Credit Transfer)
    'Pacs008Parser',
    'Pacs008Extractor',
    # pacs.009 (FI Credit Transfer - bank to bank)
    'Pacs009Parser',
    'Pacs009Extractor',
    # pacs.002 (Payment Status Report)
    'Pacs002Parser',
    'Pacs002Extractor',
    # pacs.004 (Payment Return)
    'Pacs004Parser',
    'Pacs004Extractor',
    # pain.001 (Customer Credit Transfer Initiation)
    'Pain001Parser',
    'Pain001Extractor',
    # pain.008 (Customer Direct Debit Initiation)
    'Pain008Parser',
    'Pain008Extractor',
    # camt.053 (Bank to Customer Account Statement)
    'Camt053Parser',
    'Camt053Extractor',
]

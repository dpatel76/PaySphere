"""
CDM Catalog Definitions - Module initialization
Imports all table definition files and provides a combined dictionary

ACTIVE EXTENSION TABLES (have mappings):
- ACH - US Automated Clearing House
- BACS - UK Bankers' Automated Clearing Services
- CNAPS - China National Advanced Payment System
- KFTC - Korea Financial Telecommunications & Clearings
- PAYNOW - Singapore PayNow
- PIX - Brazil Instant Payments
- PROMPTPAY - Thailand PromptPay
- SARIE - Saudi Arabia RTGS
- SWIFT - SWIFT MT messages (MT940, etc.)
- UPI - India Unified Payments Interface

DROPPED EXTENSION TABLES (no mappings - renamed with _drop suffix):
- FEDWIRE, SEPA, CHAPS, CHIPS, FEDNOW, FPS, TARGET2, NPP, RTGS_HK,
  UAEFTS, INSTAPAY, BOJNET, MEPS_PLUS, RTP, ISO20022
- cdm_payment_instruction (replaced by ISO semantic tables)
"""

from .extension_ach import CDM_EXTENSION_ACH
from .extension_regional import CDM_EXTENSION_REGIONAL
from .iso_pacs import CDM_ISO_PACS
from .iso_pain import CDM_ISO_PAIN
from .iso_camt import CDM_ISO_CAMT
from .supporting_tables import CDM_SUPPORTING_TABLES

# Combine all extension table definitions
CDM_EXTENSION_TABLES = {}
CDM_EXTENSION_TABLES.update(CDM_EXTENSION_ACH)
CDM_EXTENSION_TABLES.update(CDM_EXTENSION_REGIONAL)

# ISO 20022 semantic tables
CDM_ISO_TABLES = {}
CDM_ISO_TABLES.update(CDM_ISO_PACS)
CDM_ISO_TABLES.update(CDM_ISO_PAIN)
CDM_ISO_TABLES.update(CDM_ISO_CAMT)

# All CDM table definitions combined
CDM_ALL_TABLES = {}
CDM_ALL_TABLES.update(CDM_EXTENSION_TABLES)
CDM_ALL_TABLES.update(CDM_ISO_TABLES)
CDM_ALL_TABLES.update(CDM_SUPPORTING_TABLES)

__all__ = [
    'CDM_EXTENSION_TABLES',
    'CDM_EXTENSION_ACH',
    'CDM_EXTENSION_REGIONAL',
    'CDM_ISO_TABLES',
    'CDM_ISO_PACS',
    'CDM_ISO_PAIN',
    'CDM_ISO_CAMT',
    'CDM_SUPPORTING_TABLES',
    'CDM_ALL_TABLES',
]

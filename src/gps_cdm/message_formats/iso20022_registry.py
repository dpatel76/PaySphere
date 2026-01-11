"""ISO 20022 Base Type and Composite Format Extractor Registration.

This module registers:
1. ISO 20022 base message type extractors (pacs.002.base, pacs.004.base, pain.008.base)
2. Composite format extractors (e.g., TARGET2_pacs008, CHAPS_pacs009)

The composite formats inherit their parsing/extraction logic from the base ISO 20022
message types but are registered under their own names for the format routing system.

Registration Pattern:
    {PAYMENT_SYSTEM}_{MESSAGE_TYPE} -> Inherits from {MESSAGE_TYPE}.base

Examples:
    TARGET2_pacs008 -> Inherits from pacs.008.base
    TARGET2_pacs009 -> Inherits from pacs.009.base
    CHAPS_pacs008 -> Inherits from pacs.008.base
    SEPA_pain008 -> Inherits from pain.008.base
"""

import logging
from .base import ExtractorRegistry

# Import ISO 20022 base extractors
from .iso20022 import (
    Pacs008Extractor,
    Pacs009Extractor,
    Pacs002Extractor,
    Pacs004Extractor,
    Pain001Extractor,
    Pain008Extractor,
    Camt053Extractor,
)

logger = logging.getLogger(__name__)


# =============================================================================
# ISO 20022 BASE MESSAGE TYPE EXTRACTORS
# =============================================================================

# pacs.002.base - Payment Status Report
_pacs002_base = Pacs002Extractor()
_pacs002_base.MESSAGE_TYPE = 'pacs.002.base'
ExtractorRegistry.register('pacs.002.base', _pacs002_base)
ExtractorRegistry.register('pacs.002', _pacs002_base)
ExtractorRegistry.register('pacs_002', _pacs002_base)
ExtractorRegistry.register('pacs002', _pacs002_base)

# pacs.004.base - Payment Return
_pacs004_base = Pacs004Extractor()
_pacs004_base.MESSAGE_TYPE = 'pacs.004.base'
ExtractorRegistry.register('pacs.004.base', _pacs004_base)
ExtractorRegistry.register('pacs.004', _pacs004_base)
ExtractorRegistry.register('pacs_004', _pacs004_base)
ExtractorRegistry.register('pacs004', _pacs004_base)

# pacs.009.base - FI Credit Transfer (already registered in pacs009 module, adding base)
_pacs009_base = Pacs009Extractor()
_pacs009_base.MESSAGE_TYPE = 'pacs.009.base'
ExtractorRegistry.register('pacs.009.base', _pacs009_base)
ExtractorRegistry.register('pacs.009', _pacs009_base)
ExtractorRegistry.register('pacs_009', _pacs009_base)
ExtractorRegistry.register('pacs009', _pacs009_base)

# pain.008.base - Customer Direct Debit Initiation
_pain008_base = Pain008Extractor()
_pain008_base.MESSAGE_TYPE = 'pain.008.base'
ExtractorRegistry.register('pain.008.base', _pain008_base)
ExtractorRegistry.register('pain.008', _pain008_base)
ExtractorRegistry.register('pain_008', _pain008_base)
ExtractorRegistry.register('pain008', _pain008_base)


# =============================================================================
# COMPOSITE FORMAT EXTRACTORS (Payment System + Message Type)
# =============================================================================

def _create_composite_extractor(base_class, message_type: str, clearing_system: str = None):
    """Create a composite format extractor inheriting from a base class.

    Args:
        base_class: The ISO 20022 base extractor class
        message_type: The composite format identifier (e.g., 'TARGET2_pacs008')
        clearing_system: Optional clearing system code

    Returns:
        Configured extractor instance
    """
    extractor = base_class()
    extractor.MESSAGE_TYPE = message_type
    if clearing_system:
        extractor.CLEARING_SYSTEM = clearing_system
    return extractor


# -----------------------------------------------------------------------------
# TARGET2 Composite Formats (EU RTGS)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('TARGET2_pacs008', _create_composite_extractor(Pacs008Extractor, 'TARGET2_pacs008', 'TARGET2'))
ExtractorRegistry.register('TARGET2_pacs009', _create_composite_extractor(Pacs009Extractor, 'TARGET2_pacs009', 'TARGET2'))
ExtractorRegistry.register('TARGET2_pacs002', _create_composite_extractor(Pacs002Extractor, 'TARGET2_pacs002', 'TARGET2'))
ExtractorRegistry.register('TARGET2_pacs004', _create_composite_extractor(Pacs004Extractor, 'TARGET2_pacs004', 'TARGET2'))

# -----------------------------------------------------------------------------
# CHAPS Composite Formats (UK RTGS)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('CHAPS_pacs008', _create_composite_extractor(Pacs008Extractor, 'CHAPS_pacs008', 'CHAPS'))
ExtractorRegistry.register('CHAPS_pacs009', _create_composite_extractor(Pacs009Extractor, 'CHAPS_pacs009', 'CHAPS'))
ExtractorRegistry.register('CHAPS_pacs002', _create_composite_extractor(Pacs002Extractor, 'CHAPS_pacs002', 'CHAPS'))
ExtractorRegistry.register('CHAPS_pacs004', _create_composite_extractor(Pacs004Extractor, 'CHAPS_pacs004', 'CHAPS'))

# -----------------------------------------------------------------------------
# FPS Composite Formats (UK Faster Payments)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('FPS_pacs008', _create_composite_extractor(Pacs008Extractor, 'FPS_pacs008', 'FPS'))
ExtractorRegistry.register('FPS_pacs002', _create_composite_extractor(Pacs002Extractor, 'FPS_pacs002', 'FPS'))

# -----------------------------------------------------------------------------
# SEPA Composite Formats (EU Payments)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('SEPA_pacs008', _create_composite_extractor(Pacs008Extractor, 'SEPA_pacs008', 'SEPA'))
ExtractorRegistry.register('SEPA_pain001', _create_composite_extractor(Pain001Extractor, 'SEPA_pain001', 'SEPA'))
ExtractorRegistry.register('SEPA_pain008', _create_composite_extractor(Pain008Extractor, 'SEPA_pain008', 'SEPA'))
ExtractorRegistry.register('SEPA_pacs002', _create_composite_extractor(Pacs002Extractor, 'SEPA_pacs002', 'SEPA'))
ExtractorRegistry.register('SEPA_pacs004', _create_composite_extractor(Pacs004Extractor, 'SEPA_pacs004', 'SEPA'))

# -----------------------------------------------------------------------------
# SEPA_INST Composite Formats (SEPA Instant)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('SEPA_INST_pacs008', _create_composite_extractor(Pacs008Extractor, 'SEPA_INST_pacs008', 'SEPA_INST'))
ExtractorRegistry.register('SEPA_INST_pacs002', _create_composite_extractor(Pacs002Extractor, 'SEPA_INST_pacs002', 'SEPA_INST'))

# -----------------------------------------------------------------------------
# FEDNOW Composite Formats (US Instant)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('FEDNOW_pacs008', _create_composite_extractor(Pacs008Extractor, 'FEDNOW_pacs008', 'FEDNOW'))
ExtractorRegistry.register('FEDNOW_pacs009', _create_composite_extractor(Pacs009Extractor, 'FEDNOW_pacs009', 'FEDNOW'))
ExtractorRegistry.register('FEDNOW_pacs002', _create_composite_extractor(Pacs002Extractor, 'FEDNOW_pacs002', 'FEDNOW'))
ExtractorRegistry.register('FEDNOW_pacs004', _create_composite_extractor(Pacs004Extractor, 'FEDNOW_pacs004', 'FEDNOW'))

# -----------------------------------------------------------------------------
# NPP Composite Formats (Australia)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('NPP_pacs008', _create_composite_extractor(Pacs008Extractor, 'NPP_pacs008', 'NPP'))
ExtractorRegistry.register('NPP_pacs002', _create_composite_extractor(Pacs002Extractor, 'NPP_pacs002', 'NPP'))
ExtractorRegistry.register('NPP_pacs004', _create_composite_extractor(Pacs004Extractor, 'NPP_pacs004', 'NPP'))

# -----------------------------------------------------------------------------
# MEPS_PLUS Composite Formats (Singapore)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('MEPS_PLUS_pacs008', _create_composite_extractor(Pacs008Extractor, 'MEPS_PLUS_pacs008', 'MEPS_PLUS'))
ExtractorRegistry.register('MEPS_PLUS_pacs009', _create_composite_extractor(Pacs009Extractor, 'MEPS_PLUS_pacs009', 'MEPS_PLUS'))
ExtractorRegistry.register('MEPS_PLUS_pacs002', _create_composite_extractor(Pacs002Extractor, 'MEPS_PLUS_pacs002', 'MEPS_PLUS'))

# -----------------------------------------------------------------------------
# RTGS_HK Composite Formats (Hong Kong CHATS)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('RTGS_HK_pacs008', _create_composite_extractor(Pacs008Extractor, 'RTGS_HK_pacs008', 'RTGS_HK'))
ExtractorRegistry.register('RTGS_HK_pacs009', _create_composite_extractor(Pacs009Extractor, 'RTGS_HK_pacs009', 'RTGS_HK'))
ExtractorRegistry.register('RTGS_HK_pacs002', _create_composite_extractor(Pacs002Extractor, 'RTGS_HK_pacs002', 'RTGS_HK'))

# -----------------------------------------------------------------------------
# UAEFTS Composite Formats (UAE)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('UAEFTS_pacs008', _create_composite_extractor(Pacs008Extractor, 'UAEFTS_pacs008', 'UAEFTS'))
ExtractorRegistry.register('UAEFTS_pacs009', _create_composite_extractor(Pacs009Extractor, 'UAEFTS_pacs009', 'UAEFTS'))
ExtractorRegistry.register('UAEFTS_pacs002', _create_composite_extractor(Pacs002Extractor, 'UAEFTS_pacs002', 'UAEFTS'))

# -----------------------------------------------------------------------------
# INSTAPAY Composite Formats (Philippines)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('INSTAPAY_pacs008', _create_composite_extractor(Pacs008Extractor, 'INSTAPAY_pacs008', 'INSTAPAY'))
ExtractorRegistry.register('INSTAPAY_pacs009', _create_composite_extractor(Pacs009Extractor, 'INSTAPAY_pacs009', 'INSTAPAY'))
ExtractorRegistry.register('INSTAPAY_pacs002', _create_composite_extractor(Pacs002Extractor, 'INSTAPAY_pacs002', 'INSTAPAY'))

# -----------------------------------------------------------------------------
# CHIPS Composite Formats (US Large Value)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('CHIPS_pacs008', _create_composite_extractor(Pacs008Extractor, 'CHIPS_pacs008', 'CHIPS'))
ExtractorRegistry.register('CHIPS_pacs009', _create_composite_extractor(Pacs009Extractor, 'CHIPS_pacs009', 'CHIPS'))
ExtractorRegistry.register('CHIPS_pacs002', _create_composite_extractor(Pacs002Extractor, 'CHIPS_pacs002', 'CHIPS'))

# -----------------------------------------------------------------------------
# FEDWIRE Composite Formats (US Fed)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('FEDWIRE_pacs008', _create_composite_extractor(Pacs008Extractor, 'FEDWIRE_pacs008', 'FEDWIRE'))
ExtractorRegistry.register('FEDWIRE_pacs009', _create_composite_extractor(Pacs009Extractor, 'FEDWIRE_pacs009', 'FEDWIRE'))
ExtractorRegistry.register('FEDWIRE_pacs002', _create_composite_extractor(Pacs002Extractor, 'FEDWIRE_pacs002', 'FEDWIRE'))
ExtractorRegistry.register('FEDWIRE_pacs004', _create_composite_extractor(Pacs004Extractor, 'FEDWIRE_pacs004', 'FEDWIRE'))

# -----------------------------------------------------------------------------
# RTP Composite Formats (US Real-Time Payments - TCH)
# -----------------------------------------------------------------------------
ExtractorRegistry.register('RTP_pacs008', _create_composite_extractor(Pacs008Extractor, 'RTP_pacs008', 'RTP'))
ExtractorRegistry.register('RTP_pacs002', _create_composite_extractor(Pacs002Extractor, 'RTP_pacs002', 'RTP'))
ExtractorRegistry.register('RTP_pacs004', _create_composite_extractor(Pacs004Extractor, 'RTP_pacs004', 'RTP'))


logger.info(f"Registered {len(ExtractorRegistry.list_types())} ISO 20022 extractors including composite formats")

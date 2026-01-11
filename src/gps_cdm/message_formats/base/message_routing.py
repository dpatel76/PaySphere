"""
Message Routing Framework
=========================

This module provides intelligent routing of payment messages to their appropriate
ISO 20022 message types based on source format and message subtype detection.

Key Concepts:
- Source Format: The original payment system format (ACH, BACS, UPI, FEDWIRE, etc.)
- Message Subtype: The detected transaction type within the source format
- Target ISO Message: The ISO 20022 message type to route to (pacs.008, pain.008, etc.)
- Target CDM Table: The Gold layer table to persist to (cdm_pacs_*, cdm_pain_*, etc.)

Routing Categories:
1. NATIVE_ISO: Built on ISO 20022 - direct message type routing
2. FULLY_MIGRATED: Migrated to ISO 20022 - direct message type routing
3. INTEGRATION_ONLY: Uses translation - subtype detection required
4. LEGACY: Proprietary format - subtype detection required
5. NOT_ISO20022: Different standard (ISO 8583) - subtype detection required
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class AdoptionStatus(Enum):
    """ISO 20022 adoption status for payment standards."""
    NATIVE_ISO = "NATIVE_ISO"           # Built on ISO 20022 from inception
    FULLY_MIGRATED = "FULLY_MIGRATED"   # Completed migration to ISO 20022
    INTEGRATION_ONLY = "INTEGRATION_ONLY"  # Translation layer, not native
    LEGACY = "LEGACY"                    # Proprietary format, no migration
    NOT_ISO20022 = "NOT_ISO20022"        # Uses different standard (e.g., ISO 8583)
    PLANNED_MIGRATION = "PLANNED_MIGRATION"  # Migration announced but not complete


class MessageSubtype(Enum):
    """Standardized message subtypes for routing decisions."""

    # Credit Transfer Types
    CREDIT_TRANSFER_CUSTOMER = "CREDIT_TRANSFER_CUSTOMER"      # → pacs.008
    CREDIT_TRANSFER_FI = "CREDIT_TRANSFER_FI"                  # → pacs.009
    CREDIT_TRANSFER_BULK = "CREDIT_TRANSFER_BULK"              # → pain.001

    # Direct Debit Types
    DIRECT_DEBIT_INITIATION = "DIRECT_DEBIT_INITIATION"        # → pain.008
    DIRECT_DEBIT_EXECUTION = "DIRECT_DEBIT_EXECUTION"          # → pacs.003

    # Status/Return Types
    PAYMENT_RETURN = "PAYMENT_RETURN"                          # → pacs.004
    PAYMENT_STATUS = "PAYMENT_STATUS"                          # → pacs.002
    PAYMENT_REJECTION = "PAYMENT_REJECTION"                    # → pain.002
    PAYMENT_CANCELLATION = "PAYMENT_CANCELLATION"              # → camt.056

    # Request Types
    REQUEST_FOR_PAYMENT = "REQUEST_FOR_PAYMENT"                # → pain.013
    RFP_RESPONSE = "RFP_RESPONSE"                              # → pain.014

    # Statement Types
    ACCOUNT_STATEMENT = "ACCOUNT_STATEMENT"                    # → camt.053
    ACCOUNT_REPORT = "ACCOUNT_REPORT"                          # → camt.052
    DEBIT_CREDIT_NOTIFICATION = "DEBIT_CREDIT_NOTIFICATION"    # → camt.054

    # Unknown/Default
    UNKNOWN = "UNKNOWN"


# ISO 20022 Message Type to CDM Table Mapping
ISO_TO_CDM_TABLE = {
    'pacs.008': 'cdm_pacs_fi_customer_credit_transfer',
    'pacs.009': 'cdm_pacs_fi_credit_transfer',
    'pacs.002': 'cdm_pacs_payment_status_report',
    'pacs.003': 'cdm_pacs_fi_direct_debit',
    'pacs.004': 'cdm_pacs_payment_return',
    'pain.001': 'cdm_pain_customer_credit_transfer_initiation',
    'pain.002': 'cdm_pain_payment_status_report',
    'pain.008': 'cdm_pain_direct_debit_initiation',
    'pain.013': 'cdm_pain_request_for_payment',
    'pain.014': 'cdm_pain_rfp_response',
    'camt.052': 'cdm_camt_account_report',
    'camt.053': 'cdm_camt_account_statement',
    'camt.054': 'cdm_camt_debit_credit_notification',
    'camt.056': 'cdm_camt_cancellation_request',
}

# Message Subtype to ISO 20022 Message Type Mapping
SUBTYPE_TO_ISO = {
    MessageSubtype.CREDIT_TRANSFER_CUSTOMER: 'pacs.008',
    MessageSubtype.CREDIT_TRANSFER_FI: 'pacs.009',
    MessageSubtype.CREDIT_TRANSFER_BULK: 'pain.001',
    MessageSubtype.DIRECT_DEBIT_INITIATION: 'pain.008',
    MessageSubtype.DIRECT_DEBIT_EXECUTION: 'pacs.003',
    MessageSubtype.PAYMENT_RETURN: 'pacs.004',
    MessageSubtype.PAYMENT_STATUS: 'pacs.002',
    MessageSubtype.PAYMENT_REJECTION: 'pain.002',
    MessageSubtype.PAYMENT_CANCELLATION: 'camt.056',
    MessageSubtype.REQUEST_FOR_PAYMENT: 'pain.013',
    MessageSubtype.RFP_RESPONSE: 'pain.014',
    MessageSubtype.ACCOUNT_STATEMENT: 'camt.053',
    MessageSubtype.ACCOUNT_REPORT: 'camt.052',
    MessageSubtype.DEBIT_CREDIT_NOTIFICATION: 'camt.054',
    MessageSubtype.UNKNOWN: 'pacs.008',  # Default
}


# =============================================================================
# PAYMENT STANDARD REGISTRY
# =============================================================================

@dataclass
class PaymentStandardInfo:
    """Information about a payment standard's ISO 20022 adoption."""
    code: str
    name: str
    region: str
    adoption_status: AdoptionStatus
    supported_message_types: List[str]
    requires_subtype_detection: bool
    default_iso_type: str = 'pacs.008'
    constraints: Dict[str, Any] = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}


# Registry of all payment standards and their ISO 20022 adoption status
PAYMENT_STANDARDS: Dict[str, PaymentStandardInfo] = {
    # US Payment Systems
    'FEDWIRE': PaymentStandardInfo(
        code='FEDWIRE',
        name='Fedwire Funds Service',
        region='US',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.004', 'pacs.002'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
        constraints={
            'end_to_end_id_mandatory': True,
            'uetr_mandatory': True,
            'structured_address_from': '2025-11',
        }
    ),
    'CHIPS': PaymentStandardInfo(
        code='CHIPS',
        name='CHIPS',
        region='US',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002', 'pacs.004'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),
    'FEDNOW': PaymentStandardInfo(
        code='FEDNOW',
        name='FedNow',
        region='US',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.002', 'pacs.004', 'pacs.009', 'pain.013', 'pain.014'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),
    'RTP': PaymentStandardInfo(
        code='RTP',
        name='RTP (Real-Time Payments)',
        region='US',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.002', 'pain.013', 'pain.014'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
        constraints={
            'credit_transfer_limit': 1000000,  # $1M
            'no_debit_capability': True,
        }
    ),
    'ACH': PaymentStandardInfo(
        code='ACH',
        name='NACHA ACH',
        region='US',
        adoption_status=AdoptionStatus.INTEGRATION_ONLY,
        supported_message_types=['pacs.008', 'pain.001', 'pain.008', 'pacs.004'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
        constraints={
            'line_width': 94,
            'same_day_settlement': 'end_of_day',
        }
    ),

    # European Payment Systems
    'TARGET2': PaymentStandardInfo(
        code='TARGET2',
        name='TARGET2',
        region='EU',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002', 'pacs.004', 'pacs.010'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),
    'SEPA': PaymentStandardInfo(
        code='SEPA',
        name='SEPA',
        region='EU',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pain.001', 'pain.002', 'pain.008', 'pacs.008', 'pacs.002', 'pacs.003', 'pacs.004'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
        constraints={
            'structured_address_from': '2025-11',
        }
    ),
    'SEPA_INST': PaymentStandardInfo(
        code='SEPA_INST',
        name='SEPA Instant',
        region='EU',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.002'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
        constraints={
            'settlement_time_seconds': 10,
        }
    ),

    # UK Payment Systems
    'CHAPS': PaymentStandardInfo(
        code='CHAPS',
        name='CHAPS',
        region='UK',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002', 'pacs.004'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
        constraints={
            'lei_mandatory_from': '2025-05',
            'purpose_codes_mandatory': True,
            'structured_remittance_from': '2025-11',
        }
    ),
    'FPS': PaymentStandardInfo(
        code='FPS',
        name='UK Faster Payments',
        region='UK',
        adoption_status=AdoptionStatus.PLANNED_MIGRATION,
        supported_message_types=['pacs.008', 'pacs.002', 'pacs.004', 'pain.001'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
    ),
    'BACS': PaymentStandardInfo(
        code='BACS',
        name='BACS',
        region='UK',
        adoption_status=AdoptionStatus.LEGACY,
        supported_message_types=['pacs.008', 'pain.008'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
        constraints={
            'settlement_days': 3,
        }
    ),

    # Asia-Pacific Payment Systems
    'NPP': PaymentStandardInfo(
        code='NPP',
        name='NPP (Australia)',
        region='APAC',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.002', 'pacs.004'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
        constraints={
            'settlement_time_seconds': 15,
            'remittance_data_chars': 280,
        }
    ),
    'MEPS_PLUS': PaymentStandardInfo(
        code='MEPS_PLUS',
        name='MEPS+ (Singapore)',
        region='APAC',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),
    'PAYNOW': PaymentStandardInfo(
        code='PAYNOW',
        name='PayNow (Singapore)',
        region='APAC',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.002'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),
    'RTGS_HK': PaymentStandardInfo(
        code='RTGS_HK',
        name='CHATS (Hong Kong)',
        region='APAC',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002', 'pacs.004'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),
    'CNAPS': PaymentStandardInfo(
        code='CNAPS',
        name='CNAPS (China)',
        region='APAC',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pain.001'],
        requires_subtype_detection=True,  # HVPS vs BEPS routing
        default_iso_type='pacs.008',
        constraints={
            'mandarin_support': True,
        }
    ),
    'BOJNET': PaymentStandardInfo(
        code='BOJNET',
        name='BOJ-NET (Japan)',
        region='APAC',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
    ),
    'KFTC': PaymentStandardInfo(
        code='KFTC',
        name='KFTC (Korea)',
        region='APAC',
        adoption_status=AdoptionStatus.PLANNED_MIGRATION,
        supported_message_types=['pacs.008', 'pacs.004', 'pain.001'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
    ),
    'UPI': PaymentStandardInfo(
        code='UPI',
        name='UPI (India)',
        region='APAC',
        adoption_status=AdoptionStatus.NOT_ISO20022,  # Uses ISO 8583
        supported_message_types=['pacs.008', 'pacs.004', 'pain.008'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
        constraints={
            'base_standard': 'ISO8583',
            'currency': 'INR',
        }
    ),
    'PROMPTPAY': PaymentStandardInfo(
        code='PROMPTPAY',
        name='PromptPay (Thailand)',
        region='APAC',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.002'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),

    # Middle East Payment Systems
    'SARIE': PaymentStandardInfo(
        code='SARIE',
        name='SARIE (Saudi Arabia)',
        region='MENA',
        adoption_status=AdoptionStatus.FULLY_MIGRATED,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002', 'pacs.004'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
    ),
    'UAEFTS': PaymentStandardInfo(
        code='UAEFTS',
        name='UAEFTS (UAE)',
        region='MENA',
        adoption_status=AdoptionStatus.PLANNED_MIGRATION,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),

    # Latin America Payment Systems
    'PIX': PaymentStandardInfo(
        code='PIX',
        name='PIX (Brazil)',
        region='LATAM',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.002', 'pacs.004'],
        requires_subtype_detection=True,
        default_iso_type='pacs.008',
    ),
    'INSTAPAY': PaymentStandardInfo(
        code='INSTAPAY',
        name='InstaPay (Philippines)',
        region='APAC',
        adoption_status=AdoptionStatus.NATIVE_ISO,
        supported_message_types=['pacs.008', 'pacs.009', 'pacs.002'],
        requires_subtype_detection=False,
        default_iso_type='pacs.008',
    ),

    # NOTE: All SWIFT MT messages (MT103, MT202, MT940, MT950, etc.) were
    # decommissioned by SWIFT in November 2025. Use ISO 20022 equivalents:
    # - MT103/MT202 → pacs.008/pacs.009
    # - MT940/MT950 → camt.053
}


# =============================================================================
# SUBTYPE DETECTOR BASE CLASS
# =============================================================================

class SubtypeDetector(ABC):
    """Base class for format-specific subtype detection."""

    @abstractmethod
    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        """
        Detect the message subtype from raw or parsed content.

        Args:
            raw_content: Original raw message content
            parsed_data: Parsed/structured message data

        Returns:
            Tuple of (MessageSubtype, target_iso_message_type)
            e.g., (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")
        """
        pass

    @abstractmethod
    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        """
        Get a routing key for conditional mapping lookup.

        Returns:
            String key for database mapping lookup, e.g., "ACH_CCD_CREDIT"
        """
        pass

    def get_target_cdm_table(self, iso_message_type: str) -> str:
        """Get the CDM Gold table for an ISO message type."""
        return ISO_TO_CDM_TABLE.get(iso_message_type, 'cdm_pacs_fi_customer_credit_transfer')


# =============================================================================
# FORMAT-SPECIFIC SUBTYPE DETECTORS
# =============================================================================

class ACHSubtypeDetector(SubtypeDetector):
    """
    ACH SEC Code to ISO 20022 Message Type Mapping.

    SEC Code Categories:
    - CREDIT: CCD, CTX, PPD (credits) → pacs.008 / pain.001
    - DEBIT: PPD, CCD, WEB, TEL (debits) → pain.008
    - RETURN: Return entries → pacs.004
    """

    # Transaction codes for credits (22, 23, 24, 32, 33, 34)
    CREDIT_TRANSACTION_CODES = {'22', '23', '24', '32', '33', '34'}

    # Transaction codes for debits (27, 28, 29, 37, 38, 39)
    DEBIT_TRANSACTION_CODES = {'27', '28', '29', '37', '38', '39'}

    # Return transaction codes (21, 26, 31, 36)
    RETURN_TRANSACTION_CODES = {'21', '26', '31', '36'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        # Get transaction code from parsed data or raw content
        transaction_code = parsed_data.get('transaction_code') or parsed_data.get('transactionCode')
        if not transaction_code and raw_content:
            transaction_code = self._extract_transaction_code(raw_content)

        # Get SEC code
        sec_code = (
            parsed_data.get('standard_entry_class') or
            parsed_data.get('standardEntryClassCode') or
            self._extract_sec_code(raw_content)
        )

        # Check for return entries first
        if transaction_code in self.RETURN_TRANSACTION_CODES:
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        # Check for NOC (Notification of Change) - typically in addenda
        addenda_type = parsed_data.get('addendaTypeCode') or parsed_data.get('addenda_type')
        if addenda_type == '98':
            return (MessageSubtype.DEBIT_CREDIT_NOTIFICATION, "camt.054")

        # Check transaction code for credit vs debit
        if transaction_code in self.CREDIT_TRANSACTION_CODES:
            # Multi-entry files are bulk → pain.001
            if self._is_bulk_file(raw_content, parsed_data):
                return (MessageSubtype.CREDIT_TRANSFER_BULK, "pain.001")
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        if transaction_code in self.DEBIT_TRANSACTION_CODES:
            return (MessageSubtype.DIRECT_DEBIT_INITIATION, "pain.008")

        # Default to credit transfer
        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, iso_format = self.detect_subtype(raw_content, parsed_data)
        sec_code = (
            parsed_data.get('standard_entry_class') or
            parsed_data.get('standardEntryClassCode') or
            'UNK'
        )
        return f"ACH_{sec_code}_{subtype.name}"

    def _extract_sec_code(self, raw_content: str) -> str:
        """Extract SEC code from batch header (position 51-53)."""
        if not raw_content:
            return 'UNK'
        lines = raw_content.split('\n')
        for line in lines:
            if line and line[0] == '5':  # Batch header
                if len(line) >= 53:
                    return line[50:53].strip()
        return 'UNK'

    def _extract_transaction_code(self, raw_content: str) -> str:
        """Extract transaction code from entry detail (position 2-3)."""
        if not raw_content:
            return ''
        lines = raw_content.split('\n')
        for line in lines:
            if line and line[0] == '6':  # Entry detail
                if len(line) >= 3:
                    return line[1:3]
        return ''

    def _is_bulk_file(self, raw_content: str, parsed_data: Dict[str, Any]) -> bool:
        """Check if file contains multiple entry records."""
        # Check parsed data first
        batches = parsed_data.get('batches', [])
        if batches:
            total_entries = sum(len(b.get('entries', [])) for b in batches)
            if total_entries > 1:
                return True

        # Fall back to counting raw lines
        if raw_content:
            entry_count = sum(1 for line in raw_content.split('\n') if line and line[0] == '6')
            return entry_count > 1

        return False


class BACSSubtypeDetector(SubtypeDetector):
    """
    BACS Transaction Type to ISO 20022 Mapping.

    Transaction Types:
    - 99: Credit (BACS Credit) → pacs.008
    - 01: Debit (Direct Debit) → pain.008
    - 17: Credit (FPS fallback) → pacs.008
    """

    CREDIT_TRANSACTION_TYPES = {'99', '17', 'CR'}
    DEBIT_TRANSACTION_TYPES = {'01', '18', '19', 'DR'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        transaction_type = (
            parsed_data.get('transaction_type') or
            parsed_data.get('transactionType') or
            self._extract_transaction_type(raw_content)
        )

        if transaction_type in self.CREDIT_TRANSACTION_TYPES:
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        if transaction_type in self.DEBIT_TRANSACTION_TYPES:
            return (MessageSubtype.DIRECT_DEBIT_INITIATION, "pain.008")

        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        transaction_type = parsed_data.get('transaction_type', 'UNK')
        return f"BACS_{transaction_type}_{subtype.name}"

    def _extract_transaction_type(self, raw_content: str) -> str:
        """Extract transaction type from BACS record."""
        if not raw_content:
            return 'UNK'
        lines = raw_content.split('\n')
        for line in lines:
            # Skip header lines
            if line.startswith(('VOL', 'HDR', 'UHL', 'EOF', 'UTL')):
                continue
            # Transaction records start with transaction type
            if len(line) >= 2 and line[0:2].isdigit():
                return line[0:2]
        return 'UNK'


class UPISubtypeDetector(SubtypeDetector):
    """
    UPI (ISO 8583) to ISO 20022 Mapping.

    UPI uses ISO 8583 Message Type Indicators (MTI):
    - 0200/0210: Financial Transaction → pacs.008
    - 0420/0430: Reversal → pacs.004
    - COLLECT type: Collection request → pain.008
    """

    # MTI to message type mapping
    MTI_CREDIT_TYPES = {'0200', '0210', '0100', '0110'}
    MTI_REVERSAL_TYPES = {'0420', '0430', '0400', '0410'}

    # Transaction types
    REFUND_TXN_TYPES = {'REFUND', 'REVERSAL', 'VOID'}
    COLLECT_TXN_TYPES = {'COLLECT', 'REQUEST'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        # Check txnType field (common in UPI JSON)
        txn_type = (
            parsed_data.get('txnType') or
            parsed_data.get('Txn', {}).get('type') or
            parsed_data.get('type', '')
        ).upper()

        # Check MTI for ISO 8583 based messages
        mti = parsed_data.get('mti') or parsed_data.get('message_type_indicator', '')

        # Check for refund/reversal
        if txn_type in self.REFUND_TXN_TYPES or mti in self.MTI_REVERSAL_TYPES:
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        # Check for collect (pull payment)
        if txn_type in self.COLLECT_TXN_TYPES:
            return (MessageSubtype.DIRECT_DEBIT_INITIATION, "pain.008")

        # Default to payment (credit transfer)
        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        txn_type = parsed_data.get('txnType', 'PAY').upper()
        return f"UPI_{txn_type}_{subtype.name}"


class CNAPSSubtypeDetector(SubtypeDetector):
    """
    CNAPS (China) Message Type to ISO 20022 Mapping.

    CNAPS Systems:
    - HVPS: High Value Payment System → pacs.008/pacs.009
    - BEPS: Bulk Electronic Payment System → pain.001
    - IBPS: Internet Banking → pacs.008
    """

    HVPS_TYPES = {'HVPS', 'hvps', 'HIGH_VALUE', 'RTGS'}
    BEPS_TYPES = {'BEPS', 'beps', 'BULK', 'BATCH'}
    IBPS_TYPES = {'IBPS', 'ibps', 'INTERNET'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        system_type = (
            parsed_data.get('system_type') or
            parsed_data.get('message_type') or
            parsed_data.get('messageHeader', {}).get('systemType', '')
        ).upper()

        # Check for FI-to-FI payment
        is_fi_payment = parsed_data.get('is_fi_payment', False)

        if system_type in {'HVPS', 'HIGH_VALUE', 'RTGS'}:
            if is_fi_payment:
                return (MessageSubtype.CREDIT_TRANSFER_FI, "pacs.009")
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        if system_type in {'BEPS', 'BULK', 'BATCH'}:
            return (MessageSubtype.CREDIT_TRANSFER_BULK, "pain.001")

        if system_type in {'IBPS', 'INTERNET'}:
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        system_type = parsed_data.get('system_type', 'HVPS').upper()
        return f"CNAPS_{system_type}_{subtype.name}"


# NOTE: SwiftMTSubtypeDetector has been removed as SWIFT decommissioned
# MT103 and MT202 payment messages in November 2025. MT940/MT950 statement
# messages don't require subtype detection - they always map to camt.053.


class PIXSubtypeDetector(SubtypeDetector):
    """
    PIX (Brazil) Message Type to ISO 20022 Mapping.

    PIX Transaction Types:
    - Payment (standard) → pacs.008
    - Return/Refund → pacs.004
    - Status inquiry → pacs.002
    """

    RETURN_TYPES = {'DEVOLUTION', 'RETURN', 'REFUND', 'DEVOLUCAO'}
    STATUS_TYPES = {'STATUS', 'INQUIRY', 'CONSULTA'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        txn_type = (
            parsed_data.get('transactionType') or
            parsed_data.get('txnType') or
            parsed_data.get('tipo', '')
        ).upper()

        # Check purpose code for returns
        purpose = (parsed_data.get('purposeCode') or '').upper()

        if txn_type in self.RETURN_TYPES or purpose == 'RFND':
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        if txn_type in self.STATUS_TYPES:
            return (MessageSubtype.PAYMENT_STATUS, "pacs.002")

        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        txn_type = parsed_data.get('transactionType', 'PAYMENT').upper()
        return f"PIX_{txn_type}_{subtype.name}"


class KFTCSubtypeDetector(SubtypeDetector):
    """
    KFTC (Korea Financial Telecommunications & Clearings Institute) Message Type Mapping.

    KFTC Transaction Types:
    - Regular Transfer → pacs.008
    - Bulk/Batch Transfer → pain.001
    - Return → pacs.004
    """

    BULK_TYPES = {'BULK', 'BATCH', '일괄', 'MASS'}
    RETURN_TYPES = {'RETURN', 'REFUND', '반환', '환불'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        txn_type = (
            parsed_data.get('transactionType') or
            parsed_data.get('txnType') or
            parsed_data.get('message_type', '')
        ).upper()

        # Check for bulk indicator
        is_bulk = parsed_data.get('is_bulk', False)
        record_count = parsed_data.get('record_count', 1)
        if is_bulk or record_count > 1:
            return (MessageSubtype.CREDIT_TRANSFER_BULK, "pain.001")

        if txn_type in self.RETURN_TYPES:
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        txn_type = parsed_data.get('transactionType', 'TRANSFER').upper()
        return f"KFTC_{txn_type}_{subtype.name}"


class BOJNETSubtypeDetector(SubtypeDetector):
    """
    BOJ-NET (Bank of Japan Financial Network System) Message Type Mapping.

    BOJ-NET Transaction Types:
    - Customer Payment → pacs.008
    - Interbank Payment (FI to FI) → pacs.009
    - JGB Settlement → pacs.009
    """

    FI_TYPES = {'INTERBANK', 'FI', 'JGB', 'BOJ', '日銀'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        txn_type = (
            parsed_data.get('transactionType') or
            parsed_data.get('txnType') or
            parsed_data.get('message_type', '')
        ).upper()

        # Check messageTypeCode from Bronze extractor (e.g., 'pacs.009')
        message_type_code = (
            parsed_data.get('messageTypeCode') or
            parsed_data.get('message_type_code', '')
        ).lower()

        # Check for FI-to-FI indicator
        is_fi_payment = parsed_data.get('is_fi_payment', False)

        # pacs.009 indicates FI-to-FI credit transfer
        if message_type_code == 'pacs.009':
            return (MessageSubtype.CREDIT_TRANSFER_FI, "pacs.009")

        if txn_type in self.FI_TYPES or is_fi_payment:
            return (MessageSubtype.CREDIT_TRANSFER_FI, "pacs.009")

        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        txn_type = parsed_data.get('transactionType', 'CUSTOMER').upper()
        return f"BOJNET_{txn_type}_{subtype.name}"


class FPSSubtypeDetector(SubtypeDetector):
    """
    FPS (UK Faster Payments Service) Message Type Mapping.

    FPS Transaction Types:
    - Single Immediate Payment → pacs.008
    - Forward Dated Payment → pacs.008
    - Standing Order → pain.001 (bulk initiation)
    - Return → pacs.004
    """

    RETURN_TYPES = {'RETURN', 'REJECT', 'RECALL'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        txn_type = (
            parsed_data.get('transactionType') or
            parsed_data.get('paymentType', '')
        ).upper()

        # Check for return indicator
        if txn_type in self.RETURN_TYPES:
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        # Check for standing order (bulk)
        if 'STANDING' in txn_type or parsed_data.get('is_standing_order'):
            return (MessageSubtype.CREDIT_TRANSFER_BULK, "pain.001")

        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        txn_type = parsed_data.get('transactionType', 'SIP').upper()
        return f"FPS_{txn_type}_{subtype.name}"


class SARIESubtypeDetector(SubtypeDetector):
    """
    SARIE (Saudi Arabian Riyal Interbank Express) Message Type Mapping.

    SARIE Transaction Types:
    - Customer Credit Transfer → pacs.008
    - Financial Institution Transfer → pacs.009
    - Return → pacs.004
    - Status → pacs.002
    """

    FI_TYPES = {'FI_TRANSFER', 'INTERBANK', 'BANK_TO_BANK'}
    RETURN_TYPES = {'RETURN', 'REJECT', 'RECALL'}
    STATUS_TYPES = {'STATUS', 'INQUIRY'}

    def detect_subtype(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> Tuple[MessageSubtype, str]:
        txn_type = (
            parsed_data.get('transactionType') or
            parsed_data.get('txnType') or
            parsed_data.get('message_type', '')
        ).upper()

        is_fi_payment = parsed_data.get('is_fi_payment', False)

        if txn_type in self.RETURN_TYPES:
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        if txn_type in self.STATUS_TYPES:
            return (MessageSubtype.PAYMENT_STATUS, "pacs.002")

        if txn_type in self.FI_TYPES or is_fi_payment:
            return (MessageSubtype.CREDIT_TRANSFER_FI, "pacs.009")

        return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

    def get_routing_key(
        self,
        raw_content: str,
        parsed_data: Dict[str, Any]
    ) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        txn_type = parsed_data.get('transactionType', 'CUSTOMER').upper()
        return f"SARIE_{txn_type}_{subtype.name}"


# =============================================================================
# DETECTOR REGISTRY
# =============================================================================

# Map of format codes to their subtype detectors
SUBTYPE_DETECTORS: Dict[str, SubtypeDetector] = {
    # US Payment Systems
    'ACH': ACHSubtypeDetector(),
    'NACHA': ACHSubtypeDetector(),

    # UK Payment Systems
    'BACS': BACSSubtypeDetector(),
    'FPS': FPSSubtypeDetector(),

    # Asia-Pacific Payment Systems
    'UPI': UPISubtypeDetector(),
    'CNAPS': CNAPSSubtypeDetector(),
    'KFTC': KFTCSubtypeDetector(),
    'BOJNET': BOJNETSubtypeDetector(),

    # Latin America
    'PIX': PIXSubtypeDetector(),

    # Middle East
    'SARIE': SARIESubtypeDetector(),

    # NOTE: SWIFT MT103 and MT202 payment messages were decommissioned in November 2025
    # MT940/MT950 statement messages don't require subtype detection (always → camt.053)
}


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def get_payment_standard(format_code: str) -> Optional[PaymentStandardInfo]:
    """Get payment standard information by format code."""
    # Normalize code
    normalized = format_code.upper().replace('.', '_').replace('-', '_')

    # Handle composite formats (e.g., FEDWIRE_pacs008 → FEDWIRE)
    if '_pacs' in normalized.lower() or '_pain' in normalized.lower():
        base_format = normalized.split('_')[0]
        return PAYMENT_STANDARDS.get(base_format)

    return PAYMENT_STANDARDS.get(normalized)


def get_subtype_detector(format_code: str) -> Optional[SubtypeDetector]:
    """Get subtype detector for a format if one exists."""
    normalized = format_code.upper().replace('.', '_').replace('-', '_')

    # Handle composite formats
    if '_pacs' in normalized.lower() or '_pain' in normalized.lower():
        base_format = normalized.split('_')[0]
        return SUBTYPE_DETECTORS.get(base_format)

    return SUBTYPE_DETECTORS.get(normalized)


def detect_message_routing(
    format_code: str,
    raw_content: str,
    parsed_data: Dict[str, Any]
) -> Tuple[MessageSubtype, str, str]:
    """
    Detect the message routing based on format and content.

    Args:
        format_code: Payment format code (e.g., 'ACH', 'BACS', 'FEDWIRE_pacs008')
        raw_content: Raw message content
        parsed_data: Parsed/structured message data

    Returns:
        Tuple of (MessageSubtype, target_iso_type, routing_key)
    """
    # Check if this is already an ISO 20022 composite format
    format_upper = format_code.upper()
    if '_pacs' in format_upper.lower():
        # Extract the ISO message type (e.g., FEDWIRE_pacs008 → pacs.008)
        parts = format_upper.split('_')
        for part in parts:
            if part.lower().startswith('pacs') or part.lower().startswith('pain'):
                iso_type = part.lower().replace('pacs', 'pacs.').replace('pain', 'pain.')
                # Ensure proper formatting
                if '.' not in iso_type:
                    iso_type = iso_type[:4] + '.' + iso_type[4:]
                subtype = _iso_to_subtype(iso_type)
                routing_key = f"{parts[0]}_{iso_type}_{subtype.name}"
                return (subtype, iso_type, routing_key)

    # Get payment standard info
    standard = get_payment_standard(format_code)

    if standard and standard.requires_subtype_detection:
        # Use subtype detector
        detector = get_subtype_detector(format_code)
        if detector:
            subtype, iso_type = detector.detect_subtype(raw_content, parsed_data)
            routing_key = detector.get_routing_key(raw_content, parsed_data)
            return (subtype, iso_type, routing_key)

    # Default routing for non-detection formats
    default_iso = standard.default_iso_type if standard else 'pacs.008'
    subtype = _iso_to_subtype(default_iso)
    routing_key = f"{format_code}_{default_iso}_{subtype.name}"

    return (subtype, default_iso, routing_key)


def _iso_to_subtype(iso_type: str) -> MessageSubtype:
    """Convert ISO message type to MessageSubtype."""
    iso_to_subtype_map = {
        'pacs.008': MessageSubtype.CREDIT_TRANSFER_CUSTOMER,
        'pacs.009': MessageSubtype.CREDIT_TRANSFER_FI,
        'pacs.002': MessageSubtype.PAYMENT_STATUS,
        'pacs.003': MessageSubtype.DIRECT_DEBIT_EXECUTION,
        'pacs.004': MessageSubtype.PAYMENT_RETURN,
        'pain.001': MessageSubtype.CREDIT_TRANSFER_BULK,
        'pain.002': MessageSubtype.PAYMENT_REJECTION,
        'pain.008': MessageSubtype.DIRECT_DEBIT_INITIATION,
        'pain.013': MessageSubtype.REQUEST_FOR_PAYMENT,
        'pain.014': MessageSubtype.RFP_RESPONSE,
        'camt.053': MessageSubtype.ACCOUNT_STATEMENT,
        'camt.052': MessageSubtype.ACCOUNT_REPORT,
        'camt.054': MessageSubtype.DEBIT_CREDIT_NOTIFICATION,
        'camt.056': MessageSubtype.PAYMENT_CANCELLATION,
    }
    return iso_to_subtype_map.get(iso_type, MessageSubtype.UNKNOWN)


def get_target_cdm_table(iso_message_type: str) -> str:
    """Get the target CDM Gold table for an ISO message type."""
    return ISO_TO_CDM_TABLE.get(iso_message_type, 'cdm_pacs_fi_customer_credit_transfer')


def get_silver_table_for_iso(iso_message_type: str) -> str:
    """Get the Silver staging table name for an ISO message type."""
    # Normalize: pacs.008 → stg_pacs008
    normalized = iso_message_type.replace('.', '')
    return f"stg_{normalized}"


def is_message_type_supported(format_code: str, iso_message_type: str) -> bool:
    """Check if a message type is supported by a payment standard."""
    standard = get_payment_standard(format_code)
    if not standard:
        return True  # Unknown standards default to allowing all
    return iso_message_type in standard.supported_message_types

"""Korea KFTC (Korea Financial Telecommunications & Clearings Institute) Extractor.

ISO 20022 INHERITANCE HIERARCHY:
    KFTC/BOK-Wire+ uses ISO 20022 for RTGS payments.
    Cross-border flows (CPBR+) migrated from SWIFT MT to ISO 20022.

    BaseISO20022Parser
        ├── Pacs008Parser (FI to FI Customer Credit Transfer)
        │   └── KftcPacs008Parser
        ├── Pacs009Parser (FI Credit Transfer)
        │   └── KftcPacs009Parser
        ├── Pacs002Parser (Payment Status Report)
        │   └── KftcPacs002Parser
        └── Pacs004Parser (Payment Return)
            └── KftcPacs004Parser

SUPPORTED MESSAGE TYPES:
    - pacs.008: Customer Credit Transfer (MT103 equivalent)
    - pacs.009: FI Credit Transfer (MT202 equivalent)
    - pacs.002: Payment Status Report
    - pacs.004: Payment Return (MT103R equivalent)

KFTC-SPECIFIC ELEMENTS:
    - Korean bank codes (3-digit)
    - KRW currency (Korean Won)
    - Business registration numbers (사업자등록번호)
    - Korean naming conventions (Hangul support)

CLEARING SYSTEM:
    - KRKFTC (Korea Financial Telecommunications & Clearings)
    - BOK-Wire+ (Bank of Korea Real-Time Gross Settlement)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_kftc
    - Gold: Semantic tables via DynamicGoldMapper
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from ..base import (
    BaseExtractor,
    ExtractorRegistry,
    GoldEntities,
    PartyData,
    AccountData,
    FinancialInstitutionData,
)

logger = logging.getLogger(__name__)

# Import ISO 20022 base classes for inheritance
try:
    from ..iso20022 import (
        Pacs008Parser, Pacs008Extractor,
        Pacs009Parser, Pacs009Extractor,
        Pacs002Parser, Pacs002Extractor,
        Pacs004Parser, Pacs004Extractor,
    )
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - KFTC will use standalone implementation")


# =============================================================================
# KFTC CONSTANTS
# =============================================================================

CLEARING_SYSTEM = "KRKFTC"
DEFAULT_CURRENCY = "KRW"
DEFAULT_COUNTRY = "KR"


# =============================================================================
# KFTC ISO 20022 PARSERS (inherit from base ISO 20022 parsers)
# =============================================================================

_Pacs008Base = Pacs008Parser if ISO20022_BASE_AVAILABLE else object
_Pacs009Base = Pacs009Parser if ISO20022_BASE_AVAILABLE else object
_Pacs002Base = Pacs002Parser if ISO20022_BASE_AVAILABLE else object
_Pacs004Base = Pacs004Parser if ISO20022_BASE_AVAILABLE else object


class KftcPacs008Parser(_Pacs008Base):
    """KFTC pacs.008 parser - FI to FI Customer Credit Transfer."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "KFTC_pacs008"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        # Handle dict input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        # Handle JSON input
        if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Parse as ISO 20022 XML
        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'KFTC_pacs008'}

        result['isKftc'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        result['defaultCurrency'] = self.DEFAULT_CURRENCY
        return result


class KftcPacs009Parser(_Pacs009Base):
    """KFTC pacs.009 parser - FI Credit Transfer (BOK-Wire+ interbank)."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "KFTC_pacs009"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'KFTC_pacs009'}

        result['isKftc'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class KftcPacs002Parser(_Pacs002Base):
    """KFTC pacs.002 parser - Payment Status Report."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "KFTC_pacs002"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'KFTC_pacs002'}

        result['isKftc'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class KftcPacs004Parser(_Pacs004Base):
    """KFTC pacs.004 parser - Payment Return."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "KFTC_pacs004"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'KFTC_pacs004'}

        result['isKftc'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


# =============================================================================
# LEGACY JSON PARSER (for backward compatibility)
# =============================================================================

class KftcJsonParser:
    """Parser for KFTC JSON format messages (legacy format).

    Handles the flat JSON structure:
    {
        "messageId": "KFTC-E2E-20260106-001",
        "messageType": "KFTC",
        "transactionId": "TXN-KR-20260106-001",
        "amount": 75000000.00,
        "currency": "KRW",
        "payerName": "Seoul Electronics Corporation",
        "payerAccount": "110-123-456789",
        "payerAddress": { "streetName": "...", "city": "Seoul", ... },
        "payeeName": "Busan Semiconductor Manufacturing Ltd",
        "payeeAccount": "333-654-321098",
        "payeeAddress": { ... },
        "remittanceInfo": { "invoiceNumber": "...", ... }
    }
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse KFTC JSON message into structured dict."""
        result = {
            'messageType': 'KFTC',
        }

        # Handle dict input (pre-parsed)
        if isinstance(raw_content, dict):
            data = raw_content
        else:
            # Parse JSON string
            if raw_content.strip().startswith('{'):
                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse KFTC JSON: {e}")
                    return result
            else:
                logger.warning("KFTC content is not JSON")
                return result

        # Core fields
        result['messageId'] = data.get('messageId')
        result['messageType'] = data.get('messageType') or 'KFTC'
        result['transactionId'] = data.get('transactionId')
        result['transactionReference'] = data.get('transactionReference')
        result['creationDateTime'] = data.get('creationDateTime')
        result['settlementDate'] = data.get('settlementDate')
        result['valueDate'] = data.get('valueDate')
        result['paymentType'] = data.get('paymentType')
        result['priority'] = data.get('priority')

        # Amount
        result['amount'] = data.get('amount')
        result['currency'] = data.get('currency') or DEFAULT_CURRENCY
        result['chargeBearer'] = data.get('chargeBearer')

        # Bank codes (multiple naming conventions)
        result['sendingBankCode'] = data.get('sendingBankCode') or data.get('senderBankCode')
        result['sendingBankName'] = data.get('sendingBankName') or data.get('senderBankName')
        result['sendingBankBic'] = data.get('sendingBankBic') or data.get('senderBankBic')
        result['receivingBankCode'] = data.get('receivingBankCode') or data.get('receiverBankCode')
        result['receivingBankName'] = data.get('receivingBankName') or data.get('receiverBankName')
        result['receivingBankBic'] = data.get('receivingBankBic') or data.get('receiverBankBic')

        # Payer information (multiple naming conventions)
        result['payerName'] = data.get('payerName') or data.get('senderName')
        result['payerAccount'] = data.get('payerAccount') or data.get('senderAccount')
        result['payerAccountType'] = data.get('payerAccountType')
        result['payerBusinessNumber'] = data.get('payerBusinessNumber')

        payer_addr = data.get('payerAddress', {})
        result['payerStreetName'] = payer_addr.get('streetName')
        result['payerBuildingNumber'] = payer_addr.get('buildingNumber')
        result['payerBuildingName'] = payer_addr.get('buildingName')
        result['payerFloor'] = payer_addr.get('floor')
        result['payerPostalCode'] = payer_addr.get('postalCode')
        result['payerCity'] = payer_addr.get('city')
        result['payerDistrict'] = payer_addr.get('district')
        result['payerCountry'] = payer_addr.get('country') or DEFAULT_COUNTRY

        payer_contact = data.get('payerContact', {})
        result['payerContactName'] = payer_contact.get('name')
        result['payerContactPhone'] = payer_contact.get('phone')
        result['payerContactEmail'] = payer_contact.get('email')

        # Payee information (multiple naming conventions)
        result['payeeName'] = data.get('payeeName') or data.get('receiverName')
        result['payeeAccount'] = data.get('payeeAccount') or data.get('receiverAccount')
        result['payeeAccountType'] = data.get('payeeAccountType')
        result['payeeBusinessNumber'] = data.get('payeeBusinessNumber')

        payee_addr = data.get('payeeAddress', {})
        result['payeeStreetName'] = payee_addr.get('streetName')
        result['payeeBuildingNumber'] = payee_addr.get('buildingNumber')
        result['payeeBuildingName'] = payee_addr.get('buildingName')
        result['payeeFloor'] = payee_addr.get('floor')
        result['payeePostalCode'] = payee_addr.get('postalCode')
        result['payeeCity'] = payee_addr.get('city')
        result['payeeDistrict'] = payee_addr.get('district')
        result['payeeCountry'] = payee_addr.get('country') or DEFAULT_COUNTRY

        payee_contact = data.get('payeeContact', {})
        result['payeeContactName'] = payee_contact.get('name')
        result['payeeContactPhone'] = payee_contact.get('phone')
        result['payeeContactEmail'] = payee_contact.get('email')

        # Purpose
        result['purpose'] = data.get('purpose')
        result['purposeDescription'] = data.get('purposeDescription')

        # Remittance information
        remit = data.get('remittanceInfo', {})
        result['invoiceNumber'] = remit.get('invoiceNumber')
        result['invoiceDate'] = remit.get('invoiceDate')
        result['purchaseOrderNumber'] = remit.get('purchaseOrderNumber')
        result['description'] = remit.get('description')

        # Flags
        result['isKftc'] = True
        result['clearingSystem'] = CLEARING_SYSTEM

        return result


# =============================================================================
# UNIFIED KFTC PARSER (auto-detects message type)
# =============================================================================

class KftcISO20022Parser:
    """Unified KFTC ISO 20022 parser that auto-detects message type."""

    ROOT_TO_PARSER = {
        'FIToFICstmrCdtTrf': 'pacs008',
        'FICdtTrf': 'pacs009',
        'FIToFIPmtStsRpt': 'pacs002',
        'PmtRtr': 'pacs004',
    }

    def __init__(self):
        self.pacs008_parser = KftcPacs008Parser()
        self.pacs009_parser = KftcPacs009Parser()
        self.pacs002_parser = KftcPacs002Parser()
        self.pacs004_parser = KftcPacs004Parser()
        self.json_parser = KftcJsonParser()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse KFTC message, auto-detecting format (JSON vs XML) and message type."""
        # Handle dict input
        if isinstance(raw_content, dict):
            return self.json_parser.parse(raw_content)

        content = raw_content.strip() if isinstance(raw_content, str) else ''

        # JSON format
        if content.startswith('{'):
            return self.json_parser.parse(content)

        # XML format - detect message type
        msg_type = self._detect_message_type(content)

        parser_map = {
            'pacs008': self.pacs008_parser,
            'pacs009': self.pacs009_parser,
            'pacs002': self.pacs002_parser,
            'pacs004': self.pacs004_parser,
        }

        parser = parser_map.get(msg_type, self.pacs008_parser)
        return parser.parse(content)

    def _detect_message_type(self, xml_content: str) -> str:
        """Detect ISO 20022 message type from XML root element."""
        for root_elem, msg_type in self.ROOT_TO_PARSER.items():
            if root_elem in xml_content:
                return msg_type
        return 'pacs008'  # Default


# =============================================================================
# KFTC EXTRACTOR
# =============================================================================

class KftcExtractor(BaseExtractor):
    """Extractor for Korea KFTC payment messages.

    Supports both ISO 20022 XML format (pacs.008, pacs.009, pacs.002, pacs.004)
    and legacy JSON format for backward compatibility.
    """

    MESSAGE_TYPE = "KFTC"
    SILVER_TABLE = "stg_kftc"
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    CLEARING_SYSTEM = CLEARING_SYSTEM

    def __init__(self):
        """Initialize extractor with unified parser."""
        super().__init__()
        self.iso20022_parser = KftcISO20022Parser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw KFTC content."""
        # Parse if string
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        msg_id = parsed.get('messageId', '') or parsed.get('transactionReference', '')
        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': json.dumps(raw_content) if isinstance(raw_content, dict) else raw_content,
            'batch_id': batch_id,
        }

    # =========================================================================
    # SILVER EXTRACTION
    # =========================================================================

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract all Silver layer fields from KFTC message.

        Supports multiple field naming conventions:
        - ISO 20022 fields (debtorName, creditorName, etc.)
        - Legacy JSON fields (payerName/senderName, payeeName/receiverName)
        - Bank codes (sendingBankCode/senderBankCode, receivingBankCode/receiverBankCode)
        """
        trunc = self.trunc

        # Parse if needed
        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        elif not msg_content.get('isKftc') and not msg_content.get('isISO20022'):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = msg_content

        # Handle field name variations - ISO 20022 vs Legacy JSON
        payer_name = (
            parsed.get('payerName') or
            parsed.get('senderName') or
            parsed.get('debtorName')
        )
        payer_account = (
            parsed.get('payerAccount') or
            parsed.get('senderAccount') or
            parsed.get('debtorAccountOther') or
            parsed.get('debtorAccountIban')
        )
        payee_name = (
            parsed.get('payeeName') or
            parsed.get('receiverName') or
            parsed.get('creditorName')
        )
        payee_account = (
            parsed.get('payeeAccount') or
            parsed.get('receiverAccount') or
            parsed.get('creditorAccountOther') or
            parsed.get('creditorAccountIban')
        )
        sending_bank = (
            parsed.get('sendingBankCode') or
            parsed.get('senderBankCode') or
            parsed.get('debtorAgentMemberId') or
            parsed.get('instructingAgentMemberId')
        )
        receiving_bank = (
            parsed.get('receivingBankCode') or
            parsed.get('receiverBankCode') or
            parsed.get('creditorAgentMemberId') or
            parsed.get('instructedAgentMemberId')
        )

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type and Identification
            'message_type': parsed.get('messageType') or 'KFTC',
            'message_id': trunc(parsed.get('messageId'), 35),
            'creation_date_time': parsed.get('creationDateTime'),
            'settlement_date': parsed.get('settlementDate') or parsed.get('interbankSettlementDate'),

            # Amount
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or DEFAULT_CURRENCY,

            # Bank Codes (both naming conventions)
            'sending_bank_code': trunc(sending_bank, 11),
            'receiving_bank_code': trunc(receiving_bank, 11),

            # Transaction Details
            'transaction_reference': trunc(
                parsed.get('transactionReference') or
                parsed.get('endToEndId'),
                35
            ),
            'transaction_id': trunc(
                parsed.get('transactionId') or
                parsed.get('transactionId'),
                35
            ),

            # Payer/Sender (primary fields)
            'payer_name': trunc(payer_name, 140),
            'payer_account': trunc(payer_account, 34),

            # Payee/Receiver (primary fields)
            'payee_name': trunc(payee_name, 140),
            'payee_account': trunc(payee_account, 34),

            # Sender fields (alternate naming for backward compatibility)
            'sender_name': trunc(parsed.get('senderName'), 140),
            'sender_account': trunc(parsed.get('senderAccount'), 34),
            'sender_bank_code': trunc(parsed.get('senderBankCode'), 11),

            # Receiver fields (alternate naming for backward compatibility)
            'receiver_name': trunc(parsed.get('receiverName'), 140),
            'receiver_account': trunc(parsed.get('receiverAccount'), 34),
            'receiver_bank_code': trunc(parsed.get('receiverBankCode'), 11),

            # Purpose
            'purpose': parsed.get('purpose') or parsed.get('categoryPurposeCode'),

            # Additional parsed fields
            'sending_bank_name': trunc(
                parsed.get('sendingBankName') or
                parsed.get('debtorAgentName'),
                140
            ),
            'receiving_bank_name': trunc(
                parsed.get('receivingBankName') or
                parsed.get('creditorAgentName'),
                140
            ),
            'sending_bank_bic': trunc(
                parsed.get('sendingBankBic') or
                parsed.get('debtorAgentBic'),
                11
            ),
            'receiving_bank_bic': trunc(
                parsed.get('receivingBankBic') or
                parsed.get('creditorAgentBic'),
                11
            ),
            'payment_type': trunc(
                parsed.get('paymentType') or
                parsed.get('localInstrumentCode'),
                10
            ),
            'charge_bearer': trunc(parsed.get('chargeBearer'), 10),
            'payer_business_number': trunc(parsed.get('payerBusinessNumber'), 20),
            'payee_business_number': trunc(parsed.get('payeeBusinessNumber'), 20),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        NOTE: Column names MUST match silver.stg_kftc table exactly.
        """
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_bank_code', 'receiving_bank_code', 'transaction_reference',
            'transaction_id',
            'payer_name', 'payer_account',
            'payee_name', 'payee_account',
            'sender_name', 'sender_account', 'sender_bank_code',
            'receiver_name', 'receiver_account', 'receiver_bank_code',
            'purpose',
        ]

    def get_silver_values(self, silver_record: Dict[str, Any]) -> tuple:
        """Return ordered tuple of values for Silver table INSERT."""
        columns = self.get_silver_columns()
        return tuple(silver_record.get(col) for col in columns)

    # =========================================================================
    # GOLD ENTITY EXTRACTION
    # =========================================================================

    def extract_gold_entities(
        self,
        silver_data: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from KFTC Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Payer Party - uses Silver column names
        if silver_data.get('payer_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type='ORGANIZATION',
                identification_type='BRN',
                identification_number=silver_data.get('payer_business_number'),
                country=DEFAULT_COUNTRY,
            ))

        # Payee Party
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='ORGANIZATION',
                identification_type='BRN',
                identification_number=silver_data.get('payee_business_number'),
                country=DEFAULT_COUNTRY,
            ))

        # Payer Account
        if silver_data.get('payer_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        # Payee Account
        if silver_data.get('payee_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        # Sending Bank
        if silver_data.get('sending_bank_code') or silver_data.get('sending_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('sending_bank_name'),
                bic=silver_data.get('sending_bank_bic'),
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        # Receiving Bank
        if silver_data.get('receiving_bank_code') or silver_data.get('receiving_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('receiving_bank_name'),
                bic=silver_data.get('receiving_bank_bic'),
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        return entities


# =============================================================================
# REGISTER EXTRACTORS
# =============================================================================

ExtractorRegistry.register('KFTC', KftcExtractor())
ExtractorRegistry.register('kftc', KftcExtractor())
ExtractorRegistry.register('BOK-Wire+', KftcExtractor())
ExtractorRegistry.register('BOK_WIRE', KftcExtractor())

# Message type specific aliases
ExtractorRegistry.register('KFTC_pacs008', KftcExtractor())
ExtractorRegistry.register('KFTC_pacs009', KftcExtractor())
ExtractorRegistry.register('KFTC_pacs002', KftcExtractor())
ExtractorRegistry.register('KFTC_pacs004', KftcExtractor())

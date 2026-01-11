"""Singapore PayNow Extractor.

ISO 20022 INHERITANCE HIERARCHY:
    PayNow is Singapore's retail instant payment system. It connects to FAST
    (Fast And Secure Transfers) which settles through MEPS+ (RTGS).
    Cross-border PayNow uses ISO 20022 via SWIFT gpi.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer)
            ├── MepsPlusISO20022Parser (RTGS settlement)
            │   └── PayNowPacs008Parser (retail overlay)
            ├── Pacs002Parser (Payment Status Report)
            │   └── PayNowPacs002Parser
            └── Pacs004Parser (Payment Return)
                └── PayNowPacs004Parser

SUPPORTED MESSAGE TYPES:
    - pacs.008: Instant Credit Transfer (via FAST)
    - pacs.002: Payment Status Report
    - pacs.004: Payment Return
    - pacs.028: Payment Status Request (unique to PayNow)

PAYNOW-SPECIFIC ELEMENTS:
    - Proxy types: NRIC, UEN, MOBILE, VPA (Virtual Payment Address)
    - SGD currency (Singapore Dollars)
    - FAST (Fast And Secure Transfers) for retail instant payments
    - MEPS+ for RTGS settlement

CLEARING SYSTEM:
    - SGPAYNOW (Singapore PayNow - retail)
    - SGFAST (Singapore FAST - underlying clearing)
    - SGMEP (Singapore MEPS+ - RTGS settlement)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_paynow
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
        Pacs002Parser, Pacs002Extractor,
        Pacs004Parser, Pacs004Extractor,
    )
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - PayNow will use standalone implementation")


# =============================================================================
# PAYNOW CONSTANTS
# =============================================================================

CLEARING_SYSTEM = "SGPAYNOW"  # PayNow retail system
FAST_CLEARING_SYSTEM = "SGFAST"  # FAST underlying clearing
MEPS_CLEARING_SYSTEM = "SGMEP"  # MEPS+ RTGS settlement
DEFAULT_CURRENCY = "SGD"
DEFAULT_COUNTRY = "SG"


# =============================================================================
# PAYNOW ISO 20022 PARSERS (inherit from base ISO 20022 parsers)
# =============================================================================

_Pacs008Base = Pacs008Parser if ISO20022_BASE_AVAILABLE else object
_Pacs002Base = Pacs002Parser if ISO20022_BASE_AVAILABLE else object
_Pacs004Base = Pacs004Parser if ISO20022_BASE_AVAILABLE else object


class PayNowPacs008Parser(_Pacs008Base):
    """PayNow pacs.008 parser - Instant Credit Transfer via FAST."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "PAYNOW_pacs008"

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
            result = {'messageType': 'PAYNOW_pacs008'}

        result['isPayNow'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        result['defaultCurrency'] = self.DEFAULT_CURRENCY
        return result


class PayNowPacs002Parser(_Pacs002Base):
    """PayNow pacs.002 parser - Payment Status Report."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "PAYNOW_pacs002"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'PAYNOW_pacs002'}

        result['isPayNow'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class PayNowPacs004Parser(_Pacs004Base):
    """PayNow pacs.004 parser - Payment Return."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "PAYNOW_pacs004"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'PAYNOW_pacs004'}

        result['isPayNow'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


# =============================================================================
# LEGACY JSON PARSER (for backward compatibility)
# =============================================================================

class PayNowJsonParser:
    """Parser for PayNow JSON format messages (legacy format).

    Handles the flat JSON structure:
    {
        "transactionId": "PAYNOW-E2E-20260106-001",
        "endToEndId": "E2E-PN-20260106-001",
        "creationDateTime": "2026-01-06T10:45:00+08:00",
        "amount": 85000.00,
        "currency": "SGD",
        "payerProxyType": "UEN",
        "payerProxyValue": "202012345G",
        "payerName": "Singapore Tech Holdings Pte Ltd",
        "payerBankCode": "DBSSSGSG",
        "payerBankBic": "DBSSSGSGXXX",
        "payerAccount": "1234567890",
        "payerAddress": { "streetName": "...", "city": "Singapore", ... },
        "payeeName": "Tan Ah Kow",
        "payeeAccount": "9876543210",
        "payeeAddress": { ... },
        "remittanceInfo": { "structured": {...}, "unstructured": "..." }
    }
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse PayNow JSON message into structured dict."""
        result = {
            'messageType': 'PAYNOW',
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
                    logger.warning(f"Failed to parse PayNow JSON: {e}")
                    return result
            else:
                logger.warning("PayNow content is not JSON")
                return result

        # Core fields
        result['transactionId'] = data.get('transactionId')
        result['endToEndId'] = data.get('endToEndId')
        result['creationDateTime'] = data.get('creationDateTime')
        result['settlementDate'] = data.get('settlementDate')
        result['acceptanceDateTime'] = data.get('acceptanceDateTime')

        # Amount
        result['amount'] = data.get('amount')
        result['currency'] = data.get('currency') or DEFAULT_CURRENCY
        result['chargeBearer'] = data.get('chargeBearer')

        # Payment type
        result['paymentType'] = data.get('paymentType')
        result['localInstrument'] = data.get('localInstrument')

        # Payer information
        result['payerProxyType'] = data.get('payerProxyType')  # NRIC, UEN, MOBILE, VPA
        result['payerProxyValue'] = data.get('payerProxyValue')
        result['payerName'] = data.get('payerName')
        result['payerUen'] = data.get('payerUen')
        result['payerBankCode'] = data.get('payerBankCode')
        result['payerBankName'] = data.get('payerBankName')
        result['payerBankBic'] = data.get('payerBankBic')
        result['payerAccount'] = data.get('payerAccount')
        result['payerAccountType'] = data.get('payerAccountType')

        payer_addr = data.get('payerAddress', {})
        result['payerStreetName'] = payer_addr.get('streetName')
        result['payerBuildingNumber'] = payer_addr.get('buildingNumber')
        result['payerBuildingName'] = payer_addr.get('buildingName')
        result['payerFloor'] = payer_addr.get('floor')
        result['payerPostalCode'] = payer_addr.get('postalCode')
        result['payerCity'] = payer_addr.get('city')
        result['payerCountry'] = payer_addr.get('country') or DEFAULT_COUNTRY

        payer_contact = data.get('payerContact', {})
        result['payerContactName'] = payer_contact.get('name')
        result['payerContactPhone'] = payer_contact.get('phone')
        result['payerContactEmail'] = payer_contact.get('email')

        # Payee information
        result['payeeProxyType'] = data.get('payeeProxyType')
        result['payeeProxyValue'] = data.get('payeeProxyValue')
        result['payeeName'] = data.get('payeeName')
        result['payeeBankCode'] = data.get('payeeBankCode')
        result['payeeBankName'] = data.get('payeeBankName')
        result['payeeBankBic'] = data.get('payeeBankBic')
        result['payeeAccount'] = data.get('payeeAccount')
        result['payeeAccountType'] = data.get('payeeAccountType')

        payee_addr = data.get('payeeAddress', {})
        result['payeeStreetName'] = payee_addr.get('streetName')
        result['payeeBuildingNumber'] = payee_addr.get('buildingNumber')
        result['payeeBuildingName'] = payee_addr.get('buildingName')
        result['payeeFloor'] = payee_addr.get('floor')
        result['payeePostalCode'] = payee_addr.get('postalCode')
        result['payeeCity'] = payee_addr.get('city')
        result['payeeCountry'] = payee_addr.get('country') or DEFAULT_COUNTRY

        payee_contact = data.get('payeeContact', {})
        result['payeeContactName'] = payee_contact.get('name')
        result['payeeContactPhone'] = payee_contact.get('phone')
        result['payeeContactEmail'] = payee_contact.get('email')

        # Remittance information
        remit = data.get('remittanceInfo', {})
        if isinstance(remit, dict):
            structured = remit.get('structured', {})
            result['invoiceNumber'] = structured.get('invoiceNumber')
            result['invoiceDate'] = structured.get('invoiceDate')
            result['dueAmount'] = structured.get('dueAmount')
            result['remittanceUnstructured'] = remit.get('unstructured')
        else:
            result['remittanceUnstructured'] = str(remit) if remit else None

        # Purpose
        result['purposeCode'] = data.get('purposeCode')
        result['categoryPurpose'] = data.get('categoryPurpose')

        # Flags
        result['isPayNow'] = True
        result['clearingSystem'] = CLEARING_SYSTEM

        return result


# =============================================================================
# UNIFIED PAYNOW PARSER (auto-detects message type)
# =============================================================================

class PayNowISO20022Parser:
    """Unified PayNow ISO 20022 parser that auto-detects message type."""

    ROOT_TO_PARSER = {
        'FIToFICstmrCdtTrf': 'pacs008',
        'FIToFIPmtStsRpt': 'pacs002',
        'PmtRtr': 'pacs004',
    }

    def __init__(self):
        self.pacs008_parser = PayNowPacs008Parser()
        self.pacs002_parser = PayNowPacs002Parser()
        self.pacs004_parser = PayNowPacs004Parser()
        self.json_parser = PayNowJsonParser()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse PayNow message, auto-detecting format (JSON vs XML) and message type."""
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
# PAYNOW EXTRACTOR
# =============================================================================

class PayNowExtractor(BaseExtractor):
    """Extractor for Singapore PayNow instant payment messages.

    Supports both ISO 20022 XML format (pacs.008, pacs.002, pacs.004)
    and legacy JSON format for backward compatibility.

    PayNow leverages MEPS+ infrastructure for settlement:
    - PayNow (retail) -> FAST (clearing) -> MEPS+ (RTGS settlement)
    """

    MESSAGE_TYPE = "PAYNOW"
    SILVER_TABLE = "stg_paynow"
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    CLEARING_SYSTEM = CLEARING_SYSTEM

    def __init__(self):
        """Initialize extractor with unified parser."""
        super().__init__()
        self.iso20022_parser = PayNowISO20022Parser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw PayNow content."""
        # Parse if string
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        msg_id = parsed.get('transactionId', '') or parsed.get('endToEndId', '')
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
        """Extract all Silver layer fields from PayNow message.

        Supports multiple field naming conventions:
        - ISO 20022 fields (debtorName, creditorName, etc.)
        - Legacy JSON fields (payerName, payeeName, etc.)
        - Proxy fields (payerProxyType, payerProxyValue, etc.)
        """
        trunc = self.trunc

        # Parse if needed
        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        elif not msg_content.get('isPayNow') and not msg_content.get('isISO20022'):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = msg_content

        # Handle field name variations - ISO 20022 vs Legacy JSON
        payer_name = (
            parsed.get('payerName') or
            parsed.get('debtorName')
        )
        payer_account = (
            parsed.get('payerAccount') or
            parsed.get('debtorAccountOther') or
            parsed.get('debtorAccountIban')
        )
        payee_name = (
            parsed.get('payeeName') or
            parsed.get('creditorName')
        )
        payee_account = (
            parsed.get('payeeAccount') or
            parsed.get('creditorAccountOther') or
            parsed.get('creditorAccountIban')
        )

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'PAYNOW',
            'transaction_id': trunc(
                parsed.get('transactionId') or
                parsed.get('transactionId'),
                35
            ),
            'creation_date_time': parsed.get('creationDateTime'),

            # Amount
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or DEFAULT_CURRENCY,

            # Payer (Debtor)
            'payer_proxy_type': trunc(parsed.get('payerProxyType'), 10),  # NRIC, UEN, MOBILE, VPA
            'payer_proxy_value': trunc(parsed.get('payerProxyValue'), 50),
            'payer_name': trunc(payer_name, 140),
            'payer_bank_code': trunc(
                parsed.get('payerBankCode') or
                parsed.get('debtorAgentMemberId') or
                parsed.get('instructingAgentMemberId'),
                11
            ),
            'payer_account': trunc(payer_account, 34),

            # Payee (Creditor)
            'payee_proxy_type': trunc(parsed.get('payeeProxyType'), 10),
            'payee_proxy_value': trunc(parsed.get('payeeProxyValue'), 50),
            'payee_name': trunc(payee_name, 140),
            'payee_bank_code': trunc(
                parsed.get('payeeBankCode') or
                parsed.get('creditorAgentMemberId') or
                parsed.get('instructedAgentMemberId'),
                11
            ),
            'payee_account': trunc(payee_account, 34),

            # Payment Details
            'end_to_end_id': trunc(
                parsed.get('endToEndId') or
                parsed.get('endToEndId'),
                35
            ),
            'remittance_info': parsed.get('remittanceUnstructured') or parsed.get('remittanceUnstructured'),

            # Additional parsed fields
            'settlement_date': parsed.get('settlementDate') or parsed.get('interbankSettlementDate'),
            'acceptance_date_time': parsed.get('acceptanceDateTime'),
            'charge_bearer': trunc(parsed.get('chargeBearer'), 10),
            'payment_type': trunc(
                parsed.get('paymentType') or
                parsed.get('localInstrumentCode'),
                10
            ),
            'local_instrument': trunc(parsed.get('localInstrument'), 10),
            'payer_uen': trunc(parsed.get('payerUen'), 20),
            'payer_bank_name': trunc(
                parsed.get('payerBankName') or
                parsed.get('debtorAgentName'),
                140
            ),
            'payer_bank_bic': trunc(
                parsed.get('payerBankBic') or
                parsed.get('debtorAgentBic'),
                11
            ),
            'payer_account_type': trunc(parsed.get('payerAccountType'), 10),
            'payee_bank_name': trunc(
                parsed.get('payeeBankName') or
                parsed.get('creditorAgentName'),
                140
            ),
            'payee_bank_bic': trunc(
                parsed.get('payeeBankBic') or
                parsed.get('creditorAgentBic'),
                11
            ),
            'payee_account_type': trunc(parsed.get('payeeAccountType'), 10),
            'purpose_code': trunc(
                parsed.get('purposeCode') or
                parsed.get('categoryPurposeCode'),
                10
            ),
            'category_purpose': trunc(parsed.get('categoryPurpose'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        NOTE: Column names MUST match silver.stg_paynow table exactly.
        """
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'transaction_id', 'creation_date_time',
            'amount', 'currency',
            'payer_proxy_type', 'payer_proxy_value', 'payer_name',
            'payer_bank_code', 'payer_account',
            'payee_proxy_type', 'payee_proxy_value', 'payee_name',
            'payee_bank_code', 'payee_account',
            'end_to_end_id', 'remittance_info',
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
        """Extract Gold layer entities from PayNow Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Determine party type based on proxy type
        payer_proxy_type = silver_data.get('payer_proxy_type') or ''
        payee_proxy_type = silver_data.get('payee_proxy_type') or ''

        # Payer Party (Debtor) - uses Silver column names
        if silver_data.get('payer_name'):
            party_type = 'ORGANIZATION' if payer_proxy_type == 'UEN' else 'INDIVIDUAL'
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type=party_type,
                identification_type=payer_proxy_type if payer_proxy_type else None,
                identification_number=silver_data.get('payer_proxy_value') or silver_data.get('payer_uen'),
                country=DEFAULT_COUNTRY,
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            party_type = 'ORGANIZATION' if payee_proxy_type == 'UEN' else 'INDIVIDUAL'
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type=party_type,
                identification_type=payee_proxy_type if payee_proxy_type else None,
                identification_number=silver_data.get('payee_proxy_value'),
                country=DEFAULT_COUNTRY,
            ))

        # Payer Account (or Proxy)
        if silver_data.get('payer_account') or silver_data.get('payer_proxy_value'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account') or silver_data.get('payer_proxy_value'),
                role="DEBTOR",
                account_type=silver_data.get('payer_account_type') or 'CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        # Payee Account (or Proxy)
        if silver_data.get('payee_account') or silver_data.get('payee_proxy_value'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account') or silver_data.get('payee_proxy_value'),
                role="CREDITOR",
                account_type=silver_data.get('payee_account_type') or 'CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        # Payer Bank
        if silver_data.get('payer_bank_code') or silver_data.get('payer_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('payer_bank_name'),
                bic=silver_data.get('payer_bank_bic'),
                clearing_code=silver_data.get('payer_bank_code'),
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        # Payee Bank
        if silver_data.get('payee_bank_code') or silver_data.get('payee_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('payee_bank_name'),
                bic=silver_data.get('payee_bank_bic'),
                clearing_code=silver_data.get('payee_bank_code'),
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        return entities


# =============================================================================
# REGISTER EXTRACTORS
# =============================================================================

ExtractorRegistry.register('PAYNOW', PayNowExtractor())
ExtractorRegistry.register('paynow', PayNowExtractor())
ExtractorRegistry.register('PayNow', PayNowExtractor())
ExtractorRegistry.register('FAST', PayNowExtractor())  # FAST uses same format

# Message type specific aliases
ExtractorRegistry.register('PAYNOW_pacs008', PayNowExtractor())
ExtractorRegistry.register('PAYNOW_pacs002', PayNowExtractor())
ExtractorRegistry.register('PAYNOW_pacs004', PayNowExtractor())

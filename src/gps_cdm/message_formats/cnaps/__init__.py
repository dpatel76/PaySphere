"""China CNAPS (China National Advanced Payment System) and CIPS Extractor.

ISO 20022 INHERITANCE HIERARCHY:
    CNAPS2/CIPS uses PBOC (People's Bank of China) ISO 20022 usage guidelines.
    Supports multiple ISO 20022 message types:

    BaseISO20022Parser
        ├── Pacs008Parser (FI to FI Customer Credit Transfer)
        │   └── CnapsPacs008Parser (CNAPS2 domestic + CIPS cross-border)
        ├── Pacs009Parser (FI Credit Transfer)
        │   └── CnapsPacs009Parser (Interbank transfers)
        ├── Pacs002Parser (Payment Status Report)
        │   └── CnapsPacs002Parser
        └── Pacs004Parser (Payment Return)
            └── CnapsPacs004Parser

SUPPORTED MESSAGE TYPES:
    - pacs.008: Customer Credit Transfer (primary payment)
    - pacs.009: FI Credit Transfer (interbank)
    - pacs.002: Payment Status Report
    - pacs.004: Payment Return

CNAPS/CIPS-SPECIFIC ELEMENTS:
    - CNAPS bank codes (14-digit clearing member ID)
    - CNY currency (Chinese Yuan Renminbi)
    - Mandarin character support
    - LEI integration (CIPS)

CLEARING SYSTEMS:
    - CNCNAPS (CNAPS2 - High Value Payment System)
    - CNCIPS (Cross-border Interbank Payment System)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_cnaps
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
    logger.warning("ISO 20022 base classes not available - CNAPS will use standalone implementation")


# =============================================================================
# CNAPS CONSTANTS
# =============================================================================

CLEARING_SYSTEM_DOMESTIC = "CNCNAPS"  # CNAPS2 for domestic
CLEARING_SYSTEM_CROSSBORDER = "CNCIPS"  # CIPS for cross-border
DEFAULT_CURRENCY = "CNY"
DEFAULT_COUNTRY = "CN"


# =============================================================================
# CNAPS ISO 20022 PARSERS (inherit from base ISO 20022 parsers)
# =============================================================================

_Pacs008Base = Pacs008Parser if ISO20022_BASE_AVAILABLE else object
_Pacs009Base = Pacs009Parser if ISO20022_BASE_AVAILABLE else object
_Pacs002Base = Pacs002Parser if ISO20022_BASE_AVAILABLE else object
_Pacs004Base = Pacs004Parser if ISO20022_BASE_AVAILABLE else object


class CnapsPacs008Parser(_Pacs008Base):
    """CNAPS/CIPS pacs.008 parser - FI to FI Customer Credit Transfer.

    Primary message type for CNAPS2 domestic and CIPS cross-border payments.
    Inherits all pacs.008 parsing from base and adds CNAPS-specific fields.
    """

    CLEARING_SYSTEM = CLEARING_SYSTEM_DOMESTIC
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "CNAPS_pacs008"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse CNAPS pacs.008 message using inherited base parsing."""
        if isinstance(raw_content, dict):
            return raw_content

        if isinstance(raw_content, str) and raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'CNAPS_pacs008'}

        # Add CNAPS-specific fields
        result['isCnaps'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        result['defaultCurrency'] = self.DEFAULT_CURRENCY

        return result


class CnapsPacs009Parser(_Pacs009Base):
    """CNAPS/CIPS pacs.009 parser - FI Credit Transfer.

    Used for interbank transfers between financial institutions.
    """

    CLEARING_SYSTEM = CLEARING_SYSTEM_DOMESTIC
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "CNAPS_pacs009"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'CNAPS_pacs009'}

        result['isCnaps'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class CnapsPacs002Parser(_Pacs002Base):
    """CNAPS pacs.002 parser - Payment Status Report."""

    CLEARING_SYSTEM = CLEARING_SYSTEM_DOMESTIC
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "CNAPS_pacs002"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'CNAPS_pacs002'}

        result['isCnaps'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class CnapsPacs004Parser(_Pacs004Base):
    """CNAPS pacs.004 parser - Payment Return."""

    CLEARING_SYSTEM = CLEARING_SYSTEM_DOMESTIC
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "CNAPS_pacs004"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'CNAPS_pacs004'}

        result['isCnaps'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


# =============================================================================
# LEGACY JSON PARSER (for backward compatibility)
# =============================================================================

class CnapsJsonParser:
    """Parser for CNAPS JSON messages (legacy format).

    Kept for backward compatibility with existing JSON test data.
    """

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse CNAPS JSON content and normalize field names."""
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse CNAPS JSON: {e}")
                return {'messageType': 'CNAPS'}
        else:
            data = content

        # Map JSON keys to expected Silver field names (camelCase for parser output)
        return {
            # Message identification
            'messageId': data.get('messageId') or data.get('transactionId') or '',
            'creationDateTime': data.get('creationDateTime'),
            'settlementDate': data.get('settlementDate'),
            'businessType': data.get('businessType'),

            # Amount
            'amount': data.get('amount'),
            'currency': data.get('currency') or DEFAULT_CURRENCY,

            # Bank codes - map payerBankCode/payeeBankCode to sending/receiving
            'sendingBankCode': data.get('payerBankCode') or data.get('sendingBankCode'),
            'receivingBankCode': data.get('payeeBankCode') or data.get('receivingBankCode'),

            # Payer (Debtor)
            'debtorName': data.get('payerName'),
            'debtorAccount': data.get('payerAccount'),
            'debtorBankName': data.get('payerBankName'),

            # Payee (Creditor)
            'creditorName': data.get('payeeName'),
            'creditorAccount': data.get('payeeAccount'),
            'creditorBankName': data.get('payeeBankName'),

            # Transaction details
            'transactionReference': data.get('transactionId') or data.get('transactionReference') or data.get('messageId'),
            'purposeCode': self._extract_purpose(data),

            # Flags
            'isCnaps': True,
            'clearingSystem': CLEARING_SYSTEM_DOMESTIC,
        }

    def _extract_purpose(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract purpose from various possible locations."""
        if data.get('purpose'):
            return data.get('purpose')
        if data.get('purposeCode'):
            return data.get('purposeCode')
        remittance = data.get('remittanceInfo', {})
        if isinstance(remittance, dict) and remittance.get('description'):
            return remittance.get('description')
        return None


# =============================================================================
# UNIFIED CNAPS PARSER (auto-detects message type)
# =============================================================================

class CnapsISO20022Parser:
    """Unified CNAPS/CIPS ISO 20022 parser that auto-detects message type.

    Routes to appropriate parser based on content:
    - XML with FIToFICstmrCdtTrf -> CnapsPacs008Parser
    - XML with FICdtTrf -> CnapsPacs009Parser
    - XML with FIToFIPmtStsRpt -> CnapsPacs002Parser
    - XML with PmtRtr -> CnapsPacs004Parser
    - JSON -> CnapsJsonParser (legacy)
    """

    ROOT_TO_PARSER = {
        'FIToFICstmrCdtTrf': 'pacs008',
        'FICdtTrf': 'pacs009',
        'FIToFIPmtStsRpt': 'pacs002',
        'PmtRtr': 'pacs004',
    }

    def __init__(self):
        self.pacs008_parser = CnapsPacs008Parser()
        self.pacs009_parser = CnapsPacs009Parser()
        self.pacs002_parser = CnapsPacs002Parser()
        self.pacs004_parser = CnapsPacs004Parser()
        self.json_parser = CnapsJsonParser()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse CNAPS message, auto-detecting format and type."""
        if isinstance(raw_content, dict):
            # Already parsed dict - normalize via JSON parser
            return self.json_parser.parse(raw_content)

        content = raw_content.strip() if isinstance(raw_content, str) else ''

        # JSON format
        if content.startswith('{'):
            return self.json_parser.parse(content)

        # XML format - detect message type
        msg_type = self._detect_message_type(content)

        if msg_type == 'pacs008':
            return self.pacs008_parser.parse(content)
        elif msg_type == 'pacs009':
            return self.pacs009_parser.parse(content)
        elif msg_type == 'pacs002':
            return self.pacs002_parser.parse(content)
        elif msg_type == 'pacs004':
            return self.pacs004_parser.parse(content)
        else:
            # Default to pacs.008 for XML
            return self.pacs008_parser.parse(content)

    def _detect_message_type(self, xml_content: str) -> str:
        """Detect ISO 20022 message type from XML content."""
        for root_elem, msg_type in self.ROOT_TO_PARSER.items():
            if root_elem in xml_content:
                return msg_type
        return 'pacs008'


# =============================================================================
# CNAPS EXTRACTOR (handles all message types)
# =============================================================================

class CnapsExtractor(BaseExtractor):
    """Extractor for China CNAPS/CIPS payment messages.

    ISO 20022 INHERITANCE:
        CNAPS uses PBOC (People's Bank of China) ISO 20022 usage guidelines.
        Supports pacs.008, pacs.009, pacs.002, and pacs.004 message types.

    Message Type Support:
        - CNAPS / CNAPS_pacs008: Customer Credit Transfer (primary)
        - CNAPS_pacs009: FI Credit Transfer (interbank)
        - CNAPS_pacs002: Payment Status Report
        - CNAPS_pacs004: Payment Return

    Format Support:
        - ISO 20022 XML (CNAPS2 domestic, CIPS cross-border)
        - JSON (legacy format)

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_cnaps
        - Gold: Semantic tables via DynamicGoldMapper
    """

    MESSAGE_TYPE = "CNAPS"
    SILVER_TABLE = "stg_cnaps"
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    CLEARING_SYSTEM = CLEARING_SYSTEM_DOMESTIC

    def __init__(self):
        """Initialize extractor with ISO 20022 parser."""
        super().__init__()
        self.iso20022_parser = CnapsISO20022Parser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw CNAPS content."""
        msg_id = (
            raw_content.get('messageId') or
            raw_content.get('transactionReference') or
            raw_content.get('transactionId') or
            ''
        )
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
        """Extract Silver layer fields from CNAPS message.

        Handles both ISO 20022 parser output and legacy JSON format.
        """
        trunc = self.trunc

        # Parse if needed
        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        elif not msg_content.get('isCnaps') and not msg_content.get('isISO20022'):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = msg_content

        # Map parser output (camelCase) to Silver columns (snake_case)
        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            'message_type': 'CNAPS',

            # Message identification
            'message_id': trunc(parsed.get('messageId'), 35),
            'creation_date_time': parsed.get('creationDateTime'),
            'settlement_date': parsed.get('settlementDate'),
            'business_type': trunc(parsed.get('businessType'), 10),

            # Amount
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or DEFAULT_CURRENCY,

            # Bank codes
            'sending_bank_code': trunc(
                parsed.get('sendingBankCode') or
                parsed.get('debtorAgentBic') or
                parsed.get('instructingAgentMemberId'),
                14
            ),
            'receiving_bank_code': trunc(
                parsed.get('receivingBankCode') or
                parsed.get('creditorAgentBic') or
                parsed.get('instructedAgentMemberId'),
                14
            ),

            # Payer (Debtor)
            'payer_name': trunc(parsed.get('debtorName'), 140),
            'payer_account': trunc(
                parsed.get('debtorAccount') or
                parsed.get('debtorAccountOther'),
                34
            ),
            'payer_bank_name': trunc(parsed.get('debtorBankName') or parsed.get('debtorAgentName'), 140),

            # Payee (Creditor)
            'payee_name': trunc(parsed.get('creditorName'), 140),
            'payee_account': trunc(
                parsed.get('creditorAccount') or
                parsed.get('creditorAccountOther'),
                34
            ),
            'payee_bank_name': trunc(parsed.get('creditorBankName') or parsed.get('creditorAgentName'), 140),

            # Transaction details
            'transaction_reference': trunc(
                parsed.get('transactionReference') or
                parsed.get('endToEndId') or
                parsed.get('transactionId'),
                35
            ),
            'purpose': parsed.get('purposeCode') or parsed.get('remittanceUnstructured'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'business_type', 'amount', 'currency',
            'sending_bank_code', 'receiving_bank_code',
            'payer_name', 'payer_account', 'payer_bank_name',
            'payee_name', 'payee_account', 'payee_bank_name',
            'transaction_reference', 'purpose',
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
        """Extract Gold layer entities from CNAPS Silver record."""
        entities = GoldEntities()

        # Payer Party (Debtor)
        if silver_data.get('payer_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type='ORGANIZATION',
                country=DEFAULT_COUNTRY,
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='ORGANIZATION',
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

        # Sending Bank (Debtor Agent)
        if silver_data.get('sending_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('payer_bank_name'),
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system=CLEARING_SYSTEM_DOMESTIC,
                country=DEFAULT_COUNTRY,
            ))

        # Receiving Bank (Creditor Agent)
        if silver_data.get('receiving_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('payee_bank_name'),
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system=CLEARING_SYSTEM_DOMESTIC,
                country=DEFAULT_COUNTRY,
            ))

        return entities


# =============================================================================
# REGISTER EXTRACTORS
# =============================================================================

# Main CNAPS extractor (handles all message types via auto-detection)
ExtractorRegistry.register('CNAPS', CnapsExtractor())
ExtractorRegistry.register('cnaps', CnapsExtractor())
ExtractorRegistry.register('CIPS', CnapsExtractor())  # Cross-border alias
ExtractorRegistry.register('cips', CnapsExtractor())

# Message type specific aliases
ExtractorRegistry.register('CNAPS_pacs008', CnapsExtractor())
ExtractorRegistry.register('CNAPS_pacs009', CnapsExtractor())
ExtractorRegistry.register('CNAPS_pacs002', CnapsExtractor())
ExtractorRegistry.register('CNAPS_pacs004', CnapsExtractor())

"""Japan BOJ-NET (Bank of Japan Financial Network System) Extractor.

ISO 20022 INHERITANCE HIERARCHY:
    BOJ-NET uses Bank of Japan ISO 20022 usage guidelines (v8, 2019 version).
    Migrated to ISO 20022 in November 2025.

    BaseISO20022Parser
        ├── Pacs008Parser (FI to FI Customer Credit Transfer)
        │   └── BojnetPacs008Parser
        ├── Pacs009Parser (FI Credit Transfer)
        │   └── BojnetPacs009Parser
        ├── Pacs002Parser (Payment Status Report)
        │   └── BojnetPacs002Parser
        ├── Pacs004Parser (Payment Return)
        │   └── BojnetPacs004Parser
        └── Camt053Parser (Account Statement)
            └── BojnetCamt053Parser

SUPPORTED MESSAGE TYPES:
    - pacs.008: Customer Credit Transfer (MT103 equivalent)
    - pacs.009: FI Credit Transfer (MT202 equivalent)
    - pacs.002: Payment Status Report
    - pacs.004: Payment Return (MT103R equivalent)
    - camt.053: Account Statement (MT940/950 equivalent)

BOJ-NET-SPECIFIC ELEMENTS:
    - BOJ participant codes
    - JPY currency (Japanese Yen)
    - Real-time gross settlement via Bank of Japan
    - CBPR+ aligned (November 2025)

CLEARING SYSTEM:
    - JPBOJ (Bank of Japan Financial Network)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_bojnet
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
        Camt053Parser, Camt053Extractor,
    )
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - BOJNET will use standalone implementation")


# =============================================================================
# BOJNET CONSTANTS
# =============================================================================

CLEARING_SYSTEM = "JPBOJ"
DEFAULT_CURRENCY = "JPY"
DEFAULT_COUNTRY = "JP"


# =============================================================================
# BOJNET ISO 20022 PARSERS (inherit from base ISO 20022 parsers)
# =============================================================================

_Pacs008Base = Pacs008Parser if ISO20022_BASE_AVAILABLE else object
_Pacs009Base = Pacs009Parser if ISO20022_BASE_AVAILABLE else object
_Pacs002Base = Pacs002Parser if ISO20022_BASE_AVAILABLE else object
_Pacs004Base = Pacs004Parser if ISO20022_BASE_AVAILABLE else object
_Camt053Base = Camt053Parser if ISO20022_BASE_AVAILABLE else object


class BojnetPacs008Parser(_Pacs008Base):
    """BOJ-NET pacs.008 parser - FI to FI Customer Credit Transfer."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "BOJNET_pacs008"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
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
            result = {'messageType': 'BOJNET_pacs008'}

        result['isBojnet'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        result['defaultCurrency'] = self.DEFAULT_CURRENCY
        return result


class BojnetPacs009Parser(_Pacs009Base):
    """BOJ-NET pacs.009 parser - FI Credit Transfer."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "BOJNET_pacs009"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'BOJNET_pacs009'}

        result['isBojnet'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class BojnetPacs002Parser(_Pacs002Base):
    """BOJ-NET pacs.002 parser - Payment Status Report."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "BOJNET_pacs002"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'BOJNET_pacs002'}

        result['isBojnet'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class BojnetPacs004Parser(_Pacs004Base):
    """BOJ-NET pacs.004 parser - Payment Return."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "BOJNET_pacs004"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'BOJNET_pacs004'}

        result['isBojnet'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


class BojnetCamt053Parser(_Camt053Base):
    """BOJ-NET camt.053 parser - Account Statement."""

    CLEARING_SYSTEM = CLEARING_SYSTEM
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    MESSAGE_TYPE = "BOJNET_camt053"

    def __init__(self):
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return raw_content

        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = {'messageType': 'BOJNET_camt053'}

        result['isBojnet'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM
        return result


# =============================================================================
# LEGACY JSON PARSER (for backward compatibility)
# =============================================================================

class BojnetJsonParser:
    """Parser for BOJ-NET JSON messages (legacy format)."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            data = raw_content
        else:
            if raw_content.strip().startswith('{'):
                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse BOJ-NET JSON: {e}")
                    return {'messageType': 'BOJNET'}
            else:
                return {'messageType': 'BOJNET'}

        # Extract header fields
        header = data.get('header', {})

        # Extract first transaction (or use flat structure)
        transactions = data.get('transactions', [])
        tx = transactions[0] if transactions else data

        # Payer information
        payer = tx.get('payer', {})
        payer_addr = payer.get('address', {})

        # Payee information
        payee = tx.get('payee', {})
        payee_addr = payee.get('address', {})

        return {
            'messageType': 'BOJNET',
            'batchId': header.get('batchId'),
            'messageId': tx.get('messageId'),
            'transactionReference': tx.get('transactionReference'),
            'creationDateTime': tx.get('creationDateTime') or header.get('creationDateTime'),
            'settlementDate': tx.get('settlementDate') or header.get('settlementDate'),
            'valueDate': tx.get('valueDate'),
            'amount': tx.get('amount'),
            'currency': tx.get('currency') or DEFAULT_CURRENCY,
            'chargeBearer': tx.get('chargeBearer'),

            # Participant codes
            'sendingParticipantCode': tx.get('sendingParticipantCode'),
            'sendingParticipantName': tx.get('sendingParticipantName'),
            'sendingParticipantBic': tx.get('sendingParticipantBic'),
            'receivingParticipantCode': tx.get('receivingParticipantCode'),
            'receivingParticipantName': tx.get('receivingParticipantName'),
            'receivingParticipantBic': tx.get('receivingParticipantBic'),

            # Accounts
            'debitAccount': tx.get('debitAccount'),
            'creditAccount': tx.get('creditAccount'),

            # Payment type
            'paymentType': tx.get('paymentType'),
            'purposeCode': tx.get('purposeCode'),

            # Payer (Debtor)
            'debtorName': payer.get('name'),
            'debtorAccount': payer.get('accountNumber'),
            'debtorCountry': payer_addr.get('country') or DEFAULT_COUNTRY,

            # Payee (Creditor)
            'creditorName': payee.get('name'),
            'creditorAccount': payee.get('accountNumber'),
            'creditorCountry': payee_addr.get('country') or DEFAULT_COUNTRY,

            # Flags
            'isBojnet': True,
            'clearingSystem': CLEARING_SYSTEM,
        }


# =============================================================================
# UNIFIED BOJNET PARSER (auto-detects message type)
# =============================================================================

class BojnetISO20022Parser:
    """Unified BOJ-NET ISO 20022 parser that auto-detects message type."""

    ROOT_TO_PARSER = {
        'FIToFICstmrCdtTrf': 'pacs008',
        'FICdtTrf': 'pacs009',
        'FIToFIPmtStsRpt': 'pacs002',
        'PmtRtr': 'pacs004',
        'BkToCstmrStmt': 'camt053',
    }

    def __init__(self):
        self.pacs008_parser = BojnetPacs008Parser()
        self.pacs009_parser = BojnetPacs009Parser()
        self.pacs002_parser = BojnetPacs002Parser()
        self.pacs004_parser = BojnetPacs004Parser()
        self.camt053_parser = BojnetCamt053Parser()
        self.json_parser = BojnetJsonParser()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        if isinstance(raw_content, dict):
            return self.json_parser.parse(raw_content)

        content = raw_content.strip() if isinstance(raw_content, str) else ''

        if content.startswith('{'):
            return self.json_parser.parse(content)

        msg_type = self._detect_message_type(content)

        parser_map = {
            'pacs008': self.pacs008_parser,
            'pacs009': self.pacs009_parser,
            'pacs002': self.pacs002_parser,
            'pacs004': self.pacs004_parser,
            'camt053': self.camt053_parser,
        }

        parser = parser_map.get(msg_type, self.pacs008_parser)
        return parser.parse(content)

    def _detect_message_type(self, xml_content: str) -> str:
        for root_elem, msg_type in self.ROOT_TO_PARSER.items():
            if root_elem in xml_content:
                return msg_type
        return 'pacs008'

    def parse_iso_paths(self, raw_content: str) -> Dict[str, Any]:
        """Parse using full ISO path key naming (e.g., GrpHdr.MsgId).

        Delegates to the appropriate sub-parser's parse_iso_paths() method
        based on detected message type.
        """
        if isinstance(raw_content, dict):
            # Already parsed - return as-is (JSON format)
            return self.json_parser.parse(raw_content)

        content = raw_content.strip() if isinstance(raw_content, str) else ''

        if content.startswith('{'):
            # JSON content
            return self.json_parser.parse(content)

        msg_type = self._detect_message_type(content)

        parser_map = {
            'pacs008': self.pacs008_parser,
            'pacs009': self.pacs009_parser,
            'pacs002': self.pacs002_parser,
            'pacs004': self.pacs004_parser,
            'camt053': self.camt053_parser,
        }

        parser = parser_map.get(msg_type, self.pacs008_parser)

        # Use parse_iso_paths() if available, else fall back to parse()
        if hasattr(parser, 'parse_iso_paths'):
            result = parser.parse_iso_paths(content)
        else:
            result = parser.parse(content)

        # Add BOJNET-specific flags
        result['isBojnet'] = True
        result['clearingSystem'] = CLEARING_SYSTEM
        return result


# =============================================================================
# BOJNET EXTRACTOR
# =============================================================================

class BojnetExtractor(BaseExtractor):
    """Extractor for Japan BOJ-NET payment messages."""

    MESSAGE_TYPE = "BOJNET"
    SILVER_TABLE = "stg_bojnet"
    DEFAULT_CURRENCY = DEFAULT_CURRENCY
    CLEARING_SYSTEM = CLEARING_SYSTEM

    def __init__(self):
        super().__init__()
        self.iso20022_parser = BojnetISO20022Parser()
        self.parser = self.iso20022_parser

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        msg_id = raw_content.get('messageId', '') or raw_content.get('transactionReference', '')
        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': json.dumps(raw_content) if isinstance(raw_content, dict) else raw_content,
            'batch_id': batch_id,
        }

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        trunc = self.trunc

        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        elif not msg_content.get('isBojnet') and not msg_content.get('isISO20022'):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = msg_content

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            'message_type': 'BOJNET',
            'message_id': trunc(parsed.get('messageId'), 35),
            'creation_date_time': parsed.get('creationDateTime'),
            'settlement_date': parsed.get('settlementDate'),
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or DEFAULT_CURRENCY,
            'sending_participant_code': trunc(
                parsed.get('sendingParticipantCode') or
                parsed.get('debtorAgentMemberId') or
                parsed.get('instructingAgentMemberId'),
                11
            ),
            'receiving_participant_code': trunc(
                parsed.get('receivingParticipantCode') or
                parsed.get('creditorAgentMemberId') or
                parsed.get('instructedAgentMemberId'),
                11
            ),
            'transaction_reference': trunc(
                parsed.get('transactionReference') or
                parsed.get('endToEndId'),
                35
            ),
            'related_reference': trunc(parsed.get('relatedReference'), 35),
            'debit_account': trunc(
                parsed.get('debitAccount') or
                parsed.get('debtorAccountOther'),
                34
            ),
            'credit_account': trunc(
                parsed.get('creditAccount') or
                parsed.get('creditorAccountOther'),
                34
            ),
            'payment_type': trunc(parsed.get('paymentType'), 10),
            'payer_name': trunc(parsed.get('debtorName'), 140),
            'payee_name': trunc(parsed.get('creditorName'), 140),
            'sending_participant_name': trunc(
                parsed.get('sendingParticipantName') or
                parsed.get('debtorAgentName'),
                140
            ),
            'receiving_participant_name': trunc(
                parsed.get('receivingParticipantName') or
                parsed.get('creditorAgentName'),
                140
            ),
            'sending_participant_bic': trunc(
                parsed.get('sendingParticipantBic') or
                parsed.get('debtorAgentBic'),
                11
            ),
            'receiving_participant_bic': trunc(
                parsed.get('receivingParticipantBic') or
                parsed.get('creditorAgentBic'),
                11
            ),
            'value_date': parsed.get('valueDate'),
            'charge_bearer': trunc(parsed.get('chargeBearer'), 10),
            'purpose_code': trunc(parsed.get('purposeCode'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_participant_code', 'receiving_participant_code',
            'transaction_reference', 'related_reference',
            'debit_account', 'credit_account',
            'payment_type',
            'payer_name', 'payee_name',
            'sending_participant_name', 'receiving_participant_name',
            'sending_participant_bic', 'receiving_participant_bic',
            'value_date', 'charge_bearer', 'purpose_code',
        ]

    def get_silver_values(self, silver_record: Dict[str, Any]) -> tuple:
        columns = self.get_silver_columns()
        return tuple(silver_record.get(col) for col in columns)

    def extract_gold_entities(
        self,
        silver_data: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        entities = GoldEntities()

        if silver_data.get('payer_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type='ORGANIZATION',
                country=DEFAULT_COUNTRY,
            ))

        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='ORGANIZATION',
                country=DEFAULT_COUNTRY,
            ))

        if silver_data.get('debit_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debit_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        if silver_data.get('credit_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('credit_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or DEFAULT_CURRENCY,
            ))

        if silver_data.get('sending_participant_code') or silver_data.get('sending_participant_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('sending_participant_name'),
                bic=silver_data.get('sending_participant_bic'),
                clearing_code=silver_data.get('sending_participant_code'),
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        if silver_data.get('receiving_participant_code') or silver_data.get('receiving_participant_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('receiving_participant_name'),
                bic=silver_data.get('receiving_participant_bic'),
                clearing_code=silver_data.get('receiving_participant_code'),
                clearing_system=CLEARING_SYSTEM,
                country=DEFAULT_COUNTRY,
            ))

        return entities


# =============================================================================
# REGISTER EXTRACTORS
# =============================================================================

ExtractorRegistry.register('BOJNET', BojnetExtractor())
ExtractorRegistry.register('bojnet', BojnetExtractor())
ExtractorRegistry.register('BOJ-NET', BojnetExtractor())

# Message type specific aliases
ExtractorRegistry.register('BOJNET_pacs008', BojnetExtractor())
ExtractorRegistry.register('BOJNET_pacs009', BojnetExtractor())
ExtractorRegistry.register('BOJNET_pacs002', BojnetExtractor())
ExtractorRegistry.register('BOJNET_pacs004', BojnetExtractor())
ExtractorRegistry.register('BOJNET_camt053', BojnetExtractor())

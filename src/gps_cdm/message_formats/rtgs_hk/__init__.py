"""Hong Kong RTGS (CHATS) Extractor - JSON based."""

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


class RtgsHkParser:
    """Parser for Hong Kong RTGS (CHATS) JSON messages."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse RTGS_HK message content.

        Handles:
        1. Dict input (already parsed)
        2. JSON string input
        3. Returns empty dict with message type on parse failure
        """
        # Handle dict input (already parsed)
        if isinstance(raw_content, dict):
            return raw_content

        # Handle string input
        if isinstance(raw_content, str):
            content = raw_content.strip()

            # Try JSON parsing
            if content.startswith('{'):
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse RTGS_HK JSON: {e}")

        # Return minimal dict on failure
        return {'messageType': 'RTGS_HK'}


class RtgsHkExtractor(BaseExtractor):
    """Extractor for Hong Kong RTGS (CHATS) payment messages."""

    MESSAGE_TYPE = "RTGS_HK"
    SILVER_TABLE = "stg_rtgs_hk"

    def __init__(self):
        """Initialize extractor with parser."""
        self.parser = RtgsHkParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw RTGS_HK content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('transactionReference', '')
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
        """Extract all Silver layer fields from RTGS_HK message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'RTGS_HK',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),
            'settlement_currency': msg_content.get('settlementCurrency') or 'HKD',

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'HKD',

            # Bank Codes
            'sending_bank_code': trunc(msg_content.get('sendingBankCode'), 11),
            'receiving_bank_code': trunc(msg_content.get('receivingBankCode'), 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

            # Payer (Debtor)
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),

            # Payee (Creditor)
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_account': trunc(msg_content.get('payeeAccount'), 34),

            # Purpose
            'purpose': msg_content.get('purpose'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'settlement_currency', 'amount', 'currency',
            'sending_bank_code', 'receiving_bank_code', 'transaction_reference',
            'payer_name', 'payer_account',
            'payee_name', 'payee_account',
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
        """Extract Gold layer entities from RTGS_HK Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Payer Party (Debtor) - uses Silver column names
        if silver_data.get('payer_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='HK',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='HK',
            ))

        # Payer Account
        if silver_data.get('payer_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'HKD',
            ))

        # Payee Account
        if silver_data.get('payee_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'HKD',
            ))

        # Sending Bank
        if silver_data.get('sending_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system='HKHKCLR',  # HKICL clearing
                country='HK',
            ))

        # Receiving Bank
        if silver_data.get('receiving_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system='HKHKCLR',
                country='HK',
            ))

        return entities


# Register the extractor
# Register the extractor with all aliases
ExtractorRegistry.register('RTGS_HK', RtgsHkExtractor())
ExtractorRegistry.register('rtgs_hk', RtgsHkExtractor())
ExtractorRegistry.register('CHATS', RtgsHkExtractor())
ExtractorRegistry.register('RTGS', RtgsHkExtractor())  # Alias for NiFi filename pattern

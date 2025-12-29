"""Philippines InstaPay Extractor - JSON based."""

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


class InstaPayExtractor(BaseExtractor):
    """Extractor for Philippines InstaPay instant payment messages."""

    MESSAGE_TYPE = "INSTAPAY"
    SILVER_TABLE = "stg_instapay"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw InstaPay content."""
        msg_id = raw_content.get('transactionId', '') or raw_content.get('referenceNumber', '')
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
        """Extract all Silver layer fields from InstaPay message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'INSTAPAY',
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'PHP',

            # Sender (Debtor)
            'sender_bank_code': trunc(msg_content.get('senderBankCode'), 11),
            'sender_account': trunc(msg_content.get('senderAccount'), 34),
            'sender_name': trunc(msg_content.get('senderName'), 140),

            # Receiver (Creditor)
            'receiver_bank_code': trunc(msg_content.get('receiverBankCode'), 11),
            'receiver_account': trunc(msg_content.get('receiverAccount'), 34),
            'receiver_name': trunc(msg_content.get('receiverName'), 140),

            # Payment Details
            'reference_number': trunc(msg_content.get('referenceNumber'), 35),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'transaction_id', 'creation_date_time',
            'amount', 'currency',
            'sender_bank_code', 'sender_account', 'sender_name',
            'receiver_bank_code', 'receiver_account', 'receiver_name',
            'reference_number', 'remittance_info',
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
        """Extract Gold layer entities from InstaPay Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Sender Party (Debtor) - uses Silver column names
        if silver_data.get('sender_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('sender_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='PH',
            ))

        # Receiver Party (Creditor)
        if silver_data.get('receiver_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('receiver_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='PH',
            ))

        # Sender Account
        if silver_data.get('sender_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('sender_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'PHP',
            ))

        # Receiver Account
        if silver_data.get('receiver_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('receiver_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'PHP',
            ))

        # Sender Bank
        if silver_data.get('sender_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('sender_bank_code'),
                clearing_system='PHINSTAPAY',
                country='PH',
            ))

        # Receiver Bank
        if silver_data.get('receiver_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('receiver_bank_code'),
                clearing_system='PHINSTAPAY',
                country='PH',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('INSTAPAY', InstaPayExtractor())
ExtractorRegistry.register('instapay', InstaPayExtractor())
ExtractorRegistry.register('InstaPay', InstaPayExtractor())

"""Japan BOJ-NET (Bank of Japan Financial Network System) Extractor - JSON based."""

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


class BojnetExtractor(BaseExtractor):
    """Extractor for Japan BOJ-NET payment messages."""

    MESSAGE_TYPE = "BOJNET"
    SILVER_TABLE = "stg_bojnet"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw BOJ-NET content."""
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
        """Extract all Silver layer fields from BOJ-NET message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'BOJNET',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'JPY',

            # Participant Codes
            'sending_participant_code': trunc(msg_content.get('sendingParticipantCode'), 11),
            'receiving_participant_code': trunc(msg_content.get('receivingParticipantCode'), 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),
            'related_reference': trunc(msg_content.get('relatedReference'), 35),

            # Accounts
            'debit_account': trunc(msg_content.get('debitAccount'), 34),
            'credit_account': trunc(msg_content.get('creditAccount'), 34),

            # Payment Type
            'payment_type': trunc(msg_content.get('paymentType'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_participant_code', 'receiving_participant_code',
            'transaction_reference', 'related_reference',
            'debit_account', 'credit_account',
            'payment_type',
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
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from BOJ-NET message."""
        entities = GoldEntities()

        # Debit Account
        if msg_content.get('debitAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('debitAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'JPY',
            ))

        # Credit Account
        if msg_content.get('creditAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('creditAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'JPY',
            ))

        # Sending Participant
        if msg_content.get('sendingParticipantCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('sendingParticipantCode'),
                clearing_system='JPBOJ',  # BOJ clearing
                country='JP',
            ))

        # Receiving Participant
        if msg_content.get('receivingParticipantCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('receivingParticipantCode'),
                clearing_system='JPBOJ',
                country='JP',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('BOJNET', BojnetExtractor())
ExtractorRegistry.register('bojnet', BojnetExtractor())
ExtractorRegistry.register('BOJ-NET', BojnetExtractor())

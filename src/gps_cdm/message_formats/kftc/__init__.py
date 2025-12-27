"""Korea KFTC (Korea Financial Telecommunications & Clearings Institute) Extractor - JSON based."""

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


class KftcExtractor(BaseExtractor):
    """Extractor for Korea KFTC payment messages."""

    MESSAGE_TYPE = "KFTC"
    SILVER_TABLE = "stg_kftc"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw KFTC content."""
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
        """Extract all Silver layer fields from KFTC message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'KFTC',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'KRW',

            # Bank Codes
            'sending_bank_code': trunc(msg_content.get('sendingBankCode'), 11),
            'receiving_bank_code': trunc(msg_content.get('receivingBankCode'), 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

            # Payer
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),

            # Payee
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
            'settlement_date', 'amount', 'currency',
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
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from KFTC message."""
        entities = GoldEntities()

        # Payer Party
        if msg_content.get('payerName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payerName'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='KR',
            ))

        # Payee Party
        if msg_content.get('payeeName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payeeName'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='KR',
            ))

        # Payer Account
        if msg_content.get('payerAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payerAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'KRW',
            ))

        # Payee Account
        if msg_content.get('payeeAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payeeAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'KRW',
            ))

        # Sending Bank
        if msg_content.get('sendingBankCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('sendingBankCode'),
                clearing_system='KRKFTC',  # Korea KFTC
                country='KR',
            ))

        # Receiving Bank
        if msg_content.get('receivingBankCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('receivingBankCode'),
                clearing_system='KRKFTC',
                country='KR',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('KFTC', KftcExtractor())
ExtractorRegistry.register('kftc', KftcExtractor())

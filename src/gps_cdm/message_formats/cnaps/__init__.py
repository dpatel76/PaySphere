"""China CNAPS (China National Advanced Payment System) Extractor - JSON based."""

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


class CnapsExtractor(BaseExtractor):
    """Extractor for China CNAPS payment messages."""

    MESSAGE_TYPE = "CNAPS"
    SILVER_TABLE = "stg_cnaps"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw CNAPS content."""
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
        """Extract all Silver layer fields from CNAPS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'CNAPS',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),
            'business_type': trunc(msg_content.get('businessType'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'CNY',

            # Bank Codes
            'sending_bank_code': trunc(msg_content.get('sendingBankCode'), 14),
            'receiving_bank_code': trunc(msg_content.get('receivingBankCode'), 14),

            # Payer
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),
            'payer_bank_name': trunc(msg_content.get('payerBankName'), 140),

            # Payee
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_account': trunc(msg_content.get('payeeAccount'), 34),
            'payee_bank_name': trunc(msg_content.get('payeeBankName'), 140),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),
            'purpose': msg_content.get('purpose'),
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
        """Extract Gold layer entities from CNAPS Silver record.

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
                country='CN',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='CN',
            ))

        # Payer Account
        if silver_data.get('payer_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'CNY',
            ))

        # Payee Account
        if silver_data.get('payee_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'CNY',
            ))

        # Sending Bank (by CNAPS code)
        if silver_data.get('sending_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('payer_bank_name'),
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system='CNCNAPS',  # CNAPS
                country='CN',
            ))

        # Receiving Bank (by CNAPS code)
        if silver_data.get('receiving_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('payee_bank_name'),
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system='CNCNAPS',
                country='CN',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('CNAPS', CnapsExtractor())
ExtractorRegistry.register('cnaps', CnapsExtractor())

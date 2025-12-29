"""ISO 20022 camt.053 (Bank to Customer Statement) Extractor."""

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


class Camt053Extractor(BaseExtractor):
    """Extractor for ISO 20022 camt.053 Bank to Customer Statement messages."""

    MESSAGE_TYPE = "camt.053"
    SILVER_TABLE = "stg_camt053"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw camt.053 content."""
        msg_id = raw_content.get('msgId', '') or raw_content.get('statementId', '')
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
        """Extract all Silver layer fields from camt.053 message."""
        trunc = self.trunc

        # Extract nested objects
        opening_balance = msg_content.get('openingBalance', {})
        closing_balance = msg_content.get('closingBalance', {})

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'camt.053',
            'msg_id': trunc(msg_content.get('msgId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Statement Identification
            'statement_id': trunc(msg_content.get('statementId'), 35),
            'sequence_number': msg_content.get('sequenceNumber'),
            'from_date': msg_content.get('fromDate'),
            'to_date': msg_content.get('toDate'),

            # Account Information
            'account_iban': trunc(msg_content.get('accountIban'), 34),
            'account_number': trunc(msg_content.get('accountNumber'), 34),
            'account_currency': msg_content.get('accountCurrency'),
            'account_owner_name': trunc(msg_content.get('accountOwnerName'), 140),
            'account_servicer_bic': trunc(msg_content.get('accountServicerBic'), 11),

            # Opening Balance
            'opening_balance_amount': opening_balance.get('amount'),
            'opening_balance_currency': opening_balance.get('currency'),
            'opening_balance_credit_debit': opening_balance.get('creditDebitIndicator'),
            'opening_balance_date': opening_balance.get('date'),

            # Closing Balance
            'closing_balance_amount': closing_balance.get('amount'),
            'closing_balance_currency': closing_balance.get('currency'),
            'closing_balance_credit_debit': closing_balance.get('creditDebitIndicator'),
            'closing_balance_date': closing_balance.get('date'),

            # Entry Summary
            'number_of_entries': msg_content.get('numberOfEntries'),
            'sum_of_entries': msg_content.get('sumOfEntries'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'msg_id', 'creation_date_time',
            'statement_id', 'sequence_number', 'from_date', 'to_date',
            'account_iban', 'account_number', 'account_currency',
            'account_owner_name', 'account_servicer_bic',
            'opening_balance_amount', 'opening_balance_currency',
            'opening_balance_credit_debit', 'opening_balance_date',
            'closing_balance_amount', 'closing_balance_currency',
            'closing_balance_credit_debit', 'closing_balance_date',
            'number_of_entries', 'sum_of_entries',
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
        """Extract Gold layer entities from camt.053 Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Account Owner Party - uses Silver column names
        if silver_data.get('account_owner_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('account_owner_name'),
                role="ACCOUNT_OWNER",
                party_type='UNKNOWN',
            ))

        # Statement Account
        if silver_data.get('account_iban') or silver_data.get('account_number'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('account_number'),
                role="STATEMENT_ACCOUNT",
                iban=silver_data.get('account_iban'),
                account_type='CACC',
                currency=silver_data.get('account_currency') or 'XXX',
            ))

        # Account Servicer (Bank)
        if silver_data.get('account_servicer_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="ACCOUNT_SERVICER",
                bic=silver_data.get('account_servicer_bic'),
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('camt.053', Camt053Extractor())
ExtractorRegistry.register('camt_053', Camt053Extractor())
ExtractorRegistry.register('camt053', Camt053Extractor())

"""UK Faster Payments Service (FPS) Extractor - ISO 20022 based."""

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


class FpsExtractor(BaseExtractor):
    """Extractor for UK Faster Payments Service messages."""

    MESSAGE_TYPE = "FPS"
    SILVER_TABLE = "stg_faster_payments"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw FPS content."""
        msg_id = raw_content.get('paymentId', '') or raw_content.get('endToEndId', '')
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
        """Extract all Silver layer fields from FPS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'FPS',
            'payment_id': trunc(msg_content.get('paymentId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'GBP',

            # Payer (Debtor)
            'payer_sort_code': trunc(msg_content.get('payerSortCode'), 6),
            'payer_account': trunc(msg_content.get('payerAccount'), 8),
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_address': msg_content.get('payerAddress'),

            # Payee (Creditor)
            'payee_sort_code': trunc(msg_content.get('payeeSortCode'), 6),
            'payee_account': trunc(msg_content.get('payeeAccount'), 8),
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_address': msg_content.get('payeeAddress'),

            # Payment Details
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'payment_reference': trunc(msg_content.get('paymentReference'), 35),
            'requested_execution_date': msg_content.get('requestedExecutionDate'),
            'settlement_datetime': msg_content.get('settlementDatetime'),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'payment_id', 'creation_date_time',
            'amount', 'currency',
            'payer_sort_code', 'payer_account', 'payer_name', 'payer_address',
            'payee_sort_code', 'payee_account', 'payee_name', 'payee_address',
            'end_to_end_id', 'payment_reference',
            'requested_execution_date', 'settlement_datetime', 'remittance_info',
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
        """Extract Gold layer entities from FPS Silver record.

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
                country='GB',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='GB',
            ))

        # Payer Account
        if silver_data.get('payer_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account'),
                role="DEBTOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Payee Account
        if silver_data.get('payee_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account'),
                role="CREDITOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Payer Bank (by Sort Code)
        if silver_data.get('payer_sort_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('payer_sort_code'),
                clearing_system='GBDSC',
                country='GB',
            ))

        # Payee Bank (by Sort Code)
        if silver_data.get('payee_sort_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('payee_sort_code'),
                clearing_system='GBDSC',
                country='GB',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('FPS', FpsExtractor())
ExtractorRegistry.register('fps', FpsExtractor())
ExtractorRegistry.register('FASTER_PAYMENTS', FpsExtractor())

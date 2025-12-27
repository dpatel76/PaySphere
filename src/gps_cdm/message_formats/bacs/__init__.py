"""BACS (UK Bankers' Automated Clearing Services) Extractor."""

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


class BacsExtractor(BaseExtractor):
    """Extractor for UK BACS payment messages."""

    MESSAGE_TYPE = "BACS"
    SILVER_TABLE = "stg_bacs"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw BACS content."""
        msg_id = raw_content.get('reference', '') or raw_content.get('serviceUserNumber', '')
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
        """Extract all Silver layer fields from BACS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'BACS',

            # Service User
            'service_user_number': trunc(msg_content.get('serviceUserNumber'), 6),
            'service_user_name': trunc(msg_content.get('serviceUserName'), 18),

            # Processing Date
            'processing_date': msg_content.get('processingDate'),
            'transaction_type': trunc(msg_content.get('transactionType'), 2),

            # Originator
            'originating_sort_code': trunc(msg_content.get('originatingSortCode'), 6),
            'originating_account': trunc(msg_content.get('originatingAccount'), 8),

            # Destination
            'destination_sort_code': trunc(msg_content.get('destinationSortCode'), 6),
            'destination_account': trunc(msg_content.get('destinationAccount'), 8),

            # Amount & Reference
            'amount': msg_content.get('amount'),
            'reference': trunc(msg_content.get('reference'), 18),
            'beneficiary_name': trunc(msg_content.get('beneficiaryName'), 18),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type',
            'service_user_number', 'service_user_name',
            'processing_date', 'transaction_type',
            'originating_sort_code', 'originating_account',
            'destination_sort_code', 'destination_account',
            'amount', 'reference', 'beneficiary_name',
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
        """Extract Gold layer entities from BACS message."""
        entities = GoldEntities()

        # Service User Party (Originator/Debtor)
        if msg_content.get('serviceUserName'):
            entities.parties.append(PartyData(
                name=msg_content.get('serviceUserName'),
                role="DEBTOR",
                party_type='ORGANIZATION',
                identification_number=msg_content.get('serviceUserNumber'),
                country='GB',
            ))

        # Beneficiary Party (Creditor)
        if msg_content.get('beneficiaryName'):
            entities.parties.append(PartyData(
                name=msg_content.get('beneficiaryName'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='GB',
            ))

        # Originating Account
        if msg_content.get('originatingAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('originatingAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Destination Account
        if msg_content.get('destinationAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('destinationAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency='GBP',
            ))

        # Originating Bank (by Sort Code)
        if msg_content.get('originatingSortCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('originatingSortCode'),
                clearing_system='GBDSC',
                country='GB',
            ))

        # Destination Bank (by Sort Code)
        if msg_content.get('destinationSortCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('destinationSortCode'),
                clearing_system='GBDSC',
                country='GB',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('BACS', BacsExtractor())
ExtractorRegistry.register('bacs', BacsExtractor())

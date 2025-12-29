"""Saudi Arabia SARIE (Saudi Arabian Riyal Interbank Express) Extractor - JSON based."""

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


class SarieExtractor(BaseExtractor):
    """Extractor for Saudi Arabia SARIE payment messages."""

    MESSAGE_TYPE = "SARIE"
    SILVER_TABLE = "stg_sarie"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw SARIE content."""
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
        """Extract all Silver layer fields from SARIE message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'SARIE',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'SAR',

            # Bank Codes
            'sending_bank_code': trunc(msg_content.get('sendingBankCode'), 11),
            'receiving_bank_code': trunc(msg_content.get('receivingBankCode'), 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

            # Originator (Debtor)
            'originator_name': trunc(msg_content.get('originatorName'), 140),
            'originator_account': trunc(msg_content.get('originatorAccount'), 34),
            'originator_id': trunc(msg_content.get('originatorId'), 20),

            # Beneficiary (Creditor)
            'beneficiary_name': trunc(msg_content.get('beneficiaryName'), 140),
            'beneficiary_account': trunc(msg_content.get('beneficiaryAccount'), 34),
            'beneficiary_id': trunc(msg_content.get('beneficiaryId'), 20),

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
            'originator_name', 'originator_account', 'originator_id',
            'beneficiary_name', 'beneficiary_account', 'beneficiary_id',
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
        """Extract Gold layer entities from SARIE Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Originator Party (Debtor) - uses Silver column names
        if silver_data.get('originator_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('originator_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                identification_number=silver_data.get('originator_id'),
                country='SA',
            ))

        # Beneficiary Party (Creditor)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                identification_number=silver_data.get('beneficiary_id'),
                country='SA',
            ))

        # Originator Account
        if silver_data.get('originator_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SAR',
            ))

        # Beneficiary Account
        if silver_data.get('beneficiary_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SAR',
            ))

        # Sending Bank
        if silver_data.get('sending_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system='SASARIE',  # SARIE
                country='SA',
            ))

        # Receiving Bank
        if silver_data.get('receiving_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system='SASARIE',
                country='SA',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('SARIE', SarieExtractor())
ExtractorRegistry.register('sarie', SarieExtractor())

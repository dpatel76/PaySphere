"""UAE UAEFTS (UAE Funds Transfer System) Extractor - JSON based."""

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


class UaeftsExtractor(BaseExtractor):
    """Extractor for UAE Funds Transfer System payment messages."""

    MESSAGE_TYPE = "UAEFTS"
    SILVER_TABLE = "stg_uaefts"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw UAEFTS content."""
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
        """Extract all Silver layer fields from UAEFTS message.

        Handles both legacy JSON format and ISO 20022 parsed format.
        """
        trunc = self.trunc

        # Handle nested objects for debtor/creditor
        debtor = msg_content.get('debtor') or {}
        creditor = msg_content.get('creditor') or {}
        debtor_acct = msg_content.get('debtorAccount') or {}
        creditor_acct = msg_content.get('creditorAccount') or {}
        debtor_agent = msg_content.get('debtorAgent') or {}
        creditor_agent = msg_content.get('creditorAgent') or {}

        # Extract amount - try multiple paths
        amount = (
            msg_content.get('amount') or
            msg_content.get('interbankSettlementAmount') or
            msg_content.get('instructedAmount')
        )

        # Extract currency - try multiple paths
        currency = (
            msg_content.get('currency') or
            msg_content.get('interbankSettlementCurrency') or
            msg_content.get('instructedCurrency') or
            'AED'
        )

        # Extract originator/debtor info
        originator_name = (
            msg_content.get('originatorName') or
            msg_content.get('debtorName') or
            debtor.get('name')
        )
        originator_account = (
            msg_content.get('originatorAccount') or
            msg_content.get('debtorAccountNumber') or
            debtor_acct.get('accountNumber') or
            debtor_acct.get('iban')
        )

        # Extract beneficiary/creditor info
        beneficiary_name = (
            msg_content.get('beneficiaryName') or
            msg_content.get('creditorName') or
            creditor.get('name')
        )
        beneficiary_account = (
            msg_content.get('beneficiaryAccount') or
            msg_content.get('creditorAccountNumber') or
            creditor_acct.get('accountNumber') or
            creditor_acct.get('iban')
        )

        # Extract bank codes/BICs
        sending_bank_code = (
            msg_content.get('sendingBankCode') or
            debtor_agent.get('bic') or
            debtor_agent.get('memberId')
        )
        receiving_bank_code = (
            msg_content.get('receivingBankCode') or
            creditor_agent.get('bic') or
            creditor_agent.get('memberId')
        )

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'UAEFTS',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),

            # Amount
            'amount': amount,
            'currency': currency,

            # Bank Codes
            'sending_bank_code': trunc(sending_bank_code, 11),
            'receiving_bank_code': trunc(receiving_bank_code, 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference') or msg_content.get('endToEndId'), 35),

            # Originator (Debtor)
            'originator_name': trunc(originator_name, 140),
            'originator_account': trunc(originator_account, 34),
            'originator_address': msg_content.get('originatorAddress'),

            # Beneficiary (Creditor)
            'beneficiary_name': trunc(beneficiary_name, 140),
            'beneficiary_account': trunc(beneficiary_account, 34),
            'beneficiary_address': msg_content.get('beneficiaryAddress'),

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
            'originator_name', 'originator_account', 'originator_address',
            'beneficiary_name', 'beneficiary_account', 'beneficiary_address',
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
        """Extract Gold layer entities from UAEFTS Silver record.

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
                country='AE',
            ))

        # Beneficiary Party (Creditor)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='AE',
            ))

        # Originator Account
        if silver_data.get('originator_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'AED',
            ))

        # Beneficiary Account
        if silver_data.get('beneficiary_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'AED',
            ))

        # Sending Bank (Debtor Agent)
        sending_bank = silver_data.get('sending_bank_code')
        if sending_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=sending_bank if len(sending_bank) in (8, 11) else None,
                clearing_code=sending_bank if len(sending_bank) not in (8, 11) else None,
                clearing_system='AEUAEFTS',
                country='AE',
            ))

        # Receiving Bank (Creditor Agent)
        receiving_bank = silver_data.get('receiving_bank_code')
        if receiving_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=receiving_bank if len(receiving_bank) in (8, 11) else None,
                clearing_code=receiving_bank if len(receiving_bank) not in (8, 11) else None,
                clearing_system='AEUAEFTS',
                country='AE',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('UAEFTS', UaeftsExtractor())
ExtractorRegistry.register('uaefts', UaeftsExtractor())

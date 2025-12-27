"""CHIPS (Clearing House Interbank Payments System) Extractor."""

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


class ChipsExtractor(BaseExtractor):
    """Extractor for CHIPS payment messages."""

    MESSAGE_TYPE = "CHIPS"
    SILVER_TABLE = "stg_chips"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw CHIPS content."""
        msg_id = raw_content.get('sequenceNumber', '') or raw_content.get('senderReference', '')
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
        """Extract all Silver layer fields from CHIPS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'CHIPS',
            'sequence_number': trunc(msg_content.get('sequenceNumber'), 20),
            'message_type_code': trunc(msg_content.get('messageTypeCode'), 4),

            # Participants
            'sending_participant': trunc(msg_content.get('sendingParticipant'), 6),
            'receiving_participant': trunc(msg_content.get('receivingParticipant'), 6),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'USD',
            'value_date': msg_content.get('valueDate'),

            # References
            'sender_reference': trunc(msg_content.get('senderReference'), 16),
            'related_reference': trunc(msg_content.get('relatedReference'), 16),

            # Originator
            'originator_name': trunc(msg_content.get('originatorName'), 140),
            'originator_address': msg_content.get('originatorAddress'),
            'originator_account': trunc(msg_content.get('originatorAccount'), 34),

            # Beneficiary
            'beneficiary_name': trunc(msg_content.get('beneficiaryName'), 140),
            'beneficiary_address': msg_content.get('beneficiaryAddress'),
            'beneficiary_account': trunc(msg_content.get('beneficiaryAccount'), 34),

            # Banks
            'originator_bank': trunc(msg_content.get('originatorBank'), 11),
            'beneficiary_bank': trunc(msg_content.get('beneficiaryBank'), 11),
            'intermediary_bank': trunc(msg_content.get('intermediaryBank'), 11),

            # Additional Info
            'payment_details': msg_content.get('paymentDetails'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'sequence_number', 'message_type_code',
            'sending_participant', 'receiving_participant',
            'amount', 'currency', 'value_date',
            'sender_reference', 'related_reference',
            'originator_name', 'originator_address', 'originator_account',
            'beneficiary_name', 'beneficiary_address', 'beneficiary_account',
            'originator_bank', 'beneficiary_bank', 'intermediary_bank',
            'payment_details',
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
        """Extract Gold layer entities from CHIPS message."""
        entities = GoldEntities()

        # Originator Party (Debtor)
        if msg_content.get('originatorName'):
            entities.parties.append(PartyData(
                name=msg_content.get('originatorName'),
                role="DEBTOR",
                party_type='UNKNOWN',
            ))

        # Beneficiary Party (Creditor)
        if msg_content.get('beneficiaryName'):
            entities.parties.append(PartyData(
                name=msg_content.get('beneficiaryName'),
                role="CREDITOR",
                party_type='UNKNOWN',
            ))

        # Originator Account
        if msg_content.get('originatorAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('originatorAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency='USD',
            ))

        # Beneficiary Account
        if msg_content.get('beneficiaryAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('beneficiaryAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency='USD',
            ))

        # Originator Bank (Debtor Agent)
        if msg_content.get('originatorBank') or msg_content.get('sendingParticipant'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('sendingParticipant'),
                bic=msg_content.get('originatorBank'),
                clearing_system='CHIPS',
                country='US',
            ))

        # Beneficiary Bank (Creditor Agent)
        if msg_content.get('beneficiaryBank') or msg_content.get('receivingParticipant'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('receivingParticipant'),
                bic=msg_content.get('beneficiaryBank'),
                clearing_system='CHIPS',
                country='US',
            ))

        # Intermediary Bank
        if msg_content.get('intermediaryBank'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                bic=msg_content.get('intermediaryBank'),
                clearing_system='CHIPS',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('CHIPS', ChipsExtractor())
ExtractorRegistry.register('chips', ChipsExtractor())

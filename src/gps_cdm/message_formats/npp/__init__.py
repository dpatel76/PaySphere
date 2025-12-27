"""NPP (Australia New Payments Platform) Extractor - ISO 20022 based."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import xml.etree.ElementTree as ET
import re
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


class NppExtractor(BaseExtractor):
    """Extractor for Australia NPP instant payment messages."""

    MESSAGE_TYPE = "NPP"
    SILVER_TABLE = "stg_npp"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw NPP content."""
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
        """Extract all Silver layer fields from NPP message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'NPP',
            'payment_id': trunc(msg_content.get('paymentId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'AUD',

            # Payer (Debtor)
            'payer_bsb': trunc(msg_content.get('payerBsb'), 6),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_payid': trunc(msg_content.get('payerPayid'), 256),
            'payer_payid_type': trunc(msg_content.get('payerPayidType'), 10),

            # Payee (Creditor)
            'payee_bsb': trunc(msg_content.get('payeeBsb'), 6),
            'payee_account': trunc(msg_content.get('payeeAccount'), 34),
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_payid': trunc(msg_content.get('payeePayid'), 256),
            'payee_payid_type': trunc(msg_content.get('payeePayidType'), 10),

            # Payment Details
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'payment_reference': trunc(msg_content.get('paymentReference'), 35),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'payment_id', 'creation_date_time',
            'amount', 'currency',
            'payer_bsb', 'payer_account', 'payer_name',
            'payer_payid', 'payer_payid_type',
            'payee_bsb', 'payee_account', 'payee_name',
            'payee_payid', 'payee_payid_type',
            'end_to_end_id', 'payment_reference', 'remittance_info',
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
        """Extract Gold layer entities from NPP message."""
        entities = GoldEntities()

        # Payer Party (Debtor)
        if msg_content.get('payerName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payerName'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='AU',
            ))

        # Payee Party (Creditor)
        if msg_content.get('payeeName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payeeName'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='AU',
            ))

        # Payer Account
        if msg_content.get('payerAccount') or msg_content.get('payerPayid'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payerAccount') or msg_content.get('payerPayid'),
                role="DEBTOR",
                account_type='CACC',
                currency='AUD',
            ))

        # Payee Account
        if msg_content.get('payeeAccount') or msg_content.get('payeePayid'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payeeAccount') or msg_content.get('payeePayid'),
                role="CREDITOR",
                account_type='CACC',
                currency='AUD',
            ))

        # Payer Bank (by BSB)
        if msg_content.get('payerBsb'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('payerBsb'),
                clearing_system='AUBSB',  # Australian BSB
                country='AU',
            ))

        # Payee Bank (by BSB)
        if msg_content.get('payeeBsb'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('payeeBsb'),
                clearing_system='AUBSB',
                country='AU',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('NPP', NppExtractor())
ExtractorRegistry.register('npp', NppExtractor())

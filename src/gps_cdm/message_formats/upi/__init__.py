"""UPI (India Unified Payments Interface) Extractor - JSON based."""

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


class UpiExtractor(BaseExtractor):
    """Extractor for India UPI instant payment messages."""

    MESSAGE_TYPE = "UPI"
    SILVER_TABLE = "stg_upi"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw UPI content."""
        msg_id = raw_content.get('transactionId', '') or raw_content.get('transactionRefId', '')
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
        """Extract all Silver layer fields from UPI message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'UPI',
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'transaction_ref_id': trunc(msg_content.get('transactionRefId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'INR',

            # Payer (Debtor)
            'payer_vpa': trunc(msg_content.get('payerVpa'), 256),
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),
            'payer_ifsc': trunc(msg_content.get('payerIfsc'), 11),
            'payer_mobile': trunc(msg_content.get('payerMobile'), 15),

            # Payee (Creditor)
            'payee_vpa': trunc(msg_content.get('payeeVpa'), 256),
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_account': trunc(msg_content.get('payeeAccount'), 34),
            'payee_ifsc': trunc(msg_content.get('payeeIfsc'), 11),
            'payee_mobile': trunc(msg_content.get('payeeMobile'), 15),

            # Transaction Details
            'transaction_type': trunc(msg_content.get('transactionType'), 10),
            'sub_type': trunc(msg_content.get('subType'), 10),
            'remittance_info': msg_content.get('remittanceInfo'),
            'transaction_status': trunc(msg_content.get('transactionStatus'), 20),
            'response_code': trunc(msg_content.get('responseCode'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'transaction_id', 'transaction_ref_id',
            'creation_date_time', 'amount', 'currency',
            'payer_vpa', 'payer_name', 'payer_account',
            'payer_ifsc', 'payer_mobile',
            'payee_vpa', 'payee_name', 'payee_account',
            'payee_ifsc', 'payee_mobile',
            'transaction_type', 'sub_type', 'remittance_info',
            'transaction_status', 'response_code',
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
        """Extract Gold layer entities from UPI message."""
        entities = GoldEntities()

        # Payer Party (Debtor)
        if msg_content.get('payerName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payerName'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='IN',
            ))

        # Payee Party (Creditor)
        if msg_content.get('payeeName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payeeName'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='IN',
            ))

        # Payer Account (VPA or Account)
        if msg_content.get('payerVpa') or msg_content.get('payerAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payerVpa') or msg_content.get('payerAccount'),
                role="DEBTOR",
                account_type='CACC',
                currency='INR',
            ))

        # Payee Account (VPA or Account)
        if msg_content.get('payeeVpa') or msg_content.get('payeeAccount'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payeeVpa') or msg_content.get('payeeAccount'),
                role="CREDITOR",
                account_type='CACC',
                currency='INR',
            ))

        # Payer Bank (by IFSC)
        if msg_content.get('payerIfsc'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('payerIfsc'),
                clearing_system='INIFSC',  # India IFSC
                country='IN',
            ))

        # Payee Bank (by IFSC)
        if msg_content.get('payeeIfsc'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('payeeIfsc'),
                clearing_system='INIFSC',
                country='IN',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('UPI', UpiExtractor())
ExtractorRegistry.register('upi', UpiExtractor())

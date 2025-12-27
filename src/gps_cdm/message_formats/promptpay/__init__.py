"""Thailand PromptPay Extractor - JSON based."""

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


class PromptPayExtractor(BaseExtractor):
    """Extractor for Thailand PromptPay instant payment messages."""

    MESSAGE_TYPE = "PROMPTPAY"
    SILVER_TABLE = "stg_promptpay"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw PromptPay content."""
        msg_id = raw_content.get('transactionId', '') or raw_content.get('endToEndId', '')
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
        """Extract all Silver layer fields from PromptPay message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'PROMPTPAY',
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'THB',

            # Payer (Debtor)
            'payer_proxy_type': trunc(msg_content.get('payerProxyType'), 10),
            'payer_proxy_value': trunc(msg_content.get('payerProxyValue'), 50),
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_bank_code': trunc(msg_content.get('payerBankCode'), 11),
            'payer_account': trunc(msg_content.get('payerAccount'), 34),

            # Payee (Creditor)
            'payee_proxy_type': trunc(msg_content.get('payeeProxyType'), 10),
            'payee_proxy_value': trunc(msg_content.get('payeeProxyValue'), 50),
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_bank_code': trunc(msg_content.get('payeeBankCode'), 11),
            'payee_account': trunc(msg_content.get('payeeAccount'), 34),

            # Payment Details
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'qr_code_data': msg_content.get('qrCodeData'),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'transaction_id', 'creation_date_time',
            'amount', 'currency',
            'payer_proxy_type', 'payer_proxy_value', 'payer_name',
            'payer_bank_code', 'payer_account',
            'payee_proxy_type', 'payee_proxy_value', 'payee_name',
            'payee_bank_code', 'payee_account',
            'end_to_end_id', 'qr_code_data', 'remittance_info',
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
        """Extract Gold layer entities from PromptPay message."""
        entities = GoldEntities()

        # Payer Party (Debtor)
        if msg_content.get('payerName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payerName'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='TH',
            ))

        # Payee Party (Creditor)
        if msg_content.get('payeeName'):
            entities.parties.append(PartyData(
                name=msg_content.get('payeeName'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='TH',
            ))

        # Payer Account (or Proxy)
        if msg_content.get('payerAccount') or msg_content.get('payerProxyValue'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payerAccount') or msg_content.get('payerProxyValue'),
                role="DEBTOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'THB',
            ))

        # Payee Account (or Proxy)
        if msg_content.get('payeeAccount') or msg_content.get('payeeProxyValue'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('payeeAccount') or msg_content.get('payeeProxyValue'),
                role="CREDITOR",
                account_type='CACC',
                currency=msg_content.get('currency') or 'THB',
            ))

        # Payer Bank
        if msg_content.get('payerBankCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=msg_content.get('payerBankCode'),
                clearing_system='THPROMPTPAY',
                country='TH',
            ))

        # Payee Bank
        if msg_content.get('payeeBankCode'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=msg_content.get('payeeBankCode'),
                clearing_system='THPROMPTPAY',
                country='TH',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('PROMPTPAY', PromptPayExtractor())
ExtractorRegistry.register('promptpay', PromptPayExtractor())
ExtractorRegistry.register('PromptPay', PromptPayExtractor())

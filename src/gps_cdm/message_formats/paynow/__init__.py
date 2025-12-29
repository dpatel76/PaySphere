"""Singapore PayNow Extractor - JSON based."""

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


class PayNowExtractor(BaseExtractor):
    """Extractor for Singapore PayNow instant payment messages."""

    MESSAGE_TYPE = "PAYNOW"
    SILVER_TABLE = "stg_paynow"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw PayNow content."""
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
        """Extract all Silver layer fields from PayNow message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'PAYNOW',
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'SGD',

            # Payer (Debtor)
            'payer_proxy_type': trunc(msg_content.get('payerProxyType'), 10),  # NRIC, UEN, MOBILE, VPA
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
            'end_to_end_id', 'remittance_info',
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
        """Extract Gold layer entities from PayNow Silver record.

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
                country='SG',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='SG',
            ))

        # Payer Account (or Proxy)
        if silver_data.get('payer_account') or silver_data.get('payer_proxy_value'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account') or silver_data.get('payer_proxy_value'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SGD',
            ))

        # Payee Account (or Proxy)
        if silver_data.get('payee_account') or silver_data.get('payee_proxy_value'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account') or silver_data.get('payee_proxy_value'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SGD',
            ))

        # Payer Bank
        if silver_data.get('payer_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('payer_bank_code'),
                clearing_system='SGPAYNOW',
                country='SG',
            ))

        # Payee Bank
        if silver_data.get('payee_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('payee_bank_code'),
                clearing_system='SGPAYNOW',
                country='SG',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('PAYNOW', PayNowExtractor())
ExtractorRegistry.register('paynow', PayNowExtractor())
ExtractorRegistry.register('PayNow', PayNowExtractor())

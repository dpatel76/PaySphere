"""PIX (Brazil Instant Payments) Extractor - JSON based."""

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


class PixExtractor(BaseExtractor):
    """Extractor for Brazil PIX instant payment messages."""

    MESSAGE_TYPE = "PIX"
    SILVER_TABLE = "stg_pix"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw PIX content."""
        msg_id = raw_content.get('endToEndId', '')
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
        """Extract all Silver layer fields from PIX message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'PIX',
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 32),
            'creation_date_time': msg_content.get('creationDateTime'),
            'local_instrument': trunc(msg_content.get('localInstrument'), 10),

            # Payer (Debtor)
            'payer_ispb': trunc(msg_content.get('payerIspb'), 8),
            'payer_branch': trunc(msg_content.get('payerBranch'), 4),
            'payer_account': trunc(msg_content.get('payerAccount'), 20),
            'payer_account_type': trunc(msg_content.get('payerAccountType'), 10),
            'payer_name': trunc(msg_content.get('payerName'), 140),
            'payer_cpf_cnpj': trunc(msg_content.get('payerCpfCnpj'), 14),
            'payer_pix_key': trunc(msg_content.get('payerPixKey'), 77),
            'payer_pix_key_type': trunc(msg_content.get('payerPixKeyType'), 10),

            # Payee (Creditor)
            'payee_ispb': trunc(msg_content.get('payeeIspb'), 8),
            'payee_branch': trunc(msg_content.get('payeeBranch'), 4),
            'payee_account': trunc(msg_content.get('payeeAccount'), 20),
            'payee_account_type': trunc(msg_content.get('payeeAccountType'), 10),
            'payee_name': trunc(msg_content.get('payeeName'), 140),
            'payee_cpf_cnpj': trunc(msg_content.get('payeeCpfCnpj'), 14),
            'payee_pix_key': trunc(msg_content.get('payeePixKey'), 77),
            'payee_pix_key_type': trunc(msg_content.get('payeePixKeyType'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'BRL',

            # PIX specific
            'qr_code_type': trunc(msg_content.get('qrCodeType'), 10),
            'initiation_type': trunc(msg_content.get('initiationType'), 10),
            'payment_type': trunc(msg_content.get('paymentType'), 10),
            'remittance_info': msg_content.get('remittanceInfo'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'end_to_end_id', 'creation_date_time',
            'local_instrument',
            'payer_ispb', 'payer_branch', 'payer_account',
            'payer_account_type', 'payer_name', 'payer_cpf_cnpj',
            'payer_pix_key', 'payer_pix_key_type',
            'payee_ispb', 'payee_branch', 'payee_account',
            'payee_account_type', 'payee_name', 'payee_cpf_cnpj',
            'payee_pix_key', 'payee_pix_key_type',
            'amount', 'currency',
            'qr_code_type', 'initiation_type', 'payment_type',
            'remittance_info',
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
        """Extract Gold layer entities from PIX Silver record.

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
                party_type='INDIVIDUAL' if len(silver_data.get('payer_cpf_cnpj') or '') == 11 else 'ORGANIZATION',
                identification_type='CPF' if len(silver_data.get('payer_cpf_cnpj') or '') == 11 else 'CNPJ',
                identification_number=silver_data.get('payer_cpf_cnpj'),
                country='BR',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='INDIVIDUAL' if len(silver_data.get('payee_cpf_cnpj') or '') == 11 else 'ORGANIZATION',
                identification_type='CPF' if len(silver_data.get('payee_cpf_cnpj') or '') == 11 else 'CNPJ',
                identification_number=silver_data.get('payee_cpf_cnpj'),
                country='BR',
            ))

        # Payer Account
        if silver_data.get('payer_account') or silver_data.get('payer_pix_key'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account') or silver_data.get('payer_pix_key'),
                role="DEBTOR",
                account_type=silver_data.get('payer_account_type') or 'CACC',
                currency='BRL',
            ))

        # Payee Account
        if silver_data.get('payee_account') or silver_data.get('payee_pix_key'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account') or silver_data.get('payee_pix_key'),
                role="CREDITOR",
                account_type=silver_data.get('payee_account_type') or 'CACC',
                currency='BRL',
            ))

        # Payer Bank (by ISPB)
        if silver_data.get('payer_ispb'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('payer_ispb'),
                clearing_system='BRISPB',  # Brazil ISPB
                country='BR',
            ))

        # Payee Bank (by ISPB)
        if silver_data.get('payee_ispb'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('payee_ispb'),
                clearing_system='BRISPB',
                country='BR',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('PIX', PixExtractor())
ExtractorRegistry.register('pix', PixExtractor())

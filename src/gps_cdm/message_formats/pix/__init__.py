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


class PixParser:
    """Parser for PIX JSON format messages.

    Handles the flat JSON structure:
    {
        "endToEndId": "E2E-PIX-20260106-001",
        "transactionId": "TXN-PIX-20260106-001",
        "creationDateTime": "2026-01-06T10:30:00-03:00",
        "amount": 47500.00,
        "currency": "BRL",
        "payerIspb": "00000000",
        "payerBankCode": "001",
        "payerBankName": "Banco do Brasil S.A.",
        "payerName": "Sao Paulo Tech Ventures Ltda",
        "payerCpfCnpj": "12345678000195",
        "payerPixKey": "contato@sptechventures.com.br",
        "payerAddress": { ... },
        "payeeIspb": "60701190",
        "payeeName": "Rio de Janeiro Import Export SA",
        ...
        "remittanceInfo": { "structured": {...}, "unstructured": "..." }
    }
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse PIX JSON message into structured dict."""
        result = {
            'messageType': 'PIX',
        }

        # Handle dict input (pre-parsed)
        if isinstance(raw_content, dict):
            data = raw_content
        else:
            # Parse JSON string
            if raw_content.strip().startswith('{'):
                try:
                    data = json.loads(raw_content)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse PIX JSON: {e}")
                    return result
            else:
                logger.warning("PIX content is not JSON")
                return result

        # Core fields
        result['endToEndId'] = data.get('endToEndId')
        result['transactionId'] = data.get('transactionId')
        result['creationDateTime'] = data.get('creationDateTime')
        result['localInstrument'] = data.get('localInstrument')
        result['paymentType'] = data.get('paymentType')
        result['initiationType'] = data.get('initiationType')
        result['qrCodeType'] = data.get('qrCodeType')
        result['settlementDate'] = data.get('settlementDate')
        result['acceptanceDateTime'] = data.get('acceptanceDateTime')

        # Amount
        result['amount'] = data.get('amount')
        result['currency'] = data.get('currency') or 'BRL'
        result['chargeBearer'] = data.get('chargeBearer')

        # Payer information
        result['payerIspb'] = data.get('payerIspb')
        result['payerBankCode'] = data.get('payerBankCode')
        result['payerBankName'] = data.get('payerBankName')
        result['payerBranch'] = data.get('payerBranch')
        result['payerAccount'] = data.get('payerAccount')
        result['payerAccountType'] = data.get('payerAccountType')
        result['payerName'] = data.get('payerName')
        result['payerCpfCnpj'] = data.get('payerCpfCnpj')
        result['payerTaxIdType'] = data.get('payerTaxIdType')
        result['payerPixKey'] = data.get('payerPixKey')
        result['payerPixKeyType'] = data.get('payerPixKeyType')

        payer_addr = data.get('payerAddress', {})
        result['payerStreetName'] = payer_addr.get('streetName')
        result['payerBuildingNumber'] = payer_addr.get('buildingNumber')
        result['payerFloor'] = payer_addr.get('floor')
        result['payerPostalCode'] = payer_addr.get('postalCode')
        result['payerCity'] = payer_addr.get('city')
        result['payerState'] = payer_addr.get('state')
        result['payerCountry'] = payer_addr.get('country') or 'BR'

        payer_contact = data.get('payerContact', {})
        result['payerContactName'] = payer_contact.get('name')
        result['payerContactPhone'] = payer_contact.get('phone')
        result['payerContactEmail'] = payer_contact.get('email')

        # Payee information
        result['payeeIspb'] = data.get('payeeIspb')
        result['payeeBankCode'] = data.get('payeeBankCode')
        result['payeeBankName'] = data.get('payeeBankName')
        result['payeeBranch'] = data.get('payeeBranch')
        result['payeeAccount'] = data.get('payeeAccount')
        result['payeeAccountType'] = data.get('payeeAccountType')
        result['payeeName'] = data.get('payeeName')
        result['payeeCpfCnpj'] = data.get('payeeCpfCnpj')
        result['payeeTaxIdType'] = data.get('payeeTaxIdType')
        result['payeePixKey'] = data.get('payeePixKey')
        result['payeePixKeyType'] = data.get('payeePixKeyType')

        payee_addr = data.get('payeeAddress', {})
        result['payeeStreetName'] = payee_addr.get('streetName')
        result['payeeBuildingNumber'] = payee_addr.get('buildingNumber')
        result['payeeFloor'] = payee_addr.get('floor')
        result['payeePostalCode'] = payee_addr.get('postalCode')
        result['payeeCity'] = payee_addr.get('city')
        result['payeeState'] = payee_addr.get('state')
        result['payeeCountry'] = payee_addr.get('country') or 'BR'

        payee_contact = data.get('payeeContact', {})
        result['payeeContactName'] = payee_contact.get('name')
        result['payeeContactPhone'] = payee_contact.get('phone')
        result['payeeContactEmail'] = payee_contact.get('email')

        # Remittance information
        remit = data.get('remittanceInfo', {})
        if isinstance(remit, dict):
            structured = remit.get('structured', {})
            result['invoiceNumber'] = structured.get('invoiceNumber')
            result['invoiceDate'] = structured.get('invoiceDate')
            result['purchaseOrderNumber'] = structured.get('purchaseOrderNumber')
            result['dueAmount'] = structured.get('dueAmount')
            result['remittanceUnstructured'] = remit.get('unstructured')
        else:
            result['remittanceUnstructured'] = str(remit) if remit else None

        # Transaction purpose and regulatory
        result['transactionPurpose'] = data.get('transactionPurpose')
        reg = data.get('regulatoryReporting', {})
        result['regulatoryCode'] = reg.get('code')
        result['regulatoryDescription'] = reg.get('description')

        return result


class PixExtractor(BaseExtractor):
    """Extractor for Brazil PIX instant payment messages."""

    MESSAGE_TYPE = "PIX"
    SILVER_TABLE = "stg_pix"

    def __init__(self):
        """Initialize extractor with parser."""
        super().__init__()
        self.parser = PixParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw PIX content."""
        # Parse if string
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        msg_id = parsed.get('endToEndId', '') or parsed.get('transactionId', '')
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

        # Parse if needed
        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = self.parser.parse(msg_content)

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'PIX',
            'end_to_end_id': trunc(parsed.get('endToEndId'), 32),
            'creation_date_time': parsed.get('creationDateTime'),
            'local_instrument': trunc(parsed.get('localInstrument'), 10),

            # Payer (Debtor)
            'payer_ispb': trunc(parsed.get('payerIspb'), 8),
            'payer_branch': trunc(parsed.get('payerBranch'), 4),
            'payer_account': trunc(parsed.get('payerAccount'), 20),
            'payer_account_type': trunc(parsed.get('payerAccountType'), 10),
            'payer_name': trunc(parsed.get('payerName'), 140),
            'payer_cpf_cnpj': trunc(parsed.get('payerCpfCnpj'), 14),
            'payer_pix_key': trunc(parsed.get('payerPixKey'), 77),
            'payer_pix_key_type': trunc(parsed.get('payerPixKeyType'), 10),

            # Payee (Creditor)
            'payee_ispb': trunc(parsed.get('payeeIspb'), 8),
            'payee_branch': trunc(parsed.get('payeeBranch'), 4),
            'payee_account': trunc(parsed.get('payeeAccount'), 20),
            'payee_account_type': trunc(parsed.get('payeeAccountType'), 10),
            'payee_name': trunc(parsed.get('payeeName'), 140),
            'payee_cpf_cnpj': trunc(parsed.get('payeeCpfCnpj'), 14),
            'payee_pix_key': trunc(parsed.get('payeePixKey'), 77),
            'payee_pix_key_type': trunc(parsed.get('payeePixKeyType'), 10),

            # Amount
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or 'BRL',

            # PIX specific
            'qr_code_type': trunc(parsed.get('qrCodeType'), 10),
            'initiation_type': trunc(parsed.get('initiationType'), 10),
            'payment_type': trunc(parsed.get('paymentType'), 10),
            'remittance_info': parsed.get('remittanceUnstructured'),

            # Additional parsed fields
            'transaction_id': trunc(parsed.get('transactionId'), 35),
            'settlement_date': parsed.get('settlementDate'),
            'acceptance_date_time': parsed.get('acceptanceDateTime'),
            'charge_bearer': trunc(parsed.get('chargeBearer'), 10),
            'payer_bank_code': trunc(parsed.get('payerBankCode'), 10),
            'payer_bank_name': trunc(parsed.get('payerBankName'), 140),
            'payee_bank_code': trunc(parsed.get('payeeBankCode'), 10),
            'payee_bank_name': trunc(parsed.get('payeeBankName'), 140),
            'transaction_purpose': trunc(parsed.get('transactionPurpose'), 10),
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
            'transaction_id', 'settlement_date', 'acceptance_date_time',
            'charge_bearer',
            'payer_bank_code', 'payer_bank_name',
            'payee_bank_code', 'payee_bank_name',
            'transaction_purpose',
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

        # Determine party type based on CPF/CNPJ length
        payer_cpf_cnpj = silver_data.get('payer_cpf_cnpj') or ''
        payee_cpf_cnpj = silver_data.get('payee_cpf_cnpj') or ''

        # Payer Party (Debtor) - uses Silver column names
        if silver_data.get('payer_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type='INDIVIDUAL' if len(payer_cpf_cnpj) == 11 else 'ORGANIZATION',
                identification_type='CPF' if len(payer_cpf_cnpj) == 11 else 'CNPJ',
                identification_number=payer_cpf_cnpj or None,
                country='BR',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='INDIVIDUAL' if len(payee_cpf_cnpj) == 11 else 'ORGANIZATION',
                identification_type='CPF' if len(payee_cpf_cnpj) == 11 else 'CNPJ',
                identification_number=payee_cpf_cnpj or None,
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
        if silver_data.get('payer_ispb') or silver_data.get('payer_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('payer_bank_name'),
                clearing_code=silver_data.get('payer_ispb') or silver_data.get('payer_bank_code'),
                clearing_system='BRISPB',  # Brazil ISPB
                country='BR',
            ))

        # Payee Bank (by ISPB)
        if silver_data.get('payee_ispb') or silver_data.get('payee_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('payee_bank_name'),
                clearing_code=silver_data.get('payee_ispb') or silver_data.get('payee_bank_code'),
                clearing_system='BRISPB',
                country='BR',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('PIX', PixExtractor())
ExtractorRegistry.register('pix', PixExtractor())

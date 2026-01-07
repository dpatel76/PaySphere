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


class PayNowParser:
    """Parser for PayNow JSON format messages.

    Handles the flat JSON structure:
    {
        "transactionId": "PAYNOW-E2E-20260106-001",
        "endToEndId": "E2E-PN-20260106-001",
        "creationDateTime": "2026-01-06T10:45:00+08:00",
        "amount": 85000.00,
        "currency": "SGD",
        "payerProxyType": "UEN",
        "payerProxyValue": "202012345G",
        "payerName": "Singapore Tech Holdings Pte Ltd",
        "payerBankCode": "DBSSSGSG",
        "payerBankBic": "DBSSSGSGXXX",
        "payerAccount": "1234567890",
        "payerAddress": { "streetName": "...", "city": "Singapore", ... },
        "payeeName": "Tan Ah Kow",
        "payeeAccount": "9876543210",
        "payeeAddress": { ... },
        "remittanceInfo": { "structured": {...}, "unstructured": "..." }
    }
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse PayNow JSON message into structured dict."""
        result = {
            'messageType': 'PAYNOW',
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
                    logger.warning(f"Failed to parse PayNow JSON: {e}")
                    return result
            else:
                logger.warning("PayNow content is not JSON")
                return result

        # Core fields
        result['transactionId'] = data.get('transactionId')
        result['endToEndId'] = data.get('endToEndId')
        result['creationDateTime'] = data.get('creationDateTime')
        result['settlementDate'] = data.get('settlementDate')
        result['acceptanceDateTime'] = data.get('acceptanceDateTime')

        # Amount
        result['amount'] = data.get('amount')
        result['currency'] = data.get('currency') or 'SGD'
        result['chargeBearer'] = data.get('chargeBearer')

        # Payment type
        result['paymentType'] = data.get('paymentType')
        result['localInstrument'] = data.get('localInstrument')

        # Payer information
        result['payerProxyType'] = data.get('payerProxyType')
        result['payerProxyValue'] = data.get('payerProxyValue')
        result['payerName'] = data.get('payerName')
        result['payerUen'] = data.get('payerUen')
        result['payerBankCode'] = data.get('payerBankCode')
        result['payerBankName'] = data.get('payerBankName')
        result['payerBankBic'] = data.get('payerBankBic')
        result['payerAccount'] = data.get('payerAccount')
        result['payerAccountType'] = data.get('payerAccountType')

        payer_addr = data.get('payerAddress', {})
        result['payerStreetName'] = payer_addr.get('streetName')
        result['payerBuildingNumber'] = payer_addr.get('buildingNumber')
        result['payerBuildingName'] = payer_addr.get('buildingName')
        result['payerFloor'] = payer_addr.get('floor')
        result['payerPostalCode'] = payer_addr.get('postalCode')
        result['payerCity'] = payer_addr.get('city')
        result['payerCountry'] = payer_addr.get('country') or 'SG'

        payer_contact = data.get('payerContact', {})
        result['payerContactName'] = payer_contact.get('name')
        result['payerContactPhone'] = payer_contact.get('phone')
        result['payerContactEmail'] = payer_contact.get('email')

        # Payee information
        result['payeeProxyType'] = data.get('payeeProxyType')
        result['payeeProxyValue'] = data.get('payeeProxyValue')
        result['payeeName'] = data.get('payeeName')
        result['payeeBankCode'] = data.get('payeeBankCode')
        result['payeeBankName'] = data.get('payeeBankName')
        result['payeeBankBic'] = data.get('payeeBankBic')
        result['payeeAccount'] = data.get('payeeAccount')
        result['payeeAccountType'] = data.get('payeeAccountType')

        payee_addr = data.get('payeeAddress', {})
        result['payeeStreetName'] = payee_addr.get('streetName')
        result['payeeBuildingNumber'] = payee_addr.get('buildingNumber')
        result['payeeBuildingName'] = payee_addr.get('buildingName')
        result['payeeFloor'] = payee_addr.get('floor')
        result['payeePostalCode'] = payee_addr.get('postalCode')
        result['payeeCity'] = payee_addr.get('city')
        result['payeeCountry'] = payee_addr.get('country') or 'SG'

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
            result['dueAmount'] = structured.get('dueAmount')
            result['remittanceUnstructured'] = remit.get('unstructured')
        else:
            result['remittanceUnstructured'] = str(remit) if remit else None

        # Purpose
        result['purposeCode'] = data.get('purposeCode')
        result['categoryPurpose'] = data.get('categoryPurpose')

        return result


class PayNowExtractor(BaseExtractor):
    """Extractor for Singapore PayNow instant payment messages."""

    MESSAGE_TYPE = "PAYNOW"
    SILVER_TABLE = "stg_paynow"

    def __init__(self):
        """Initialize extractor with parser."""
        super().__init__()
        self.parser = PayNowParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw PayNow content."""
        # Parse if string
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        msg_id = parsed.get('transactionId', '') or parsed.get('endToEndId', '')
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
            'message_type': 'PAYNOW',
            'transaction_id': trunc(parsed.get('transactionId'), 35),
            'creation_date_time': parsed.get('creationDateTime'),

            # Amount
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or 'SGD',

            # Payer (Debtor)
            'payer_proxy_type': trunc(parsed.get('payerProxyType'), 10),  # NRIC, UEN, MOBILE, VPA
            'payer_proxy_value': trunc(parsed.get('payerProxyValue'), 50),
            'payer_name': trunc(parsed.get('payerName'), 140),
            'payer_bank_code': trunc(parsed.get('payerBankCode'), 11),
            'payer_account': trunc(parsed.get('payerAccount'), 34),

            # Payee (Creditor)
            'payee_proxy_type': trunc(parsed.get('payeeProxyType'), 10),
            'payee_proxy_value': trunc(parsed.get('payeeProxyValue'), 50),
            'payee_name': trunc(parsed.get('payeeName'), 140),
            'payee_bank_code': trunc(parsed.get('payeeBankCode'), 11),
            'payee_account': trunc(parsed.get('payeeAccount'), 34),

            # Payment Details
            'end_to_end_id': trunc(parsed.get('endToEndId'), 35),
            'remittance_info': parsed.get('remittanceUnstructured'),

            # Additional parsed fields
            'settlement_date': parsed.get('settlementDate'),
            'acceptance_date_time': parsed.get('acceptanceDateTime'),
            'charge_bearer': trunc(parsed.get('chargeBearer'), 10),
            'payment_type': trunc(parsed.get('paymentType'), 10),
            'local_instrument': trunc(parsed.get('localInstrument'), 10),
            'payer_uen': trunc(parsed.get('payerUen'), 20),
            'payer_bank_name': trunc(parsed.get('payerBankName'), 140),
            'payer_bank_bic': trunc(parsed.get('payerBankBic'), 11),
            'payer_account_type': trunc(parsed.get('payerAccountType'), 10),
            'payee_bank_name': trunc(parsed.get('payeeBankName'), 140),
            'payee_bank_bic': trunc(parsed.get('payeeBankBic'), 11),
            'payee_account_type': trunc(parsed.get('payeeAccountType'), 10),
            'purpose_code': trunc(parsed.get('purposeCode'), 10),
            'category_purpose': trunc(parsed.get('categoryPurpose'), 10),
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
            'settlement_date', 'acceptance_date_time', 'charge_bearer',
            'payment_type', 'local_instrument',
            'payer_uen', 'payer_bank_name', 'payer_bank_bic', 'payer_account_type',
            'payee_bank_name', 'payee_bank_bic', 'payee_account_type',
            'purpose_code', 'category_purpose',
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

        # Determine party type based on proxy type
        payer_proxy_type = silver_data.get('payer_proxy_type') or ''
        payee_proxy_type = silver_data.get('payee_proxy_type') or ''

        # Payer Party (Debtor) - uses Silver column names
        if silver_data.get('payer_name'):
            party_type = 'ORGANIZATION' if payer_proxy_type == 'UEN' else 'INDIVIDUAL'
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type=party_type,
                identification_type=payer_proxy_type if payer_proxy_type else None,
                identification_number=silver_data.get('payer_proxy_value') or silver_data.get('payer_uen'),
                country='SG',
            ))

        # Payee Party (Creditor)
        if silver_data.get('payee_name'):
            party_type = 'ORGANIZATION' if payee_proxy_type == 'UEN' else 'INDIVIDUAL'
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type=party_type,
                identification_type=payee_proxy_type if payee_proxy_type else None,
                identification_number=silver_data.get('payee_proxy_value'),
                country='SG',
            ))

        # Payer Account (or Proxy)
        if silver_data.get('payer_account') or silver_data.get('payer_proxy_value'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account') or silver_data.get('payer_proxy_value'),
                role="DEBTOR",
                account_type=silver_data.get('payer_account_type') or 'CACC',
                currency=silver_data.get('currency') or 'SGD',
            ))

        # Payee Account (or Proxy)
        if silver_data.get('payee_account') or silver_data.get('payee_proxy_value'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account') or silver_data.get('payee_proxy_value'),
                role="CREDITOR",
                account_type=silver_data.get('payee_account_type') or 'CACC',
                currency=silver_data.get('currency') or 'SGD',
            ))

        # Payer Bank
        if silver_data.get('payer_bank_code') or silver_data.get('payer_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('payer_bank_name'),
                bic=silver_data.get('payer_bank_bic'),
                clearing_code=silver_data.get('payer_bank_code'),
                clearing_system='SGPAYNOW',
                country='SG',
            ))

        # Payee Bank
        if silver_data.get('payee_bank_code') or silver_data.get('payee_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('payee_bank_name'),
                bic=silver_data.get('payee_bank_bic'),
                clearing_code=silver_data.get('payee_bank_code'),
                clearing_system='SGPAYNOW',
                country='SG',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('PAYNOW', PayNowExtractor())
ExtractorRegistry.register('paynow', PayNowExtractor())
ExtractorRegistry.register('PayNow', PayNowExtractor())

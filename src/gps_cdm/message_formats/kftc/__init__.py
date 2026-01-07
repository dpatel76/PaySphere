"""Korea KFTC (Korea Financial Telecommunications & Clearings Institute) Extractor - JSON based."""

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


class KftcParser:
    """Parser for KFTC JSON format messages.

    Handles the flat JSON structure:
    {
        "messageId": "KFTC-E2E-20260106-001",
        "messageType": "KFTC",
        "transactionId": "TXN-KR-20260106-001",
        "amount": 75000000.00,
        "currency": "KRW",
        "payerName": "Seoul Electronics Corporation",
        "payerAccount": "110-123-456789",
        "payerAddress": { "streetName": "...", "city": "Seoul", ... },
        "payeeName": "Busan Semiconductor Manufacturing Ltd",
        "payeeAccount": "333-654-321098",
        "payeeAddress": { ... },
        "remittanceInfo": { "invoiceNumber": "...", ... }
    }
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse KFTC JSON message into structured dict."""
        result = {
            'messageType': 'KFTC',
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
                    logger.warning(f"Failed to parse KFTC JSON: {e}")
                    return result
            else:
                logger.warning("KFTC content is not JSON")
                return result

        # Core fields
        result['messageId'] = data.get('messageId')
        result['messageType'] = data.get('messageType') or 'KFTC'
        result['transactionId'] = data.get('transactionId')
        result['transactionReference'] = data.get('transactionReference')
        result['creationDateTime'] = data.get('creationDateTime')
        result['settlementDate'] = data.get('settlementDate')
        result['valueDate'] = data.get('valueDate')
        result['paymentType'] = data.get('paymentType')
        result['priority'] = data.get('priority')

        # Amount
        result['amount'] = data.get('amount')
        result['currency'] = data.get('currency') or 'KRW'
        result['chargeBearer'] = data.get('chargeBearer')

        # Bank codes
        result['sendingBankCode'] = data.get('sendingBankCode')
        result['sendingBankName'] = data.get('sendingBankName')
        result['sendingBankBic'] = data.get('sendingBankBic')
        result['receivingBankCode'] = data.get('receivingBankCode')
        result['receivingBankName'] = data.get('receivingBankName')
        result['receivingBankBic'] = data.get('receivingBankBic')

        # Payer information
        result['payerName'] = data.get('payerName')
        result['payerAccount'] = data.get('payerAccount')
        result['payerAccountType'] = data.get('payerAccountType')
        result['payerBusinessNumber'] = data.get('payerBusinessNumber')

        payer_addr = data.get('payerAddress', {})
        result['payerStreetName'] = payer_addr.get('streetName')
        result['payerBuildingNumber'] = payer_addr.get('buildingNumber')
        result['payerBuildingName'] = payer_addr.get('buildingName')
        result['payerFloor'] = payer_addr.get('floor')
        result['payerPostalCode'] = payer_addr.get('postalCode')
        result['payerCity'] = payer_addr.get('city')
        result['payerDistrict'] = payer_addr.get('district')
        result['payerCountry'] = payer_addr.get('country') or 'KR'

        payer_contact = data.get('payerContact', {})
        result['payerContactName'] = payer_contact.get('name')
        result['payerContactPhone'] = payer_contact.get('phone')
        result['payerContactEmail'] = payer_contact.get('email')

        # Payee information
        result['payeeName'] = data.get('payeeName')
        result['payeeAccount'] = data.get('payeeAccount')
        result['payeeAccountType'] = data.get('payeeAccountType')
        result['payeeBusinessNumber'] = data.get('payeeBusinessNumber')

        payee_addr = data.get('payeeAddress', {})
        result['payeeStreetName'] = payee_addr.get('streetName')
        result['payeeBuildingNumber'] = payee_addr.get('buildingNumber')
        result['payeeBuildingName'] = payee_addr.get('buildingName')
        result['payeeFloor'] = payee_addr.get('floor')
        result['payeePostalCode'] = payee_addr.get('postalCode')
        result['payeeCity'] = payee_addr.get('city')
        result['payeeDistrict'] = payee_addr.get('district')
        result['payeeCountry'] = payee_addr.get('country') or 'KR'

        payee_contact = data.get('payeeContact', {})
        result['payeeContactName'] = payee_contact.get('name')
        result['payeeContactPhone'] = payee_contact.get('phone')
        result['payeeContactEmail'] = payee_contact.get('email')

        # Purpose
        result['purpose'] = data.get('purpose')
        result['purposeDescription'] = data.get('purposeDescription')

        # Remittance information
        remit = data.get('remittanceInfo', {})
        result['invoiceNumber'] = remit.get('invoiceNumber')
        result['invoiceDate'] = remit.get('invoiceDate')
        result['purchaseOrderNumber'] = remit.get('purchaseOrderNumber')
        result['description'] = remit.get('description')

        return result


class KftcExtractor(BaseExtractor):
    """Extractor for Korea KFTC payment messages."""

    MESSAGE_TYPE = "KFTC"
    SILVER_TABLE = "stg_kftc"

    def __init__(self):
        """Initialize extractor with parser."""
        super().__init__()
        self.parser = KftcParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw KFTC content."""
        # Parse if string
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        msg_id = parsed.get('messageId', '') or parsed.get('transactionReference', '')
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
        """Extract all Silver layer fields from KFTC message.

        Supports multiple field naming conventions:
        - payerName/payerAccount or senderName/senderAccount
        - payeeName/payeeAccount or receiverName/receiverAccount
        - sendingBankCode/senderBankCode, receivingBankCode/receiverBankCode
        """
        trunc = self.trunc

        # Parse if needed
        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = self.parser.parse(msg_content)

        # Handle field name variations (payer/sender, payee/receiver)
        payer_name = parsed.get('payerName') or parsed.get('senderName')
        payer_account = parsed.get('payerAccount') or parsed.get('senderAccount')
        payee_name = parsed.get('payeeName') or parsed.get('receiverName')
        payee_account = parsed.get('payeeAccount') or parsed.get('receiverAccount')
        sending_bank = parsed.get('sendingBankCode') or parsed.get('senderBankCode')
        receiving_bank = parsed.get('receivingBankCode') or parsed.get('receiverBankCode')

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type and Identification
            'message_type': parsed.get('messageType') or 'KFTC',
            'message_id': trunc(parsed.get('messageId'), 35),
            'creation_date_time': parsed.get('creationDateTime'),
            'settlement_date': parsed.get('settlementDate'),

            # Amount
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or 'KRW',

            # Bank Codes (both naming conventions)
            'sending_bank_code': trunc(sending_bank, 11),
            'receiving_bank_code': trunc(receiving_bank, 11),

            # Transaction Details
            'transaction_reference': trunc(parsed.get('transactionReference'), 35),
            'transaction_id': trunc(parsed.get('transactionId'), 35),

            # Payer/Sender (primary fields)
            'payer_name': trunc(payer_name, 140),
            'payer_account': trunc(payer_account, 34),

            # Payee/Receiver (primary fields)
            'payee_name': trunc(payee_name, 140),
            'payee_account': trunc(payee_account, 34),

            # Sender fields (alternate naming)
            'sender_name': trunc(parsed.get('senderName'), 140),
            'sender_account': trunc(parsed.get('senderAccount'), 34),
            'sender_bank_code': trunc(parsed.get('senderBankCode'), 11),

            # Receiver fields (alternate naming)
            'receiver_name': trunc(parsed.get('receiverName'), 140),
            'receiver_account': trunc(parsed.get('receiverAccount'), 34),
            'receiver_bank_code': trunc(parsed.get('receiverBankCode'), 11),

            # Purpose
            'purpose': parsed.get('purpose'),

            # Additional parsed fields
            'sending_bank_name': trunc(parsed.get('sendingBankName'), 140),
            'receiving_bank_name': trunc(parsed.get('receivingBankName'), 140),
            'sending_bank_bic': trunc(parsed.get('sendingBankBic'), 11),
            'receiving_bank_bic': trunc(parsed.get('receivingBankBic'), 11),
            'payment_type': trunc(parsed.get('paymentType'), 10),
            'charge_bearer': trunc(parsed.get('chargeBearer'), 10),
            'payer_business_number': trunc(parsed.get('payerBusinessNumber'), 20),
            'payee_business_number': trunc(parsed.get('payeeBusinessNumber'), 20),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Matches the silver.stg_kftc table schema exactly.
        """
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_bank_code', 'receiving_bank_code', 'transaction_reference',
            'transaction_id',
            'payer_name', 'payer_account',
            'payee_name', 'payee_account',
            'sender_name', 'sender_account', 'sender_bank_code',
            'receiver_name', 'receiver_account', 'receiver_bank_code',
            'purpose',
            'sending_bank_name', 'receiving_bank_name',
            'sending_bank_bic', 'receiving_bank_bic',
            'payment_type', 'charge_bearer',
            'payer_business_number', 'payee_business_number',
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
        """Extract Gold layer entities from KFTC Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Payer Party - uses Silver column names
        if silver_data.get('payer_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payer_name'),
                role="DEBTOR",
                party_type='ORGANIZATION',
                identification_type='BRN',
                identification_number=silver_data.get('payer_business_number'),
                country='KR',
            ))

        # Payee Party
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='ORGANIZATION',
                identification_type='BRN',
                identification_number=silver_data.get('payee_business_number'),
                country='KR',
            ))

        # Payer Account
        if silver_data.get('payer_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payer_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'KRW',
            ))

        # Payee Account
        if silver_data.get('payee_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('payee_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'KRW',
            ))

        # Sending Bank
        if silver_data.get('sending_bank_code') or silver_data.get('sending_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('sending_bank_name'),
                bic=silver_data.get('sending_bank_bic'),
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system='KRKFTC',  # Korea KFTC
                country='KR',
            ))

        # Receiving Bank
        if silver_data.get('receiving_bank_code') or silver_data.get('receiving_bank_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('receiving_bank_name'),
                bic=silver_data.get('receiving_bank_bic'),
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system='KRKFTC',
                country='KR',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('KFTC', KftcExtractor())
ExtractorRegistry.register('kftc', KftcExtractor())

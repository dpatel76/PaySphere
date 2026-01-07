"""Japan BOJ-NET (Bank of Japan Financial Network System) Extractor - JSON based."""

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


class BojnetParser:
    """Parser for BOJ-NET JSON format messages.

    Handles the JSON structure with header and transactions array:
    {
        "header": { "messageType": "BOJNET", "batchId": "...", ... },
        "transactions": [
            {
                "messageId": "...",
                "transactionReference": "...",
                "amount": 125000000.00,
                "currency": "JPY",
                "payer": { "name": "...", "accountNumber": "...", "address": {...} },
                "payee": { "name": "...", "accountNumber": "...", "address": {...} },
                ...
            }
        ]
    }
    """

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse BOJ-NET JSON message into structured dict."""
        result = {
            'messageType': 'BOJNET',
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
                    logger.warning(f"Failed to parse BOJ-NET JSON: {e}")
                    return result
            else:
                logger.warning("BOJ-NET content is not JSON")
                return result

        # Extract header fields
        header = data.get('header', {})
        result['batchId'] = header.get('batchId')
        result['headerMessageType'] = header.get('messageType')
        result['recordCount'] = header.get('recordCount')
        result['headerCreationDateTime'] = header.get('creationDateTime')
        result['headerSettlementDate'] = header.get('settlementDate')
        result['priority'] = header.get('priority')

        # Extract first transaction (or use flat structure)
        transactions = data.get('transactions', [])
        if transactions:
            tx = transactions[0]
        else:
            # Flat structure - transaction fields at root level
            tx = data

        # Core transaction fields
        result['messageId'] = tx.get('messageId')
        result['transactionReference'] = tx.get('transactionReference')
        result['creationDateTime'] = tx.get('creationDateTime')
        result['settlementDate'] = tx.get('settlementDate')
        result['valueDate'] = tx.get('valueDate')
        result['amount'] = tx.get('amount')
        result['currency'] = tx.get('currency') or 'JPY'
        result['chargeBearer'] = tx.get('chargeBearer')

        # Participant codes
        result['sendingParticipantCode'] = tx.get('sendingParticipantCode')
        result['sendingParticipantName'] = tx.get('sendingParticipantName')
        result['sendingParticipantBic'] = tx.get('sendingParticipantBic')
        result['receivingParticipantCode'] = tx.get('receivingParticipantCode')
        result['receivingParticipantName'] = tx.get('receivingParticipantName')
        result['receivingParticipantBic'] = tx.get('receivingParticipantBic')

        # Account numbers
        result['debitAccount'] = tx.get('debitAccount')
        result['creditAccount'] = tx.get('creditAccount')

        # Payment type
        result['paymentType'] = tx.get('paymentType')
        result['relatedReference'] = tx.get('relatedReference')
        result['purposeCode'] = tx.get('purposeCode')

        # Payer information
        payer = tx.get('payer', {})
        result['payerName'] = payer.get('name')
        result['payerAccountNumber'] = payer.get('accountNumber')
        result['payerAccountType'] = payer.get('accountType')
        result['payerCorporateNumber'] = payer.get('corporateNumber')

        payer_addr = payer.get('address', {})
        result['payerStreetName'] = payer_addr.get('streetName')
        result['payerBuildingNumber'] = payer_addr.get('buildingNumber')
        result['payerBuildingName'] = payer_addr.get('buildingName')
        result['payerFloor'] = payer_addr.get('floor')
        result['payerPostalCode'] = payer_addr.get('postalCode')
        result['payerCity'] = payer_addr.get('city')
        result['payerPrefecture'] = payer_addr.get('prefecture')
        result['payerCountry'] = payer_addr.get('country') or 'JP'

        payer_contact = payer.get('contact', {})
        result['payerContactName'] = payer_contact.get('name')
        result['payerContactPhone'] = payer_contact.get('phone')
        result['payerContactEmail'] = payer_contact.get('email')

        # Payee information
        payee = tx.get('payee', {})
        result['payeeName'] = payee.get('name')
        result['payeeAccountNumber'] = payee.get('accountNumber')
        result['payeeAccountType'] = payee.get('accountType')
        result['payeeCorporateNumber'] = payee.get('corporateNumber')

        payee_addr = payee.get('address', {})
        result['payeeStreetName'] = payee_addr.get('streetName')
        result['payeeBuildingNumber'] = payee_addr.get('buildingNumber')
        result['payeeBuildingName'] = payee_addr.get('buildingName')
        result['payeeFloor'] = payee_addr.get('floor')
        result['payeePostalCode'] = payee_addr.get('postalCode')
        result['payeeCity'] = payee_addr.get('city')
        result['payeePrefecture'] = payee_addr.get('prefecture')
        result['payeeCountry'] = payee_addr.get('country') or 'JP'

        payee_contact = payee.get('contact', {})
        result['payeeContactName'] = payee_contact.get('name')
        result['payeeContactPhone'] = payee_contact.get('phone')
        result['payeeContactEmail'] = payee_contact.get('email')

        # Remittance information
        remit = tx.get('remittanceInfo', {})
        result['invoiceNumber'] = remit.get('invoiceNumber')
        result['invoiceDate'] = remit.get('invoiceDate')
        result['description'] = remit.get('description')

        return result


class BojnetExtractor(BaseExtractor):
    """Extractor for Japan BOJ-NET payment messages."""

    MESSAGE_TYPE = "BOJNET"
    SILVER_TABLE = "stg_bojnet"

    def __init__(self):
        """Initialize extractor with parser."""
        super().__init__()
        self.parser = BojnetParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw BOJ-NET content."""
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
        """Extract all Silver layer fields from BOJ-NET message."""
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
            'message_type': 'BOJNET',
            'message_id': trunc(parsed.get('messageId'), 35),
            'creation_date_time': parsed.get('creationDateTime'),
            'settlement_date': parsed.get('settlementDate'),

            # Amount
            'amount': parsed.get('amount'),
            'currency': parsed.get('currency') or 'JPY',

            # Participant Codes
            'sending_participant_code': trunc(parsed.get('sendingParticipantCode'), 11),
            'receiving_participant_code': trunc(parsed.get('receivingParticipantCode'), 11),

            # Transaction Details
            'transaction_reference': trunc(parsed.get('transactionReference'), 35),
            'related_reference': trunc(parsed.get('relatedReference'), 35),

            # Accounts
            'debit_account': trunc(parsed.get('debitAccount'), 34),
            'credit_account': trunc(parsed.get('creditAccount'), 34),

            # Payment Type
            'payment_type': trunc(parsed.get('paymentType'), 10),

            # Additional fields from parsed data
            'payer_name': trunc(parsed.get('payerName'), 140),
            'payee_name': trunc(parsed.get('payeeName'), 140),
            'sending_participant_name': trunc(parsed.get('sendingParticipantName'), 140),
            'receiving_participant_name': trunc(parsed.get('receivingParticipantName'), 140),
            'sending_participant_bic': trunc(parsed.get('sendingParticipantBic'), 11),
            'receiving_participant_bic': trunc(parsed.get('receivingParticipantBic'), 11),
            'value_date': parsed.get('valueDate'),
            'charge_bearer': trunc(parsed.get('chargeBearer'), 10),
            'purpose_code': trunc(parsed.get('purposeCode'), 10),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_participant_code', 'receiving_participant_code',
            'transaction_reference', 'related_reference',
            'debit_account', 'credit_account',
            'payment_type',
            'payer_name', 'payee_name',
            'sending_participant_name', 'receiving_participant_name',
            'sending_participant_bic', 'receiving_participant_bic',
            'value_date', 'charge_bearer', 'purpose_code',
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
        """Extract Gold layer entities from BOJ-NET Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Payer Party (Debtor)
        payer_name = silver_data.get('payer_name')
        if payer_name:
            entities.parties.append(PartyData(
                name=payer_name,
                role="DEBTOR",
                party_type='ORGANIZATION',
                country='JP',
            ))

        # Payee Party (Creditor)
        payee_name = silver_data.get('payee_name')
        if payee_name:
            entities.parties.append(PartyData(
                name=payee_name,
                role="CREDITOR",
                party_type='ORGANIZATION',
                country='JP',
            ))

        # Debit Account - uses Silver column names
        if silver_data.get('debit_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debit_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'JPY',
            ))

        # Credit Account
        if silver_data.get('credit_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('credit_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'JPY',
            ))

        # Sending Participant
        if silver_data.get('sending_participant_code') or silver_data.get('sending_participant_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('sending_participant_name'),
                bic=silver_data.get('sending_participant_bic'),
                clearing_code=silver_data.get('sending_participant_code'),
                clearing_system='JPBOJ',  # BOJ clearing
                country='JP',
            ))

        # Receiving Participant
        if silver_data.get('receiving_participant_code') or silver_data.get('receiving_participant_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('receiving_participant_name'),
                bic=silver_data.get('receiving_participant_bic'),
                clearing_code=silver_data.get('receiving_participant_code'),
                clearing_system='JPBOJ',
                country='JP',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('BOJNET', BojnetExtractor())
ExtractorRegistry.register('bojnet', BojnetExtractor())
ExtractorRegistry.register('BOJ-NET', BojnetExtractor())

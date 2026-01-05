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


class KftcExtractor(BaseExtractor):
    """Extractor for Korea KFTC payment messages."""

    MESSAGE_TYPE = "KFTC"
    SILVER_TABLE = "stg_kftc"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw KFTC content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('transactionReference', '')
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

        # Handle field name variations (payer/sender, payee/receiver)
        payer_name = msg_content.get('payerName') or msg_content.get('senderName')
        payer_account = msg_content.get('payerAccount') or msg_content.get('senderAccount')
        payee_name = msg_content.get('payeeName') or msg_content.get('receiverName')
        payee_account = msg_content.get('payeeAccount') or msg_content.get('receiverAccount')
        sending_bank = msg_content.get('sendingBankCode') or msg_content.get('senderBankCode')
        receiving_bank = msg_content.get('receivingBankCode') or msg_content.get('receiverBankCode')

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type and Identification
            'message_type': msg_content.get('messageType') or 'KFTC',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'KRW',

            # Bank Codes (both naming conventions)
            'sending_bank_code': trunc(sending_bank, 11),
            'receiving_bank_code': trunc(receiving_bank, 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),

            # Payer/Sender (primary fields)
            'payer_name': trunc(payer_name, 140),
            'payer_account': trunc(payer_account, 34),

            # Payee/Receiver (primary fields)
            'payee_name': trunc(payee_name, 140),
            'payee_account': trunc(payee_account, 34),

            # Sender fields (alternate naming)
            'sender_name': trunc(msg_content.get('senderName'), 140),
            'sender_account': trunc(msg_content.get('senderAccount'), 34),
            'sender_bank_code': trunc(msg_content.get('senderBankCode'), 11),

            # Receiver fields (alternate naming)
            'receiver_name': trunc(msg_content.get('receiverName'), 140),
            'receiver_account': trunc(msg_content.get('receiverAccount'), 34),
            'receiver_bank_code': trunc(msg_content.get('receiverBankCode'), 11),

            # Purpose
            'purpose': msg_content.get('purpose'),
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
                party_type='UNKNOWN',
                country='KR',
            ))

        # Payee Party
        if silver_data.get('payee_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('payee_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
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
        if silver_data.get('sending_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('sending_bank_code'),
                clearing_system='KRKFTC',  # Korea KFTC
                country='KR',
            ))

        # Receiving Bank
        if silver_data.get('receiving_bank_code'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('receiving_bank_code'),
                clearing_system='KRKFTC',
                country='KR',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('KFTC', KftcExtractor())
ExtractorRegistry.register('kftc', KftcExtractor())

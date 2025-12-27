"""SWIFT MT940 (Customer Statement Message) Extractor."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
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


class Mt940Extractor(BaseExtractor):
    """Extractor for SWIFT MT940 Customer Statement messages."""

    MESSAGE_TYPE = "MT940"
    SILVER_TABLE = "stg_mt940"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw MT940 content."""
        msg_id = raw_content.get('transactionReference', '') or raw_content.get('statementNumber', '')
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
        """Extract all Silver layer fields from MT940 message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'MT940',

            # Sender/Receiver
            'sender_bic': trunc(msg_content.get('senderBic'), 11),
            'receiver_bic': trunc(msg_content.get('receiverBic'), 11),

            # Transaction Reference (Field 20)
            'transaction_reference': trunc(msg_content.get('transactionReference'), 16),

            # Account Identification (Field 25)
            'account_identification': trunc(msg_content.get('accountIdentification'), 35),

            # Statement Number/Sequence (Field 28C)
            'statement_number': msg_content.get('statementNumber'),
            'sequence_number': msg_content.get('sequenceNumber'),

            # Opening Balance (Field 60a - F or M)
            'opening_balance_date': msg_content.get('openingBalanceDate'),
            'opening_balance_currency': msg_content.get('openingBalanceCurrency'),
            'opening_balance_amount': msg_content.get('openingBalanceAmount'),
            'opening_balance_indicator': trunc(msg_content.get('openingBalanceIndicator'), 1),  # C or D

            # Closing Balance (Field 62a - F or M)
            'closing_balance_date': msg_content.get('closingBalanceDate'),
            'closing_balance_currency': msg_content.get('closingBalanceCurrency'),
            'closing_balance_amount': msg_content.get('closingBalanceAmount'),
            'closing_balance_indicator': trunc(msg_content.get('closingBalanceIndicator'), 1),  # C or D

            # Statement Line Count
            'number_of_lines': msg_content.get('numberOfLines'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'sender_bic', 'receiver_bic',
            'transaction_reference', 'account_identification',
            'statement_number', 'sequence_number',
            'opening_balance_date', 'opening_balance_currency',
            'opening_balance_amount', 'opening_balance_indicator',
            'closing_balance_date', 'closing_balance_currency',
            'closing_balance_amount', 'closing_balance_indicator',
            'number_of_lines',
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
        """Extract Gold layer entities from MT940 message."""
        entities = GoldEntities()

        # Statement Account
        if msg_content.get('accountIdentification'):
            entities.accounts.append(AccountData(
                account_number=msg_content.get('accountIdentification'),
                role="STATEMENT_ACCOUNT",
                account_type='CACC',
                currency=msg_content.get('openingBalanceCurrency') or 'XXX',
            ))

        # Sender Bank
        if msg_content.get('senderBic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="ACCOUNT_SERVICER",
                bic=msg_content.get('senderBic'),
            ))

        # Receiver (Account Owner's Bank or Correspondent)
        if msg_content.get('receiverBic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="MESSAGE_RECIPIENT",
                bic=msg_content.get('receiverBic'),
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('MT940', Mt940Extractor())
ExtractorRegistry.register('mt940', Mt940Extractor())

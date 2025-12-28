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


class Mt940BlockParser:
    """Parser for SWIFT MT940 block format messages."""

    # Block patterns
    BLOCK_PATTERN = re.compile(r'\{(\d):([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}')
    TAG_PATTERN = re.compile(r':(\d{2}[A-Z]?):([^\r\n:]+(?:\r?\n(?!:)[^\r\n:]*)*)', re.MULTILINE)

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse MT940 message into structured dict."""
        result = {
            'messageType': 'MT940',
            'blocks': {},
            'statementLines': [],
        }

        # Handle JSON input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and 'messageType' not in parsed:
                    parsed['messageType'] = 'MT940'
                return parsed
            except json.JSONDecodeError:
                pass

        # Parse SWIFT block format
        for match in self.BLOCK_PATTERN.finditer(raw_content):
            block_num = match.group(1)
            block_content = match.group(2)
            result['blocks'][f'block{block_num}'] = block_content

            if block_num == '1':
                self._parse_basic_header(block_content, result)
            elif block_num == '2':
                self._parse_application_header(block_content, result)
            elif block_num == '4':
                self._parse_text_block(block_content, result)

        return result

    def _parse_basic_header(self, content: str, result: Dict):
        """Parse Block 1: Basic Header."""
        if len(content) >= 12:
            result['senderBic'] = content[3:15].strip() if len(content) >= 15 else content[3:].strip()

    def _parse_application_header(self, content: str, result: Dict):
        """Parse Block 2: Application Header."""
        if content.startswith('O'):
            result['messageType'] = content[1:4] if len(content) >= 4 else 'MT940'
            if len(content) >= 28:
                result['receiverBic'] = content[16:28].strip()
        elif content.startswith('I'):
            result['messageType'] = content[1:4] if len(content) >= 4 else 'MT940'
            if len(content) >= 16:
                result['receiverBic'] = content[4:16].strip()

    def _parse_text_block(self, content: str, result: Dict):
        """Parse Block 4: Text Block (Statement Content)."""
        line_count = 0

        for match in self.TAG_PATTERN.finditer(content):
            tag = match.group(1)
            value = match.group(2).strip()

            # Transaction Reference (Field 20)
            if tag == '20':
                result['transactionReference'] = value

            # Account Identification (Field 25)
            elif tag == '25':
                result['accountIdentification'] = value

            # Statement Number/Sequence (Field 28C)
            elif tag == '28C':
                parts = value.split('/')
                result['statementNumber'] = parts[0] if parts else None
                result['sequenceNumber'] = parts[1] if len(parts) > 1 else None

            # Opening Balance (Field 60F or 60M)
            elif tag in ('60F', '60M'):
                self._parse_balance(value, result, 'opening')

            # Statement Line (Field 61)
            elif tag == '61':
                line_count += 1
                # Parse statement line - we just count for now
                result['statementLines'].append(value)

            # Closing Balance (Field 62F or 62M)
            elif tag in ('62F', '62M'):
                self._parse_balance(value, result, 'closing')

        result['numberOfLines'] = line_count

    def _parse_balance(self, value: str, result: Dict, balance_type: str):
        """Parse balance field (60F/60M or 62F/62M)."""
        prefix = f'{balance_type}Balance'

        if len(value) >= 1:
            # First character is C (Credit) or D (Debit)
            result[f'{prefix}Indicator'] = value[0]

        if len(value) >= 7:
            # Date: YYMMDD
            date_str = value[1:7]
            try:
                year = int(date_str[:2])
                full_year = 2000 + year if year < 50 else 1900 + year
                result[f'{prefix}Date'] = f"{full_year}-{date_str[2:4]}-{date_str[4:6]}"
            except ValueError:
                result[f'{prefix}Date'] = None

        if len(value) >= 10:
            # Currency: 3 chars
            result[f'{prefix}Currency'] = value[7:10]

        if len(value) > 10:
            # Amount
            amount_str = value[10:].replace(',', '.')
            try:
                result[f'{prefix}Amount'] = float(amount_str)
            except ValueError:
                result[f'{prefix}Amount'] = None


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

            # Sender/Receiver (12 chars for SWIFT block format with XXX)
            'sender_bic': trunc(msg_content.get('senderBic'), 12),
            'receiver_bic': trunc(msg_content.get('receiverBic'), 12),

            # Transaction Reference (Field 20 - up to 35 chars per SWIFT)
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

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

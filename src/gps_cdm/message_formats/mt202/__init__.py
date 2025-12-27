"""SWIFT MT202 (General Financial Institution Transfer) Extractor."""

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


class Mt202BlockParser:
    """Parser for SWIFT MT202 block format messages."""

    # Block patterns
    BLOCK_PATTERN = re.compile(r'\{(\d):([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}')
    TAG_PATTERN = re.compile(r':(\d{2}[A-Z]?):([^\r\n:]+(?:\r?\n(?!:)[^\r\n:]*)*)', re.MULTILINE)

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse MT202 message into structured dict."""
        result = {
            'messageType': 'MT202',
            'blocks': {},
            'fields': {},
        }

        # Handle JSON input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and 'messageType' not in parsed:
                    parsed['messageType'] = 'MT202'
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
            # Output header
            result['messageType'] = content[1:4] if len(content) >= 4 else 'MT202'
            if len(content) >= 16:
                result['receiverBic'] = content[16:28].strip() if len(content) >= 28 else None
        elif content.startswith('I'):
            # Input header
            result['messageType'] = content[1:4] if len(content) >= 4 else 'MT202'
            if len(content) >= 16:
                result['receiverBic'] = content[4:16].strip()

    def _parse_text_block(self, content: str, result: Dict):
        """Parse Block 4: Text Block (Message Content)."""
        fields = result['fields']

        for match in self.TAG_PATTERN.finditer(content):
            tag = match.group(1)
            value = match.group(2).strip()

            # Map MT202 tags to fields
            if tag == '20':
                fields['transactionReference'] = value
                result['transactionReference'] = value
            elif tag == '21':
                fields['relatedReference'] = value
                result['relatedReference'] = value
            elif tag == '32A':
                self._parse_value_date_amount(value, result)
            elif tag == '52A' or tag == '52D':
                fields['orderingInstitution'] = value
                result['orderingInstitutionBic'] = self._extract_bic(value)
            elif tag == '53A' or tag == '53B' or tag == '53D':
                fields['sendersCorrespondent'] = value
                result['sendersCorrespondentBic'] = self._extract_bic(value)
            elif tag == '54A' or tag == '54B' or tag == '54D':
                fields['receiversCorrespondent'] = value
                result['receiversCorrespondentBic'] = self._extract_bic(value)
            elif tag == '56A' or tag == '56D':
                fields['intermediary'] = value
                result['intermediaryBic'] = self._extract_bic(value)
            elif tag == '57A' or tag == '57B' or tag == '57D':
                fields['accountWithInstitution'] = value
                result['accountWithInstitutionBic'] = self._extract_bic(value)
            elif tag == '58A' or tag == '58D':
                fields['beneficiaryInstitution'] = value
                result['beneficiaryInstitutionBic'] = self._extract_bic(value)
            elif tag == '72':
                fields['senderToReceiverInfo'] = value
                result['senderToReceiverInfo'] = value
            elif tag == '121':
                result['uetr'] = value

    def _parse_value_date_amount(self, value: str, result: Dict):
        """Parse tag 32A: Value Date/Currency/Amount."""
        if len(value) >= 6:
            date_str = value[:6]
            try:
                year = int(date_str[:2])
                full_year = 2000 + year if year < 50 else 1900 + year
                result['valueDate'] = f"{full_year}-{date_str[2:4]}-{date_str[4:6]}"
            except ValueError:
                result['valueDate'] = None

        if len(value) >= 9:
            result['currency'] = value[6:9]

        if len(value) > 9:
            amount_str = value[9:].replace(',', '.')
            try:
                result['amount'] = float(amount_str)
            except ValueError:
                result['amount'] = None

    def _extract_bic(self, value: str) -> Optional[str]:
        """Extract BIC from field value."""
        lines = value.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) >= 8 and line[:8].isalnum():
                return line[:11] if len(line) >= 11 else line[:8]
        return None


class Mt202Extractor(BaseExtractor):
    """Extractor for SWIFT MT202 messages."""

    MESSAGE_TYPE = "MT202"
    SILVER_TABLE = "stg_mt202"

    def __init__(self):
        self.parser = Mt202BlockParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw MT202 content."""
        msg_id = raw_content.get('transactionReference', '') or raw_content.get('messageId', '')
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
        """Extract all Silver layer fields from MT202 message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': msg_content.get('messageType', 'MT202'),

            # BICs
            'sender_bic': trunc(msg_content.get('senderBic'), 12),
            'receiver_bic': trunc(msg_content.get('receiverBic'), 12),

            # Transaction References
            'transaction_reference': trunc(msg_content.get('transactionReference'), 16),
            'related_reference': trunc(msg_content.get('relatedReference'), 16),

            # Value Date and Amount
            'value_date': msg_content.get('valueDate'),
            'currency': msg_content.get('currency') or 'USD',
            'amount': msg_content.get('amount'),

            # Institution BICs
            'ordering_institution_bic': trunc(msg_content.get('orderingInstitutionBic'), 11),
            'senders_correspondent_bic': trunc(msg_content.get('sendersCorrespondentBic'), 11),
            'receivers_correspondent_bic': trunc(msg_content.get('receiversCorrespondentBic'), 11),
            'intermediary_bic': trunc(msg_content.get('intermediaryBic'), 11),
            'account_with_institution_bic': trunc(msg_content.get('accountWithInstitutionBic'), 11),
            'beneficiary_institution_bic': trunc(msg_content.get('beneficiaryInstitutionBic'), 11),

            # Additional Info
            'sender_to_receiver_info': msg_content.get('senderToReceiverInfo'),
            'uetr': msg_content.get('uetr'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'sender_bic', 'receiver_bic',
            'transaction_reference', 'related_reference',
            'value_date', 'currency', 'amount',
            'ordering_institution_bic', 'senders_correspondent_bic',
            'receivers_correspondent_bic', 'intermediary_bic',
            'account_with_institution_bic', 'beneficiary_institution_bic',
            'sender_to_receiver_info', 'uetr',
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
        """Extract Gold layer entities from MT202 message."""
        entities = GoldEntities()

        # Ordering Institution (Debtor Agent)
        if msg_content.get('orderingInstitutionBic') or msg_content.get('senderBic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=msg_content.get('orderingInstitutionBic') or msg_content.get('senderBic'),
                country='XX',
            ))

        # Sender's Correspondent
        if msg_content.get('sendersCorrespondentBic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                bic=msg_content.get('sendersCorrespondentBic'),
                country='XX',
            ))

        # Beneficiary Institution (Creditor Agent)
        if msg_content.get('beneficiaryInstitutionBic') or msg_content.get('receiverBic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=msg_content.get('beneficiaryInstitutionBic') or msg_content.get('receiverBic'),
                country='XX',
            ))

        # Account with Institution
        if msg_content.get('accountWithInstitutionBic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=msg_content.get('accountWithInstitutionBic'),
                country='XX',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('MT202', Mt202Extractor())
ExtractorRegistry.register('mt202', Mt202Extractor())
ExtractorRegistry.register('MT202COV', Mt202Extractor())
ExtractorRegistry.register('mt202cov', Mt202Extractor())

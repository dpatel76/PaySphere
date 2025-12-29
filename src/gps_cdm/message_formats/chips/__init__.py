"""CHIPS (Clearing House Interbank Payments System) Extractor."""

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


class ChipsXmlParser:
    """Parser for CHIPS XML format messages."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse CHIPS message into structured dict."""
        result = {
            'messageType': 'CHIPS',
        }

        # Handle JSON input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and 'messageType' not in parsed:
                    parsed['messageType'] = 'CHIPS'
                return parsed
            except json.JSONDecodeError:
                pass

        # Parse CHIPS XML format using regex
        content = raw_content

        # Message Header
        result['sequenceNumber'] = self._extract_tag(content, 'UID')
        result['messageTypeCode'] = self._extract_tag(content, 'MSG_TYPE')
        result['sendingParticipant'] = self._extract_tag(content, 'SENDER_UID')
        result['receivingParticipant'] = self._extract_tag(content, 'RECEIVER_UID')

        # Payment Info
        amount_str = self._extract_tag(content, 'AMOUNT')
        if amount_str:
            try:
                result['amount'] = float(amount_str.replace(',', ''))
            except ValueError:
                result['amount'] = None
        result['currency'] = self._extract_tag(content, 'CURRENCY') or 'USD'

        value_date = self._extract_tag(content, 'VALUE_DATE')
        if value_date and len(value_date) >= 8:
            result['valueDate'] = f"{value_date[:4]}-{value_date[4:6]}-{value_date[6:8]}"
        else:
            result['valueDate'] = value_date

        result['senderReference'] = self._extract_tag(content, 'SENDER_REF')

        # Sender Info
        sender_info = self._extract_section(content, 'SENDER_INFO')
        if sender_info:
            result['originatorBank'] = self._extract_tag(sender_info, 'ABA')
            result['sendingBankName'] = self._extract_tag(sender_info, 'NAME')

        # Receiver Info
        receiver_info = self._extract_section(content, 'RECEIVER_INFO')
        if receiver_info:
            result['beneficiaryBank'] = self._extract_tag(receiver_info, 'ABA')
            result['receivingBankName'] = self._extract_tag(receiver_info, 'NAME')

        # Originator Info
        orig_info = self._extract_section(content, 'ORIG_INFO')
        if orig_info:
            result['originatorName'] = self._extract_tag(orig_info, 'NAME')
            result['originatorAccount'] = self._extract_tag(orig_info, 'ACCOUNT')
            addr1 = self._extract_tag(orig_info, 'ADDR1') or ''
            addr2 = self._extract_tag(orig_info, 'ADDR2') or ''
            result['originatorAddress'] = f"{addr1} {addr2}".strip()

        # Beneficiary Info
        benef_info = self._extract_section(content, 'BENEF_INFO')
        if benef_info:
            result['beneficiaryName'] = self._extract_tag(benef_info, 'NAME')
            result['beneficiaryAccount'] = self._extract_tag(benef_info, 'ACCOUNT')
            addr1 = self._extract_tag(benef_info, 'ADDR1') or ''
            addr2 = self._extract_tag(benef_info, 'ADDR2') or ''
            result['beneficiaryAddress'] = f"{addr1} {addr2}".strip()

        # Payment Details
        pmt_details = self._extract_section(content, 'PAYMENT_DETAILS')
        if pmt_details:
            purpose = self._extract_tag(pmt_details, 'PURPOSE') or ''
            ref_info = self._extract_tag(pmt_details, 'REF_INFO') or ''
            result['paymentDetails'] = f"{purpose} {ref_info}".strip()

        return result

    def _extract_tag(self, content: str, tag_name: str) -> Optional[str]:
        """Extract value from XML-like tag."""
        pattern = rf'<{tag_name}>\s*([^<]+?)\s*</{tag_name}>'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract entire section content."""
        pattern = rf'<{section_name}>(.*?)</{section_name}>'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        return None


class ChipsExtractor(BaseExtractor):
    """Extractor for CHIPS payment messages."""

    MESSAGE_TYPE = "CHIPS"
    SILVER_TABLE = "stg_chips"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw CHIPS content."""
        msg_id = raw_content.get('sequenceNumber', '') or raw_content.get('senderReference', '')
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
        """Extract all Silver layer fields from CHIPS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'CHIPS',
            'sequence_number': trunc(msg_content.get('sequenceNumber'), 20),
            'message_type_code': trunc(msg_content.get('messageTypeCode'), 4),

            # Participants
            'sending_participant': trunc(msg_content.get('sendingParticipant'), 6),
            'receiving_participant': trunc(msg_content.get('receivingParticipant'), 6),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'USD',
            'value_date': msg_content.get('valueDate'),

            # References
            'sender_reference': trunc(msg_content.get('senderReference'), 16),
            'related_reference': trunc(msg_content.get('relatedReference'), 16),

            # Originator
            'originator_name': trunc(msg_content.get('originatorName'), 140),
            'originator_address': msg_content.get('originatorAddress'),
            'originator_account': trunc(msg_content.get('originatorAccount'), 34),

            # Beneficiary
            'beneficiary_name': trunc(msg_content.get('beneficiaryName'), 140),
            'beneficiary_address': msg_content.get('beneficiaryAddress'),
            'beneficiary_account': trunc(msg_content.get('beneficiaryAccount'), 34),

            # Banks
            'originator_bank': trunc(msg_content.get('originatorBank'), 11),
            'beneficiary_bank': trunc(msg_content.get('beneficiaryBank'), 11),
            'intermediary_bank': trunc(msg_content.get('intermediaryBank'), 11),

            # Additional Info
            'payment_details': msg_content.get('paymentDetails'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'sequence_number', 'message_type_code',
            'sending_participant', 'receiving_participant',
            'amount', 'currency', 'value_date',
            'sender_reference', 'related_reference',
            'originator_name', 'originator_address', 'originator_account',
            'beneficiary_name', 'beneficiary_address', 'beneficiary_account',
            'originator_bank', 'beneficiary_bank', 'intermediary_bank',
            'payment_details',
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
        """Extract Gold layer entities from CHIPS Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Originator Party (Debtor) - uses Silver column names
        if silver_data.get('originator_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('originator_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                country='US',
            ))

        # Beneficiary Party (Creditor)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                country='US',
            ))

        # Originator Account
        if silver_data.get('originator_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'USD',
            ))

        # Beneficiary Account
        if silver_data.get('beneficiary_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'USD',
            ))

        # Originator Bank (Debtor Agent)
        if silver_data.get('originator_bank') or silver_data.get('sending_participant'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('sending_participant'),
                bic=silver_data.get('originator_bank'),
                clearing_system='CHIPS',
                country='US',
            ))

        # Beneficiary Bank (Creditor Agent)
        if silver_data.get('beneficiary_bank') or silver_data.get('receiving_participant'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('receiving_participant'),
                bic=silver_data.get('beneficiary_bank'),
                clearing_system='CHIPS',
                country='US',
            ))

        # Intermediary Bank
        if silver_data.get('intermediary_bank'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                bic=silver_data.get('intermediary_bank'),
                clearing_system='CHIPS',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('CHIPS', ChipsExtractor())
ExtractorRegistry.register('chips', ChipsExtractor())

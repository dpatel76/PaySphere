"""Saudi Arabia SARIE (Saudi Arabian Riyal Interbank Express) Extractor.

Supports both JSON format and SWIFT MT-like format.
"""

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


def parse_swift_mt_message(raw_text: str) -> Dict[str, Any]:
    """Parse SWIFT MT-like message format used by SARIE.

    Format: {1:...}{2:...}{4:\n:tag:value\n...-}
    """
    result = {}

    # Extract Block 1 (Basic Header)
    block1_match = re.search(r'\{1:([^}]+)\}', raw_text)
    if block1_match:
        result['block1'] = block1_match.group(1)

    # Extract Block 2 (Application Header)
    block2_match = re.search(r'\{2:([^}]+)\}', raw_text)
    if block2_match:
        result['block2'] = block2_match.group(1)

    # Extract Block 4 (Text Block) - contains the actual message
    block4_match = re.search(r'\{4:\s*\n?(.*?)\n?-\}', raw_text, re.DOTALL)
    if block4_match:
        block4_text = block4_match.group(1)
        # Parse tag:value pairs
        tag_pattern = re.compile(r':(\d{2}[A-Z]?):(.+?)(?=\n:|\n-\}|$)', re.DOTALL)

        for match in tag_pattern.finditer(block4_text):
            tag = match.group(1)
            value = match.group(2).strip()
            result[f'tag_{tag}'] = value

    return result


class SarieExtractor(BaseExtractor):
    """Extractor for Saudi Arabia SARIE payment messages."""

    MESSAGE_TYPE = "SARIE"
    SILVER_TABLE = "stg_sarie"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw SARIE content."""
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
        """Extract all Silver layer fields from SARIE message.

        Handles:
        1. ChapsSwiftParser output (debtorName, creditorName, etc.)
        2. Raw SWIFT MT format in "raw" key
        3. Legacy JSON format (originatorName, beneficiaryName, etc.)
        """
        trunc = self.trunc

        # Check if already parsed by ChapsSwiftParser (has debtorName/creditorName keys)
        if msg_content.get('debtorName') or msg_content.get('creditorName') or msg_content.get('debtorAgentBic'):
            return self._extract_from_swift_parsed(msg_content, raw_id, stg_id, batch_id, trunc)

        # Check if this is a SWIFT MT format (wrapped in "raw" key or contains block markers)
        raw_text = msg_content.get('raw', '')
        if raw_text and '{1:' in raw_text:
            # Parse SWIFT MT format
            parsed = parse_swift_mt_message(raw_text)
            return self._extract_from_swift_mt(parsed, raw_id, stg_id, batch_id, trunc)
        elif isinstance(msg_content, str) and '{1:' in msg_content:
            parsed = parse_swift_mt_message(msg_content)
            return self._extract_from_swift_mt(parsed, raw_id, stg_id, batch_id, trunc)
        else:
            # Legacy JSON format
            return self._extract_from_json(msg_content, raw_id, stg_id, batch_id, trunc)

    def _extract_from_swift_parsed(
        self, msg_content: Dict[str, Any], raw_id: str, stg_id: str, batch_id: str, trunc
    ) -> Dict[str, Any]:
        """Extract Silver fields from ChapsSwiftParser output format.

        ChapsSwiftParser produces:
        - debtorName, debtorAccount, debtorAgentBic
        - creditorName, creditorAccount, creditorAgentBic
        - messageId, instructionId, amount, currency, settlementDate
        """
        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            'message_type': 'SARIE',
            'message_id': trunc(msg_content.get('messageId') or msg_content.get('instructionId'), 35),
            'creation_date_time': None,
            'settlement_date': msg_content.get('settlementDate'),
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'SAR',
            'sending_bank_code': trunc(msg_content.get('debtorAgentBic'), 11),
            'receiving_bank_code': trunc(msg_content.get('creditorAgentBic'), 11),
            'transaction_reference': trunc(msg_content.get('instructionId') or msg_content.get('messageId'), 35),
            'originator_name': trunc(msg_content.get('debtorName'), 140),
            'originator_account': trunc(msg_content.get('debtorAccount'), 34),
            'originator_id': None,
            'beneficiary_name': trunc(msg_content.get('creditorName'), 140),
            'beneficiary_account': trunc(msg_content.get('creditorAccount'), 34),
            'beneficiary_id': None,
            'purpose': msg_content.get('remittanceInfo'),
        }

    def _extract_from_swift_mt(
        self, parsed: Dict[str, Any], raw_id: str, stg_id: str, batch_id: str, trunc
    ) -> Dict[str, Any]:
        """Extract Silver fields from parsed SWIFT MT format."""

        # Tag 20: Transaction Reference
        transaction_ref = parsed.get('tag_20', '')

        # Tag 32A: Value Date, Currency and Amount (YYMMDDCCCAMOUNT,DD)
        tag_32a = parsed.get('tag_32A', '')
        settlement_date = None
        currency = 'SAR'
        amount = None
        if tag_32a:
            # Format: YYMMDDCCCAMOUNT,DD (e.g., 250106SAR15000,00)
            match = re.match(r'(\d{6})([A-Z]{3})([0-9,\.]+)', tag_32a)
            if match:
                date_str = match.group(1)
                currency = match.group(2)
                amount_str = match.group(3).replace(',', '.')
                try:
                    amount = float(amount_str)
                    # Parse date YYMMDD
                    settlement_date = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
                except ValueError:
                    pass

        # Tag 50K: Ordering Customer (Account + Name + Address)
        tag_50k = parsed.get('tag_50K', '')
        originator_account = None
        originator_name = None
        if tag_50k:
            lines = tag_50k.strip().split('\n')
            if lines:
                # First line is usually account (starts with /)
                if lines[0].startswith('/'):
                    originator_account = lines[0][1:]  # Remove leading /
                    originator_name = lines[1] if len(lines) > 1 else None
                else:
                    originator_name = lines[0]

        # Tag 52A: Ordering Institution (Sender BIC)
        sending_bank_code = parsed.get('tag_52A', '')

        # Tag 57A: Account With Institution (Receiver BIC)
        receiving_bank_code = parsed.get('tag_57A', '')

        # Tag 59: Beneficiary Customer (Account + Name + Address)
        tag_59 = parsed.get('tag_59', '')
        beneficiary_account = None
        beneficiary_name = None
        if tag_59:
            lines = tag_59.strip().split('\n')
            if lines:
                if lines[0].startswith('/'):
                    beneficiary_account = lines[0][1:]
                    beneficiary_name = lines[1] if len(lines) > 1 else None
                else:
                    beneficiary_name = lines[0]

        # Tag 70: Remittance Information
        purpose = parsed.get('tag_70', '')

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            'message_type': 'SARIE',
            'message_id': trunc(transaction_ref, 35),
            'creation_date_time': None,
            'settlement_date': settlement_date,
            'amount': amount,
            'currency': currency,
            'sending_bank_code': trunc(sending_bank_code, 11),
            'receiving_bank_code': trunc(receiving_bank_code, 11),
            'transaction_reference': trunc(transaction_ref, 35),
            'originator_name': trunc(originator_name, 140),
            'originator_account': trunc(originator_account, 34),
            'originator_id': None,
            'beneficiary_name': trunc(beneficiary_name, 140),
            'beneficiary_account': trunc(beneficiary_account, 34),
            'beneficiary_id': None,
            'purpose': purpose,
        }

    def _extract_from_json(
        self, msg_content: Dict[str, Any], raw_id: str, stg_id: str, batch_id: str, trunc
    ) -> Dict[str, Any]:
        """Extract Silver fields from JSON format."""
        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'SARIE',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'SAR',

            # Bank Codes
            'sending_bank_code': trunc(msg_content.get('sendingBankCode'), 11),
            'receiving_bank_code': trunc(msg_content.get('receivingBankCode'), 11),

            # Transaction Details
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

            # Originator (Debtor)
            'originator_name': trunc(msg_content.get('originatorName'), 140),
            'originator_account': trunc(msg_content.get('originatorAccount'), 34),
            'originator_id': trunc(msg_content.get('originatorId'), 20),

            # Beneficiary (Creditor)
            'beneficiary_name': trunc(msg_content.get('beneficiaryName'), 140),
            'beneficiary_account': trunc(msg_content.get('beneficiaryAccount'), 34),
            'beneficiary_id': trunc(msg_content.get('beneficiaryId'), 20),

            # Purpose
            'purpose': msg_content.get('purpose'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'amount', 'currency',
            'sending_bank_code', 'receiving_bank_code', 'transaction_reference',
            'originator_name', 'originator_account', 'originator_id',
            'beneficiary_name', 'beneficiary_account', 'beneficiary_id',
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
        """Extract Gold layer entities from SARIE Silver record.

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
                identification_number=silver_data.get('originator_id'),
                country='SA',
            ))

        # Beneficiary Party (Creditor)
        if silver_data.get('beneficiary_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('beneficiary_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                identification_number=silver_data.get('beneficiary_id'),
                country='SA',
            ))

        # Originator Account
        if silver_data.get('originator_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('originator_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SAR',
            ))

        # Beneficiary Account
        if silver_data.get('beneficiary_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('beneficiary_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('currency') or 'SAR',
            ))

        # Sending Bank (Debtor Agent)
        sending_bank = silver_data.get('sending_bank_code')
        if sending_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=sending_bank if len(sending_bank) in (8, 11) else None,
                clearing_code=sending_bank if len(sending_bank) not in (8, 11) else None,
                clearing_system='SASARIE',
                country='SA',
            ))

        # Receiving Bank (Creditor Agent)
        receiving_bank = silver_data.get('receiving_bank_code')
        if receiving_bank:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=receiving_bank if len(receiving_bank) in (8, 11) else None,
                clearing_code=receiving_bank if len(receiving_bank) not in (8, 11) else None,
                clearing_system='SASARIE',
                country='SA',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('SARIE', SarieExtractor())
ExtractorRegistry.register('sarie', SarieExtractor())

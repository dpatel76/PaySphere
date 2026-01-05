"""SWIFT MT940 (Customer Statement Message) Extractor.

MT940 is a SWIFT Customer Statement Message used for end-of-day account statements.
It reports account balances and transaction entries.

Key Fields:
- Field 20: Transaction Reference Number (Mandatory)
- Field 21: Related Reference (Optional)
- Field 25/25P: Account Identification (Mandatory)
- Field 28C: Statement Number/Sequence Number (Mandatory)
- Field 60a: Opening Balance (Mandatory - 60F or 60M)
- Field 61: Statement Line (Optional, repeatable)
- Field 86: Information to Account Owner (Optional, follows 61)
- Field 62a: Closing Balance (Mandatory - 62F or 62M)
- Field 64: Closing Available Balance (Optional)
- Field 65: Forward Available Balance (Optional, repeatable)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
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
    SwiftExtension,
)

logger = logging.getLogger(__name__)


@dataclass
class StatementLineData:
    """Parsed statement line (Field 61) data."""
    value_date: Optional[str] = None
    entry_date: Optional[str] = None
    dc_mark: Optional[str] = None  # C, D, RC, RD
    funds_code: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: Optional[str] = None
    identification_code: Optional[str] = None
    reference_account_owner: Optional[str] = None
    reference_account_servicer: Optional[str] = None
    supplementary_details: Optional[str] = None
    info_to_account_owner: Optional[str] = None  # From Field 86


class Mt940BlockParser:
    """Parser for SWIFT MT940 block format messages.

    Parses SWIFT MT940 Customer Statement messages according to SWIFT standards.
    Handles both native SWIFT block format and pre-parsed JSON input.
    """

    # Block patterns for SWIFT format
    BLOCK_PATTERN = re.compile(r'\{(\d):([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}')
    TAG_PATTERN = re.compile(r':(\d{2}[A-Z]?):([^\r\n:]+(?:\r?\n(?!:)[^\r\n:]*)*)', re.MULTILINE)

    # Statement line (Field 61) pattern
    # Format: YYMMDD[MMDD]DC[Funds Code]Amount,Transaction Type Identification Code Reference//Account Servicer Ref[Additional Info]
    STATEMENT_LINE_PATTERN = re.compile(
        r'^(\d{6})'              # Value date YYMMDD (mandatory)
        r'(\d{4})?'              # Entry date MMDD (optional)
        r'(R?[CD])'              # D/C mark (C, D, RC, RD)
        r'([A-Z])?'              # Funds code (optional, 3rd char of currency)
        r'([\d,]+)'              # Amount with comma as decimal
        r'([A-Z]\d{3})?'         # Transaction type + identification code (optional)
        r'(.{0,16})?'            # Reference for account owner (up to 16 chars)
        r'(?://(.{0,16}))?'      # Reference for account servicer (optional)
        r'(?:\n(.*))?'           # Supplementary details on next line
        , re.DOTALL
    )

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse MT940 message into structured dict.

        Args:
            raw_content: Raw MT940 message content (SWIFT block format or JSON)

        Returns:
            Dict with parsed message fields
        """
        result = {
            'messageType': 'MT940',
            'blocks': {},
            'statementLines': [],
            'parsedStatementLines': [],
        }

        # Handle dict input (already parsed)
        if isinstance(raw_content, dict):
            # Merge with defaults and ensure messageType
            for key, value in raw_content.items():
                result[key] = value
            result['messageType'] = raw_content.get('messageType', 'MT940')
            return result

        # Try JSON parsing first
        if raw_content.strip().startswith('{'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict):
                    for key, value in parsed.items():
                        result[key] = value
                    result['messageType'] = parsed.get('messageType', 'MT940')
                    return result
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
        """Parse Block 1: Basic Header.

        Format: F01BANKBEBBAXXX0000000000
        Position 0: Application ID (F=FIN)
        Position 1-2: Service ID (01)
        Position 3-14: Sender BIC (12 chars with optional XXX)
        """
        if len(content) >= 12:
            result['senderBic'] = content[3:15].strip() if len(content) >= 15 else content[3:].strip()

    def _parse_application_header(self, content: str, result: Dict):
        """Parse Block 2: Application Header.

        Output format (O): O940HHMMSSBANKBEBBAXXX0000000000YYMMDD...
        Input format (I): I940BANKBEBBXXXXN
        """
        if content.startswith('O'):
            result['messageType'] = content[1:4] if len(content) >= 4 else 'MT940'
            if len(content) >= 28:
                result['receiverBic'] = content[16:28].strip()
        elif content.startswith('I'):
            result['messageType'] = content[1:4] if len(content) >= 4 else 'MT940'
            if len(content) >= 16:
                result['receiverBic'] = content[4:16].strip()

    def _parse_text_block(self, content: str, result: Dict):
        """Parse Block 4: Text Block (Statement Content).

        Contains all statement fields:
        - :20: Transaction Reference
        - :21: Related Reference
        - :25: Account Identification
        - :28C: Statement Number/Sequence
        - :60F/M: Opening Balance
        - :61: Statement Lines
        - :86: Info to Account Owner
        - :62F/M: Closing Balance
        - :64: Closing Available Balance
        - :65: Forward Available Balance
        """
        line_count = 0
        current_statement_line = None

        for match in self.TAG_PATTERN.finditer(content):
            tag = match.group(1)
            value = match.group(2).strip()

            # Transaction Reference (Field 20 - Mandatory)
            if tag == '20':
                result['transactionReference'] = value

            # Related Reference (Field 21 - Optional)
            elif tag == '21':
                result['relatedReference'] = value

            # Account Identification (Field 25 - Mandatory)
            elif tag == '25':
                result['accountIdentification'] = value
                result['accountId'] = value  # Alias

            # Account with Party Identification (Field 25P - Alternative)
            elif tag == '25P':
                # Format: Account\nBIC
                lines = value.split('\n')
                result['accountIdentification'] = lines[0] if lines else value
                result['accountId'] = lines[0] if lines else value
                if len(lines) > 1:
                    result['accountOwnerBic'] = lines[1]

            # Statement Number/Sequence (Field 28C - Mandatory)
            elif tag == '28C':
                parts = value.split('/')
                result['statementNumber'] = parts[0] if parts else None
                result['sequenceNumber'] = parts[1] if len(parts) > 1 else None

            # Opening Balance (Field 60F or 60M - Mandatory)
            elif tag in ('60F', '60M'):
                result['openingBalanceType'] = 'F' if tag == '60F' else 'M'
                self._parse_balance(value, result, 'opening')

            # Statement Line (Field 61 - Optional, repeatable)
            elif tag == '61':
                line_count += 1
                result['statementLines'].append(value)
                current_statement_line = self._parse_statement_line(value)
                result['parsedStatementLines'].append(current_statement_line)

            # Information to Account Owner (Field 86 - Optional)
            elif tag == '86':
                if current_statement_line:
                    current_statement_line['infoToAccountOwner'] = value
                result['infoToAccountOwner'] = value  # Last one for summary

            # Closing Balance (Field 62F or 62M - Mandatory)
            elif tag in ('62F', '62M'):
                result['closingBalanceType'] = 'F' if tag == '62F' else 'M'
                self._parse_balance(value, result, 'closing')

            # Closing Available Balance (Field 64 - Optional)
            elif tag == '64':
                self._parse_balance(value, result, 'available')

            # Forward Available Balance (Field 65 - Optional, repeatable)
            elif tag == '65':
                if 'forwardBalances' not in result:
                    result['forwardBalances'] = []
                forward_balance = {}
                self._parse_balance(value, forward_balance, 'forward')
                result['forwardBalances'].append(forward_balance)

        result['numberOfLines'] = line_count

        # Extract first statement line details for Silver table
        if result['parsedStatementLines']:
            first_line = result['parsedStatementLines'][0]
            result['statementLinesValueDate'] = first_line.get('valueDate')
            result['statementLinesEntryDate'] = first_line.get('entryDate')
            result['statementLinesIndicator'] = first_line.get('dcMark')
            result['statementLinesFundsCode'] = first_line.get('fundsCode')
            result['statementLinesAmount'] = first_line.get('amount')
            result['statementLinesTransactionType'] = first_line.get('transactionType')
            result['statementLinesIdentificationCode'] = first_line.get('identificationCode')
            result['statementLinesReference'] = first_line.get('referenceAccountOwner')
            result['statementLinesReferenceAccountServicer'] = first_line.get('referenceAccountServicer')
            result['statementLinesSupplementaryDetails'] = first_line.get('supplementaryDetails')

        # Calculate derived fields from statement lines
        if result['parsedStatementLines']:
            total_credit = 0.0
            total_debit = 0.0
            credit_count = 0
            debit_count = 0
            for line in result['parsedStatementLines']:
                dc_mark = line.get('dcMark', '')
                amount = line.get('amount') or 0
                if dc_mark in ('C', 'RC'):
                    total_credit += amount
                    credit_count += 1
                elif dc_mark in ('D', 'RD'):
                    total_debit += amount
                    debit_count += 1
            result['totalCreditAmount'] = total_credit if credit_count > 0 else None
            result['totalCreditCount'] = credit_count if credit_count > 0 else None
            result['totalDebitAmount'] = total_debit if debit_count > 0 else None
            result['totalDebitCount'] = debit_count if debit_count > 0 else None

        # Set period dates from opening/closing balance dates
        result['periodStartDate'] = result.get('openingBalanceDate')
        result['periodEndDate'] = result.get('closingBalanceDate')

        # Extract first forward balance for Silver table (if present)
        if result.get('forwardBalances'):
            first_forward = result['forwardBalances'][0]
            result['forwardBalanceDate'] = first_forward.get('forwardBalanceDate')
            result['forwardBalanceCurrency'] = first_forward.get('forwardBalanceCurrency')
            result['forwardBalanceAmount'] = first_forward.get('forwardBalanceAmount')
            result['forwardBalanceIndicator'] = first_forward.get('forwardBalanceIndicator')

        # Parse info to account owner structured fields
        info = result.get('infoToAccountOwner', '')
        if info and '/' in info:
            # Structured format: /CODE/value
            parts = info.split('/')
            for i, part in enumerate(parts):
                if part and len(part) <= 4 and part.isupper():
                    result['infoAccountOwnerCode'] = part
                    if i + 1 < len(parts):
                        result['infoAccountOwnerReference'] = parts[i + 1]
                    break
            # Try to extract name from common patterns
            for part in parts:
                if len(part) > 10 and not part.isupper():
                    result['infoAccountOwnerName'] = part[:70]
                    break

    def _parse_balance(self, value: str, result: Dict, balance_type: str):
        """Parse balance field (60a, 62a, 64, or 65).

        Format: [D/C]YYMMDDCCCAMOUNT
        - D/C: Debit or Credit indicator (1 char)
        - YYMMDD: Date (6 chars)
        - CCC: Currency code (3 chars)
        - Amount: Decimal amount with comma
        """
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
            # Amount with comma as decimal separator
            # Remove any trailing block end marker (-) and whitespace
            amount_str = value[10:].replace(',', '.').strip().rstrip('-').strip()
            # Also remove any newlines or control characters
            amount_str = ''.join(c for c in amount_str if c.isdigit() or c == '.')
            try:
                result[f'{prefix}Amount'] = float(amount_str) if amount_str else None
            except ValueError:
                result[f'{prefix}Amount'] = None

    def _parse_statement_line(self, value: str) -> Dict[str, Any]:
        """Parse a single statement line (Field 61).

        Format: YYMMDD[MMDD][R]D/C[FundsCode]Amount,TransactionTypeIdRef[//ServicerRef][\nSuppl]

        Args:
            value: Raw Field 61 content

        Returns:
            Dict with parsed statement line fields
        """
        line_data = {
            'valueDate': None,
            'entryDate': None,
            'dcMark': None,
            'fundsCode': None,
            'amount': None,
            'transactionType': None,
            'identificationCode': None,
            'referenceAccountOwner': None,
            'referenceAccountServicer': None,
            'supplementaryDetails': None,
        }

        if not value:
            return line_data

        # Extract value date (YYMMDD) - always at start
        if len(value) >= 6:
            date_str = value[:6]
            try:
                year = int(date_str[:2])
                full_year = 2000 + year if year < 50 else 1900 + year
                line_data['valueDate'] = f"{full_year}-{date_str[2:4]}-{date_str[4:6]}"
            except ValueError:
                pass

        # Rest of parsing after date
        pos = 6

        # Check for entry date (MMDD) - optional
        if len(value) > pos + 4 and value[pos:pos+4].isdigit():
            line_data['entryDate'] = value[pos:pos+4]
            pos += 4

        # D/C Mark (C, D, RC, RD)
        if len(value) > pos:
            if value[pos:pos+2] in ('RC', 'RD'):
                line_data['dcMark'] = value[pos:pos+2]
                pos += 2
            elif value[pos] in ('C', 'D'):
                line_data['dcMark'] = value[pos]
                pos += 1

        # Funds code (optional single letter)
        if len(value) > pos and value[pos].isalpha() and not value[pos:pos+1].isdigit():
            line_data['fundsCode'] = value[pos]
            pos += 1

        # Amount (digits with comma)
        amount_match = re.match(r'([\d,]+)', value[pos:])
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '.')
            try:
                line_data['amount'] = float(amount_str)
            except ValueError:
                pass
            pos += len(amount_match.group(1))

        # Transaction type (S/N + 3 chars) and rest
        if len(value) > pos:
            remaining = value[pos:]

            # Transaction type is usually first char (S or N) + 3 char code
            if len(remaining) >= 4:
                line_data['transactionType'] = remaining[:1]
                line_data['identificationCode'] = remaining[1:4]
                remaining = remaining[4:]

            # Reference for account owner (up to // or newline)
            if '//' in remaining:
                ref_owner, rest = remaining.split('//', 1)
                line_data['referenceAccountOwner'] = ref_owner.strip()[:16]

                # Reference for account servicer
                if '\n' in rest:
                    ref_servicer, suppl = rest.split('\n', 1)
                    line_data['referenceAccountServicer'] = ref_servicer.strip()[:16]
                    line_data['supplementaryDetails'] = suppl.strip()[:34]
                else:
                    line_data['referenceAccountServicer'] = rest.strip()[:16]
            elif '\n' in remaining:
                ref_owner, suppl = remaining.split('\n', 1)
                line_data['referenceAccountOwner'] = ref_owner.strip()[:16]
                line_data['supplementaryDetails'] = suppl.strip()[:34]
            else:
                line_data['referenceAccountOwner'] = remaining.strip()[:16]

        return line_data


class Mt940Extractor(BaseExtractor):
    """Extractor for SWIFT MT940 Customer Statement messages.

    MT940 is a bank-to-customer statement message used for end-of-day
    account reconciliation. It contains opening/closing balances and
    detailed transaction entries.
    """

    MESSAGE_TYPE = "MT940"
    SILVER_TABLE = "stg_mt940"

    def __init__(self):
        """Initialize extractor with parser instance."""
        self.parser = Mt940BlockParser()

    # =========================================================================
    # PARSING
    # =========================================================================

    def parse(self, raw_content: Any) -> Dict[str, Any]:
        """Parse raw MT940 content into structured dict.

        Args:
            raw_content: Raw message content (SWIFT format, JSON, or dict)

        Returns:
            Parsed message dictionary
        """
        return self.parser.parse(raw_content)

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw MT940 content.

        Args:
            raw_content: Raw or pre-parsed message content
            batch_id: Processing batch identifier

        Returns:
            Dict with raw_id, message_type, raw_content, batch_id
        """
        # Parse if not already parsed
        if isinstance(raw_content, str):
            parsed = self.parser.parse(raw_content)
        else:
            parsed = raw_content

        # Generate message ID from transaction reference or statement number
        msg_id = (
            parsed.get('transactionReference') or
            parsed.get('statementNumber') or
            ''
        )

        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': json.dumps(parsed) if isinstance(parsed, dict) else str(parsed),
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
        """Extract all Silver layer fields from MT940 message.

        Maps all MT940 fields to Silver table columns per the silver_field_mappings.

        Args:
            msg_content: Parsed message content
            raw_id: Reference to Bronze record
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            Dict with all fields for stg_mt940 Silver table
        """
        trunc = self.trunc

        return {
            # Identity Fields
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Type
            'message_type': 'MT940',

            # Header Fields (Block 1 & 2)
            'sender_bic': trunc(msg_content.get('senderBic'), 12),
            'receiver_bic': trunc(msg_content.get('receiverBic'), 12),

            # Field 20 - Transaction Reference (Mandatory)
            'transaction_reference': trunc(msg_content.get('transactionReference'), 35),

            # Field 21 - Related Reference (Optional)
            'related_reference': trunc(msg_content.get('relatedReference'), 35),

            # Field 25 - Account Identification (Mandatory)
            'account_identification': trunc(msg_content.get('accountIdentification'), 35),

            # Field 25P/BIC - Account Owner BIC (Optional)
            'account_owner_bic': trunc(msg_content.get('accountOwnerBic'), 12),

            # Field 28C - Statement Number/Sequence (Mandatory)
            'statement_number': trunc(msg_content.get('statementNumber'), 10),
            'sequence_number': trunc(msg_content.get('sequenceNumber'), 10),

            # Field 60a - Opening Balance (Mandatory)
            'opening_balance_date': msg_content.get('openingBalanceDate'),
            'opening_balance_currency': trunc(msg_content.get('openingBalanceCurrency'), 3),
            'opening_balance_amount': msg_content.get('openingBalanceAmount'),
            'opening_balance_indicator': trunc(msg_content.get('openingBalanceIndicator'), 1),
            'opening_balance_type': trunc(msg_content.get('openingBalanceType'), 5),

            # Field 62a - Closing Balance (Mandatory)
            'closing_balance_date': msg_content.get('closingBalanceDate'),
            'closing_balance_currency': trunc(msg_content.get('closingBalanceCurrency'), 3),
            'closing_balance_amount': msg_content.get('closingBalanceAmount'),
            'closing_balance_indicator': trunc(msg_content.get('closingBalanceIndicator'), 1),
            'closing_balance_type': trunc(msg_content.get('closingBalanceType'), 5),

            # Field 64 - Closing Available Balance (Optional)
            'available_balance_date': msg_content.get('availableBalanceDate'),
            'available_balance_currency': trunc(msg_content.get('availableBalanceCurrency'), 3),
            'available_balance_amount': msg_content.get('availableBalanceAmount'),
            'available_balance_indicator': trunc(msg_content.get('availableBalanceIndicator'), 1),

            # Field 65 - Forward Available Balance (Optional)
            'forward_balance_date': msg_content.get('forwardBalanceDate'),
            'forward_balance_currency': trunc(msg_content.get('forwardBalanceCurrency'), 3),
            'forward_balance_amount': msg_content.get('forwardBalanceAmount'),
            'forward_balance_indicator': trunc(msg_content.get('forwardBalanceIndicator'), 1),

            # Field 86 - Information to Account Owner (Optional)
            'info_to_account_owner': trunc(msg_content.get('infoToAccountOwner'), 500),
            'info_account_owner_code': trunc(msg_content.get('infoAccountOwnerCode'), 20),
            'info_account_owner_name': trunc(msg_content.get('infoAccountOwnerName'), 100),
            'info_account_owner_reference': trunc(msg_content.get('infoAccountOwnerReference'), 50),

            # Statement Lines Summary
            'number_of_lines': msg_content.get('numberOfLines') or 0,

            # Processing Status
            'processing_status': 'RECEIVED',

            # Account ID (alias for account_identification)
            'account_id': trunc(msg_content.get('accountIdentification') or msg_content.get('accountId'), 50),

            # Message ID (generated or from transaction reference)
            'message_id': trunc(
                msg_content.get('messageId') or msg_content.get('transactionReference'),
                50
            ),

            # First Statement Line Details (Field 61)
            'statement_lines_value_date': msg_content.get('statementLinesValueDate'),
            'statement_lines_entry_date': trunc(msg_content.get('statementLinesEntryDate'), 10),
            'statement_lines_indicator': trunc(msg_content.get('statementLinesIndicator'), 2),
            'statement_lines_funds_code': trunc(msg_content.get('statementLinesFundsCode'), 5),
            'statement_lines_amount': msg_content.get('statementLinesAmount'),
            'statement_lines_transaction_type': trunc(msg_content.get('statementLinesTransactionType'), 10),
            'statement_lines_identification_code': trunc(msg_content.get('statementLinesIdentificationCode'), 10),
            'statement_lines_reference': trunc(msg_content.get('statementLinesReference'), 35),
            'statement_lines_reference_account_servicer': trunc(msg_content.get('statementLinesReferenceAccountServicer'), 35),
            'statement_lines_supplementary_details': trunc(msg_content.get('statementLinesSupplementaryDetails'), 70),

            # Derived Fields
            'period_start_date': msg_content.get('periodStartDate'),
            'period_end_date': msg_content.get('periodEndDate'),
            'total_credit_amount': msg_content.get('totalCreditAmount'),
            'total_credit_count': msg_content.get('totalCreditCount'),
            'total_debit_amount': msg_content.get('totalDebitAmount'),
            'total_debit_count': msg_content.get('totalDebitCount'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Matches exact columns in silver.stg_mt940 table.
        """
        return [
            # Identity fields
            'stg_id', 'raw_id', '_batch_id',
            # Message type
            'message_type',
            # Header
            'sender_bic', 'receiver_bic',
            # References
            'transaction_reference', 'related_reference',
            'account_identification', 'account_owner_bic',
            'statement_number', 'sequence_number',
            # Opening Balance
            'opening_balance_date', 'opening_balance_currency',
            'opening_balance_amount', 'opening_balance_indicator',
            'opening_balance_type',
            # Closing Balance
            'closing_balance_date', 'closing_balance_currency',
            'closing_balance_amount', 'closing_balance_indicator',
            'closing_balance_type',
            # Available Balance (Tag 64)
            'available_balance_date', 'available_balance_currency',
            'available_balance_amount', 'available_balance_indicator',
            # Forward Balance (Tag 65)
            'forward_balance_date', 'forward_balance_currency',
            'forward_balance_amount', 'forward_balance_indicator',
            # Info to Account Owner (Tag 86)
            'info_to_account_owner', 'info_account_owner_code',
            'info_account_owner_name', 'info_account_owner_reference',
            # Line Count
            'number_of_lines',
            # Status
            'processing_status',
            # Additional fields
            'account_id', 'message_id',
            # Statement Line fields (first line summary)
            'statement_lines_value_date', 'statement_lines_entry_date',
            'statement_lines_indicator', 'statement_lines_funds_code',
            'statement_lines_amount', 'statement_lines_transaction_type',
            'statement_lines_identification_code', 'statement_lines_reference',
            'statement_lines_reference_account_servicer',
            'statement_lines_supplementary_details',
            # Derived fields
            'period_start_date', 'period_end_date',
            'total_credit_amount', 'total_credit_count',
            'total_debit_amount', 'total_debit_count',
        ]

    def get_silver_values(self, silver_record: Dict[str, Any]) -> tuple:
        """Return ordered tuple of values for Silver table INSERT.

        Args:
            silver_record: Dict from extract_silver()

        Returns:
            Tuple of values in column order
        """
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
        """Extract Gold layer entities from MT940 Silver record.

        MT940 produces:
        - Account (statement account)
        - Financial Institutions (account servicer, message recipient)

        Note: MT940 is a statement, not a payment instruction, so it doesn't
        produce Party entities (debtor/creditor) like payment messages do.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier

        Returns:
            GoldEntities with extracted accounts and financial institutions
        """
        entities = GoldEntities()

        # Statement Account from Field 25
        account_id = silver_data.get('account_identification')
        if account_id:
            # Check if it's an IBAN (starts with 2 letters, 2 digits)
            iban = None
            if account_id and len(account_id) >= 4:
                if account_id[:2].isalpha() and account_id[2:4].isdigit():
                    iban = account_id

            entities.accounts.append(AccountData(
                account_number=account_id,
                iban=iban,
                role="STATEMENT_ACCOUNT",
                account_type='CACC',  # Current Account
                currency=silver_data.get('opening_balance_currency') or 'XXX',
            ))

        # Account Servicer (Sender) - the bank providing the statement
        sender_bic = silver_data.get('sender_bic')
        if sender_bic:
            # Extract country from BIC (positions 5-6)
            country = sender_bic[4:6] if len(sender_bic) >= 6 else 'XX'
            entities.financial_institutions.append(FinancialInstitutionData(
                role="ACCOUNT_SERVICER",
                bic=sender_bic,
                country=country,
            ))

        # Message Recipient (Receiver)
        receiver_bic = silver_data.get('receiver_bic')
        if receiver_bic:
            country = receiver_bic[4:6] if len(receiver_bic) >= 6 else 'XX'
            entities.financial_institutions.append(FinancialInstitutionData(
                role="MESSAGE_RECIPIENT",
                bic=receiver_bic,
                country=country,
            ))

        return entities

    def get_extension_data(self, silver_data: Dict[str, Any]) -> SwiftExtension:
        """Extract SWIFT extension data for MT940.

        Args:
            silver_data: Silver record dict

        Returns:
            SwiftExtension with MT940-specific fields
        """
        return SwiftExtension(
            swift_message_type='MT940',
            sender_bic=silver_data.get('sender_bic'),
            receiver_bic=silver_data.get('receiver_bic'),
        )


# Register the extractor with multiple aliases
_extractor = Mt940Extractor()
ExtractorRegistry.register('MT940', _extractor)
ExtractorRegistry.register('mt940', _extractor)
ExtractorRegistry.register('mt_940', _extractor)

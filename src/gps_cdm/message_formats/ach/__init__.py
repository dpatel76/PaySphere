"""NACHA ACH (Automated Clearing House) Extractor."""

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


class AchFixedWidthParser:
    """Parser for NACHA ACH fixed-width format messages."""

    # Record type definitions - each record is 94 characters
    RECORD_TYPES = {
        '1': 'file_header',
        '5': 'batch_header',
        '6': 'entry_detail',
        '7': 'addenda',
        '8': 'batch_control',
        '9': 'file_control',
    }

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse ACH fixed-width file into structured dict."""
        result = {
            'fileHeader': {},
            'batches': [],
            'fileControl': {},
        }

        lines = raw_content.strip().split('\n')
        current_batch = None
        current_entries = []
        current_addenda = []

        for line in lines:
            # Pad line to 94 chars if needed
            line = line.ljust(94)
            record_type = line[0]

            if record_type == '1':
                result['fileHeader'] = self._parse_file_header(line)
            elif record_type == '5':
                # Save previous batch if exists
                if current_batch:
                    current_batch['entries'] = current_entries
                    result['batches'].append(current_batch)
                current_batch = self._parse_batch_header(line)
                current_entries = []
            elif record_type == '6':
                entry = self._parse_entry_detail(line)
                entry['addenda'] = []
                current_entries.append(entry)
                current_addenda = entry['addenda']
            elif record_type == '7':
                addenda = self._parse_addenda(line)
                current_addenda.append(addenda)
            elif record_type == '8':
                if current_batch:
                    current_batch['control'] = self._parse_batch_control(line)
                    current_batch['entries'] = current_entries
                    result['batches'].append(current_batch)
                    current_batch = None
                    current_entries = []
            elif record_type == '9' and not line[1:].strip().replace('9', '') == '':
                result['fileControl'] = self._parse_file_control(line)

        # Handle incomplete file (no batch control) - save current batch if exists
        if current_batch and current_batch not in result['batches']:
            current_batch['entries'] = current_entries
            result['batches'].append(current_batch)

        # Convert to flat structure for first batch/entry (most common case)
        if result['batches']:
            batch = result['batches'][0]
            result.update(self._flatten_batch(batch, result['fileHeader']))

        return result

    def _parse_file_header(self, line: str) -> Dict[str, Any]:
        """Parse Record Type 1: File Header."""
        return {
            'recordType': line[0:1],
            'priorityCode': line[1:3],
            'immediateDestination': line[3:13].strip(),
            'immediateOrigin': line[13:23].strip(),
            'fileCreationDate': self._parse_date(line[23:29]),
            'fileCreationTime': line[29:33],
            'fileIdModifier': line[33:34],
            'recordSize': line[34:37],
            'blockingFactor': line[37:39],
            'formatCode': line[39:40],
            'immediateDestinationName': line[40:63].strip(),
            'immediateOriginName': line[63:86].strip(),
            'referenceCode': line[86:94].strip(),
        }

    def _parse_batch_header(self, line: str) -> Dict[str, Any]:
        """Parse Record Type 5: Batch Header."""
        return {
            'recordType': line[0:1],
            'serviceClassCode': line[1:4],
            'companyName': line[4:20].strip(),
            'companyDiscretionaryData': line[20:40].strip(),
            'companyIdentification': line[40:50].strip(),
            'standardEntryClassCode': line[50:53],
            'companyEntryDescription': line[53:63].strip(),
            'companyDescriptiveDate': line[63:69].strip(),
            'effectiveEntryDate': self._parse_date(line[69:75]),
            'settlementDate': line[75:78].strip(),
            'originatorStatusCode': line[78:79],
            'originatingDfiIdentification': line[79:87],
            'batchNumber': line[87:94].strip(),
        }

    def _parse_entry_detail(self, line: str) -> Dict[str, Any]:
        """Parse Record Type 6: Entry Detail."""
        # Amount is in cents (8 digits with 2 implied decimals)
        amount_str = line[29:39].strip()
        amount = float(amount_str) / 100 if amount_str else 0.0

        return {
            'recordType': line[0:1],
            'transactionCode': line[1:3],
            'receivingDfiIdentification': line[3:11],
            'checkDigit': line[11:12],
            'dfiAccountNumber': line[12:29].strip(),
            'amount': amount,
            'individualIdentificationNumber': line[39:54].strip(),
            'individualName': line[54:76].strip(),
            'discretionaryData': line[76:78].strip(),
            'addendaRecordIndicator': line[78:79],
            'traceNumber': line[79:94].strip(),
        }

    def _parse_addenda(self, line: str) -> Dict[str, Any]:
        """Parse Record Type 7: Addenda."""
        return {
            'recordType': line[0:1],
            'addendaTypeCode': line[1:3],
            'paymentRelatedInfo': line[3:83].strip(),
            'addendaSequenceNumber': line[83:87].strip(),
            'entryDetailSequenceNumber': line[87:94].strip(),
        }

    def _parse_batch_control(self, line: str) -> Dict[str, Any]:
        """Parse Record Type 8: Batch Control."""
        return {
            'recordType': line[0:1],
            'serviceClassCode': line[1:4],
            'entryAddendaCount': line[4:10].strip(),
            'entryHash': line[10:20].strip(),
            'totalDebitAmount': float(line[20:32].strip() or 0) / 100,
            'totalCreditAmount': float(line[32:44].strip() or 0) / 100,
            'companyIdentification': line[44:54].strip(),
            'messageAuthenticationCode': line[54:73].strip(),
            'reserved': line[73:79],
            'originatingDfiIdentification': line[79:87],
            'batchNumber': line[87:94].strip(),
        }

    def _parse_file_control(self, line: str) -> Dict[str, Any]:
        """Parse Record Type 9: File Control."""
        return {
            'recordType': line[0:1],
            'batchCount': line[1:7].strip(),
            'blockCount': line[7:13].strip(),
            'entryAddendaCount': line[13:21].strip(),
            'entryHash': line[21:31].strip(),
            'totalDebitAmount': float(line[31:43].strip() or 0) / 100,
            'totalCreditAmount': float(line[43:55].strip() or 0) / 100,
            'reserved': line[55:94].strip(),
        }

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse YYMMDD date to ISO format."""
        if not date_str or len(date_str) < 6:
            return None
        try:
            year = int(date_str[:2])
            # Handle Y2K: 00-49 = 2000s, 50-99 = 1900s
            full_year = 2000 + year if year < 50 else 1900 + year
            return f"{full_year}-{date_str[2:4]}-{date_str[4:6]}"
        except (ValueError, IndexError):
            return None

    def _flatten_batch(self, batch: Dict[str, Any], file_header: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten batch/entry structure for single-entry processing."""
        result = {}

        # Copy file header fields
        result['immediateDestination'] = file_header.get('immediateDestination')
        result['immediateOrigin'] = file_header.get('immediateOrigin')
        result['immediateDestinationName'] = file_header.get('immediateDestinationName')
        result['immediateOriginName'] = file_header.get('immediateOriginName')
        result['fileCreationDate'] = file_header.get('fileCreationDate')
        result['fileCreationTime'] = file_header.get('fileCreationTime')

        # Copy batch header fields
        result['companyName'] = batch.get('companyName')
        result['companyIdentification'] = batch.get('companyIdentification')
        result['standardEntryClassCode'] = batch.get('standardEntryClassCode')
        result['companyEntryDescription'] = batch.get('companyEntryDescription')
        result['effectiveEntryDate'] = batch.get('effectiveEntryDate')
        result['originatingDfiIdentification'] = batch.get('originatingDfiIdentification')
        result['batchNumber'] = batch.get('batchNumber')

        # Copy first entry fields
        entries = batch.get('entries', [])
        if entries:
            entry = entries[0]
            result['transactionCode'] = entry.get('transactionCode')
            result['receivingDfiIdentification'] = entry.get('receivingDfiIdentification')
            result['dfiAccountNumber'] = entry.get('dfiAccountNumber')
            result['amount'] = entry.get('amount')
            result['individualIdentificationNumber'] = entry.get('individualIdentificationNumber')
            result['individualName'] = entry.get('individualName')
            result['traceNumber'] = entry.get('traceNumber')

            # Copy addenda info
            addenda = entry.get('addenda', [])
            if addenda:
                result['paymentRelatedInfo'] = addenda[0].get('paymentRelatedInfo')

        # Copy batch control fields
        control = batch.get('control', {})
        result['totalDebitAmount'] = control.get('totalDebitAmount')
        result['totalCreditAmount'] = control.get('totalCreditAmount')
        result['entryAddendaCount'] = control.get('entryAddendaCount')

        return result


class AchExtractor(BaseExtractor):
    """Extractor for NACHA ACH messages.

    ACH requires subtype detection to route to appropriate ISO 20022 types:
    - Credit transactions → pacs.008
    - Debit transactions → pain.008
    - Returns → pacs.004
    - Bulk files → pain.001
    """

    MESSAGE_TYPE = "ACH"
    SILVER_TABLE = "stg_ach"

    def __init__(self):
        super().__init__()  # Initialize base class with routing support
        self.parser = AchFixedWidthParser()

    def _safe_int(self, value) -> int | None:
        """Safely convert value to integer, returning None if not convertible."""
        if value is None:
            return None
        try:
            # Handle string values like "0000001" from fixed-width parsing
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw ACH content."""
        msg_id = raw_content.get('traceNumber', '') or raw_content.get('batchNumber', '')
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
        """Extract all Silver layer fields from ACH message."""
        trunc = self.trunc
        parser = AchFixedWidthParser()

        # Handle raw text content - parse it first
        if isinstance(msg_content, dict) and '_raw_text' in msg_content:
            raw_text = msg_content['_raw_text']
            # ACH/NACHA format has fixed-width records starting with record type codes
            # Record type 1 = file header, 5 = batch header, 6 = entry detail
            lines = raw_text.strip().split('\n')
            if lines and lines[0] and lines[0][0] in '156789':
                parsed = parser.parse(raw_text)

                # If parser returned data, use it
                if parsed.get('immediateDestination') or parsed.get('companyName'):
                    msg_content = parsed
                else:
                    # NiFi may have split the file - check for pre-parsed headers
                    if 'file_header' in msg_content:
                        fh = parser._parse_file_header(msg_content['file_header'].ljust(94))
                        msg_content.update(fh)
                    if 'batch_header' in msg_content:
                        bh = parser._parse_batch_header(msg_content['batch_header'].ljust(94))
                        msg_content.update(bh)
                    # Parse entry detail from _raw_text (look for record type 6)
                    for line in lines:
                        if line and line[0] == '6':
                            ed = parser._parse_entry_detail(line.ljust(94))
                            msg_content.update(ed)
                            break

        # Also handle case where file_header/batch_header are provided without _raw_text parsing
        elif isinstance(msg_content, dict):
            if 'file_header' in msg_content and not msg_content.get('immediateDestination'):
                fh = parser._parse_file_header(msg_content['file_header'].ljust(94))
                msg_content.update(fh)
            if 'batch_header' in msg_content and not msg_content.get('companyName'):
                bh = parser._parse_batch_header(msg_content['batch_header'].ljust(94))
                msg_content.update(bh)

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # File Header (matching DB schema)
            'immediate_destination': trunc(msg_content.get('immediateDestination'), 10),
            'immediate_origin': trunc(msg_content.get('immediateOrigin'), 10),
            'file_creation_date': msg_content.get('fileCreationDate'),
            'file_creation_time': trunc(msg_content.get('fileCreationTime'), 4),

            # Batch Header
            'company_name': trunc(msg_content.get('companyName'), 16),
            'company_identification': trunc(msg_content.get('companyIdentification'), 10),
            'standard_entry_class': trunc(msg_content.get('standardEntryClassCode'), 3),
            'company_entry_description': trunc(msg_content.get('companyEntryDescription'), 10),
            'effective_entry_date': msg_content.get('effectiveEntryDate'),
            'originating_dfi_id': trunc(msg_content.get('originatingDfiIdentification'), 8),
            'batch_number': self._safe_int(msg_content.get('batchNumber')),

            # Entry Detail
            'transaction_code': trunc(msg_content.get('transactionCode'), 2),
            'receiving_dfi_id': trunc(msg_content.get('receivingDfiIdentification'), 8),
            'receiving_dfi_account': trunc(msg_content.get('dfiAccountNumber'), 17),
            'amount': msg_content.get('amount'),
            'individual_id': trunc(msg_content.get('individualIdentificationNumber'), 15),
            'individual_name': trunc(msg_content.get('individualName'), 22),
            'trace_number': trunc(msg_content.get('traceNumber'), 15),

            # Addenda
            'addenda_info': trunc(msg_content.get('paymentRelatedInfo'), 80),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            'immediate_destination', 'immediate_origin',
            'file_creation_date', 'file_creation_time',
            'company_name', 'company_identification',
            'standard_entry_class', 'company_entry_description',
            'effective_entry_date', 'originating_dfi_id', 'batch_number',
            'transaction_code', 'receiving_dfi_id', 'receiving_dfi_account',
            'amount', 'individual_id', 'individual_name', 'trace_number',
            'addenda_info',
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
        """Extract Gold layer entities from ACH Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Originator (Company = Debtor for credits, Creditor for debits)
        if silver_data.get('company_name'):
            # Transaction codes: 22, 23, 24 = credit, 27, 28, 29 = debit
            tx_code = silver_data.get('transaction_code') or ''
            is_credit = tx_code in ['22', '23', '24', '32', '33', '34']

            entities.parties.append(PartyData(
                name=silver_data.get('company_name'),
                role="DEBTOR" if is_credit else "CREDITOR",
                party_type='ORGANIZATION',
                identification_type='EIN',
                identification_number=silver_data.get('company_identification'),
            ))

        # Receiver (Individual)
        if silver_data.get('individual_name'):
            tx_code = silver_data.get('transaction_code') or ''
            is_credit = tx_code in ['22', '23', '24', '32', '33', '34']

            entities.parties.append(PartyData(
                name=silver_data.get('individual_name'),
                role="CREDITOR" if is_credit else "DEBTOR",
                party_type='INDIVIDUAL',
                identification_number=silver_data.get('individual_id'),
            ))

        # Receiver Account
        if silver_data.get('receiving_dfi_account'):
            tx_code = silver_data.get('transaction_code') or ''
            is_credit = tx_code in ['22', '23', '24', '32', '33', '34']
            account_type = 'CHECKING'
            if tx_code and tx_code[0] == '3':
                account_type = 'SAVINGS'

            entities.accounts.append(AccountData(
                account_number=silver_data.get('receiving_dfi_account'),
                role="CREDITOR" if is_credit else "DEBTOR",
                account_type=account_type,
                currency='USD',
            ))

        # Originating DFI (Debtor Agent)
        if silver_data.get('originating_dfi_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('immediate_origin'),
                clearing_code=silver_data.get('originating_dfi_id'),
                clearing_system='USABA',
                country='US',
            ))

        # Receiving DFI (Creditor Agent)
        if silver_data.get('receiving_dfi_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('immediate_destination'),
                clearing_code=silver_data.get('receiving_dfi_id'),
                clearing_system='USABA',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('ACH', AchExtractor())
ExtractorRegistry.register('ach', AchExtractor())
ExtractorRegistry.register('NACHA', AchExtractor())

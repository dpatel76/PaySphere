"""CHAPS (Clearing House Automated Payment System) Extractor - UK Real-Time Gross Settlement."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import xml.etree.ElementTree as ET
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


class ChapsSwiftParser:
    """Parser for CHAPS SWIFT block format messages (MT103-like)."""

    BLOCK_PATTERN = re.compile(r'\{(\d):([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}')
    TAG_PATTERN = re.compile(r':(\d{2}[A-Z]?):([^\r\n:]+(?:\r?\n(?!:)[^\r\n:]*)*)', re.MULTILINE)

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse CHAPS SWIFT block message into structured dict."""
        result = {
            'messageType': 'CHAPS',
        }

        # Handle JSON input (pre-parsed)
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{') and not raw_content.strip().startswith('{1:'):
            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and 'messageType' not in parsed:
                    parsed['messageType'] = 'CHAPS'
                return parsed
            except json.JSONDecodeError:
                pass

        # Parse SWIFT block format
        for match in self.BLOCK_PATTERN.finditer(raw_content):
            block_num = match.group(1)
            block_content = match.group(2)

            if block_num == '1':
                self._parse_basic_header(block_content, result)
            elif block_num == '2':
                self._parse_application_header(block_content, result)
            elif block_num == '3':
                self._parse_user_header(block_content, result)
            elif block_num == '4':
                self._parse_text_block(block_content, result)

        return result

    def _parse_basic_header(self, content: str, result: Dict):
        """Parse Block 1: Basic Header."""
        if len(content) >= 12:
            result['debtorAgentBic'] = content[3:15].strip() if len(content) >= 15 else content[3:].strip()

    def _parse_application_header(self, content: str, result: Dict):
        """Parse Block 2: Application Header."""
        if content.startswith('O'):
            if len(content) >= 28:
                result['creditorAgentBic'] = content[16:28].strip()

    def _parse_user_header(self, content: str, result: Dict):
        """Parse Block 3: User Header."""
        # Extract {108:value} for message reference
        match = re.search(r'\{108:([^}]+)\}', content)
        if match:
            result['messageId'] = match.group(1)

    def _parse_text_block(self, content: str, result: Dict):
        """Parse Block 4: Text Block (CHAPS Fields)."""
        for match in self.TAG_PATTERN.finditer(content):
            tag = match.group(1)
            value = match.group(2).strip()

            # Transaction Reference (Field 20)
            if tag == '20':
                result['instructionId'] = value
                if not result.get('messageId'):
                    result['messageId'] = value

            # Bank Operation Code (Field 23B)
            elif tag == '23B':
                result['bankOperationCode'] = value

            # Value Date/Currency/Amount (Field 32A)
            elif tag == '32A':
                self._parse_value_date_amount(value, result)

            # Instructed Amount (Field 33B)
            elif tag == '33B':
                if len(value) >= 4:
                    result['currency'] = value[:3]

            # Ordering Customer (Field 50K)
            elif tag in ('50K', '50A', '50F'):
                self._parse_party(value, result, 'debtor')

            # Ordering Institution (Field 52A)
            elif tag in ('52A', '52D'):
                bic = self._extract_bic(value)
                if bic:
                    result['debtorAgentBic'] = bic

            # Beneficiary Customer (Field 59)
            elif tag in ('59', '59A', '59F'):
                self._parse_party(value, result, 'creditor')

            # Beneficiary Institution (Field 57A)
            elif tag in ('57A', '57D'):
                bic = self._extract_bic(value)
                if bic:
                    result['creditorAgentBic'] = bic

            # Remittance Information (Field 70)
            elif tag == '70':
                result['remittanceInfo'] = value.replace('\n', ' ')

            # Details of Charges (Field 71A)
            elif tag == '71A':
                result['chargeBearer'] = value

            # Sender to Receiver Info (Field 72)
            elif tag == '72':
                result['senderToReceiverInfo'] = value.replace('\n', ' ')

    def _parse_value_date_amount(self, value: str, result: Dict):
        """Parse tag 32A: YYMMDDCCCAMOUNT"""
        if len(value) >= 6:
            date_str = value[:6]
            try:
                year = int(date_str[:2])
                full_year = 2000 + year if year < 50 else 1900 + year
                result['settlementDate'] = f"{full_year}-{date_str[2:4]}-{date_str[4:6]}"
            except ValueError:
                pass

        if len(value) >= 9:
            result['currency'] = value[6:9]

        if len(value) > 9:
            amount_str = value[9:].replace(',', '.')
            try:
                result['amount'] = float(amount_str)
            except ValueError:
                pass

    def _parse_party(self, value: str, result: Dict, party_type: str):
        """Parse party field (50 or 59) with full address extraction.

        SWIFT MT format for field 50K/59:
        Line 1: /account_number (optional)
        Line 2: Party name
        Line 3: Street address
        Line 4: City + Post code
        Line 5: Country
        """
        lines = [line.strip() for line in value.split('\n') if line.strip()]
        address_lines = []

        for i, line in enumerate(lines):
            if i == 0 and line.startswith('/'):
                # Account number on first line
                result[f'{party_type}Account'] = line[1:].split('\n')[0][:34]
                # Extract sort code from UK IBAN format /GBNNSSSSSSNNNNNNNN
                if line.startswith('/GB') and len(line) >= 10:
                    result[f'{party_type}SortCode'] = line[5:11]
            elif f'{party_type}Name' not in result:
                # First non-account line is the name
                result[f'{party_type}Name'] = line[:140]
            else:
                # Remaining lines are address
                address_lines.append(line)

        # Parse address lines
        if address_lines:
            # Full combined address
            result[f'{party_type}Address'] = ', '.join(address_lines)

            # Street address (first address line)
            if len(address_lines) >= 1:
                result[f'{party_type}StreetName'] = address_lines[0][:70]

            # City/Town and Post code (second address line typically has "CITY POSTCODE")
            if len(address_lines) >= 2:
                city_line = address_lines[1]
                # Try to extract post code (UK format: letter(s) + number(s) + space + number + letters)
                import re
                uk_postcode = re.search(r'([A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})', city_line)
                if uk_postcode:
                    result[f'{party_type}PostCode'] = uk_postcode.group(1)
                    result[f'{party_type}TownName'] = city_line[:city_line.find(uk_postcode.group(1))].strip()
                else:
                    result[f'{party_type}TownName'] = city_line[:35]

            # Country (last address line if it looks like a country name)
            if len(address_lines) >= 3:
                country_line = address_lines[-1].upper()
                # Map common country names to ISO codes
                country_map = {
                    'UNITED KINGDOM': 'GB', 'UK': 'GB', 'GREAT BRITAIN': 'GB', 'ENGLAND': 'GB',
                    'UNITED STATES': 'US', 'USA': 'US', 'AMERICA': 'US',
                    'GERMANY': 'DE', 'DEUTSCHLAND': 'DE',
                    'FRANCE': 'FR', 'SPAIN': 'ES', 'ITALY': 'IT', 'NETHERLANDS': 'NL',
                    'BELGIUM': 'BE', 'SWITZERLAND': 'CH', 'IRELAND': 'IE',
                    'AUSTRALIA': 'AU', 'CANADA': 'CA', 'JAPAN': 'JP', 'CHINA': 'CN',
                }
                result[f'{party_type}Country'] = country_map.get(country_line, country_line[:2])

    def _extract_bic(self, value: str) -> Optional[str]:
        """Extract BIC from field value."""
        lines = value.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) >= 8 and line[:8].isalnum():
                return line[:11] if len(line) >= 11 else line[:8]
        return None


class ChapsXmlParser:
    """Parser for CHAPS ISO 20022 XML messages."""

    NS_PATTERN = re.compile(r'\{[^}]+\}')

    def _strip_ns(self, tag: str) -> str:
        """Remove namespace from XML tag."""
        return self.NS_PATTERN.sub('', tag)

    def _find(self, element: ET.Element, path: str) -> Optional[ET.Element]:
        """Find element using local names (ignoring namespaces)."""
        if element is None:
            return None
        parts = path.split('/')
        current = element
        for part in parts:
            found = None
            for child in current:
                if self._strip_ns(child.tag) == part:
                    found = child
                    break
            if found is None:
                return None
            current = found
        return current

    def _find_text(self, element: ET.Element, path: str) -> Optional[str]:
        """Find element text using local names."""
        elem = self._find(element, path)
        return elem.text if elem is not None else None

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse CHAPS message content."""
        # Handle JSON input
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Parse XML
        try:
            if raw_content.startswith('\ufeff'):
                raw_content = raw_content[1:]
            root = ET.fromstring(raw_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse CHAPS XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        return self._parse_iso20022(root)

    def _parse_iso20022(self, root: ET.Element) -> Dict[str, Any]:
        """Parse CHAPS ISO 20022 structure."""
        result = {'isChaps': True}

        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')
        if fi_transfer is None:
            if self._strip_ns(root.tag) == 'FIToFICstmrCdtTrf':
                fi_transfer = root

        if fi_transfer is None:
            return result

        # Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['settlementMethod'] = self._find_text(grp_hdr, 'SttlmInf/SttlmMtd')
            result['settlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')

        # Credit Transfer Transaction
        cdt_trf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf is not None:
            result.update(self._parse_transaction(cdt_trf))

        return result

    def _parse_transaction(self, tx: ET.Element) -> Dict[str, Any]:
        """Parse credit transfer transaction."""
        result = {}

        # Payment ID
        pmt_id = self._find(tx, 'PmtId')
        if pmt_id is not None:
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Amount
        result['amount'] = self._safe_decimal(self._find_text(tx, 'IntrBkSttlmAmt'))
        result['currency'] = self._find_attr(tx, 'IntrBkSttlmAmt', 'Ccy') or 'GBP'

        # Debtor
        dbtr = self._find(tx, 'Dbtr')
        if dbtr is not None:
            result['debtorName'] = self._find_text(dbtr, 'Nm')
            result['debtorAddress'] = self._find_text(dbtr, 'PstlAdr/AdrLine')

        dbtr_acct = self._find(tx, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorAccount'] = self._find_text(dbtr_acct, 'Id/Othr/Id')
            result['debtorSortCode'] = self._find_text(dbtr_acct, 'Id/Othr/SchmeNm/Cd')

        dbtr_agt = self._find(tx, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgentBic'] = self._find_text(dbtr_agt, 'FinInstnId/BICFI')
            result['debtorSortCode'] = result.get('debtorSortCode') or self._find_text(dbtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Creditor
        cdtr = self._find(tx, 'Cdtr')
        if cdtr is not None:
            result['creditorName'] = self._find_text(cdtr, 'Nm')
            result['creditorAddress'] = self._find_text(cdtr, 'PstlAdr/AdrLine')

        cdtr_acct = self._find(tx, 'CdtrAcct')
        if cdtr_acct is not None:
            result['creditorAccount'] = self._find_text(cdtr_acct, 'Id/Othr/Id')
            result['creditorSortCode'] = self._find_text(cdtr_acct, 'Id/Othr/SchmeNm/Cd')

        cdtr_agt = self._find(tx, 'CdtrAgt')
        if cdtr_agt is not None:
            result['creditorAgentBic'] = self._find_text(cdtr_agt, 'FinInstnId/BICFI')
            result['creditorSortCode'] = result.get('creditorSortCode') or self._find_text(cdtr_agt, 'FinInstnId/ClrSysMmbId/MmbId')

        # Remittance Info
        result['remittanceInfo'] = self._find_text(tx, 'RmtInf/Ustrd')

        return result

    def _find_attr(self, element: ET.Element, path: str, attr: str) -> Optional[str]:
        """Find element attribute."""
        elem = self._find(element, path)
        return elem.get(attr) if elem is not None else None

    def _safe_decimal(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to decimal."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class ChapsExtractor(BaseExtractor):
    """Extractor for CHAPS payment messages."""

    MESSAGE_TYPE = "CHAPS"
    SILVER_TABLE = "stg_chaps"

    def __init__(self):
        self.swift_parser = ChapsSwiftParser()
        self.xml_parser = ChapsXmlParser()
        # Set parser attribute for zone_tasks.py compatibility - use self as the parser
        # since ChapsExtractor.parse() auto-detects format (XML vs SWIFT MT)
        self.parser = self

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse raw CHAPS content - auto-detect SWIFT MT vs XML format."""
        if isinstance(raw_content, dict):
            return raw_content

        content = raw_content.strip() if isinstance(raw_content, str) else str(raw_content)

        # Auto-detect format
        if content.startswith('{1:') or content.startswith('{2:'):
            # SWIFT MT block format
            return self.swift_parser.parse(content)
        elif content.startswith('<') or content.startswith('<?xml'):
            # XML format
            return self.xml_parser.parse(content)
        elif content.startswith('{'):
            # JSON format - try to parse
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

        # Default to SWIFT parser
        return self.swift_parser.parse(content)

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw CHAPS content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('instructionId', '')
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
        """Extract all Silver layer fields from CHAPS message."""
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header
            'message_type': 'CHAPS',
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'settlement_date': msg_content.get('settlementDate'),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or 'GBP',

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_address': msg_content.get('debtorAddress'),
            'debtor_sort_code': trunc(msg_content.get('debtorSortCode'), 10),
            'debtor_account': trunc(msg_content.get('debtorAccount'), 34),  # IBAN max length
            'debtor_agent_bic': trunc(msg_content.get('debtorAgentBic'), 11),
            'debtor_street_name': trunc(msg_content.get('debtorStreetName'), 70),
            'debtor_town_name': trunc(msg_content.get('debtorTownName'), 35),
            'debtor_post_code': trunc(msg_content.get('debtorPostCode'), 16),
            'debtor_country': trunc(msg_content.get('debtorCountry'), 2) or 'GB',

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_address': msg_content.get('creditorAddress'),
            'creditor_sort_code': trunc(msg_content.get('creditorSortCode'), 10),
            'creditor_account': trunc(msg_content.get('creditorAccount'), 34),  # IBAN max length
            'creditor_agent_bic': trunc(msg_content.get('creditorAgentBic'), 11),
            'creditor_street_name': trunc(msg_content.get('creditorStreetName'), 70),
            'creditor_town_name': trunc(msg_content.get('creditorTownName'), 35),
            'creditor_post_code': trunc(msg_content.get('creditorPostCode'), 16),
            'creditor_country': trunc(msg_content.get('creditorCountry'), 2) or 'GB',

            # Payment IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'uetr': msg_content.get('uetr'),
            'senders_reference': trunc(msg_content.get('senders_reference') or msg_content.get('instructionId'), 35),
            # value_date is VARCHAR(8) for YYYYMMDD format - strip hyphens from ISO date
            'value_date': (msg_content.get('settlementDate') or '').replace('-', '')[:8] or None,

            # Remittance
            'remittance_info': msg_content.get('remittanceInfo'),

            # Processing status
            'processing_status': 'PENDING',
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        MUST match silver.stg_chaps table columns exactly.
        """
        return [
            'stg_id', 'raw_id', '_batch_id',
            'message_type', 'message_id', 'creation_date_time',
            'settlement_date', 'settlement_method',
            'amount', 'currency',
            'debtor_name', 'debtor_address', 'debtor_sort_code',
            'debtor_account', 'debtor_agent_bic',
            'debtor_street_name', 'debtor_town_name', 'debtor_post_code', 'debtor_country',
            'creditor_name', 'creditor_address', 'creditor_sort_code',
            'creditor_account', 'creditor_agent_bic',
            'creditor_street_name', 'creditor_town_name', 'creditor_post_code', 'creditor_country',
            'instruction_id', 'end_to_end_id', 'uetr',
            'senders_reference', 'value_date',
            'remittance_info', 'processing_status',
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
        """Extract Gold layer entities from CHAPS Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Debtor Party - uses Silver column names with full address details
        if silver_data.get('debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('debtor_name'),
                role="DEBTOR",
                party_type='INDIVIDUAL',  # Assume individual for CHAPS
                street_name=silver_data.get('debtor_street_name'),
                post_code=silver_data.get('debtor_post_code'),
                town_name=silver_data.get('debtor_town_name'),
                country=silver_data.get('debtor_country') or 'GB',
            ))

        # Creditor Party with full address details
        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='INDIVIDUAL',
                street_name=silver_data.get('creditor_street_name'),
                post_code=silver_data.get('creditor_post_code'),
                town_name=silver_data.get('creditor_town_name'),
                country=silver_data.get('creditor_country') or 'GB',
            ))

        # Debtor Account - detect if IBAN
        if silver_data.get('debtor_account'):
            acct = silver_data.get('debtor_account')
            is_iban = acct.startswith('GB') and len(acct) >= 22
            entities.accounts.append(AccountData(
                account_number=acct,
                role="DEBTOR",
                iban=acct if is_iban else None,
                account_type='CACC',
                currency=silver_data.get('currency') or 'GBP',
            ))

        # Creditor Account
        if silver_data.get('creditor_account'):
            acct = silver_data.get('creditor_account')
            is_iban = acct.startswith('GB') and len(acct) >= 22
            entities.accounts.append(AccountData(
                account_number=acct,
                role="CREDITOR",
                iban=acct if is_iban else None,
                account_type='CACC',
                currency=silver_data.get('currency') or 'GBP',
            ))

        # Debtor Agent - generate institution name from BIC
        if silver_data.get('debtor_agent_bic') or silver_data.get('debtor_sort_code'):
            bic = silver_data.get('debtor_agent_bic')
            sort_code = silver_data.get('debtor_sort_code')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=f"FI_{bic}" if bic else f"FI_SC_{sort_code}",
                bic=bic,
                clearing_code=sort_code,
                clearing_system='GBDSC',  # UK Domestic Sort Code
                country='GB',
            ))

        # Creditor Agent
        if silver_data.get('creditor_agent_bic') or silver_data.get('creditor_sort_code'):
            bic = silver_data.get('creditor_agent_bic')
            sort_code = silver_data.get('creditor_sort_code')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=f"FI_{bic}" if bic else f"FI_SC_{sort_code}",
                bic=bic,
                clearing_code=sort_code,
                clearing_system='GBDSC',
                country='GB',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('CHAPS', ChapsExtractor())
ExtractorRegistry.register('chaps', ChapsExtractor())

"""TCH RTP (Real-Time Payments) Extractor - based on pacs.008."""

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


class RtpXmlParser:
    """Parser for TCH RTP XML messages (pacs.008 variant)."""

    NS_PATTERN = re.compile(r'\{[^}]+\}')

    def __init__(self):
        self.ns = {}

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

    def _find_attr(self, element: ET.Element, path: str, attr: str) -> Optional[str]:
        """Find element attribute."""
        elem = self._find(element, path)
        return elem.get(attr) if elem is not None else None

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse RTP XML content into structured dict."""
        try:
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]

            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse RTP XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        # Find the main content element (FIToFICstmrCdtTrf for pacs.008)
        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')
        if fi_transfer is None:
            if self._strip_ns(root.tag) == 'FIToFICstmrCdtTrf':
                fi_transfer = root
            else:
                raise ValueError("Cannot find FIToFICstmrCdtTrf element in RTP message")

        return self._parse_fi_transfer(fi_transfer)

    def _parse_fi_transfer(self, fi_transfer: ET.Element) -> Dict[str, Any]:
        """Parse FIToFICstmrCdtTrf element."""
        result = {'isRtp': True}

        # Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))

            # Settlement Information
            sttlm_inf = self._find(grp_hdr, 'SttlmInf')
            if sttlm_inf is not None:
                result['settlementMethod'] = self._find_text(sttlm_inf, 'SttlmMtd')
                result['clearingSystem'] = self._find_text(sttlm_inf, 'ClrSys/Cd')

        # Credit Transfer Transaction Information
        cdt_trf_tx_inf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf_tx_inf is not None:
            result.update(self._parse_transaction(cdt_trf_tx_inf))

        return result

    def _parse_transaction(self, tx_inf: ET.Element) -> Dict[str, Any]:
        """Parse CdtTrfTxInf element."""
        result = {}

        # Payment ID
        pmt_id = self._find(tx_inf, 'PmtId')
        if pmt_id is not None:
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['transactionId'] = self._find_text(pmt_id, 'TxId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Amounts
        result['interbankSettlementAmount'] = self._safe_decimal(self._find_text(tx_inf, 'IntrBkSttlmAmt'))
        result['interbankSettlementCurrency'] = self._find_attr(tx_inf, 'IntrBkSttlmAmt', 'Ccy')
        result['instructedAmount'] = self._safe_decimal(self._find_text(tx_inf, 'InstdAmt'))
        result['instructedCurrency'] = self._find_attr(tx_inf, 'InstdAmt', 'Ccy')

        # Settlement Date
        result['interbankSettlementDate'] = self._find_text(tx_inf, 'IntrBkSttlmDt')

        # Charge Bearer
        result['chargeBearer'] = self._find_text(tx_inf, 'ChrgBr')

        # Debtor Agent (RTN)
        dbtr_agt = self._find(tx_inf, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgent'] = self._parse_agent(dbtr_agt)

        # Debtor
        dbtr = self._find(tx_inf, 'Dbtr')
        if dbtr is not None:
            result['debtor'] = self._parse_party(dbtr)

        # Debtor Account
        dbtr_acct = self._find(tx_inf, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorAccount'] = self._parse_account(dbtr_acct)

        # Creditor Agent (RTN)
        cdtr_agt = self._find(tx_inf, 'CdtrAgt')
        if cdtr_agt is not None:
            result['creditorAgent'] = self._parse_agent(cdtr_agt)

        # Creditor
        cdtr = self._find(tx_inf, 'Cdtr')
        if cdtr is not None:
            result['creditor'] = self._parse_party(cdtr)

        # Creditor Account
        cdtr_acct = self._find(tx_inf, 'CdtrAcct')
        if cdtr_acct is not None:
            result['creditorAccount'] = self._parse_account(cdtr_acct)

        # Purpose
        purp = self._find(tx_inf, 'Purp')
        if purp is not None:
            result['purposeCode'] = self._find_text(purp, 'Cd')

        # Remittance Information
        rmt_inf = self._find(tx_inf, 'RmtInf')
        if rmt_inf is not None:
            result['remittanceInformation'] = {
                'unstructured': self._find_text(rmt_inf, 'Ustrd')
            }

        return result

    def _parse_party(self, party_elem: ET.Element) -> Dict[str, Any]:
        """Parse party element."""
        result = {
            'name': self._find_text(party_elem, 'Nm')
        }

        # Postal Address
        pstl_adr = self._find(party_elem, 'PstlAdr')
        if pstl_adr is not None:
            result['streetName'] = self._find_text(pstl_adr, 'StrtNm')
            result['postalCode'] = self._find_text(pstl_adr, 'PstCd')
            result['townName'] = self._find_text(pstl_adr, 'TwnNm')
            result['countrySubDivision'] = self._find_text(pstl_adr, 'CtrySubDvsn')
            result['country'] = self._find_text(pstl_adr, 'Ctry')

        return result

    def _parse_account(self, acct_elem: ET.Element) -> Dict[str, Any]:
        """Parse account element - RTP uses account numbers, not IBAN."""
        result = {}

        acct_id = self._find(acct_elem, 'Id')
        if acct_id is not None:
            # RTP uses Othr/Id for account numbers
            result['accountNumber'] = self._find_text(acct_id, 'Othr/Id')

        return result

    def _parse_agent(self, agt_elem: ET.Element) -> Dict[str, Any]:
        """Parse agent element - RTN for RTP."""
        result = {}

        fin_instn_id = self._find(agt_elem, 'FinInstnId')
        if fin_instn_id is not None:
            # RTP uses ClrSysMmbId/MmbId for RTN
            result['memberId'] = self._find_text(fin_instn_id, 'ClrSysMmbId/MmbId')
            result['clearingSystem'] = 'RTP'

        return result

    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Safely convert string to int."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_decimal(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to decimal."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class RtpExtractor(BaseExtractor):
    """Extractor for TCH RTP messages."""

    MESSAGE_TYPE = "RTP"
    SILVER_TABLE = "stg_rtp"

    def __init__(self):
        self.parser = RtpXmlParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw RTP content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('transactionId', '')
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
        """Extract all Silver layer fields from RTP message."""
        trunc = self.trunc

        # Handle raw text content - parse it first
        if isinstance(msg_content, dict) and '_raw_text' in msg_content:
            raw_text = msg_content['_raw_text']
            # RTP is XML-based (pacs.008 variant)
            if raw_text.strip().startswith('<?xml') or raw_text.strip().startswith('<'):
                parser = RtpXmlParser()
                msg_content = parser.parse(raw_text)

        # Extract nested objects
        debtor = msg_content.get('debtor', {})
        debtor_account = msg_content.get('debtorAccount', {})
        debtor_agent = msg_content.get('debtorAgent', {})
        creditor = msg_content.get('creditor', {})
        creditor_account = msg_content.get('creditorAccount', {})
        creditor_agent = msg_content.get('creditorAgent', {})
        remittance_info = msg_content.get('remittanceInformation', {})

        # Get account number and RTN values
        debtor_acct_num = trunc(debtor_account.get('accountNumber'), 34)
        creditor_acct_num = trunc(creditor_account.get('accountNumber'), 34)
        debtor_rtn = trunc(debtor_agent.get('memberId'), 9)
        creditor_rtn = trunc(creditor_agent.get('memberId'), 9)

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header (matching DB schema)
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Payment Identification
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),
            'clearing_system_reference': msg_content.get('clearingSystemReference'),

            # Amounts
            'instructed_amount': msg_content.get('instructedAmount') or msg_content.get('interbankSettlementAmount'),
            'instructed_currency': msg_content.get('instructedCurrency') or msg_content.get('interbankSettlementCurrency') or 'USD',

            # Debtor (matching DB columns)
            'debtor_name': trunc(debtor.get('name'), 140),
            'debtor_account': debtor_acct_num,
            'debtor_agent_id': debtor_rtn,
            'debtor_account_number': debtor_acct_num,  # Alternate column
            'debtor_routing_number': debtor_rtn,  # Alternate column

            # Creditor (matching DB columns)
            'creditor_name': trunc(creditor.get('name'), 140),
            'creditor_account': creditor_acct_num,
            'creditor_agent_id': creditor_rtn,
            'creditor_account_number': creditor_acct_num,  # Alternate column
            'creditor_routing_number': creditor_rtn,  # Alternate column

            # Purpose
            'purpose_code': msg_content.get('purposeCode'),

            # Remittance Information
            'remittance_info': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Column order matches silver.stg_rtp table schema.
        """
        return [
            'stg_id', 'raw_id', '_batch_id',
            'msg_id', 'creation_date_time',
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr',
            'clearing_system_reference',
            'instructed_amount', 'instructed_currency',
            'debtor_name', 'debtor_account', 'debtor_agent_id',
            'debtor_account_number', 'debtor_routing_number',
            'creditor_name', 'creditor_account', 'creditor_agent_id',
            'creditor_account_number', 'creditor_routing_number',
            'purpose_code', 'remittance_info',
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
        """Extract Gold layer entities from RTP Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Debtor Party - uses Silver column names
        if silver_data.get('debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('debtor_name'),
                role="DEBTOR",
                party_type='UNKNOWN',
            ))

        # Creditor Party
        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='UNKNOWN',
            ))

        # Debtor Account
        if silver_data.get('debtor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debtor_account'),
                role="DEBTOR",
                account_type='CACC',
                currency=silver_data.get('instructed_currency') or 'USD',
            ))

        # Creditor Account
        if silver_data.get('creditor_account'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('creditor_account'),
                role="CREDITOR",
                account_type='CACC',
                currency=silver_data.get('instructed_currency') or 'USD',
            ))

        # Debtor Agent (RTN)
        if silver_data.get('debtor_agent_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                clearing_code=silver_data.get('debtor_agent_id'),
                clearing_system='RTP',
                country='US',
            ))

        # Creditor Agent (RTN)
        if silver_data.get('creditor_agent_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                clearing_code=silver_data.get('creditor_agent_id'),
                clearing_system='RTP',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('RTP', RtpExtractor())
ExtractorRegistry.register('rtp', RtpExtractor())
ExtractorRegistry.register('TCH_RTP', RtpExtractor())

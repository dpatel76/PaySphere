"""ISO 20022 pain.001 (Customer Credit Transfer Initiation) Extractor."""

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


class Pain001XmlParser:
    """Parser for ISO 20022 pain.001 XML messages."""

    # Namespace patterns for pain.001
    NS_PATTERN = re.compile(r'\{[^}]+\}')
    PAIN001_NAMESPACES = {
        'pain001': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.09',
        'pain001_08': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.08',
        'pain001_03': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03',
    }

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
        """Parse pain.001 XML content into structured dict."""
        try:
            # Remove BOM if present
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]

            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse pain.001 XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        # Find the main content element (CstmrCdtTrfInitn)
        initn = self._find(root, 'CstmrCdtTrfInitn')
        if initn is None:
            # Try direct if root is the initiation
            if self._strip_ns(root.tag) == 'CstmrCdtTrfInitn':
                initn = root
            else:
                raise ValueError("Cannot find CstmrCdtTrfInitn element in pain.001")

        return self._parse_initiation(initn)

    def _parse_initiation(self, initn: ET.Element) -> Dict[str, Any]:
        """Parse CstmrCdtTrfInitn element."""
        result = {}

        # Group Header
        grp_hdr = self._find(initn, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))
            result['controlSum'] = self._safe_decimal(self._find_text(grp_hdr, 'CtrlSum'))

            # Initiating Party
            initg_pty = self._find(grp_hdr, 'InitgPty')
            if initg_pty is not None:
                result['initiatingParty'] = self._parse_party(initg_pty)

        # Payment Information
        pmt_inf = self._find(initn, 'PmtInf')
        if pmt_inf is not None:
            result.update(self._parse_payment_info(pmt_inf))

        return result

    def _parse_payment_info(self, pmt_inf: ET.Element) -> Dict[str, Any]:
        """Parse PmtInf element."""
        result = {
            'paymentInformation': {}
        }
        pmt_info = result['paymentInformation']

        pmt_info['paymentInfoId'] = self._find_text(pmt_inf, 'PmtInfId')
        pmt_info['paymentMethod'] = self._find_text(pmt_inf, 'PmtMtd')
        pmt_info['batchBooking'] = self._find_text(pmt_inf, 'BtchBookg') == 'true'

        # Requested Execution Date
        req_exctn_dt = self._find(pmt_inf, 'ReqdExctnDt')
        if req_exctn_dt is not None:
            pmt_info['requestedExecutionDate'] = self._find_text(req_exctn_dt, 'Dt')

        # Payment Type Information
        pmt_tp_inf = self._find(pmt_inf, 'PmtTpInf')
        if pmt_tp_inf is not None:
            pmt_info['serviceLevel'] = self._find_text(pmt_tp_inf, 'SvcLvl/Cd')
            pmt_info['localInstrument'] = self._find_text(pmt_tp_inf, 'LclInstrm/Cd')
            pmt_info['categoryPurpose'] = self._find_text(pmt_tp_inf, 'CtgyPurp/Cd')
            pmt_info['instructionPriority'] = self._find_text(pmt_tp_inf, 'InstrPrty')

        # Debtor
        dbtr = self._find(pmt_inf, 'Dbtr')
        if dbtr is not None:
            result['debtor'] = self._parse_party(dbtr)

        # Debtor Account
        dbtr_acct = self._find(pmt_inf, 'DbtrAcct')
        if dbtr_acct is not None:
            result['debtorAccount'] = self._parse_account(dbtr_acct)

        # Debtor Agent
        dbtr_agt = self._find(pmt_inf, 'DbtrAgt')
        if dbtr_agt is not None:
            result['debtorAgent'] = self._parse_agent(dbtr_agt)

        # Charge Bearer
        result['chargeBearer'] = self._find_text(pmt_inf, 'ChrgBr')

        # Credit Transfer Transaction Information
        cdt_trf_tx_inf = self._find(pmt_inf, 'CdtTrfTxInf')
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
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Amount
        amt = self._find(tx_inf, 'Amt')
        if amt is not None:
            instd_amt = self._find(amt, 'InstdAmt')
            if instd_amt is not None:
                result['instructedAmount'] = self._safe_decimal(instd_amt.text)
                result['instructedCurrency'] = instd_amt.get('Ccy')

        # Creditor Agent
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
            result['purposeProprietary'] = self._find_text(purp, 'Prtry')

        # Remittance Information
        rmt_inf = self._find(tx_inf, 'RmtInf')
        if rmt_inf is not None:
            result['remittanceInformation'] = {
                'unstructured': self._find_text(rmt_inf, 'Ustrd')
            }
            # Structured remittance
            strd = self._find(rmt_inf, 'Strd')
            if strd is not None:
                result['remittanceInformation']['structured'] = {
                    'referenceNumber': self._find_text(strd, 'RfrdDocInf/Nb'),
                    'referenceType': self._find_text(strd, 'RfrdDocInf/Tp/CdOrPrtry/Cd'),
                    'referenceDate': self._find_text(strd, 'RfrdDocInf/RltdDt'),
                }

        return result

    def _parse_party(self, party_elem: ET.Element) -> Dict[str, Any]:
        """Parse a party element (Dbtr, Cdtr, InitgPty, etc.)."""
        result = {
            'name': self._find_text(party_elem, 'Nm')
        }

        # Postal Address
        pstl_adr = self._find(party_elem, 'PstlAdr')
        if pstl_adr is not None:
            result['streetName'] = self._find_text(pstl_adr, 'StrtNm')
            result['buildingNumber'] = self._find_text(pstl_adr, 'BldgNb')
            result['postalCode'] = self._find_text(pstl_adr, 'PstCd')
            result['townName'] = self._find_text(pstl_adr, 'TwnNm')
            result['countrySubDivision'] = self._find_text(pstl_adr, 'CtrySubDvsn')
            result['country'] = self._find_text(pstl_adr, 'Ctry')
            # Address lines
            adr_line = self._find_text(pstl_adr, 'AdrLine')
            if adr_line:
                result['addressLine'] = adr_line

        # ID - Organization
        org_id = self._find(party_elem, 'Id/OrgId')
        if org_id is not None:
            result['id'] = (
                self._find_text(org_id, 'AnyBIC') or
                self._find_text(org_id, 'LEI') or
                self._find_text(org_id, 'Othr/Id')
            )
            result['idType'] = 'ORG'

        # ID - Private
        prvt_id = self._find(party_elem, 'Id/PrvtId')
        if prvt_id is not None:
            result['id'] = (
                self._find_text(prvt_id, 'DtAndPlcOfBirth/BirthDt') or
                self._find_text(prvt_id, 'Othr/Id')
            )
            result['idType'] = 'PRVT'

        return result

    def _parse_account(self, acct_elem: ET.Element) -> Dict[str, Any]:
        """Parse an account element (DbtrAcct, CdtrAcct)."""
        result = {}

        acct_id = self._find(acct_elem, 'Id')
        if acct_id is not None:
            result['iban'] = self._find_text(acct_id, 'IBAN')
            result['other'] = self._find_text(acct_id, 'Othr/Id')
            result['accountNumber'] = result['iban'] or result['other']

        result['currency'] = self._find_text(acct_elem, 'Ccy')
        result['accountType'] = self._find_text(acct_elem, 'Tp/Cd')

        return result

    def _parse_agent(self, agt_elem: ET.Element) -> Dict[str, Any]:
        """Parse an agent element (DbtrAgt, CdtrAgt)."""
        result = {}

        fin_instn_id = self._find(agt_elem, 'FinInstnId')
        if fin_instn_id is not None:
            result['bic'] = self._find_text(fin_instn_id, 'BICFI')
            result['lei'] = self._find_text(fin_instn_id, 'LEI')
            result['name'] = self._find_text(fin_instn_id, 'Nm')

            # Clearing System
            clr_sys = self._find(fin_instn_id, 'ClrSysMmbId')
            if clr_sys is not None:
                result['clearingSystem'] = self._find_text(clr_sys, 'ClrSysId/Cd')
                result['memberId'] = self._find_text(clr_sys, 'MmbId')

            # Postal Address
            pstl_adr = self._find(fin_instn_id, 'PstlAdr')
            if pstl_adr is not None:
                result['country'] = self._find_text(pstl_adr, 'Ctry')

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


class Pain001Extractor(BaseExtractor):
    """Extractor for ISO 20022 pain.001 messages."""

    MESSAGE_TYPE = "pain.001"
    SILVER_TABLE = "stg_pain001"

    def __init__(self):
        self.parser = Pain001XmlParser()

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw pain.001 content."""
        msg_id = raw_content.get('messageId', '')
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
        """Extract all Silver layer fields from pain.001 message."""
        trunc = self.trunc

        # Handle raw XML content - parse it first
        if isinstance(msg_content, dict) and '_raw_text' in msg_content:
            raw_text = msg_content['_raw_text']
            if raw_text.strip().startswith('<?xml') or raw_text.strip().startswith('<'):
                parser = Pain001XmlParser()
                msg_content = parser.parse(raw_text)

        # Extract nested objects
        initiating_party = msg_content.get('initiatingParty', {})
        pmt_info = msg_content.get('paymentInformation', {})
        debtor = msg_content.get('debtor', {})
        debtor_account = msg_content.get('debtorAccount', {})
        debtor_agent = msg_content.get('debtorAgent', {})
        creditor = msg_content.get('creditor', {})
        creditor_account = msg_content.get('creditorAccount', {})
        creditor_agent = msg_content.get('creditorAgent', {})
        ultimate_debtor = msg_content.get('ultimateDebtor', {})
        ultimate_creditor = msg_content.get('ultimateCreditor', {})
        remittance_info = msg_content.get('remittanceInformation', {})
        structured_remit = remittance_info.get('structured', {}) if remittance_info else {}
        regulatory = msg_content.get('regulatoryReporting', {})

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header (msg_id matches table schema)
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'number_of_transactions': msg_content.get('numberOfTransactions'),
            'control_sum': msg_content.get('controlSum'),

            # Initiating Party
            'initiating_party_name': trunc(initiating_party.get('name'), 140),
            'initiating_party_id': trunc(initiating_party.get('id'), 35),
            'initiating_party_id_type': trunc(initiating_party.get('idType'), 35),
            'initiating_party_country': initiating_party.get('country'),

            # Payment Information
            'payment_info_id': trunc(pmt_info.get('paymentInfoId'), 35),
            'payment_method': pmt_info.get('paymentMethod'),
            'batch_booking': pmt_info.get('batchBooking'),
            'requested_execution_date': pmt_info.get('requestedExecutionDate'),
            'service_level': trunc(pmt_info.get('serviceLevel'), 35),
            'local_instrument': trunc(pmt_info.get('localInstrument'), 35),
            'category_purpose': trunc(pmt_info.get('categoryPurpose'), 35),

            # Debtor (column names match table: debtor_street_name, debtor_town_name)
            'debtor_name': trunc(debtor.get('name'), 140),
            'debtor_street_name': trunc(debtor.get('streetName'), 70),
            'debtor_building_number': trunc(debtor.get('buildingNumber'), 16),
            'debtor_postal_code': trunc(debtor.get('postalCode'), 16),
            'debtor_town_name': trunc(debtor.get('townName'), 35),
            'debtor_country_sub_division': trunc(debtor.get('countrySubDivision'), 35),
            'debtor_country': debtor.get('country'),
            'debtor_id': trunc(debtor.get('id'), 35),
            'debtor_id_type': trunc(debtor.get('idType'), 35),

            # Debtor Account (includes debtor_account_other)
            'debtor_account_iban': trunc(debtor_account.get('iban'), 34),
            'debtor_account_other': trunc(debtor_account.get('other') or debtor_account.get('accountNumber'), 34),
            'debtor_account_currency': debtor_account.get('currency'),
            'debtor_account_type': trunc(debtor_account.get('accountType'), 35),

            # Debtor Agent
            'debtor_agent_bic': debtor_agent.get('bic'),
            'debtor_agent_name': trunc(debtor_agent.get('name'), 140),
            'debtor_agent_clearing_system': trunc(debtor_agent.get('clearingSystem'), 35),
            'debtor_agent_member_id': trunc(debtor_agent.get('memberId'), 35),
            'debtor_agent_country': debtor_agent.get('country'),

            # Instruction
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'uetr': msg_content.get('uetr'),

            # Amounts
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency'),
            'equivalent_amount': msg_content.get('equivalentAmount'),
            'equivalent_currency': msg_content.get('equivalentCurrency'),
            'exchange_rate': msg_content.get('exchangeRate'),

            # Creditor Agent
            'creditor_agent_bic': creditor_agent.get('bic'),
            'creditor_agent_name': trunc(creditor_agent.get('name'), 140),
            'creditor_agent_clearing_system': trunc(creditor_agent.get('clearingSystem'), 35),
            'creditor_agent_member_id': trunc(creditor_agent.get('memberId'), 35),
            'creditor_agent_country': creditor_agent.get('country'),

            # Creditor (column names match table: creditor_street_name, creditor_town_name)
            'creditor_name': trunc(creditor.get('name'), 140),
            'creditor_street_name': trunc(creditor.get('streetName'), 70),
            'creditor_building_number': trunc(creditor.get('buildingNumber'), 16),
            'creditor_postal_code': trunc(creditor.get('postalCode'), 16),
            'creditor_town_name': trunc(creditor.get('townName'), 35),
            'creditor_country_sub_division': trunc(creditor.get('countrySubDivision'), 35),
            'creditor_country': creditor.get('country'),
            'creditor_id': trunc(creditor.get('id'), 35),
            'creditor_id_type': trunc(creditor.get('idType'), 35),

            # Creditor Account
            'creditor_account_iban': trunc(creditor_account.get('iban'), 34),
            'creditor_account_other': trunc(creditor_account.get('other') or creditor_account.get('accountNumber'), 34),
            'creditor_account_currency': creditor_account.get('currency'),
            'creditor_account_type': trunc(creditor_account.get('accountType'), 10),

            # Ultimate Parties
            'ultimate_debtor_name': trunc(ultimate_debtor.get('name'), 140),
            'ultimate_debtor_id': trunc(ultimate_debtor.get('id'), 35),
            'ultimate_debtor_id_type': trunc(ultimate_debtor.get('idType'), 35),
            'ultimate_creditor_name': trunc(ultimate_creditor.get('name'), 140),
            'ultimate_creditor_id': trunc(ultimate_creditor.get('id'), 35),
            'ultimate_creditor_id_type': trunc(ultimate_creditor.get('idType'), 35),

            # Purpose & Charges
            'purpose_code': msg_content.get('purposeCode'),
            'purpose_proprietary': msg_content.get('purposeProprietary'),
            'charge_bearer': msg_content.get('chargeBearer'),

            # Remittance Information (table uses single columns, not broken out)
            'remittance_information': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,
            'structured_remittance': json.dumps(structured_remit) if structured_remit else None,

            # Regulatory Reporting (table uses single JSON column)
            'regulatory_reporting': json.dumps(regulatory) if regulatory else None,
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Column order matches silver.stg_pain001 table schema exactly.
        Note: _processed_at has a default, so we don't include it.
        """
        return [
            # Core identifiers
            'stg_id', 'raw_id', 'msg_id',
            # Message header
            'creation_date_time', 'number_of_transactions', 'control_sum',
            # Initiating party
            'initiating_party_name', 'initiating_party_id',
            # Payment info
            'payment_info_id', 'payment_method', 'batch_booking', 'requested_execution_date',
            # Debtor
            'debtor_name', 'debtor_street_name', 'debtor_building_number', 'debtor_postal_code',
            'debtor_town_name', 'debtor_country', 'debtor_id', 'debtor_id_type',
            # Debtor account
            'debtor_account_iban', 'debtor_account_other', 'debtor_account_currency',
            # Debtor agent
            'debtor_agent_bic', 'debtor_agent_name', 'debtor_agent_clearing_system', 'debtor_agent_member_id',
            # Instruction
            'instruction_id', 'end_to_end_id', 'uetr',
            # Amounts
            'instructed_amount', 'instructed_currency', 'equivalent_amount', 'equivalent_currency',
            # Creditor agent
            'creditor_agent_bic', 'creditor_agent_name', 'creditor_agent_clearing_system', 'creditor_agent_member_id',
            # Creditor
            'creditor_name', 'creditor_street_name', 'creditor_building_number', 'creditor_postal_code',
            'creditor_town_name', 'creditor_country', 'creditor_id', 'creditor_id_type',
            # Creditor account
            'creditor_account_iban', 'creditor_account_other', 'creditor_account_currency',
            # Purpose & charges
            'purpose_code', 'purpose_proprietary', 'charge_bearer',
            # Remittance & regulatory
            'remittance_information', 'structured_remittance', 'regulatory_reporting',
            # Batch info
            '_batch_id',
            # Extended fields (added later)
            'initiating_party_id_type', 'initiating_party_country',
            'service_level', 'local_instrument', 'category_purpose',
            'debtor_country_sub_division', 'debtor_account_type', 'debtor_agent_country',
            'exchange_rate',
            'creditor_country_sub_division', 'creditor_account_type', 'creditor_agent_country',
            'ultimate_debtor_name', 'ultimate_debtor_id', 'ultimate_debtor_id_type',
            'ultimate_creditor_name', 'ultimate_creditor_id', 'ultimate_creditor_id_type',
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
        """Extract Gold layer entities from pain.001 Silver record.

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
                party_type='ORGANIZATION' if silver_data.get('debtor_id') else 'UNKNOWN',
                street_name=silver_data.get('debtor_street_name'),
                building_number=silver_data.get('debtor_building_number'),
                post_code=silver_data.get('debtor_postal_code'),
                town_name=silver_data.get('debtor_town_name'),
                country_sub_division=silver_data.get('debtor_country_sub_division'),
                country=silver_data.get('debtor_country'),
                identification_type=silver_data.get('debtor_id_type'),
                identification_number=silver_data.get('debtor_id'),
            ))

        # Creditor Party
        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='ORGANIZATION' if silver_data.get('creditor_id') else 'UNKNOWN',
                street_name=silver_data.get('creditor_street_name'),
                building_number=silver_data.get('creditor_building_number'),
                post_code=silver_data.get('creditor_postal_code'),
                town_name=silver_data.get('creditor_town_name'),
                country_sub_division=silver_data.get('creditor_country_sub_division'),
                country=silver_data.get('creditor_country'),
                identification_type=silver_data.get('creditor_id_type'),
                identification_number=silver_data.get('creditor_id'),
            ))

        # Ultimate Debtor Party
        if silver_data.get('ultimate_debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('ultimate_debtor_name'),
                role="ULTIMATE_DEBTOR",
                party_type='UNKNOWN',
                identification_type=silver_data.get('ultimate_debtor_id_type'),
                identification_number=silver_data.get('ultimate_debtor_id'),
            ))

        # Ultimate Creditor Party
        if silver_data.get('ultimate_creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('ultimate_creditor_name'),
                role="ULTIMATE_CREDITOR",
                party_type='UNKNOWN',
                identification_type=silver_data.get('ultimate_creditor_id_type'),
                identification_number=silver_data.get('ultimate_creditor_id'),
            ))

        # Debtor Account
        if silver_data.get('debtor_account_iban') or silver_data.get('debtor_account_other'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debtor_account_iban') or silver_data.get('debtor_account_other'),
                role="DEBTOR",
                iban=silver_data.get('debtor_account_iban'),
                account_type=silver_data.get('debtor_account_type') or 'CACC',
                currency=silver_data.get('debtor_account_currency') or 'XXX',
            ))

        # Creditor Account
        if silver_data.get('creditor_account_iban') or silver_data.get('creditor_account_other'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('creditor_account_iban') or silver_data.get('creditor_account_other'),
                role="CREDITOR",
                iban=silver_data.get('creditor_account_iban'),
                account_type=silver_data.get('creditor_account_type') or 'CACC',
                currency=silver_data.get('creditor_account_currency') or 'XXX',
            ))

        # Debtor Agent
        if silver_data.get('debtor_agent_bic') or silver_data.get('debtor_agent_member_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('debtor_agent_name'),
                bic=silver_data.get('debtor_agent_bic'),
                clearing_code=silver_data.get('debtor_agent_member_id'),
                clearing_system=silver_data.get('debtor_agent_clearing_system'),
                country=silver_data.get('debtor_agent_country') or 'XX',
            ))

        # Creditor Agent
        if silver_data.get('creditor_agent_bic') or silver_data.get('creditor_agent_member_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('creditor_agent_name'),
                bic=silver_data.get('creditor_agent_bic'),
                clearing_code=silver_data.get('creditor_agent_member_id'),
                clearing_system=silver_data.get('creditor_agent_clearing_system'),
                country=silver_data.get('creditor_agent_country') or 'XX',
            ))

        # Payment instruction fields
        entities.service_level = silver_data.get('service_level')
        entities.local_instrument = silver_data.get('local_instrument')
        entities.category_purpose = silver_data.get('category_purpose')
        entities.exchange_rate = silver_data.get('exchange_rate')

        return entities


# Register the extractor
ExtractorRegistry.register('pain.001', Pain001Extractor())
ExtractorRegistry.register('pain_001', Pain001Extractor())
ExtractorRegistry.register('pain001', Pain001Extractor())

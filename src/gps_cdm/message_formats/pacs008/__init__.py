"""ISO 20022 pacs.008 (FI to FI Customer Credit Transfer) Extractor."""

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


class Pacs008XmlParser:
    """Parser for ISO 20022 pacs.008 XML messages."""

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
        """Parse pacs.008 XML content into structured dict."""
        try:
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]

            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Failed to parse pacs.008 XML: {e}")
            raise ValueError(f"Invalid XML: {e}")

        # Find the main content element (FIToFICstmrCdtTrf)
        fi_transfer = self._find(root, 'FIToFICstmrCdtTrf')
        if fi_transfer is None:
            if self._strip_ns(root.tag) == 'FIToFICstmrCdtTrf':
                fi_transfer = root
            else:
                raise ValueError("Cannot find FIToFICstmrCdtTrf element in pacs.008 message")

        return self._parse_fi_transfer(fi_transfer)

    def _parse_fi_transfer(self, fi_transfer: ET.Element) -> Dict[str, Any]:
        """Parse FIToFICstmrCdtTrf element."""
        result = {}

        # Group Header
        grp_hdr = self._find(fi_transfer, 'GrpHdr')
        if grp_hdr is not None:
            result['messageId'] = self._find_text(grp_hdr, 'MsgId')
            result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
            result['numberOfTransactions'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))
            result['totalInterbankSettlementAmount'] = self._safe_decimal(self._find_text(grp_hdr, 'TtlIntrBkSttlmAmt'))
            result['totalInterbankSettlementCurrency'] = self._find_attr(grp_hdr, 'TtlIntrBkSttlmAmt', 'Ccy')
            result['interbankSettlementDate'] = self._find_text(grp_hdr, 'IntrBkSttlmDt')

            # Settlement Information
            sttlm_inf = self._find(grp_hdr, 'SttlmInf')
            if sttlm_inf is not None:
                result['settlementMethod'] = self._find_text(sttlm_inf, 'SttlmMtd')
                result['clearingSystem'] = self._find_text(sttlm_inf, 'ClrSys/Cd')

            # Instructing Agent
            instg_agt = self._find(grp_hdr, 'InstgAgt')
            if instg_agt is not None:
                result['instructingAgent'] = self._parse_agent(instg_agt)

            # Instructed Agent
            instd_agt = self._find(grp_hdr, 'InstdAgt')
            if instd_agt is not None:
                result['instructedAgent'] = self._parse_agent(instd_agt)

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
            result['clearingSystemReference'] = self._find_text(pmt_id, 'ClrSysRef')

        # Payment Type Information
        pmt_tp_inf = self._find(tx_inf, 'PmtTpInf')
        if pmt_tp_inf is not None:
            result['paymentTypeInformation'] = {
                'instructionPriority': self._find_text(pmt_tp_inf, 'InstrPrty'),
                'clearingChannel': self._find_text(pmt_tp_inf, 'ClrChanl'),
                'serviceLevel': self._find_text(pmt_tp_inf, 'SvcLvl/Cd'),
                'localInstrument': self._find_text(pmt_tp_inf, 'LclInstrm/Cd'),
                'categoryPurpose': self._find_text(pmt_tp_inf, 'CtgyPurp/Cd'),
            }

        # Amounts
        result['interbankSettlementAmount'] = self._safe_decimal(self._find_text(tx_inf, 'IntrBkSttlmAmt'))
        result['interbankSettlementCurrency'] = self._find_attr(tx_inf, 'IntrBkSttlmAmt', 'Ccy')
        result['instructedAmount'] = self._safe_decimal(self._find_text(tx_inf, 'InstdAmt'))
        result['instructedCurrency'] = self._find_attr(tx_inf, 'InstdAmt', 'Ccy')
        result['exchangeRate'] = self._safe_decimal(self._find_text(tx_inf, 'XchgRate'))

        # Charge Bearer
        result['chargeBearer'] = self._find_text(tx_inf, 'ChrgBr')

        # Charges Information
        chrgs_inf = self._find(tx_inf, 'ChrgsInf')
        if chrgs_inf is not None:
            result['chargesInformation'] = [{
                'amount': self._safe_decimal(self._find_text(chrgs_inf, 'Amt')),
                'currency': self._find_attr(chrgs_inf, 'Amt', 'Ccy'),
            }]

        # Debtor Agent
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

        # Ultimate Debtor
        ultmt_dbtr = self._find(tx_inf, 'UltmtDbtr')
        if ultmt_dbtr is not None:
            result['ultimateDebtor'] = self._parse_party(ultmt_dbtr)

        # Ultimate Creditor
        ultmt_cdtr = self._find(tx_inf, 'UltmtCdtr')
        if ultmt_cdtr is not None:
            result['ultimateCreditor'] = self._parse_party(ultmt_cdtr)

        # Intermediary Agents
        for i, tag in enumerate(['IntrmyAgt1', 'IntrmyAgt2', 'IntrmyAgt3'], 1):
            intrmy = self._find(tx_inf, tag)
            if intrmy is not None:
                result[f'intermediaryAgent{i}'] = self._parse_agent(intrmy)

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
            strd = self._find(rmt_inf, 'Strd')
            if strd is not None:
                result['remittanceInformation']['structured'] = {
                    'referenceNumber': self._find_text(strd, 'RfrdDocInf/Nb'),
                    'referenceType': self._find_text(strd, 'RfrdDocInf/Tp/CdOrPrtry/Cd'),
                }

        # Regulatory Reporting
        rgltry_rptg = self._find(tx_inf, 'RgltryRptg')
        if rgltry_rptg is not None:
            result['regulatoryReporting'] = {
                'code': self._find_text(rgltry_rptg, 'Dtls/Cd'),
                'info': self._find_text(rgltry_rptg, 'Dtls/Inf'),
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
            result['buildingNumber'] = self._find_text(pstl_adr, 'BldgNb')
            result['postalCode'] = self._find_text(pstl_adr, 'PstCd')
            result['townName'] = self._find_text(pstl_adr, 'TwnNm')
            result['countrySubDivision'] = self._find_text(pstl_adr, 'CtrySubDvsn')
            result['country'] = self._find_text(pstl_adr, 'Ctry')

        # Organization ID
        org_id = self._find(party_elem, 'Id/OrgId')
        if org_id is not None:
            result['id'] = (
                self._find_text(org_id, 'AnyBIC') or
                self._find_text(org_id, 'LEI') or
                self._find_text(org_id, 'Othr/Id')
            )
            result['idType'] = 'ORG'

        # Private ID
        prvt_id = self._find(party_elem, 'Id/PrvtId')
        if prvt_id is not None:
            result['id'] = self._find_text(prvt_id, 'Othr/Id')
            result['idType'] = 'PRVT'

        return result

    def _parse_account(self, acct_elem: ET.Element) -> Dict[str, Any]:
        """Parse account element."""
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
        """Parse agent element."""
        result = {}

        fin_instn_id = self._find(agt_elem, 'FinInstnId')
        if fin_instn_id is not None:
            result['bic'] = self._find_text(fin_instn_id, 'BICFI')
            result['lei'] = self._find_text(fin_instn_id, 'LEI')
            result['name'] = self._find_text(fin_instn_id, 'Nm')

            # Clearing System Member ID
            clr_sys = self._find(fin_instn_id, 'ClrSysMmbId')
            if clr_sys is not None:
                result['clearingSystemMemberId'] = self._find_text(clr_sys, 'MmbId')

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


class Pacs008Extractor(BaseExtractor):
    """Extractor for ISO 20022 pacs.008 messages."""

    MESSAGE_TYPE = "pacs.008"
    SILVER_TABLE = "stg_pacs008"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw pacs.008 content."""
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
        """Extract all Silver layer fields from pacs.008 message - matches DB schema exactly."""
        trunc = self.trunc

        # Handle raw text content - parse it first
        if isinstance(msg_content, dict) and '_raw_text' in msg_content:
            raw_text = msg_content['_raw_text']
            # pacs.008 is XML-based (ISO 20022 FI to FI Customer Credit Transfer)
            if raw_text.strip().startswith('<?xml') or raw_text.strip().startswith('<'):
                parser = Pacs008XmlParser()
                msg_content = parser.parse(raw_text)

        # Extract nested objects
        instructing_agent = msg_content.get('instructingAgent', {}) or {}
        instructed_agent = msg_content.get('instructedAgent', {}) or {}
        pmt_type_info = msg_content.get('paymentTypeInformation', {}) or {}
        debtor = msg_content.get('debtor', {}) or {}
        debtor_account = msg_content.get('debtorAccount', {}) or {}
        debtor_agent = msg_content.get('debtorAgent', {}) or {}
        creditor = msg_content.get('creditor', {}) or {}
        creditor_account = msg_content.get('creditorAccount', {}) or {}
        creditor_agent = msg_content.get('creditorAgent', {}) or {}
        ultimate_debtor = msg_content.get('ultimateDebtor', {}) or {}
        ultimate_creditor = msg_content.get('ultimateCreditor', {}) or {}
        remittance_info = msg_content.get('remittanceInformation', {}) or {}
        structured_remit = remittance_info.get('structured', {}) if remittance_info else {}
        regulatory = msg_content.get('regulatoryReporting', {}) or {}

        # Charges can be an array
        charges = msg_content.get('chargesInformation', [])
        charges_amount = charges[0].get('amount') if charges and len(charges) > 0 else None
        charges_currency = charges[0].get('currency') if charges and len(charges) > 0 else None

        # Build debtor/creditor address from components
        debtor_address_parts = [
            debtor.get('streetName'),
            debtor.get('buildingNumber'),
            debtor.get('townName'),
            debtor.get('postalCode'),
            debtor.get('countrySubDivision'),
        ]
        debtor_address = ', '.join([p for p in debtor_address_parts if p])

        creditor_address_parts = [
            creditor.get('streetName'),
            creditor.get('buildingNumber'),
            creditor.get('townName'),
            creditor.get('postalCode'),
            creditor.get('countrySubDivision'),
        ]
        creditor_address = ', '.join([p for p in creditor_address_parts if p])

        # Structured remittance as JSON
        structured_remittance = json.dumps(structured_remit) if structured_remit else None

        # Regulatory reporting as JSON
        regulatory_reporting = json.dumps(regulatory) if regulatory else None

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header - uses 'msg_id' not 'message_id'
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'number_of_transactions': msg_content.get('numberOfTransactions'),
            'settlement_method': msg_content.get('settlementMethod'),
            'clearing_system': trunc(msg_content.get('clearingSystem'), 35),
            'interbank_settlement_date': msg_content.get('interbankSettlementDate'),
            'total_interbank_settlement_amount': msg_content.get('totalInterbankSettlementAmount'),
            'total_interbank_settlement_currency': msg_content.get('totalInterbankSettlementCurrency') or msg_content.get('interbankSettlementCurrency'),

            # Instructing/Instructed Agents
            'instructing_agent_bic': instructing_agent.get('bic'),
            'instructed_agent_bic': instructed_agent.get('bic'),

            # Transaction IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),
            'clearing_system_reference': trunc(msg_content.get('clearingSystemReference'), 35),

            # Amounts
            'interbank_settlement_amount': msg_content.get('interbankSettlementAmount'),
            'interbank_settlement_currency': msg_content.get('interbankSettlementAmountCurrency') or msg_content.get('interbankSettlementCurrency'),
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency'),
            'exchange_rate': msg_content.get('exchangeRate'),
            'charge_bearer': msg_content.get('chargeBearer'),
            'charges_amount': charges_amount,
            'charges_currency': charges_currency,

            # Debtor
            'debtor_name': trunc(debtor.get('name'), 140),
            'debtor_address': trunc(debtor_address, 140) if debtor_address else None,
            'debtor_country': debtor.get('country'),
            'debtor_account_iban': trunc(debtor_account.get('iban'), 34),
            'debtor_agent_bic': debtor_agent.get('bic'),

            # Creditor
            'creditor_name': trunc(creditor.get('name'), 140),
            'creditor_address': trunc(creditor_address, 140) if creditor_address else None,
            'creditor_country': creditor.get('country'),
            'creditor_account_iban': trunc(creditor_account.get('iban'), 34),
            'creditor_agent_bic': creditor_agent.get('bic'),

            # Purpose
            'purpose_code': msg_content.get('purposeCode'),

            # Remittance Information - single column 'remittance_info'
            'remittance_info': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,

            # Ultimate Parties
            'ultimate_debtor_name': trunc(ultimate_debtor.get('name'), 140),
            'ultimate_creditor_name': trunc(ultimate_creditor.get('name'), 140),

            # Intermediary Agents
            'intermediary_agent_1_bic': msg_content.get('intermediaryAgent1', {}).get('bic') if msg_content.get('intermediaryAgent1') else None,
            'intermediary_agent_2_bic': msg_content.get('intermediaryAgent2', {}).get('bic') if msg_content.get('intermediaryAgent2') else None,
            'intermediary_agent_3_bic': msg_content.get('intermediaryAgent3', {}).get('bic') if msg_content.get('intermediaryAgent3') else None,

            # Structured remittance and regulatory as JSON
            'structured_remittance': structured_remittance,
            'regulatory_reporting': regulatory_reporting,

            # Extended agent fields
            'instructing_agent_name': trunc(instructing_agent.get('name'), 140),
            'instructing_agent_lei': trunc(instructing_agent.get('lei'), 20),
            'instructing_agent_country': instructing_agent.get('country'),
            'instructed_agent_name': trunc(instructed_agent.get('name'), 140),
            'instructed_agent_lei': trunc(instructed_agent.get('lei'), 20),
            'instructed_agent_country': instructed_agent.get('country'),

            # Payment Type Information
            'instruction_priority': pmt_type_info.get('instructionPriority'),
            'clearing_channel': trunc(pmt_type_info.get('clearingChannel'), 35),
            'service_level': trunc(pmt_type_info.get('serviceLevel'), 35),
            'local_instrument': trunc(pmt_type_info.get('localInstrument'), 35),
            'category_purpose': trunc(pmt_type_info.get('categoryPurpose'), 35),

            # Debtor address components
            'debtor_street_name': trunc(debtor.get('streetName'), 70),
            'debtor_building_number': trunc(debtor.get('buildingNumber'), 16),
            'debtor_postal_code': trunc(debtor.get('postalCode'), 16),
            'debtor_town_name': trunc(debtor.get('townName'), 35),
            'debtor_country_sub_division': trunc(debtor.get('countrySubDivision'), 35),
            'debtor_id': trunc(debtor.get('id'), 35),
            'debtor_id_type': trunc(debtor.get('idType'), 35),
            'debtor_account_currency': debtor_account.get('currency'),
            'debtor_account_type': trunc(debtor_account.get('accountType'), 10),
            'debtor_agent_name': trunc(debtor_agent.get('name'), 140),
            'debtor_agent_clearing_member_id': trunc(debtor_agent.get('clearingSystemMemberId'), 35),
            'debtor_agent_lei': trunc(debtor_agent.get('lei'), 20),

            # Creditor Agent extended
            'creditor_agent_name': trunc(creditor_agent.get('name'), 140),
            'creditor_agent_clearing_member_id': trunc(creditor_agent.get('clearingSystemMemberId'), 35),
            'creditor_agent_lei': trunc(creditor_agent.get('lei'), 20),

            # Creditor address components
            'creditor_street_name': trunc(creditor.get('streetName'), 70),
            'creditor_building_number': trunc(creditor.get('buildingNumber'), 16),
            'creditor_postal_code': trunc(creditor.get('postalCode'), 16),
            'creditor_town_name': trunc(creditor.get('townName'), 35),
            'creditor_country_sub_division': trunc(creditor.get('countrySubDivision'), 35),
            'creditor_id': trunc(creditor.get('id'), 35),
            'creditor_id_type': trunc(creditor.get('idType'), 35),
            'creditor_account_currency': creditor_account.get('currency'),
            'creditor_account_type': trunc(creditor_account.get('accountType'), 10),

            # Ultimate parties IDs
            'ultimate_debtor_id': trunc(ultimate_debtor.get('id'), 35),
            'ultimate_debtor_id_type': trunc(ultimate_debtor.get('idType'), 35),
            'ultimate_creditor_id': trunc(ultimate_creditor.get('id'), 35),
            'ultimate_creditor_id_type': trunc(ultimate_creditor.get('idType'), 35),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT - matches DB schema exactly."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            # Message header
            'msg_id', 'creation_date_time', 'number_of_transactions',
            'settlement_method', 'clearing_system', 'interbank_settlement_date',
            'total_interbank_settlement_amount', 'total_interbank_settlement_currency',
            # Agents
            'instructing_agent_bic', 'instructed_agent_bic',
            # Transaction IDs
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr', 'clearing_system_reference',
            # Amounts
            'interbank_settlement_amount', 'interbank_settlement_currency',
            'instructed_amount', 'instructed_currency', 'exchange_rate',
            'charge_bearer', 'charges_amount', 'charges_currency',
            # Debtor
            'debtor_name', 'debtor_address', 'debtor_country',
            'debtor_account_iban', 'debtor_agent_bic',
            # Creditor
            'creditor_name', 'creditor_address', 'creditor_country',
            'creditor_account_iban', 'creditor_agent_bic',
            # Purpose and remittance
            'purpose_code', 'remittance_info',
            # Ultimate parties
            'ultimate_debtor_name', 'ultimate_creditor_name',
            # Intermediary agents
            'intermediary_agent_1_bic', 'intermediary_agent_2_bic', 'intermediary_agent_3_bic',
            # JSON columns
            'structured_remittance', 'regulatory_reporting',
            # Extended agent info
            'instructing_agent_name', 'instructing_agent_lei', 'instructing_agent_country',
            'instructed_agent_name', 'instructed_agent_lei', 'instructed_agent_country',
            # Payment type info
            'instruction_priority', 'clearing_channel', 'service_level', 'local_instrument', 'category_purpose',
            # Debtor details
            'debtor_street_name', 'debtor_building_number', 'debtor_postal_code',
            'debtor_town_name', 'debtor_country_sub_division',
            'debtor_id', 'debtor_id_type',
            'debtor_account_currency', 'debtor_account_type',
            'debtor_agent_name', 'debtor_agent_clearing_member_id', 'debtor_agent_lei',
            # Creditor agent details
            'creditor_agent_name', 'creditor_agent_clearing_member_id', 'creditor_agent_lei',
            # Creditor details
            'creditor_street_name', 'creditor_building_number', 'creditor_postal_code',
            'creditor_town_name', 'creditor_country_sub_division',
            'creditor_id', 'creditor_id_type',
            'creditor_account_currency', 'creditor_account_type',
            # Ultimate party IDs
            'ultimate_debtor_id', 'ultimate_debtor_id_type',
            'ultimate_creditor_id', 'ultimate_creditor_id_type',
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
        """Extract Gold layer entities from pacs.008 Silver record.

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
        if silver_data.get('debtor_account_iban'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('debtor_account_iban'),
                role="DEBTOR",
                iban=silver_data.get('debtor_account_iban'),
                account_type=silver_data.get('debtor_account_type') or 'CACC',
                currency=silver_data.get('debtor_account_currency') or 'XXX',
            ))

        # Creditor Account
        if silver_data.get('creditor_account_iban'):
            entities.accounts.append(AccountData(
                account_number=silver_data.get('creditor_account_iban'),
                role="CREDITOR",
                iban=silver_data.get('creditor_account_iban'),
                account_type=silver_data.get('creditor_account_type') or 'CACC',
                currency=silver_data.get('creditor_account_currency') or 'XXX',
            ))

        # Instructing Agent (Debtor Agent)
        if silver_data.get('instructing_agent_bic') or silver_data.get('debtor_agent_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('instructing_agent_name') or silver_data.get('debtor_agent_name'),
                bic=silver_data.get('instructing_agent_bic') or silver_data.get('debtor_agent_bic'),
                lei=silver_data.get('instructing_agent_lei') or silver_data.get('debtor_agent_lei'),
                clearing_code=silver_data.get('debtor_agent_clearing_member_id'),
                country=silver_data.get('instructing_agent_country') or 'XX',
            ))

        # Instructed Agent (Creditor Agent)
        if silver_data.get('instructed_agent_bic') or silver_data.get('creditor_agent_bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('instructed_agent_name') or silver_data.get('creditor_agent_name'),
                bic=silver_data.get('instructed_agent_bic') or silver_data.get('creditor_agent_bic'),
                lei=silver_data.get('instructed_agent_lei') or silver_data.get('creditor_agent_lei'),
                clearing_code=silver_data.get('creditor_agent_clearing_member_id'),
                country=silver_data.get('instructed_agent_country') or 'XX',
            ))

        # Payment instruction fields
        entities.service_level = silver_data.get('service_level')
        entities.local_instrument = silver_data.get('local_instrument')
        entities.category_purpose = silver_data.get('category_purpose')
        entities.exchange_rate = silver_data.get('exchange_rate')

        return entities


# Register the extractor
ExtractorRegistry.register('pacs.008', Pacs008Extractor())
ExtractorRegistry.register('pacs_008', Pacs008Extractor())
ExtractorRegistry.register('pacs008', Pacs008Extractor())

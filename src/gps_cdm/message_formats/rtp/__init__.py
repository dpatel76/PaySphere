"""TCH RTP (Real-Time Payments) Extractor - ISO 20022 based.

ISO 20022 INHERITANCE HIERARCHY:
    RTP uses The Clearing House ISO 20022 usage guidelines based on pacs.008.
    The RtpISO20022Parser inherits from Pacs008Parser.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer - pacs.008.001.08)
            └── RtpISO20022Parser (The Clearing House RTP guidelines)

RTP-SPECIFIC ELEMENTS:
    - RTN Routing Numbers (USRTP clearing system)
    - USD currency (US Dollars)
    - Real-time instant payments (24/7/365)
    - Maximum $1,000,000 per transaction

CLEARING SYSTEM:
    - USRTP (US Real-Time Payments)
    - Operated by The Clearing House

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_rtp
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_rtp

MAPPING INHERITANCE:
    RTP -> pacs.008.base (COMPLETE)
"""

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

# Import ISO 20022 base classes for inheritance
try:
    from ..iso20022 import Pacs008Parser, Pacs008Extractor
    ISO20022_BASE_AVAILABLE = True
except ImportError:
    ISO20022_BASE_AVAILABLE = False
    logger.warning("ISO 20022 base classes not available - RTP will use standalone implementation")


# =============================================================================
# RTP ISO 20022 PARSER (inherits from Pacs008Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_RtpParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class RtpISO20022Parser(_RtpParserBase):
    """RTP ISO 20022 pacs.008 parser with The Clearing House usage guidelines.

    Inherits from Pacs008Parser and adds RTP-specific processing:
    - RTN Routing Number extraction (USRTP scheme)
    - RTP-specific clearing system identification
    - US address format handling

    ISO 20022 Version: pacs.008.001.08
    Usage Guidelines: The Clearing House RTP Service

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pacs008Parser -> RtpISO20022Parser
    """

    # RTP-specific constants
    CLEARING_SYSTEM = "USRTP"  # The Clearing House RTP
    DEFAULT_CURRENCY = "USD"
    MESSAGE_TYPE = "RTP"

    def __init__(self):
        """Initialize RTP parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse RTP ISO 20022 pacs.008 message.

        Uses inherited pacs.008 parsing from Pacs008Parser and adds
        RTP-specific fields.
        """
        # Handle JSON/dict input
        if isinstance(raw_content, dict):
            return raw_content

        if raw_content.strip().startswith('{'):
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError:
                pass

        # Use parent pacs.008 parsing if available
        if ISO20022_BASE_AVAILABLE:
            result = super().parse(raw_content)
        else:
            result = self._parse_standalone(raw_content)

        # Add RTP-specific fields
        result['isRtp'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available."""
        legacy_parser = RtpXmlParser()
        return legacy_parser.parse(raw_content)


# =============================================================================
# LEGACY XML PARSER (kept for backward compatibility)
# =============================================================================


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
                # Try both paths for clearing system code
                result['clearingSystem'] = (
                    self._find_text(sttlm_inf, 'ClrSys/Cd') or
                    self._find_text(sttlm_inf, 'ClrSys/Prtry')
                )

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

        # Amounts - extract both IntrBkSttlmAmt and InstdAmt
        interbank_amt = self._safe_decimal(self._find_text(tx_inf, 'IntrBkSttlmAmt'))
        interbank_ccy = self._find_attr(tx_inf, 'IntrBkSttlmAmt', 'Ccy')
        instructed_amt = self._safe_decimal(self._find_text(tx_inf, 'InstdAmt'))
        instructed_ccy = self._find_attr(tx_inf, 'InstdAmt', 'Ccy')

        # Store interbank settlement amount
        result['interbankSettlementAmount'] = interbank_amt
        result['interbankSettlementCurrency'] = interbank_ccy

        # For instructed amount, fall back to interbank if not present
        # This is critical because RTP messages typically use IntrBkSttlmAmt
        result['instructedAmount'] = instructed_amt if instructed_amt is not None else interbank_amt
        result['instructedCurrency'] = instructed_ccy if instructed_ccy is not None else interbank_ccy

        # Settlement Date
        result['interbankSettlementDate'] = self._find_text(tx_inf, 'IntrBkSttlmDt')

        # Charge Bearer
        result['chargeBearer'] = self._find_text(tx_inf, 'ChrgBr')

        # Payment Type Information
        pmt_tp_inf = self._find(tx_inf, 'PmtTpInf')
        if pmt_tp_inf is not None:
            result['instructionPriority'] = self._find_text(pmt_tp_inf, 'InstrPrty')
            result['serviceLevel'] = (
                self._find_text(pmt_tp_inf, 'SvcLvl/Cd') or
                self._find_text(pmt_tp_inf, 'SvcLvl/Prtry')
            )
            result['localInstrument'] = (
                self._find_text(pmt_tp_inf, 'LclInstrm/Cd') or
                self._find_text(pmt_tp_inf, 'LclInstrm/Prtry')
            )
            result['categoryPurpose'] = (
                self._find_text(pmt_tp_inf, 'CtgyPurp/Cd') or
                self._find_text(pmt_tp_inf, 'CtgyPurp/Prtry')
            )

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
                result['remittanceInformation']['referenceNumber'] = self._find_text(strd, 'RfrdDocInf/Nb')
                result['remittanceInformation']['referenceType'] = self._find_text(strd, 'RfrdDocInf/Tp/CdOrPrtry/Cd')
                result['remittanceInformation']['creditorReference'] = self._find_text(strd, 'CdtrRefInf/Ref')

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
            result['orgId'] = (
                self._find_text(org_id, 'LEI') or
                self._find_text(org_id, 'Othr/Id')
            )

        # Private ID
        prvt_id = self._find(party_elem, 'Id/PrvtId')
        if prvt_id is not None:
            result['prvtId'] = self._find_text(prvt_id, 'Othr/Id')

        return result

    def _parse_account(self, acct_elem: ET.Element) -> Dict[str, Any]:
        """Parse account element - RTP uses account numbers, not IBAN."""
        result = {}

        acct_id = self._find(acct_elem, 'Id')
        if acct_id is not None:
            # RTP uses Othr/Id for account numbers
            result['accountNumber'] = self._find_text(acct_id, 'Othr/Id')
            # Also try IBAN in case it's used
            if not result.get('accountNumber'):
                result['accountNumber'] = self._find_text(acct_id, 'IBAN')

        # Account type
        tp = self._find(acct_elem, 'Tp')
        if tp is not None:
            result['type'] = self._find_text(tp, 'Cd')

        # Currency
        result['currency'] = self._find_text(acct_elem, 'Ccy')

        return result

    def _parse_agent(self, agt_elem: ET.Element) -> Dict[str, Any]:
        """Parse agent element - RTN for RTP."""
        result = {}

        fin_instn_id = self._find(agt_elem, 'FinInstnId')
        if fin_instn_id is not None:
            # RTP uses ClrSysMmbId/MmbId for RTN
            result['memberId'] = self._find_text(fin_instn_id, 'ClrSysMmbId/MmbId')
            result['clearingSystem'] = 'RTP'

            # Also capture BIC if present
            result['bic'] = self._find_text(fin_instn_id, 'BICFI')

            # Name and country
            result['name'] = self._find_text(fin_instn_id, 'Nm')
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


class RtpExtractor(BaseExtractor):
    """Extractor for TCH RTP (The Clearing House Real-Time Payments) messages.

    ISO 20022 INHERITANCE:
        RTP inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The RtpISO20022Parser inherits from Pacs008Parser.
        Uses The Clearing House RTP Service usage guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008.001.08) - Current standard

    RTP-Specific Elements:
        - RTN Routing Numbers (USRTP clearing system)
        - USD currency (US Dollars)
        - Real-time 24/7/365 instant payments
        - Maximum $1,000,000 per transaction

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_rtp
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_rtp

    Inheritance Hierarchy:
        BaseExtractor -> RtpExtractor
        (Parser: Pacs008Parser -> RtpISO20022Parser)
    """

    MESSAGE_TYPE = "RTP"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "USD"
    CLEARING_SYSTEM = "USRTP"

    def __init__(self):
        """Initialize RTP extractor with ISO 20022 parser."""
        self.iso20022_parser = RtpISO20022Parser()
        self.legacy_parser = RtpXmlParser()
        self.parser = self.iso20022_parser

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
        debtor = msg_content.get('debtor') or {}
        debtor_account = msg_content.get('debtorAccount') or {}
        debtor_agent = msg_content.get('debtorAgent') or {}
        creditor = msg_content.get('creditor') or {}
        creditor_account = msg_content.get('creditorAccount') or {}
        creditor_agent = msg_content.get('creditorAgent') or {}
        remittance_info = msg_content.get('remittanceInformation') or {}

        # Get account number and RTN values
        debtor_acct_num = trunc(debtor_account.get('accountNumber'), 34)
        creditor_acct_num = trunc(creditor_account.get('accountNumber'), 34)
        debtor_rtn = trunc(debtor_agent.get('memberId'), 9)
        creditor_rtn = trunc(creditor_agent.get('memberId'), 9)

        # Amount with fallback: instructedAmount -> interbankSettlementAmount
        instructed_amount = (
            msg_content.get('instructedAmount') or
            msg_content.get('interbankSettlementAmount')
        )
        instructed_currency = (
            msg_content.get('instructedCurrency') or
            msg_content.get('interbankSettlementCurrency') or
            'USD'
        )

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

            # Amounts - both instructed_amount and interbank columns
            'instructed_amount': instructed_amount,
            'instructed_currency': instructed_currency,
            'instd_amt': msg_content.get('instructedAmount'),
            'instd_amt_ccy': msg_content.get('instructedCurrency'),
            'intrbnk_sttlm_amt': msg_content.get('interbankSettlementAmount'),
            'intrbnk_sttlm_ccy': msg_content.get('interbankSettlementCurrency'),
            'intrbnk_sttlm_dt': msg_content.get('interbankSettlementDate'),

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
            'purp_cd': msg_content.get('purposeCode'),
            'purp_prtry': msg_content.get('purposeProprietary'),

            # Remittance Information
            'remittance_info': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,
            'rmt_inf_ustrd': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,
            'rmt_inf_ref_nb': remittance_info.get('referenceNumber') if remittance_info else None,
            'rmt_inf_ref_tp': remittance_info.get('referenceType') if remittance_info else None,
            'rmt_inf_cdtr_ref': remittance_info.get('creditorReference') if remittance_info else None,

            # Payment type info
            'instr_prty': msg_content.get('instructionPriority'),
            'svc_lvl_cd': msg_content.get('serviceLevel'),
            'lcl_instrm_cd': msg_content.get('localInstrument'),
            'ctgy_purp_cd': msg_content.get('categoryPurpose'),
            'chrg_br': msg_content.get('chargeBearer'),
            'sttlm_mtd': msg_content.get('settlementMethod'),
            'clr_sys_cd': msg_content.get('clearingSystem'),

            # Extended debtor info
            'dbtr_org_id': debtor.get('orgId'),
            'dbtr_prvt_id': debtor.get('prvtId'),
            'dbtr_strt_nm': debtor.get('streetName'),
            'dbtr_bldg_nb': debtor.get('buildingNumber'),
            'dbtr_pst_cd': debtor.get('postalCode'),
            'dbtr_twn_nm': debtor.get('townName'),
            'dbtr_ctry_sub_dvsn': debtor.get('countrySubDivision'),
            'dbtr_ctry': debtor.get('country'),
            'dbtr_acct_tp': debtor_account.get('type'),
            'dbtr_agt_nm': debtor_agent.get('name'),
            'dbtr_agt_ctry': debtor_agent.get('country'),

            # Extended creditor info
            'cdtr_org_id': creditor.get('orgId'),
            'cdtr_prvt_id': creditor.get('prvtId'),
            'cdtr_strt_nm': creditor.get('streetName'),
            'cdtr_bldg_nb': creditor.get('buildingNumber'),
            'cdtr_pst_cd': creditor.get('postalCode'),
            'cdtr_twn_nm': creditor.get('townName'),
            'cdtr_ctry_sub_dvsn': creditor.get('countrySubDivision'),
            'cdtr_ctry': creditor.get('country'),
            'cdtr_acct_tp': creditor_account.get('type'),
            'cdtr_agt_nm': creditor_agent.get('name'),
            'cdtr_agt_ctry': creditor_agent.get('country'),
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

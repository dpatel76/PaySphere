"""Philippines InstaPay Extractor - ISO 20022 pacs.008 based.

ISO 20022 INHERITANCE HIERARCHY:
    InstaPay uses Philippine Clearing House ISO 20022 usage guidelines based on pacs.008.
    The InstapayISO20022Parser inherits from Pacs008Parser.

    BaseISO20022Parser
        └── Pacs008Parser (FI to FI Customer Credit Transfer - pacs.008.001.08)
            └── InstapayISO20022Parser (Philippine Clearing House instant payments guidelines)

INSTAPAY-SPECIFIC ELEMENTS:
    - Philippine Peso (PHP) currency
    - PHPCH clearing system (Philippines Clearing House)
    - Real-time instant payments
    - Bank clearing member IDs

CLEARING SYSTEM:
    - PHPCH (Philippines Clearing House Corporation)
    - Operated by PCHC (Philippine Clearing House Corporation)

DATABASE TABLES:
    - Bronze: bronze.raw_payment_messages
    - Silver: silver.stg_instapay
    - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_instapay

MAPPING INHERITANCE:
    INSTAPAY -> pacs.008.base (COMPLETE)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import re
import xml.etree.ElementTree as ET

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
    logger.warning("ISO 20022 base classes not available - InstaPay will use standalone implementation")


# =============================================================================
# INSTAPAY ISO 20022 PARSER (inherits from Pacs008Parser)
# =============================================================================

# Use conditional inheritance pattern for backward compatibility
_InstapayParserBase = Pacs008Parser if ISO20022_BASE_AVAILABLE else object


class InstapayISO20022Parser(_InstapayParserBase):
    """InstaPay ISO 20022 pacs.008 parser with Philippine Clearing House usage guidelines.

    Inherits from Pacs008Parser and adds InstaPay-specific processing:
    - PHPCH clearing system identification
    - PHP currency defaults
    - Philippine bank clearing member ID extraction

    ISO 20022 Version: pacs.008.001.08
    Usage Guidelines: Philippine Clearing House Corporation (PCHC)

    Inheritance Hierarchy:
        BaseISO20022Parser -> Pacs008Parser -> InstapayISO20022Parser
    """

    # InstaPay-specific constants
    CLEARING_SYSTEM = "PHPCH"  # Philippines Clearing House
    DEFAULT_CURRENCY = "PHP"
    MESSAGE_TYPE = "INSTAPAY"

    def __init__(self):
        """Initialize InstaPay parser."""
        if ISO20022_BASE_AVAILABLE:
            super().__init__()

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse InstaPay ISO 20022 pacs.008 message.

        Uses inherited pacs.008 parsing from Pacs008Parser and adds
        InstaPay-specific fields.
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

        # Add InstaPay-specific fields
        result['isInstaPay'] = True
        result['clearingSystem'] = self.CLEARING_SYSTEM

        return result

    def _parse_standalone(self, raw_content: str) -> Dict[str, Any]:
        """Standalone parsing when base class not available."""
        legacy_parser = InstaPayParser()
        return legacy_parser.parse(raw_content)


# =============================================================================
# LEGACY XML PARSER (kept for backward compatibility)
# =============================================================================


class InstaPayParser:
    """Parser for InstaPay ISO 20022 pacs.008 XML messages (legacy standalone)."""

    def parse(self, raw_content: str) -> Dict[str, Any]:
        """Parse InstaPay XML/JSON content into flat dictionary."""
        # Handle JSON input (legacy format)
        if raw_content.strip().startswith('{'):
            return self._parse_json(raw_content)

        # Handle XML input (ISO 20022 format)
        return self._parse_xml(raw_content)

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse legacy JSON format."""
        data = json.loads(content)
        return data

    def _parse_xml(self, content: str) -> Dict[str, Any]:
        """Parse ISO 20022 pacs.008 XML format."""
        # Strip XML namespaces for easier parsing
        content = re.sub(r'\sxmlns[^"]*"[^"]*"', '', content)
        content = re.sub(r'<([a-zA-Z_]+):', '<', content)
        content = re.sub(r'</([a-zA-Z_]+):', '</', content)

        root = ET.fromstring(content)
        result = {}

        # Find the FIToFICstmrCdtTrf element
        fi_cdt = root.find('.//FIToFICstmrCdtTrf')
        if fi_cdt is None:
            fi_cdt = root

        # Group Header
        grp_hdr = fi_cdt.find('GrpHdr')
        if grp_hdr is not None:
            result['msgId'] = self._get_text(grp_hdr, 'MsgId')
            result['creDtTm'] = self._get_text(grp_hdr, 'CreDtTm')
            result['nbOfTxs'] = self._get_int(grp_hdr, 'NbOfTxs')
            result['ttlIntrBkSttlmAmt'] = self._get_decimal(grp_hdr, 'TtlIntrBkSttlmAmt')
            result['intrBkSttlmDt'] = self._get_text(grp_hdr, 'IntrBkSttlmDt')

            sttlm_inf = grp_hdr.find('SttlmInf')
            if sttlm_inf is not None:
                result['sttlmMtd'] = self._get_text(sttlm_inf, 'SttlmMtd')
                result['sttlmClrSys'] = self._get_text(sttlm_inf, 'ClrSys/Cd')

        # Credit Transfer Transaction Info
        cdt_trf = fi_cdt.find('CdtTrfTxInf')
        if cdt_trf is not None:
            # Payment Identification
            pmt_id = cdt_trf.find('PmtId')
            if pmt_id is not None:
                result['instrId'] = self._get_text(pmt_id, 'InstrId')
                result['endToEndId'] = self._get_text(pmt_id, 'EndToEndId')
                result['txId'] = self._get_text(pmt_id, 'TxId')
                result['uetr'] = self._get_text(pmt_id, 'UETR')
                result['clrSysRef'] = self._get_text(pmt_id, 'ClrSysRef')

            # Payment Type Info
            pmt_tp = cdt_trf.find('PmtTpInf')
            if pmt_tp is not None:
                result['pmtTpInstrPrty'] = self._get_text(pmt_tp, 'InstrPrty')
                result['pmtTpSvcLvl'] = self._get_text(pmt_tp, 'SvcLvl/Cd')
                result['pmtTpLclInstrm'] = self._get_text(pmt_tp, 'LclInstrm/Cd')
                result['pmtTpCtgyPurp'] = self._get_text(pmt_tp, 'CtgyPurp/Cd')

            # Amounts
            intr_bk = cdt_trf.find('IntrBkSttlmAmt')
            if intr_bk is not None:
                result['intrBkSttlmAmt'] = self._get_decimal_value(intr_bk)
                result['intrBkSttlmCcy'] = intr_bk.get('Ccy')

            instd = cdt_trf.find('InstdAmt')
            if instd is not None:
                result['instdAmt'] = self._get_decimal_value(instd)
                result['instdAmtCcy'] = instd.get('Ccy')

            result['xchgRate'] = self._get_decimal(cdt_trf, 'XchgRate')
            result['chrgBr'] = self._get_text(cdt_trf, 'ChrgBr')

            chrgs = cdt_trf.find('ChrgsInf')
            if chrgs is not None:
                result['chrgsAmt'] = self._get_decimal(chrgs, 'Amt')
                result['chrgsAgt'] = self._get_text(chrgs, 'Agt/FinInstnId/BICFI')

            # Instructing Agent
            instg = cdt_trf.find('InstgAgt/FinInstnId')
            if instg is not None:
                result['instgAgtBicfi'] = self._get_text(instg, 'BICFI')
                result['instgAgtClrMmbId'] = self._get_text(instg, 'ClrSysMmbId/MmbId')

            # Instructed Agent
            instd_agt = cdt_trf.find('InstdAgt/FinInstnId')
            if instd_agt is not None:
                result['instdAgtBicfi'] = self._get_text(instd_agt, 'BICFI')
                result['instdAgtClrMmbId'] = self._get_text(instd_agt, 'ClrSysMmbId/MmbId')

            # Debtor
            self._parse_party(cdt_trf, 'Dbtr', 'dbtr', result)

            # Debtor Account
            dbtr_acct = cdt_trf.find('DbtrAcct')
            if dbtr_acct is not None:
                result['dbtrAcctIban'] = self._get_text(dbtr_acct, 'Id/IBAN')
                result['dbtrAcctOthrId'] = self._get_text(dbtr_acct, 'Id/Othr/Id')
                result['dbtrAcctTp'] = self._get_text(dbtr_acct, 'Tp/Cd')
                result['dbtrAcctCcy'] = self._get_text(dbtr_acct, 'Ccy')
                result['dbtrAcctNm'] = self._get_text(dbtr_acct, 'Nm')

            # Debtor Agent
            self._parse_agent(cdt_trf, 'DbtrAgt', 'dbtrAgt', result)

            # Creditor
            self._parse_party(cdt_trf, 'Cdtr', 'cdtr', result)

            # Creditor Account
            cdtr_acct = cdt_trf.find('CdtrAcct')
            if cdtr_acct is not None:
                result['cdtrAcctIban'] = self._get_text(cdtr_acct, 'Id/IBAN')
                result['cdtrAcctOthrId'] = self._get_text(cdtr_acct, 'Id/Othr/Id')
                result['cdtrAcctTp'] = self._get_text(cdtr_acct, 'Tp/Cd')
                result['cdtrAcctCcy'] = self._get_text(cdtr_acct, 'Ccy')
                result['cdtrAcctNm'] = self._get_text(cdtr_acct, 'Nm')

            # Creditor Agent
            self._parse_agent(cdt_trf, 'CdtrAgt', 'cdtrAgt', result)

            # Purpose
            purp = cdt_trf.find('Purp')
            if purp is not None:
                result['purpCd'] = self._get_text(purp, 'Cd')
                result['purpPrtry'] = self._get_text(purp, 'Prtry')

            # Remittance Information
            rmt = cdt_trf.find('RmtInf')
            if rmt is not None:
                result['rmtUstrd'] = self._get_text(rmt, 'Ustrd')
                result['rmtCdtrRef'] = self._get_text(rmt, 'Strd/CdtrRefInf/Ref')
                result['rmtAddtlInfo'] = self._get_text(rmt, 'Strd/AddtlRmtInf')

            # Regulatory Reporting
            rgltry = cdt_trf.find('RgltryRptg')
            if rgltry is not None:
                result['rgltryDbtCdtInd'] = self._get_text(rgltry, 'DbtCdtRptgInd')
                result['rgltryAuthrtyCtry'] = self._get_text(rgltry, 'Authrty/Ctry')
                result['rgltryDtlsTp'] = self._get_text(rgltry, 'Dtls/Tp')
                result['rgltryDtlsCd'] = self._get_text(rgltry, 'Dtls/Cd')
                result['rgltryDtlsInf'] = self._get_text(rgltry, 'Dtls/Inf')

        return result

    def _parse_party(self, parent: ET.Element, tag: str, prefix: str, result: Dict):
        """Parse party (Dbtr/Cdtr) fields."""
        party = parent.find(tag)
        if party is None:
            return

        result[f'{prefix}Nm'] = self._get_text(party, 'Nm')

        addr = party.find('PstlAdr')
        if addr is not None:
            result[f'{prefix}StrtNm'] = self._get_text(addr, 'StrtNm')
            result[f'{prefix}BldgNb'] = self._get_text(addr, 'BldgNb')
            result[f'{prefix}PstCd'] = self._get_text(addr, 'PstCd')
            result[f'{prefix}TwnNm'] = self._get_text(addr, 'TwnNm')
            result[f'{prefix}CtrySubDvsn'] = self._get_text(addr, 'CtrySubDvsn')
            result[f'{prefix}Ctry'] = self._get_text(addr, 'Ctry')

        org_id = party.find('Id/OrgId')
        if org_id is not None:
            result[f'{prefix}OrgBic'] = self._get_text(org_id, 'AnyBIC')
            result[f'{prefix}OrgOthrId'] = self._get_text(org_id, 'Othr/Id')

        prvt_id = party.find('Id/PrvtId')
        if prvt_id is not None:
            result[f'{prefix}PrvtId'] = self._get_text(prvt_id, 'Othr/Id')

        ctct = party.find('CtctDtls')
        if ctct is not None:
            result[f'{prefix}PhneNb'] = self._get_text(ctct, 'PhneNb')
            result[f'{prefix}Email'] = self._get_text(ctct, 'EmailAdr')

    def _parse_agent(self, parent: ET.Element, tag: str, prefix: str, result: Dict):
        """Parse agent (DbtrAgt/CdtrAgt) fields."""
        agt = parent.find(tag)
        if agt is None:
            return

        fin_instn = agt.find('FinInstnId')
        if fin_instn is not None:
            result[f'{prefix}Bicfi'] = self._get_text(fin_instn, 'BICFI')
            result[f'{prefix}Lei'] = self._get_text(fin_instn, 'LEI')
            result[f'{prefix}ClrMmbId'] = self._get_text(fin_instn, 'ClrSysMmbId/MmbId')
            result[f'{prefix}ClrSysCd'] = self._get_text(fin_instn, 'ClrSysMmbId/ClrSysId/Cd')
            result[f'{prefix}Nm'] = self._get_text(fin_instn, 'Nm')
            result[f'{prefix}Ctry'] = self._get_text(fin_instn, 'PstlAdr/Ctry')

        brnch = agt.find('BrnchId')
        if brnch is not None:
            result[f'{prefix}BrnchId'] = self._get_text(brnch, 'Id')
            result[f'{prefix}BrnchNm'] = self._get_text(brnch, 'Nm')

    def _get_text(self, elem: ET.Element, path: str) -> Optional[str]:
        """Get text from element path."""
        if elem is None:
            return None
        child = elem.find(path)
        return child.text if child is not None and child.text else None

    def _get_int(self, elem: ET.Element, path: str) -> Optional[int]:
        """Get integer from element path."""
        text = self._get_text(elem, path)
        return int(text) if text else None

    def _get_decimal(self, elem: ET.Element, path: str) -> Optional[float]:
        """Get decimal from element path."""
        text = self._get_text(elem, path)
        return float(text) if text else None

    def _get_decimal_value(self, elem: ET.Element) -> Optional[float]:
        """Get decimal from element text."""
        if elem is not None and elem.text:
            return float(elem.text)
        return None


class InstaPayExtractor(BaseExtractor):
    """Extractor for Philippines InstaPay instant payment messages (ISO 20022 pacs.008).

    ISO 20022 INHERITANCE:
        InstaPay inherits from pacs.008 (FI to FI Customer Credit Transfer).
        The InstapayISO20022Parser inherits from Pacs008Parser.
        Uses Philippine Clearing House Corporation (PCHC) usage guidelines.

    Format Support:
        1. ISO 20022 XML (pacs.008.001.08) - Current standard
        2. Legacy JSON format - Backward compatibility

    InstaPay-Specific Elements:
        - PHPCH clearing system (Philippines Clearing House)
        - PHP currency (Philippine Peso)
        - Real-time instant payments
        - Bank clearing member IDs

    Database Tables:
        - Bronze: bronze.raw_payment_messages
        - Silver: silver.stg_instapay
        - Gold: gold.cdm_payment_instruction + gold.cdm_payment_extension_instapay

    Inheritance Hierarchy:
        BaseExtractor -> InstaPayExtractor
        (Parser: Pacs008Parser -> InstapayISO20022Parser)
    """

    MESSAGE_TYPE = "INSTAPAY"
    SILVER_TABLE = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    DEFAULT_CURRENCY = "PHP"
    CLEARING_SYSTEM = "PHPCH"

    def __init__(self):
        """Initialize InstaPay extractor with ISO 20022 parser."""
        super().__init__()
        self.iso20022_parser = InstapayISO20022Parser()
        self.legacy_parser = InstaPayParser()
        self.parser = self.iso20022_parser

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw InstaPay content."""
        # Handle string content
        if isinstance(raw_content, str):
            content_str = raw_content
            try:
                parsed = self.parser.parse(raw_content)
                msg_id = parsed.get('msgId') or parsed.get('txId') or ''
            except:
                msg_id = ''
        else:
            content_str = json.dumps(raw_content) if isinstance(raw_content, dict) else str(raw_content)
            msg_id = raw_content.get('msgId') or raw_content.get('transactionId') or raw_content.get('referenceNumber') or ''

        return {
            'raw_id': self.generate_raw_id(msg_id),
            'message_type': self.MESSAGE_TYPE,
            'raw_content': content_str,
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
        """Extract all Silver layer fields from InstaPay message."""
        trunc = self.trunc

        # Parse content if it's a string
        if isinstance(msg_content, str):
            parsed = self.parser.parse(msg_content)
        else:
            parsed = msg_content

        return {
            # System columns
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            'message_type': 'INSTAPAY',

            # Group Header
            'msg_id': trunc(parsed.get('msgId'), 35),
            'cre_dt_tm': parsed.get('creDtTm'),
            'nb_of_txs': parsed.get('nbOfTxs'),
            'ttl_intr_bk_sttlm_amt': parsed.get('ttlIntrBkSttlmAmt'),
            'intr_bk_sttlm_dt': parsed.get('intrBkSttlmDt'),
            'sttlm_mtd': trunc(parsed.get('sttlmMtd'), 4),
            'sttlm_clr_sys': trunc(parsed.get('sttlmClrSys'), 5),

            # Payment Identification
            'instr_id': trunc(parsed.get('instrId'), 35),
            'end_to_end_id': trunc(parsed.get('endToEndId'), 35),
            'tx_id': trunc(parsed.get('txId'), 35),
            'uetr': trunc(parsed.get('uetr'), 36),
            'clr_sys_ref': trunc(parsed.get('clrSysRef'), 35),

            # Payment Type Information
            'pmt_tp_instr_prty': trunc(parsed.get('pmtTpInstrPrty'), 4),
            'pmt_tp_svc_lvl': trunc(parsed.get('pmtTpSvcLvl'), 4),
            'pmt_tp_lcl_instrm': trunc(parsed.get('pmtTpLclInstrm'), 35),
            'pmt_tp_ctgy_purp': trunc(parsed.get('pmtTpCtgyPurp'), 4),

            # Amounts
            'intr_bk_sttlm_amt': parsed.get('intrBkSttlmAmt'),
            'intr_bk_sttlm_ccy': trunc(parsed.get('intrBkSttlmCcy'), 3),
            'instd_amt': parsed.get('instdAmt'),
            'instd_amt_ccy': trunc(parsed.get('instdAmtCcy'), 3),
            'xchg_rate': parsed.get('xchgRate'),
            'chrg_br': trunc(parsed.get('chrgBr'), 4),
            'chrgs_amt': parsed.get('chrgsAmt'),
            'chrgs_agt': trunc(parsed.get('chrgsAgt'), 11),

            # Instructing/Instructed Agents
            'instg_agt_bicfi': trunc(parsed.get('instgAgtBicfi'), 11),
            'instg_agt_clr_mmb_id': trunc(parsed.get('instgAgtClrMmbId'), 35),
            'instd_agt_bicfi': trunc(parsed.get('instdAgtBicfi'), 11),
            'instd_agt_clr_mmb_id': trunc(parsed.get('instdAgtClrMmbId'), 35),

            # Debtor
            'dbtr_nm': trunc(parsed.get('dbtrNm'), 140),
            'dbtr_strt_nm': trunc(parsed.get('dbtrStrtNm'), 70),
            'dbtr_bldg_nb': trunc(parsed.get('dbtrBldgNb'), 16),
            'dbtr_pst_cd': trunc(parsed.get('dbtrPstCd'), 16),
            'dbtr_twn_nm': trunc(parsed.get('dbtrTwnNm'), 35),
            'dbtr_ctry_sub_dvsn': trunc(parsed.get('dbtrCtrySubDvsn'), 35),
            'dbtr_ctry': trunc(parsed.get('dbtrCtry'), 2),
            'dbtr_org_bic': trunc(parsed.get('dbtrOrgBic'), 11),
            'dbtr_org_othr_id': trunc(parsed.get('dbtrOrgOthrId'), 35),
            'dbtr_prvt_id': trunc(parsed.get('dbtrPrvtId'), 35),
            'dbtr_phne_nb': trunc(parsed.get('dbtrPhneNb'), 35),
            'dbtr_email': trunc(parsed.get('dbtrEmail'), 256),

            # Debtor Account
            'dbtr_acct_iban': trunc(parsed.get('dbtrAcctIban'), 34),
            'dbtr_acct_othr_id': trunc(parsed.get('dbtrAcctOthrId'), 34),
            'dbtr_acct_tp': trunc(parsed.get('dbtrAcctTp'), 4),
            'dbtr_acct_ccy': trunc(parsed.get('dbtrAcctCcy'), 3),
            'dbtr_acct_nm': trunc(parsed.get('dbtrAcctNm'), 70),

            # Debtor Agent
            'dbtr_agt_bicfi': trunc(parsed.get('dbtrAgtBicfi'), 11),
            'dbtr_agt_lei': trunc(parsed.get('dbtrAgtLei'), 20),
            'dbtr_agt_clr_mmb_id': trunc(parsed.get('dbtrAgtClrMmbId'), 35),
            'dbtr_agt_clr_sys_cd': trunc(parsed.get('dbtrAgtClrSysCd'), 5),
            'dbtr_agt_nm': trunc(parsed.get('dbtrAgtNm'), 140),
            'dbtr_agt_ctry': trunc(parsed.get('dbtrAgtCtry'), 2),
            'dbtr_agt_brnch_id': trunc(parsed.get('dbtrAgtBrnchId'), 35),
            'dbtr_agt_brnch_nm': trunc(parsed.get('dbtrAgtBrnchNm'), 140),

            # Creditor
            'cdtr_nm': trunc(parsed.get('cdtrNm'), 140),
            'cdtr_strt_nm': trunc(parsed.get('cdtrStrtNm'), 70),
            'cdtr_bldg_nb': trunc(parsed.get('cdtrBldgNb'), 16),
            'cdtr_pst_cd': trunc(parsed.get('cdtrPstCd'), 16),
            'cdtr_twn_nm': trunc(parsed.get('cdtrTwnNm'), 35),
            'cdtr_ctry_sub_dvsn': trunc(parsed.get('cdtrCtrySubDvsn'), 35),
            'cdtr_ctry': trunc(parsed.get('cdtrCtry'), 2),
            'cdtr_org_bic': trunc(parsed.get('cdtrOrgBic'), 11),
            'cdtr_org_othr_id': trunc(parsed.get('cdtrOrgOthrId'), 35),
            'cdtr_prvt_id': trunc(parsed.get('cdtrPrvtId'), 35),
            'cdtr_phne_nb': trunc(parsed.get('cdtrPhneNb'), 35),
            'cdtr_email': trunc(parsed.get('cdtrEmail'), 256),

            # Creditor Account
            'cdtr_acct_iban': trunc(parsed.get('cdtrAcctIban'), 34),
            'cdtr_acct_othr_id': trunc(parsed.get('cdtrAcctOthrId'), 34),
            'cdtr_acct_tp': trunc(parsed.get('cdtrAcctTp'), 4),
            'cdtr_acct_ccy': trunc(parsed.get('cdtrAcctCcy'), 3),
            'cdtr_acct_nm': trunc(parsed.get('cdtrAcctNm'), 70),

            # Creditor Agent
            'cdtr_agt_bicfi': trunc(parsed.get('cdtrAgtBicfi'), 11),
            'cdtr_agt_lei': trunc(parsed.get('cdtrAgtLei'), 20),
            'cdtr_agt_clr_mmb_id': trunc(parsed.get('cdtrAgtClrMmbId'), 35),
            'cdtr_agt_clr_sys_cd': trunc(parsed.get('cdtrAgtClrSysCd'), 5),
            'cdtr_agt_nm': trunc(parsed.get('cdtrAgtNm'), 140),
            'cdtr_agt_ctry': trunc(parsed.get('cdtrAgtCtry'), 2),
            'cdtr_agt_brnch_id': trunc(parsed.get('cdtrAgtBrnchId'), 35),
            'cdtr_agt_brnch_nm': trunc(parsed.get('cdtrAgtBrnchNm'), 140),

            # Purpose
            'purp_cd': trunc(parsed.get('purpCd'), 4),
            'purp_prtry': trunc(parsed.get('purpPrtry'), 35),

            # Remittance Information
            'rmt_ustrd': parsed.get('rmtUstrd'),
            'rmt_cdtr_ref': trunc(parsed.get('rmtCdtrRef'), 35),
            'rmt_addtl_info': parsed.get('rmtAddtlInfo'),

            # Regulatory Reporting
            'rgltry_dbt_cdt_ind': trunc(parsed.get('rgltryDbtCdtInd'), 4),
            'rgltry_authrty_ctry': trunc(parsed.get('rgltryAuthrtyCtry'), 2),
            'rgltry_dtls_tp': trunc(parsed.get('rgltryDtlsTp'), 35),
            'rgltry_dtls_cd': trunc(parsed.get('rgltryDtlsCd'), 10),
            'rgltry_dtls_inf': parsed.get('rgltryDtlsInf'),

            # Legacy columns (for backward compatibility)
            'transaction_id': trunc(parsed.get('txId') or parsed.get('transactionId'), 35),
            'creation_date_time': parsed.get('creDtTm') or parsed.get('creationDateTime'),
            'amount': parsed.get('intrBkSttlmAmt') or parsed.get('amount'),
            'currency': trunc(parsed.get('intrBkSttlmCcy') or parsed.get('currency') or 'PHP', 3),
            'sender_bank_code': trunc(parsed.get('dbtrAgtClrMmbId') or parsed.get('senderBankCode'), 11),
            'sender_account': trunc(parsed.get('dbtrAcctOthrId') or parsed.get('dbtrAcctIban') or parsed.get('senderAccount'), 34),
            'sender_name': trunc(parsed.get('dbtrNm') or parsed.get('senderName'), 140),
            'receiver_bank_code': trunc(parsed.get('cdtrAgtClrMmbId') or parsed.get('receiverBankCode'), 11),
            'receiver_account': trunc(parsed.get('cdtrAcctOthrId') or parsed.get('cdtrAcctIban') or parsed.get('receiverAccount'), 34),
            'receiver_name': trunc(parsed.get('cdtrNm') or parsed.get('receiverName'), 140),
            'reference_number': trunc(parsed.get('endToEndId') or parsed.get('referenceNumber'), 35),
            'remittance_info': parsed.get('rmtUstrd') or parsed.get('remittanceInfo'),
            'message_id': trunc(parsed.get('msgId') or parsed.get('messageId'), 35),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            # System columns
            'stg_id', 'raw_id', '_batch_id', 'message_type',

            # Group Header
            'msg_id', 'cre_dt_tm', 'nb_of_txs', 'ttl_intr_bk_sttlm_amt',
            'intr_bk_sttlm_dt', 'sttlm_mtd', 'sttlm_clr_sys',

            # Payment Identification
            'instr_id', 'end_to_end_id', 'tx_id', 'uetr', 'clr_sys_ref',

            # Payment Type Information
            'pmt_tp_instr_prty', 'pmt_tp_svc_lvl', 'pmt_tp_lcl_instrm', 'pmt_tp_ctgy_purp',

            # Amounts
            'intr_bk_sttlm_amt', 'intr_bk_sttlm_ccy', 'instd_amt', 'instd_amt_ccy',
            'xchg_rate', 'chrg_br', 'chrgs_amt', 'chrgs_agt',

            # Instructing/Instructed Agents
            'instg_agt_bicfi', 'instg_agt_clr_mmb_id', 'instd_agt_bicfi', 'instd_agt_clr_mmb_id',

            # Debtor
            'dbtr_nm', 'dbtr_strt_nm', 'dbtr_bldg_nb', 'dbtr_pst_cd',
            'dbtr_twn_nm', 'dbtr_ctry_sub_dvsn', 'dbtr_ctry',
            'dbtr_org_bic', 'dbtr_org_othr_id', 'dbtr_prvt_id',
            'dbtr_phne_nb', 'dbtr_email',

            # Debtor Account
            'dbtr_acct_iban', 'dbtr_acct_othr_id', 'dbtr_acct_tp', 'dbtr_acct_ccy', 'dbtr_acct_nm',

            # Debtor Agent
            'dbtr_agt_bicfi', 'dbtr_agt_lei', 'dbtr_agt_clr_mmb_id', 'dbtr_agt_clr_sys_cd',
            'dbtr_agt_nm', 'dbtr_agt_ctry', 'dbtr_agt_brnch_id', 'dbtr_agt_brnch_nm',

            # Creditor
            'cdtr_nm', 'cdtr_strt_nm', 'cdtr_bldg_nb', 'cdtr_pst_cd',
            'cdtr_twn_nm', 'cdtr_ctry_sub_dvsn', 'cdtr_ctry',
            'cdtr_org_bic', 'cdtr_org_othr_id', 'cdtr_prvt_id',
            'cdtr_phne_nb', 'cdtr_email',

            # Creditor Account
            'cdtr_acct_iban', 'cdtr_acct_othr_id', 'cdtr_acct_tp', 'cdtr_acct_ccy', 'cdtr_acct_nm',

            # Creditor Agent
            'cdtr_agt_bicfi', 'cdtr_agt_lei', 'cdtr_agt_clr_mmb_id', 'cdtr_agt_clr_sys_cd',
            'cdtr_agt_nm', 'cdtr_agt_ctry', 'cdtr_agt_brnch_id', 'cdtr_agt_brnch_nm',

            # Purpose
            'purp_cd', 'purp_prtry',

            # Remittance Information
            'rmt_ustrd', 'rmt_cdtr_ref', 'rmt_addtl_info',

            # Regulatory Reporting
            'rgltry_dbt_cdt_ind', 'rgltry_authrty_ctry', 'rgltry_dtls_tp', 'rgltry_dtls_cd', 'rgltry_dtls_inf',

            # Legacy columns
            'transaction_id', 'creation_date_time', 'amount', 'currency',
            'sender_bank_code', 'sender_account', 'sender_name',
            'receiver_bank_code', 'receiver_account', 'receiver_name',
            'reference_number', 'remittance_info', 'message_id',
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
        """Extract Gold layer entities from InstaPay Silver record.

        Args:
            silver_data: Dict with Silver table columns (snake_case field names)
            stg_id: Silver staging ID
            batch_id: Batch identifier
        """
        entities = GoldEntities()

        # Debtor Party
        dbtr_name = silver_data.get('dbtr_nm') or silver_data.get('sender_name')
        if dbtr_name:
            entities.parties.append(PartyData(
                name=dbtr_name,
                role="DEBTOR",
                party_type='UNKNOWN',
                country=silver_data.get('dbtr_ctry') or 'PH',
                street_name=silver_data.get('dbtr_strt_nm'),
                building_number=silver_data.get('dbtr_bldg_nb'),
                post_code=silver_data.get('dbtr_pst_cd'),
                town_name=silver_data.get('dbtr_twn_nm'),
                country_sub_division=silver_data.get('dbtr_ctry_sub_dvsn'),
                org_id=silver_data.get('dbtr_org_othr_id'),
                private_id=silver_data.get('dbtr_prvt_id'),
                phone=silver_data.get('dbtr_phne_nb'),
                email=silver_data.get('dbtr_email'),
            ))

        # Creditor Party
        cdtr_name = silver_data.get('cdtr_nm') or silver_data.get('receiver_name')
        if cdtr_name:
            entities.parties.append(PartyData(
                name=cdtr_name,
                role="CREDITOR",
                party_type='UNKNOWN',
                country=silver_data.get('cdtr_ctry') or 'PH',
                street_name=silver_data.get('cdtr_strt_nm'),
                building_number=silver_data.get('cdtr_bldg_nb'),
                post_code=silver_data.get('cdtr_pst_cd'),
                town_name=silver_data.get('cdtr_twn_nm'),
                country_sub_division=silver_data.get('cdtr_ctry_sub_dvsn'),
                org_id=silver_data.get('cdtr_org_othr_id'),
                private_id=silver_data.get('cdtr_prvt_id'),
                phone=silver_data.get('cdtr_phne_nb'),
                email=silver_data.get('cdtr_email'),
            ))

        # Debtor Account
        dbtr_acct = silver_data.get('dbtr_acct_othr_id') or silver_data.get('dbtr_acct_iban') or silver_data.get('sender_account')
        if dbtr_acct:
            entities.accounts.append(AccountData(
                account_number=dbtr_acct,
                role="DEBTOR",
                account_type=silver_data.get('dbtr_acct_tp') or 'CACC',
                currency=silver_data.get('dbtr_acct_ccy') or silver_data.get('intr_bk_sttlm_ccy') or silver_data.get('currency') or 'PHP',
                account_name=silver_data.get('dbtr_acct_nm'),
                iban=silver_data.get('dbtr_acct_iban'),
            ))

        # Creditor Account
        cdtr_acct = silver_data.get('cdtr_acct_othr_id') or silver_data.get('cdtr_acct_iban') or silver_data.get('receiver_account')
        if cdtr_acct:
            entities.accounts.append(AccountData(
                account_number=cdtr_acct,
                role="CREDITOR",
                account_type=silver_data.get('cdtr_acct_tp') or 'CACC',
                currency=silver_data.get('cdtr_acct_ccy') or silver_data.get('intr_bk_sttlm_ccy') or silver_data.get('currency') or 'PHP',
                account_name=silver_data.get('cdtr_acct_nm'),
                iban=silver_data.get('cdtr_acct_iban'),
            ))

        # Debtor Agent
        dbtr_agt_code = silver_data.get('dbtr_agt_clr_mmb_id') or silver_data.get('dbtr_agt_bicfi') or silver_data.get('sender_bank_code')
        if dbtr_agt_code:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                bic=silver_data.get('dbtr_agt_bicfi'),
                lei=silver_data.get('dbtr_agt_lei'),
                clearing_code=silver_data.get('dbtr_agt_clr_mmb_id'),
                clearing_system=silver_data.get('dbtr_agt_clr_sys_cd') or 'PHINSTAPAY',
                name=silver_data.get('dbtr_agt_nm'),
                country=silver_data.get('dbtr_agt_ctry') or 'PH',
                branch_id=silver_data.get('dbtr_agt_brnch_id'),
                branch_name=silver_data.get('dbtr_agt_brnch_nm'),
            ))

        # Creditor Agent
        cdtr_agt_code = silver_data.get('cdtr_agt_clr_mmb_id') or silver_data.get('cdtr_agt_bicfi') or silver_data.get('receiver_bank_code')
        if cdtr_agt_code:
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                bic=silver_data.get('cdtr_agt_bicfi'),
                lei=silver_data.get('cdtr_agt_lei'),
                clearing_code=silver_data.get('cdtr_agt_clr_mmb_id'),
                clearing_system=silver_data.get('cdtr_agt_clr_sys_cd') or 'PHINSTAPAY',
                name=silver_data.get('cdtr_agt_nm'),
                country=silver_data.get('cdtr_agt_ctry') or 'PH',
                branch_id=silver_data.get('cdtr_agt_brnch_id'),
                branch_name=silver_data.get('cdtr_agt_brnch_nm'),
            ))

        # Instructing Agent
        if silver_data.get('instg_agt_bicfi') or silver_data.get('instg_agt_clr_mmb_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTING_AGENT",
                bic=silver_data.get('instg_agt_bicfi'),
                clearing_code=silver_data.get('instg_agt_clr_mmb_id'),
                clearing_system='PHINSTAPAY',
                country='PH',
            ))

        # Instructed Agent
        if silver_data.get('instd_agt_bicfi') or silver_data.get('instd_agt_clr_mmb_id'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTED_AGENT",
                bic=silver_data.get('instd_agt_bicfi'),
                clearing_code=silver_data.get('instd_agt_clr_mmb_id'),
                clearing_system='PHINSTAPAY',
                country='PH',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('INSTAPAY', InstaPayExtractor())
ExtractorRegistry.register('instapay', InstaPayExtractor())
ExtractorRegistry.register('InstaPay', InstaPayExtractor())

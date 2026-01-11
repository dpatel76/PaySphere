"""ISO 20022 pain.008 Parser and Extractor base classes.

pain.008 (Customer Direct Debit Initiation) is used by creditors to initiate
direct debit collections from debtor accounts. Key elements:
- GrpHdr: Group header with batch identification
- PmtInf: Payment information with creditor details
- DrctDbtTxInf: Direct debit transaction details with mandate information

Systems using pain.008:
- SEPA Direct Debit (SDD) - Core and B2B schemes
- Other direct debit clearing systems

Reference: ISO 20022 Message Definition Report - pain.008.001.08
"""

from typing import Dict, Any, List, Optional
import logging

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor

logger = logging.getLogger(__name__)


class Pain008Parser(BaseISO20022Parser):
    """Base parser for pain.008 Customer Direct Debit Initiation messages.

    pain.008 is used for direct debit collections. The structure differs from
    credit transfers - the creditor initiates collection from debtor accounts.

    pain.008 structure:
    - Document
      - CstmrDrctDbtInitn
        - GrpHdr (Group Header)
        - PmtInf (Payment Information) [1..*]
          - DrctDbtTxInf (Direct Debit Transaction Info) [1..*]
    """

    ROOT_ELEMENT = "CstmrDrctDbtInitn"
    MESSAGE_TYPE = "pain.008"

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse pain.008 Customer Direct Debit Initiation message.

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pain.008 fields
        """
        root = self._parse_xml(xml_content)

        # Find the CstmrDrctDbtInitn element
        dd_initn = self._find(root, self.ROOT_ELEMENT)
        if dd_initn is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                dd_initn = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pain.008 message")

        return self._parse_direct_debit_initiation(dd_initn)

    def _parse_direct_debit_initiation(self, dd_initn) -> Dict[str, Any]:
        """Parse CstmrDrctDbtInitn element.

        Args:
            dd_initn: CstmrDrctDbtInitn element

        Returns:
            Dict with extracted fields
        """
        result = {
            'isISO20022': True,
            'messageTypeCode': 'pain.008',
        }

        # Extract Group Header
        result.update(self._extract_dd_group_header(dd_initn))

        # Extract first Payment Information block
        pmt_inf = self._find(dd_initn, 'PmtInf')
        if pmt_inf is not None:
            result.update(self._parse_payment_info(pmt_inf))

        return result

    def _extract_dd_group_header(self, dd_initn: 'ET.Element') -> Dict[str, Any]:
        """Extract Group Header for direct debit initiation.

        Args:
            dd_initn: CstmrDrctDbtInitn element

        Returns:
            Dict with group header fields
        """
        result = {}
        grp_hdr = self._find(dd_initn, 'GrpHdr')

        if grp_hdr is None:
            return result

        result['messageId'] = self._find_text(grp_hdr, 'MsgId')
        result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
        result['numberOfTransactions'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))
        result['controlSum'] = self._safe_float(self._find_text(grp_hdr, 'CtrlSum'))

        # Initiating Party
        initg_pty = self._find(grp_hdr, 'InitgPty')
        if initg_pty:
            result['initiatingPartyName'] = self._find_text(initg_pty, 'Nm')
            result['initiatingPartyId'] = self._find_text(initg_pty, 'Id/OrgId/Othr/Id')

        return result

    def _parse_payment_info(self, pmt_inf: 'ET.Element') -> Dict[str, Any]:
        """Parse PmtInf element for direct debit.

        Args:
            pmt_inf: PmtInf element

        Returns:
            Dict with payment information fields
        """
        result = {}

        # Payment Information Identification
        result['paymentInformationId'] = self._find_text(pmt_inf, 'PmtInfId')
        result['paymentMethod'] = self._find_text(pmt_inf, 'PmtMtd')  # Should be 'DD'
        result['batchBooking'] = self._find_text(pmt_inf, 'BtchBookg')
        result['pmtInfNumberOfTransactions'] = self._safe_int(self._find_text(pmt_inf, 'NbOfTxs'))
        result['pmtInfControlSum'] = self._safe_float(self._find_text(pmt_inf, 'CtrlSum'))

        # Payment Type Information
        pmt_tp_inf = self._find(pmt_inf, 'PmtTpInf')
        if pmt_tp_inf:
            result['serviceLevel'] = self._find_text(pmt_tp_inf, 'SvcLvl/Cd')
            result['localInstrument'] = self._find_text(pmt_tp_inf, 'LclInstrm/Cd')
            result['sequenceType'] = self._find_text(pmt_tp_inf, 'SeqTp')  # FRST, RCUR, FNAL, OOFF
            result['categoryPurpose'] = self._find_text(pmt_tp_inf, 'CtgyPurp/Cd')

        # Requested Collection Date
        result['requestedCollectionDate'] = self._find_text(pmt_inf, 'ReqdColltnDt')

        # Creditor (the party initiating the direct debit)
        cdtr = self._find(pmt_inf, 'Cdtr')
        if cdtr:
            result['creditorName'] = self._find_text(cdtr, 'Nm')
            pstl_adr = self._find(cdtr, 'PstlAdr')
            if pstl_adr:
                result['creditorStreetName'] = self._find_text(pstl_adr, 'StrtNm')
                result['creditorBuildingNumber'] = self._find_text(pstl_adr, 'BldgNb')
                result['creditorPostCode'] = self._find_text(pstl_adr, 'PstCd')
                result['creditorTownName'] = self._find_text(pstl_adr, 'TwnNm')
                result['creditorCountry'] = self._find_text(pstl_adr, 'Ctry')

        # Creditor Account
        cdtr_acct = self._find(pmt_inf, 'CdtrAcct')
        if cdtr_acct:
            result['creditorIBAN'] = self._find_text(cdtr_acct, 'Id/IBAN')
            result['creditorAccountOther'] = self._find_text(cdtr_acct, 'Id/Othr/Id')

        # Creditor Agent (Creditor's bank)
        cdtr_agt = self._find(pmt_inf, 'CdtrAgt')
        if cdtr_agt:
            result['creditorAgentBIC'] = self._find_text(cdtr_agt, 'FinInstnId/BICFI')
            result['creditorAgentName'] = self._find_text(cdtr_agt, 'FinInstnId/Nm')

        # Creditor Scheme Identification (for SEPA SDD)
        cdtr_schme_id = self._find(pmt_inf, 'CdtrSchmeId')
        if cdtr_schme_id:
            result['creditorSchemeId'] = self._find_text(cdtr_schme_id, 'Id/PrvtId/Othr/Id')
            result['creditorSchemeName'] = self._find_text(cdtr_schme_id, 'Id/PrvtId/Othr/SchmeNm/Prtry')

        # Extract first Direct Debit Transaction
        drct_dbt_tx_inf = self._find(pmt_inf, 'DrctDbtTxInf')
        if drct_dbt_tx_inf:
            result.update(self._parse_direct_debit_tx(drct_dbt_tx_inf))

        return result

    def _parse_direct_debit_tx(self, dd_tx: 'ET.Element') -> Dict[str, Any]:
        """Parse DrctDbtTxInf element.

        Args:
            dd_tx: DrctDbtTxInf element

        Returns:
            Dict with direct debit transaction fields
        """
        result = {}

        # Payment Identification
        pmt_id = self._find(dd_tx, 'PmtId')
        if pmt_id:
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')

        # Instructed Amount
        instd_amt = self._find(dd_tx, 'InstdAmt')
        if instd_amt is not None:
            result['amount'] = self._safe_float(instd_amt.text)
            result['currency'] = instd_amt.get('Ccy')

        # Direct Debit Transaction (Mandate Information)
        drct_dbt_tx = self._find(dd_tx, 'DrctDbtTx')
        if drct_dbt_tx:
            mndt_rltd_inf = self._find(drct_dbt_tx, 'MndtRltdInf')
            if mndt_rltd_inf:
                result['mandateId'] = self._find_text(mndt_rltd_inf, 'MndtId')
                result['mandateDateOfSignature'] = self._find_text(mndt_rltd_inf, 'DtOfSgntr')
                result['amendmentIndicator'] = self._find_text(mndt_rltd_inf, 'AmdmntInd')

                # Amendment Information Details
                amdmnt_inf_dtls = self._find(mndt_rltd_inf, 'AmdmntInfDtls')
                if amdmnt_inf_dtls:
                    result['originalMandateId'] = self._find_text(amdmnt_inf_dtls, 'OrgnlMndtId')
                    result['originalDebtorAccount'] = self._find_text(amdmnt_inf_dtls, 'OrgnlDbtrAcct/Id/IBAN')
                    result['originalDebtorAgentBIC'] = self._find_text(amdmnt_inf_dtls, 'OrgnlDbtrAgt/FinInstnId/BICFI')

            # Creditor Scheme ID at transaction level
            result['txCreditorSchemeId'] = self._find_text(drct_dbt_tx, 'CdtrSchmeId/Id/PrvtId/Othr/Id')

        # Debtor Agent (Debtor's bank)
        dbtr_agt = self._find(dd_tx, 'DbtrAgt')
        if dbtr_agt:
            result['debtorAgentBIC'] = self._find_text(dbtr_agt, 'FinInstnId/BICFI')
            result['debtorAgentName'] = self._find_text(dbtr_agt, 'FinInstnId/Nm')

        # Debtor (the party being debited)
        dbtr = self._find(dd_tx, 'Dbtr')
        if dbtr:
            result['debtorName'] = self._find_text(dbtr, 'Nm')
            pstl_adr = self._find(dbtr, 'PstlAdr')
            if pstl_adr:
                result['debtorStreetName'] = self._find_text(pstl_adr, 'StrtNm')
                result['debtorBuildingNumber'] = self._find_text(pstl_adr, 'BldgNb')
                result['debtorPostCode'] = self._find_text(pstl_adr, 'PstCd')
                result['debtorTownName'] = self._find_text(pstl_adr, 'TwnNm')
                result['debtorCountry'] = self._find_text(pstl_adr, 'Ctry')

        # Debtor Account
        dbtr_acct = self._find(dd_tx, 'DbtrAcct')
        if dbtr_acct:
            result['debtorIBAN'] = self._find_text(dbtr_acct, 'Id/IBAN')
            result['debtorAccountOther'] = self._find_text(dbtr_acct, 'Id/Othr/Id')

        # Ultimate Creditor (if different from creditor)
        ultmt_cdtr = self._find(dd_tx, 'UltmtCdtr')
        if ultmt_cdtr:
            result['ultimateCreditorName'] = self._find_text(ultmt_cdtr, 'Nm')

        # Ultimate Debtor (if different from debtor)
        ultmt_dbtr = self._find(dd_tx, 'UltmtDbtr')
        if ultmt_dbtr:
            result['ultimateDebtorName'] = self._find_text(ultmt_dbtr, 'Nm')

        # Purpose
        purp = self._find(dd_tx, 'Purp')
        if purp:
            result['purposeCode'] = self._find_text(purp, 'Cd')

        # Remittance Information
        rmt_inf = self._find(dd_tx, 'RmtInf')
        if rmt_inf:
            result['remittanceUnstructured'] = self._find_text(rmt_inf, 'Ustrd')

        return result

    # ==========================================================================
    # ISO PATH KEY NAMING METHODS (DOT-NOTATION)
    # ==========================================================================

    def parse_iso_paths(self, xml_content: str) -> Dict[str, Any]:
        """Parse pain.008 message using full ISO path key naming.

        Returns keys in dot-notation format matching ISO 20022 element paths:
        - GrpHdr.MsgId, GrpHdr.CreDtTm, GrpHdr.InitgPty.Nm
        - PmtInf.PmtInfId, PmtInf.PmtMtd, PmtInf.ReqdColltnDt
        - PmtInf.Cdtr.Nm, PmtInf.CdtrAcct.Id.IBAN
        - PmtInf.DrctDbtTxInf.PmtId.EndToEndId
        - PmtInf.DrctDbtTxInf.DrctDbtTx.MndtRltdInf.MndtId

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pain.008 fields using full ISO path keys
        """
        root = self._parse_xml(xml_content)

        # Find the CstmrDrctDbtInitn element
        dd_initn = self._find(root, self.ROOT_ELEMENT)
        if dd_initn is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                dd_initn = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pain.008 message")

        result = {
            'isISO20022': True,
            'messageTypeCode': 'pain.008',
        }

        # Extract Group Header
        result.update(self._extract_dd_group_header_iso_path(dd_initn))

        # Extract first Payment Information block
        pmt_inf = self._find(dd_initn, 'PmtInf')
        if pmt_inf is not None:
            result.update(self._parse_payment_info_iso_paths(pmt_inf))

        return result

    def _extract_dd_group_header_iso_path(self, dd_initn: 'ET.Element') -> Dict[str, Any]:
        """Extract Group Header using ISO path keys.

        Args:
            dd_initn: CstmrDrctDbtInitn element

        Returns:
            Dict with ISO path keys like 'GrpHdr.MsgId', 'GrpHdr.InitgPty.Nm'
        """
        result = {}
        grp_hdr = self._find(dd_initn, 'GrpHdr')

        if grp_hdr is None:
            return result

        result['GrpHdr.MsgId'] = self._find_text(grp_hdr, 'MsgId')
        result['GrpHdr.CreDtTm'] = self._find_text(grp_hdr, 'CreDtTm')
        result['GrpHdr.NbOfTxs'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))
        result['GrpHdr.CtrlSum'] = self._safe_float(self._find_text(grp_hdr, 'CtrlSum'))

        # Initiating Party
        initg_pty = self._find(grp_hdr, 'InitgPty')
        if initg_pty:
            result.update(self._extract_party_iso_path(initg_pty, 'GrpHdr.InitgPty'))

        return result

    def _parse_payment_info_iso_paths(self, pmt_inf: 'ET.Element') -> Dict[str, Any]:
        """Parse PmtInf element using ISO path keys.

        Args:
            pmt_inf: PmtInf element

        Returns:
            Dict with ISO path keys like 'PmtInf.PmtInfId', 'PmtInf.Cdtr.Nm'
        """
        result = {}
        prefix = 'PmtInf'

        # Payment Information Identification
        result[f'{prefix}.PmtInfId'] = self._find_text(pmt_inf, 'PmtInfId')
        result[f'{prefix}.PmtMtd'] = self._find_text(pmt_inf, 'PmtMtd')
        result[f'{prefix}.BtchBookg'] = self._find_text(pmt_inf, 'BtchBookg')
        result[f'{prefix}.NbOfTxs'] = self._safe_int(self._find_text(pmt_inf, 'NbOfTxs'))
        result[f'{prefix}.CtrlSum'] = self._safe_float(self._find_text(pmt_inf, 'CtrlSum'))

        # Payment Type Information
        pmt_tp_inf = self._find(pmt_inf, 'PmtTpInf')
        if pmt_tp_inf:
            result.update(self._extract_payment_type_info_iso_path(pmt_tp_inf, f'{prefix}.PmtTpInf'))

        # Requested Collection Date
        result[f'{prefix}.ReqdColltnDt'] = self._find_text(pmt_inf, 'ReqdColltnDt')

        # Creditor (the party initiating the direct debit)
        cdtr = self._find(pmt_inf, 'Cdtr')
        if cdtr:
            result.update(self._extract_party_iso_path(cdtr, f'{prefix}.Cdtr'))

        # Creditor Account
        cdtr_acct = self._find(pmt_inf, 'CdtrAcct')
        if cdtr_acct:
            result.update(self._extract_account_iso_path(cdtr_acct, f'{prefix}.CdtrAcct'))

        # Creditor Agent
        cdtr_agt = self._find(pmt_inf, 'CdtrAgt')
        if cdtr_agt:
            result.update(self._extract_financial_institution_iso_path(cdtr_agt, f'{prefix}.CdtrAgt'))

        # Creditor Scheme Identification
        cdtr_schme_id = self._find(pmt_inf, 'CdtrSchmeId')
        if cdtr_schme_id:
            schme_prefix = f'{prefix}.CdtrSchmeId'
            result[f'{schme_prefix}.Id.PrvtId.Othr.Id'] = self._find_text(
                cdtr_schme_id, 'Id/PrvtId/Othr/Id'
            )
            result[f'{schme_prefix}.Id.PrvtId.Othr.SchmeNm.Prtry'] = self._find_text(
                cdtr_schme_id, 'Id/PrvtId/Othr/SchmeNm/Prtry'
            )
            result[f'{schme_prefix}.Id.PrvtId.Othr.SchmeNm.Cd'] = self._find_text(
                cdtr_schme_id, 'Id/PrvtId/Othr/SchmeNm/Cd'
            )

        # Extract first Direct Debit Transaction
        drct_dbt_tx_inf = self._find(pmt_inf, 'DrctDbtTxInf')
        if drct_dbt_tx_inf:
            result.update(self._parse_direct_debit_tx_iso_paths(drct_dbt_tx_inf))

        return result

    def _parse_direct_debit_tx_iso_paths(self, dd_tx: 'ET.Element') -> Dict[str, Any]:
        """Parse DrctDbtTxInf element using ISO path keys.

        Args:
            dd_tx: DrctDbtTxInf element

        Returns:
            Dict with ISO path keys like 'PmtInf.DrctDbtTxInf.PmtId.EndToEndId'
        """
        result = {}
        prefix = 'PmtInf.DrctDbtTxInf'

        # Payment Identification
        pmt_id = self._find(dd_tx, 'PmtId')
        if pmt_id:
            result.update(self._extract_payment_id_iso_path(pmt_id, f'{prefix}.PmtId'))

        # Instructed Amount
        result.update(self._extract_amount_iso_path(dd_tx, 'InstdAmt', prefix))

        # Charge Bearer
        result[f'{prefix}.ChrgBr'] = self._find_text(dd_tx, 'ChrgBr')

        # Direct Debit Transaction (Mandate Information)
        drct_dbt_tx = self._find(dd_tx, 'DrctDbtTx')
        if drct_dbt_tx:
            mndt_prefix = f'{prefix}.DrctDbtTx.MndtRltdInf'
            mndt_rltd_inf = self._find(drct_dbt_tx, 'MndtRltdInf')
            if mndt_rltd_inf:
                result[f'{mndt_prefix}.MndtId'] = self._find_text(mndt_rltd_inf, 'MndtId')
                result[f'{mndt_prefix}.DtOfSgntr'] = self._find_text(mndt_rltd_inf, 'DtOfSgntr')
                result[f'{mndt_prefix}.AmdmntInd'] = self._find_text(mndt_rltd_inf, 'AmdmntInd')

                # Amendment Information Details
                amdmnt_inf_dtls = self._find(mndt_rltd_inf, 'AmdmntInfDtls')
                if amdmnt_inf_dtls:
                    amdmnt_prefix = f'{mndt_prefix}.AmdmntInfDtls'
                    result[f'{amdmnt_prefix}.OrgnlMndtId'] = self._find_text(
                        amdmnt_inf_dtls, 'OrgnlMndtId'
                    )
                    result[f'{amdmnt_prefix}.OrgnlDbtrAcct.Id.IBAN'] = self._find_text(
                        amdmnt_inf_dtls, 'OrgnlDbtrAcct/Id/IBAN'
                    )
                    result[f'{amdmnt_prefix}.OrgnlDbtrAgt.FinInstnId.BICFI'] = self._find_text(
                        amdmnt_inf_dtls, 'OrgnlDbtrAgt/FinInstnId/BICFI'
                    )

            # Creditor Scheme ID at transaction level
            result[f'{prefix}.DrctDbtTx.CdtrSchmeId.Id.PrvtId.Othr.Id'] = self._find_text(
                drct_dbt_tx, 'CdtrSchmeId/Id/PrvtId/Othr/Id'
            )

        # Debtor Agent
        dbtr_agt = self._find(dd_tx, 'DbtrAgt')
        if dbtr_agt:
            result.update(self._extract_financial_institution_iso_path(dbtr_agt, f'{prefix}.DbtrAgt'))

        # Debtor
        dbtr = self._find(dd_tx, 'Dbtr')
        if dbtr:
            result.update(self._extract_party_iso_path(dbtr, f'{prefix}.Dbtr'))

        # Debtor Account
        dbtr_acct = self._find(dd_tx, 'DbtrAcct')
        if dbtr_acct:
            result.update(self._extract_account_iso_path(dbtr_acct, f'{prefix}.DbtrAcct'))

        # Ultimate Creditor
        ultmt_cdtr = self._find(dd_tx, 'UltmtCdtr')
        if ultmt_cdtr:
            result.update(self._extract_party_iso_path(ultmt_cdtr, f'{prefix}.UltmtCdtr'))

        # Ultimate Debtor
        ultmt_dbtr = self._find(dd_tx, 'UltmtDbtr')
        if ultmt_dbtr:
            result.update(self._extract_party_iso_path(ultmt_dbtr, f'{prefix}.UltmtDbtr'))

        # Purpose
        purp = self._find(dd_tx, 'Purp')
        if purp:
            result[f'{prefix}.Purp.Cd'] = self._find_text(purp, 'Cd')
            result[f'{prefix}.Purp.Prtry'] = self._find_text(purp, 'Prtry')

        # Remittance Information
        rmt_inf = self._find(dd_tx, 'RmtInf')
        if rmt_inf:
            result.update(self._extract_remittance_info_iso_path(rmt_inf, f'{prefix}.RmtInf'))

        return result


class Pain008Extractor(BaseISO20022Extractor):
    """Base extractor for all pain.008-based direct debit messages.

    pain.008 is for direct debit initiations. Key differences:
    - Creditor initiates (collects from debtor)
    - Contains mandate information
    - Has sequence type (first, recurring, final, one-off)

    Systems inheriting from this:
    - SepaSddExtractor (SEPA Direct Debit)
    - etc.
    """

    MESSAGE_TYPE: str = "pain.008"
    SILVER_TABLE: str = "stg_iso20022_pain008"
    PARSER_CLASS = Pain008Parser
    DEFAULT_CURRENCY: str = "EUR"  # SEPA default
    CLEARING_SYSTEM: str = None

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from parsed pain.008 message.

        Args:
            msg_content: Parsed message content
            raw_id: Reference to Bronze record
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            Dict with all fields for Silver staging table
        """
        trunc = self.trunc

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            'source_format': self.MESSAGE_TYPE,
            '_batch_id': batch_id,

            # Group Header
            'grp_hdr_msg_id': trunc(msg_content.get('messageId'), 35),
            'grp_hdr_cre_dt_tm': msg_content.get('creationDateTime'),
            'grp_hdr_nb_of_txs': msg_content.get('numberOfTransactions'),
            'grp_hdr_ctrl_sum': msg_content.get('controlSum'),
            'grp_hdr_initg_pty_nm': trunc(msg_content.get('initiatingPartyName'), 140),
            'grp_hdr_initg_pty_id': trunc(msg_content.get('initiatingPartyId'), 35),

            # Payment Information
            'pmt_inf_id': trunc(msg_content.get('paymentInformationId'), 35),
            'pmt_mtd': trunc(msg_content.get('paymentMethod'), 3),
            'btch_bookg': msg_content.get('batchBooking'),
            'pmt_inf_nb_of_txs': msg_content.get('pmtInfNumberOfTransactions'),
            'pmt_inf_ctrl_sum': msg_content.get('pmtInfControlSum'),

            # Payment Type
            'pmt_tp_inf_svc_lvl_cd': trunc(msg_content.get('serviceLevel'), 10),
            'pmt_tp_inf_lcl_instrm_cd': trunc(msg_content.get('localInstrument'), 35),
            'pmt_tp_inf_seq_tp': trunc(msg_content.get('sequenceType'), 10),
            'pmt_tp_inf_ctgy_purp_cd': trunc(msg_content.get('categoryPurpose'), 10),

            # Collection Date
            'reqd_colltn_dt': msg_content.get('requestedCollectionDate'),

            # Creditor (collecting party)
            'cdtr_nm': trunc(msg_content.get('creditorName'), 140),
            'cdtr_pstl_adr_strt_nm': trunc(msg_content.get('creditorStreetName'), 70),
            'cdtr_pstl_adr_bldg_nb': trunc(msg_content.get('creditorBuildingNumber'), 16),
            'cdtr_pstl_adr_pst_cd': trunc(msg_content.get('creditorPostCode'), 16),
            'cdtr_pstl_adr_twn_nm': trunc(msg_content.get('creditorTownName'), 35),
            'cdtr_pstl_adr_ctry': trunc(msg_content.get('creditorCountry'), 2),
            'cdtr_acct_id_iban': trunc(msg_content.get('creditorIBAN'), 34),
            'cdtr_acct_id_othr': trunc(msg_content.get('creditorAccountOther'), 34),
            'cdtr_agt_bic': trunc(msg_content.get('creditorAgentBIC'), 11),
            'cdtr_agt_nm': trunc(msg_content.get('creditorAgentName'), 140),

            # Creditor Scheme (SEPA Direct Debit)
            'cdtr_schme_id': trunc(msg_content.get('creditorSchemeId'), 35),
            'cdtr_schme_nm': trunc(msg_content.get('creditorSchemeName'), 35),

            # Direct Debit Transaction
            'drct_dbt_tx_inf_pmt_id_instr_id': trunc(msg_content.get('instructionId'), 35),
            'drct_dbt_tx_inf_pmt_id_end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'drct_dbt_tx_inf_instd_amt': msg_content.get('amount'),
            'drct_dbt_tx_inf_instd_amt_ccy': msg_content.get('currency'),

            # Mandate Information
            'drct_dbt_tx_inf_mndt_id': trunc(msg_content.get('mandateId'), 35),
            'drct_dbt_tx_inf_dt_of_sgntr': msg_content.get('mandateDateOfSignature'),
            'drct_dbt_tx_inf_amdmnt_ind': msg_content.get('amendmentIndicator'),
            'drct_dbt_tx_inf_orgnl_mndt_id': trunc(msg_content.get('originalMandateId'), 35),
            'drct_dbt_tx_inf_orgnl_dbtr_acct': trunc(msg_content.get('originalDebtorAccount'), 34),
            'drct_dbt_tx_inf_orgnl_dbtr_agt_bic': trunc(msg_content.get('originalDebtorAgentBIC'), 11),

            # Debtor (party being debited)
            'dbtr_nm': trunc(msg_content.get('debtorName'), 140),
            'dbtr_pstl_adr_strt_nm': trunc(msg_content.get('debtorStreetName'), 70),
            'dbtr_pstl_adr_bldg_nb': trunc(msg_content.get('debtorBuildingNumber'), 16),
            'dbtr_pstl_adr_pst_cd': trunc(msg_content.get('debtorPostCode'), 16),
            'dbtr_pstl_adr_twn_nm': trunc(msg_content.get('debtorTownName'), 35),
            'dbtr_pstl_adr_ctry': trunc(msg_content.get('debtorCountry'), 2),
            'dbtr_acct_id_iban': trunc(msg_content.get('debtorIBAN'), 34),
            'dbtr_acct_id_othr': trunc(msg_content.get('debtorAccountOther'), 34),
            'dbtr_agt_bic': trunc(msg_content.get('debtorAgentBIC'), 11),
            'dbtr_agt_nm': trunc(msg_content.get('debtorAgentName'), 140),

            # Ultimate Parties
            'ultmt_cdtr_nm': trunc(msg_content.get('ultimateCreditorName'), 140),
            'ultmt_dbtr_nm': trunc(msg_content.get('ultimateDebtorName'), 140),

            # Purpose and Remittance
            'purp_cd': trunc(msg_content.get('purposeCode'), 10),
            # rmt_inf_ustrd is a TEXT[] array in PostgreSQL, wrap single value in list
            'rmt_inf_ustrd': [msg_content.get('remittanceUnstructured')] if msg_content.get('remittanceUnstructured') else None,

            # Processing status
            'processing_status': 'PENDING',
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Returns:
            List of column names in INSERT order
        """
        return [
            # Core identifiers
            'stg_id', 'raw_id', 'source_format', '_batch_id',

            # Group Header
            'grp_hdr_msg_id', 'grp_hdr_cre_dt_tm', 'grp_hdr_nb_of_txs', 'grp_hdr_ctrl_sum',
            'grp_hdr_initg_pty_nm', 'grp_hdr_initg_pty_id',

            # Payment Information
            'pmt_inf_id', 'pmt_mtd', 'btch_bookg', 'pmt_inf_nb_of_txs', 'pmt_inf_ctrl_sum',

            # Payment Type
            'pmt_tp_inf_svc_lvl_cd', 'pmt_tp_inf_lcl_instrm_cd',
            'pmt_tp_inf_seq_tp', 'pmt_tp_inf_ctgy_purp_cd',

            # Collection Date
            'reqd_colltn_dt',

            # Creditor
            'cdtr_nm', 'cdtr_pstl_adr_strt_nm', 'cdtr_pstl_adr_bldg_nb',
            'cdtr_pstl_adr_pst_cd', 'cdtr_pstl_adr_twn_nm', 'cdtr_pstl_adr_ctry',
            'cdtr_acct_id_iban', 'cdtr_acct_id_othr',
            'cdtr_agt_bic', 'cdtr_agt_nm',

            # Creditor Scheme
            'cdtr_schme_id', 'cdtr_schme_nm',

            # Direct Debit Transaction
            'drct_dbt_tx_inf_pmt_id_instr_id', 'drct_dbt_tx_inf_pmt_id_end_to_end_id',
            'drct_dbt_tx_inf_instd_amt', 'drct_dbt_tx_inf_instd_amt_ccy',

            # Mandate
            'drct_dbt_tx_inf_mndt_id', 'drct_dbt_tx_inf_dt_of_sgntr',
            'drct_dbt_tx_inf_amdmnt_ind', 'drct_dbt_tx_inf_orgnl_mndt_id',
            'drct_dbt_tx_inf_orgnl_dbtr_acct', 'drct_dbt_tx_inf_orgnl_dbtr_agt_bic',

            # Debtor
            'dbtr_nm', 'dbtr_pstl_adr_strt_nm', 'dbtr_pstl_adr_bldg_nb',
            'dbtr_pstl_adr_pst_cd', 'dbtr_pstl_adr_twn_nm', 'dbtr_pstl_adr_ctry',
            'dbtr_acct_id_iban', 'dbtr_acct_id_othr',
            'dbtr_agt_bic', 'dbtr_agt_nm',

            # Ultimate Parties
            'ultmt_cdtr_nm', 'ultmt_dbtr_nm',

            # Purpose and Remittance
            'purp_cd', 'rmt_inf_ustrd',

            # Processing
            'processing_status',
        ]

    def _extract_parties(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract party entities from pain.008 Silver record.

        In direct debit, creditor is the initiator/collector.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import PartyData

        # Creditor (collecting party)
        if silver_data.get('cdtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('cdtr_nm'),
                role="CREDITOR",
                party_type='UNKNOWN',
                street_name=silver_data.get('cdtr_pstl_adr_strt_nm'),
                building_number=silver_data.get('cdtr_pstl_adr_bldg_nb'),
                post_code=silver_data.get('cdtr_pstl_adr_pst_cd'),
                town_name=silver_data.get('cdtr_pstl_adr_twn_nm'),
                country=silver_data.get('cdtr_pstl_adr_ctry'),
            ))

        # Debtor (party being debited)
        if silver_data.get('dbtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('dbtr_nm'),
                role="DEBTOR",
                party_type='UNKNOWN',
                street_name=silver_data.get('dbtr_pstl_adr_strt_nm'),
                building_number=silver_data.get('dbtr_pstl_adr_bldg_nb'),
                post_code=silver_data.get('dbtr_pstl_adr_pst_cd'),
                town_name=silver_data.get('dbtr_pstl_adr_twn_nm'),
                country=silver_data.get('dbtr_pstl_adr_ctry'),
            ))

        # Ultimate Creditor
        if silver_data.get('ultmt_cdtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('ultmt_cdtr_nm'),
                role="ULTIMATE_CREDITOR",
                party_type='UNKNOWN',
            ))

        # Ultimate Debtor
        if silver_data.get('ultmt_dbtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('ultmt_dbtr_nm'),
                role="ULTIMATE_DEBTOR",
                party_type='UNKNOWN',
            ))

        # Initiating Party
        if silver_data.get('grp_hdr_initg_pty_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('grp_hdr_initg_pty_nm'),
                role="INITIATING_PARTY",
                party_type='UNKNOWN',
            ))

    def _extract_accounts(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract account entities from pain.008 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import AccountData

        currency = silver_data.get('drct_dbt_tx_inf_instd_amt_ccy') or self.DEFAULT_CURRENCY

        # Creditor Account
        creditor_acct = silver_data.get('cdtr_acct_id_iban') or silver_data.get('cdtr_acct_id_othr')
        if creditor_acct:
            entities.accounts.append(AccountData(
                account_number=creditor_acct,
                role="CREDITOR",
                iban=silver_data.get('cdtr_acct_id_iban'),
                account_type='CACC',
                currency=currency,
            ))

        # Debtor Account
        debtor_acct = silver_data.get('dbtr_acct_id_iban') or silver_data.get('dbtr_acct_id_othr')
        if debtor_acct:
            entities.accounts.append(AccountData(
                account_number=debtor_acct,
                role="DEBTOR",
                iban=silver_data.get('dbtr_acct_id_iban'),
                account_type='CACC',
                currency=currency,
            ))

    def _extract_financial_institutions(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract financial institution entities from pain.008 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import FinancialInstitutionData

        # Creditor Agent
        if silver_data.get('cdtr_agt_bic'):
            bic = silver_data.get('cdtr_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('cdtr_agt_nm') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, silver_data.get('cdtr_pstl_adr_ctry')),
            ))

        # Debtor Agent
        if silver_data.get('dbtr_agt_bic'):
            bic = silver_data.get('dbtr_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('dbtr_agt_nm') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, silver_data.get('dbtr_pstl_adr_ctry')),
            ))

        # Original Debtor Agent (if mandate amended)
        if silver_data.get('drct_dbt_tx_inf_orgnl_dbtr_agt_bic'):
            bic = silver_data.get('drct_dbt_tx_inf_orgnl_dbtr_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="ORIGINAL_DEBTOR_AGENT",
                name=f"FI_{bic}" if bic else None,
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

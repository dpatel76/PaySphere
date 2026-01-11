"""ISO 20022 pacs.002 Parser and Extractor base classes.

pacs.002 (FI to FI Payment Status Report) is used to inform the sender of a
payment about the status/confirmation of that payment. Key elements:
- OrgnlGrpInfAndSts: Original group information and status
- TxInfAndSts: Transaction-level status information
- OrgnlTxRef: Reference to original transaction

Systems using pacs.002:
- All ISO 20022-based payment systems for acknowledgments
- TARGET2, CHAPS, FPS, FEDNOW, RTP, NPP, etc.

Reference: ISO 20022 Message Definition Report - pacs.002.001.10
"""

from typing import Dict, Any, List, Optional
import logging

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor

logger = logging.getLogger(__name__)


class Pacs002Parser(BaseISO20022Parser):
    """Base parser for pacs.002 Payment Status Report messages.

    pacs.002 is used to provide status information about a previous payment.
    The main elements are:
    - OrgnlGrpInfAndSts: Status at group level
    - TxInfAndSts: Status at transaction level with original references

    pacs.002 structure:
    - Document
      - FIToFIPmtStsRpt
        - GrpHdr (Group Header)
        - OrgnlGrpInfAndSts (Original Group Info and Status)
        - TxInfAndSts (Transaction Info and Status) [0..*]
    """

    ROOT_ELEMENT = "FIToFIPmtStsRpt"
    MESSAGE_TYPE = "pacs.002"

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse pacs.002 Payment Status Report message.

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pacs.002 fields
        """
        root = self._parse_xml(xml_content)

        # Find the FIToFIPmtStsRpt element
        pmt_sts_rpt = self._find(root, self.ROOT_ELEMENT)
        if pmt_sts_rpt is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                pmt_sts_rpt = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pacs.002 message")

        return self._parse_payment_status_report(pmt_sts_rpt)

    def _parse_payment_status_report(self, pmt_sts_rpt) -> Dict[str, Any]:
        """Parse FIToFIPmtStsRpt element.

        Args:
            pmt_sts_rpt: FIToFIPmtStsRpt element

        Returns:
            Dict with extracted fields
        """
        result = {
            'isISO20022': True,
            'messageTypeCode': 'pacs.002',
        }

        # Extract Group Header
        result.update(self._extract_group_header(pmt_sts_rpt))

        # Extract Original Group Information and Status
        orgnl_grp_inf = self._find(pmt_sts_rpt, 'OrgnlGrpInfAndSts')
        if orgnl_grp_inf is not None:
            result.update(self._extract_original_group_info(orgnl_grp_inf))

        # Extract first Transaction Information and Status
        tx_inf_and_sts = self._find(pmt_sts_rpt, 'TxInfAndSts')
        if tx_inf_and_sts is not None:
            result.update(self._parse_tx_info_and_status(tx_inf_and_sts))

        return result

    def _extract_original_group_info(self, orgnl_grp: 'ET.Element') -> Dict[str, Any]:
        """Extract OrgnlGrpInfAndSts element.

        Args:
            orgnl_grp: OrgnlGrpInfAndSts element

        Returns:
            Dict with original group fields
        """
        if orgnl_grp is None:
            return {}

        result = {
            'originalMessageId': self._find_text(orgnl_grp, 'OrgnlMsgId'),
            'originalMessageNameId': self._find_text(orgnl_grp, 'OrgnlMsgNmId'),
            'originalCreationDateTime': self._find_text(orgnl_grp, 'OrgnlCreDtTm'),
            'originalNumberOfTransactions': self._safe_int(self._find_text(orgnl_grp, 'OrgnlNbOfTxs')),
            'groupStatus': self._find_text(orgnl_grp, 'GrpSts'),
        }

        # Status Reason Information
        sts_rsn_inf = self._find(orgnl_grp, 'StsRsnInf')
        if sts_rsn_inf:
            result['groupStatusReasonCode'] = self._find_text(sts_rsn_inf, 'Rsn/Cd')
            result['groupStatusReasonProprietary'] = self._find_text(sts_rsn_inf, 'Rsn/Prtry')
            result['groupStatusAdditionalInfo'] = self._find_text(sts_rsn_inf, 'AddtlInf')

        return result

    def _parse_tx_info_and_status(self, tx_inf: 'ET.Element') -> Dict[str, Any]:
        """Parse TxInfAndSts element.

        Args:
            tx_inf: TxInfAndSts element

        Returns:
            Dict with extracted transaction status fields
        """
        result = {}

        # Status identification
        result['statusId'] = self._find_text(tx_inf, 'StsId')

        # Original payment identification
        result['originalInstructionId'] = self._find_text(tx_inf, 'OrgnlInstrId')
        result['originalEndToEndId'] = self._find_text(tx_inf, 'OrgnlEndToEndId')
        result['originalTransactionId'] = self._find_text(tx_inf, 'OrgnlTxId')
        result['originalUETR'] = self._find_text(tx_inf, 'OrgnlUETR')

        # Transaction status
        result['transactionStatus'] = self._find_text(tx_inf, 'TxSts')

        # Status Reason Information
        sts_rsn_inf = self._find(tx_inf, 'StsRsnInf')
        if sts_rsn_inf:
            result['txStatusReasonCode'] = self._find_text(sts_rsn_inf, 'Rsn/Cd')
            result['txStatusReasonProprietary'] = self._find_text(sts_rsn_inf, 'Rsn/Prtry')
            result['txStatusAdditionalInfo'] = self._find_text(sts_rsn_inf, 'AddtlInf')

            # Originator (who raised the status)
            orgtr = self._find(sts_rsn_inf, 'Orgtr')
            if orgtr:
                result['statusOriginatorName'] = self._find_text(orgtr, 'Nm')
                result['statusOriginatorBic'] = self._find_text(orgtr, 'Id/OrgId/AnyBIC')

        # Acceptance DateTime
        result['acceptanceDateTime'] = self._find_text(tx_inf, 'AccptncDtTm')

        # Effective Interbank Settlement Date
        result['effectiveSettlementDate'] = self._find_text(tx_inf, 'FctvIntrBkSttlmDt')

        # Clearing System Reference
        result['clearingSystemReference'] = self._find_text(tx_inf, 'ClrSysRef')

        # Original Transaction Reference
        orgnl_tx_ref = self._find(tx_inf, 'OrgnlTxRef')
        if orgnl_tx_ref:
            result.update(self._extract_original_tx_reference(orgnl_tx_ref))

        return result

    def _extract_original_tx_reference(self, orgnl_tx_ref: 'ET.Element') -> Dict[str, Any]:
        """Extract OrgnlTxRef (Original Transaction Reference) element.

        This contains key details from the original payment message.

        Args:
            orgnl_tx_ref: OrgnlTxRef element

        Returns:
            Dict with original transaction fields
        """
        if orgnl_tx_ref is None:
            return {}

        result = {}

        # Original Amount
        amt_data = self._extract_amount(orgnl_tx_ref, 'IntrBkSttlmAmt')
        result['originalSettlementAmount'] = amt_data.get('amount')
        result['originalSettlementCurrency'] = amt_data.get('currency')

        # Original Settlement Date
        result['originalSettlementDate'] = self._find_text(orgnl_tx_ref, 'IntrBkSttlmDt')

        # Original Debtor
        dbtr = self._find(orgnl_tx_ref, 'Dbtr')
        if dbtr:
            result['originalDebtorName'] = self._find_text(dbtr, 'Nm')

        # Original Debtor Account
        dbtr_acct = self._find(orgnl_tx_ref, 'DbtrAcct')
        if dbtr_acct:
            result['originalDebtorIBAN'] = self._find_text(dbtr_acct, 'Id/IBAN')
            result['originalDebtorAccount'] = self._find_text(dbtr_acct, 'Id/Othr/Id')

        # Original Debtor Agent
        dbtr_agt = self._find(orgnl_tx_ref, 'DbtrAgt')
        if dbtr_agt:
            result['originalDebtorAgentBIC'] = self._find_text(dbtr_agt, 'FinInstnId/BICFI')

        # Original Creditor
        cdtr = self._find(orgnl_tx_ref, 'Cdtr')
        if cdtr:
            result['originalCreditorName'] = self._find_text(cdtr, 'Nm')

        # Original Creditor Account
        cdtr_acct = self._find(orgnl_tx_ref, 'CdtrAcct')
        if cdtr_acct:
            result['originalCreditorIBAN'] = self._find_text(cdtr_acct, 'Id/IBAN')
            result['originalCreditorAccount'] = self._find_text(cdtr_acct, 'Id/Othr/Id')

        # Original Creditor Agent
        cdtr_agt = self._find(orgnl_tx_ref, 'CdtrAgt')
        if cdtr_agt:
            result['originalCreditorAgentBIC'] = self._find_text(cdtr_agt, 'FinInstnId/BICFI')

        return result

    def parse_iso_paths(self, xml_content: str) -> Dict[str, Any]:
        """Parse pacs.002 message using full ISO path key naming.

        Returns keys using ISO 20022 element path notation:
        - GrpHdr.MsgId, GrpHdr.CreDtTm
        - OrgnlGrpInfAndSts.OrgnlMsgId, OrgnlGrpInfAndSts.GrpSts
        - TxInfAndSts.OrgnlInstrId, TxInfAndSts.TxSts
        - TxInfAndSts.OrgnlTxRef.Dbtr.Nm

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with full ISO path keys
        """
        root = self._parse_xml(xml_content)

        # Find the FIToFIPmtStsRpt element
        pmt_sts_rpt = self._find(root, self.ROOT_ELEMENT)
        if pmt_sts_rpt is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                pmt_sts_rpt = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pacs.002 message")

        result = {
            'isISO20022': True,
            'messageTypeCode': 'pacs.002',
        }

        # Extract Group Header using ISO paths
        result.update(self._extract_group_header_iso_path(pmt_sts_rpt))

        # Extract Original Group Information and Status
        orgnl_grp_inf = self._find(pmt_sts_rpt, 'OrgnlGrpInfAndSts')
        if orgnl_grp_inf is not None:
            result.update(self._extract_original_group_info_iso_path(orgnl_grp_inf))

        # Extract first Transaction Information and Status
        tx_inf_and_sts = self._find(pmt_sts_rpt, 'TxInfAndSts')
        if tx_inf_and_sts is not None:
            result.update(self._parse_tx_info_and_status_iso_paths(tx_inf_and_sts))

        return result

    def _extract_original_group_info_iso_path(self, orgnl_grp) -> Dict[str, Any]:
        """Extract OrgnlGrpInfAndSts using full ISO path keys.

        Args:
            orgnl_grp: OrgnlGrpInfAndSts element

        Returns:
            Dict with full ISO path keys
        """
        if orgnl_grp is None:
            return {}

        prefix = 'OrgnlGrpInfAndSts'
        result = {
            f'{prefix}.OrgnlMsgId': self._find_text(orgnl_grp, 'OrgnlMsgId'),
            f'{prefix}.OrgnlMsgNmId': self._find_text(orgnl_grp, 'OrgnlMsgNmId'),
            f'{prefix}.OrgnlCreDtTm': self._find_text(orgnl_grp, 'OrgnlCreDtTm'),
            f'{prefix}.OrgnlNbOfTxs': self._find_text(orgnl_grp, 'OrgnlNbOfTxs'),
            f'{prefix}.GrpSts': self._find_text(orgnl_grp, 'GrpSts'),
        }

        # Status Reason Information
        sts_rsn_inf = self._find(orgnl_grp, 'StsRsnInf')
        if sts_rsn_inf:
            result[f'{prefix}.StsRsnInf.Rsn.Cd'] = self._find_text(sts_rsn_inf, 'Rsn/Cd')
            result[f'{prefix}.StsRsnInf.Rsn.Prtry'] = self._find_text(sts_rsn_inf, 'Rsn/Prtry')
            result[f'{prefix}.StsRsnInf.AddtlInf'] = self._find_text(sts_rsn_inf, 'AddtlInf')

        return result

    def _parse_tx_info_and_status_iso_paths(self, tx_inf) -> Dict[str, Any]:
        """Parse TxInfAndSts element using full ISO path keys.

        Args:
            tx_inf: TxInfAndSts element

        Returns:
            Dict with full ISO path keys
        """
        prefix = 'TxInfAndSts'
        result = {}

        # Status identification
        result[f'{prefix}.StsId'] = self._find_text(tx_inf, 'StsId')

        # Original payment identification
        result[f'{prefix}.OrgnlInstrId'] = self._find_text(tx_inf, 'OrgnlInstrId')
        result[f'{prefix}.OrgnlEndToEndId'] = self._find_text(tx_inf, 'OrgnlEndToEndId')
        result[f'{prefix}.OrgnlTxId'] = self._find_text(tx_inf, 'OrgnlTxId')
        result[f'{prefix}.OrgnlUETR'] = self._find_text(tx_inf, 'OrgnlUETR')

        # Transaction status
        result[f'{prefix}.TxSts'] = self._find_text(tx_inf, 'TxSts')

        # Status Reason Information
        sts_rsn_inf = self._find(tx_inf, 'StsRsnInf')
        if sts_rsn_inf:
            result[f'{prefix}.StsRsnInf.Rsn.Cd'] = self._find_text(sts_rsn_inf, 'Rsn/Cd')
            result[f'{prefix}.StsRsnInf.Rsn.Prtry'] = self._find_text(sts_rsn_inf, 'Rsn/Prtry')
            result[f'{prefix}.StsRsnInf.AddtlInf'] = self._find_text(sts_rsn_inf, 'AddtlInf')

            # Originator
            orgtr = self._find(sts_rsn_inf, 'Orgtr')
            if orgtr:
                result[f'{prefix}.StsRsnInf.Orgtr.Nm'] = self._find_text(orgtr, 'Nm')
                result[f'{prefix}.StsRsnInf.Orgtr.Id.OrgId.AnyBIC'] = self._find_text(orgtr, 'Id/OrgId/AnyBIC')

        # Acceptance DateTime
        result[f'{prefix}.AccptncDtTm'] = self._find_text(tx_inf, 'AccptncDtTm')

        # Effective Interbank Settlement Date
        result[f'{prefix}.FctvIntrBkSttlmDt'] = self._find_text(tx_inf, 'FctvIntrBkSttlmDt')

        # Clearing System Reference
        result[f'{prefix}.ClrSysRef'] = self._find_text(tx_inf, 'ClrSysRef')

        # Original Transaction Reference
        orgnl_tx_ref = self._find(tx_inf, 'OrgnlTxRef')
        if orgnl_tx_ref:
            result.update(self._extract_original_tx_reference_iso_path(orgnl_tx_ref, f'{prefix}.OrgnlTxRef'))

        return result

    def _extract_original_tx_reference_iso_path(self, orgnl_tx_ref, path_prefix: str) -> Dict[str, Any]:
        """Extract OrgnlTxRef using full ISO path keys.

        Args:
            orgnl_tx_ref: OrgnlTxRef element
            path_prefix: ISO path prefix

        Returns:
            Dict with full ISO path keys
        """
        if orgnl_tx_ref is None:
            return {}

        result = {}

        # Original Amount
        result.update(self._extract_amount_iso_path(orgnl_tx_ref, 'IntrBkSttlmAmt', f'{path_prefix}.IntrBkSttlmAmt'))

        # Original Settlement Date
        result[f'{path_prefix}.IntrBkSttlmDt'] = self._find_text(orgnl_tx_ref, 'IntrBkSttlmDt')

        # Original Debtor
        dbtr = self._find(orgnl_tx_ref, 'Dbtr')
        if dbtr:
            result[f'{path_prefix}.Dbtr.Nm'] = self._find_text(dbtr, 'Nm')

        # Original Debtor Account
        dbtr_acct = self._find(orgnl_tx_ref, 'DbtrAcct')
        if dbtr_acct:
            result.update(self._extract_account_iso_path(dbtr_acct, f'{path_prefix}.DbtrAcct'))

        # Original Debtor Agent
        dbtr_agt = self._find(orgnl_tx_ref, 'DbtrAgt')
        if dbtr_agt:
            result.update(self._extract_financial_institution_iso_path(dbtr_agt, f'{path_prefix}.DbtrAgt'))

        # Original Creditor
        cdtr = self._find(orgnl_tx_ref, 'Cdtr')
        if cdtr:
            result[f'{path_prefix}.Cdtr.Nm'] = self._find_text(cdtr, 'Nm')

        # Original Creditor Account
        cdtr_acct = self._find(orgnl_tx_ref, 'CdtrAcct')
        if cdtr_acct:
            result.update(self._extract_account_iso_path(cdtr_acct, f'{path_prefix}.CdtrAcct'))

        # Original Creditor Agent
        cdtr_agt = self._find(orgnl_tx_ref, 'CdtrAgt')
        if cdtr_agt:
            result.update(self._extract_financial_institution_iso_path(cdtr_agt, f'{path_prefix}.CdtrAgt'))

        return result


class Pacs002Extractor(BaseISO20022Extractor):
    """Base extractor for all pacs.002-based payment status messages.

    pacs.002 provides status information about payments. Key differences:
    - Contains original message references, not new payments
    - Status codes indicate acceptance/rejection/pending
    - May include reason codes for rejections

    Systems inheriting from this:
    - Target2Pacs002Extractor
    - FednowPacs002Extractor
    - RtpPacs002Extractor
    - etc.
    """

    MESSAGE_TYPE: str = "pacs.002"
    SILVER_TABLE: str = "stg_iso20022_pacs002"
    PARSER_CLASS = Pacs002Parser
    DEFAULT_CURRENCY: str = "XXX"
    CLEARING_SYSTEM: str = None

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from parsed pacs.002 message.

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

            # Original Group Information
            'orgnl_grp_inf_orgnl_msg_id': trunc(msg_content.get('originalMessageId'), 35),
            'orgnl_grp_inf_orgnl_msg_nm_id': trunc(msg_content.get('originalMessageNameId'), 35),
            'orgnl_grp_inf_orgnl_cre_dt_tm': msg_content.get('originalCreationDateTime'),
            'orgnl_grp_inf_orgnl_nb_of_txs': msg_content.get('originalNumberOfTransactions'),
            'orgnl_grp_inf_grp_sts': trunc(msg_content.get('groupStatus'), 10),
            'orgnl_grp_inf_sts_rsn_cd': trunc(msg_content.get('groupStatusReasonCode'), 10),
            'orgnl_grp_inf_sts_rsn_prtry': trunc(msg_content.get('groupStatusReasonProprietary'), 35),
            'orgnl_grp_inf_addtl_inf': msg_content.get('groupStatusAdditionalInfo'),

            # Transaction Info and Status
            'tx_inf_sts_id': trunc(msg_content.get('statusId'), 35),
            'tx_inf_orgnl_instr_id': trunc(msg_content.get('originalInstructionId'), 35),
            'tx_inf_orgnl_end_to_end_id': trunc(msg_content.get('originalEndToEndId'), 35),
            'tx_inf_orgnl_tx_id': trunc(msg_content.get('originalTransactionId'), 35),
            'tx_inf_orgnl_uetr': msg_content.get('originalUETR'),
            'tx_inf_tx_sts': trunc(msg_content.get('transactionStatus'), 10),
            'tx_inf_sts_rsn_cd': trunc(msg_content.get('txStatusReasonCode'), 10),
            'tx_inf_sts_rsn_prtry': trunc(msg_content.get('txStatusReasonProprietary'), 35),
            'tx_inf_addtl_inf': msg_content.get('txStatusAdditionalInfo'),
            'tx_inf_accptnc_dt_tm': msg_content.get('acceptanceDateTime'),
            'tx_inf_fctv_intr_bk_sttlm_dt': msg_content.get('effectiveSettlementDate'),
            'tx_inf_clr_sys_ref': trunc(msg_content.get('clearingSystemReference'), 35),

            # Status Originator
            'sts_orgtr_nm': trunc(msg_content.get('statusOriginatorName'), 140),
            'sts_orgtr_bic': trunc(msg_content.get('statusOriginatorBic'), 11),

            # Original Transaction Reference
            'orgnl_tx_ref_intr_bk_sttlm_amt': msg_content.get('originalSettlementAmount'),
            'orgnl_tx_ref_intr_bk_sttlm_ccy': msg_content.get('originalSettlementCurrency'),
            'orgnl_tx_ref_intr_bk_sttlm_dt': msg_content.get('originalSettlementDate'),
            'orgnl_tx_ref_dbtr_nm': trunc(msg_content.get('originalDebtorName'), 140),
            'orgnl_tx_ref_dbtr_acct_id_iban': trunc(msg_content.get('originalDebtorIBAN'), 34),
            'orgnl_tx_ref_dbtr_acct_id_othr': trunc(msg_content.get('originalDebtorAccount'), 34),
            'orgnl_tx_ref_dbtr_agt_bic': trunc(msg_content.get('originalDebtorAgentBIC'), 11),
            'orgnl_tx_ref_cdtr_nm': trunc(msg_content.get('originalCreditorName'), 140),
            'orgnl_tx_ref_cdtr_acct_id_iban': trunc(msg_content.get('originalCreditorIBAN'), 34),
            'orgnl_tx_ref_cdtr_acct_id_othr': trunc(msg_content.get('originalCreditorAccount'), 34),
            'orgnl_tx_ref_cdtr_agt_bic': trunc(msg_content.get('originalCreditorAgentBIC'), 11),

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
            'grp_hdr_msg_id', 'grp_hdr_cre_dt_tm',

            # Original Group Information
            'orgnl_grp_inf_orgnl_msg_id', 'orgnl_grp_inf_orgnl_msg_nm_id',
            'orgnl_grp_inf_orgnl_cre_dt_tm', 'orgnl_grp_inf_orgnl_nb_of_txs',
            'orgnl_grp_inf_grp_sts', 'orgnl_grp_inf_sts_rsn_cd',
            'orgnl_grp_inf_sts_rsn_prtry', 'orgnl_grp_inf_addtl_inf',

            # Transaction Info and Status
            'tx_inf_sts_id', 'tx_inf_orgnl_instr_id', 'tx_inf_orgnl_end_to_end_id',
            'tx_inf_orgnl_tx_id', 'tx_inf_orgnl_uetr', 'tx_inf_tx_sts',
            'tx_inf_sts_rsn_cd', 'tx_inf_sts_rsn_prtry', 'tx_inf_addtl_inf',
            'tx_inf_accptnc_dt_tm', 'tx_inf_fctv_intr_bk_sttlm_dt', 'tx_inf_clr_sys_ref',

            # Status Originator
            'sts_orgtr_nm', 'sts_orgtr_bic',

            # Original Transaction Reference
            'orgnl_tx_ref_intr_bk_sttlm_amt', 'orgnl_tx_ref_intr_bk_sttlm_ccy',
            'orgnl_tx_ref_intr_bk_sttlm_dt',
            'orgnl_tx_ref_dbtr_nm', 'orgnl_tx_ref_dbtr_acct_id_iban',
            'orgnl_tx_ref_dbtr_acct_id_othr', 'orgnl_tx_ref_dbtr_agt_bic',
            'orgnl_tx_ref_cdtr_nm', 'orgnl_tx_ref_cdtr_acct_id_iban',
            'orgnl_tx_ref_cdtr_acct_id_othr', 'orgnl_tx_ref_cdtr_agt_bic',

            # Processing
            'processing_status',
        ]

    def _extract_parties(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract party entities from pacs.002 Silver record.

        pacs.002 contains original transaction reference with debtor/creditor.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import PartyData

        # Original Debtor
        if silver_data.get('orgnl_tx_ref_dbtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('orgnl_tx_ref_dbtr_nm'),
                role="DEBTOR",
                party_type='UNKNOWN',
            ))

        # Original Creditor
        if silver_data.get('orgnl_tx_ref_cdtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('orgnl_tx_ref_cdtr_nm'),
                role="CREDITOR",
                party_type='UNKNOWN',
            ))

    def _extract_accounts(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract account entities from pacs.002 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import AccountData

        # Original Debtor Account
        debtor_acct = silver_data.get('orgnl_tx_ref_dbtr_acct_id_iban') or silver_data.get('orgnl_tx_ref_dbtr_acct_id_othr')
        if debtor_acct:
            entities.accounts.append(AccountData(
                account_number=debtor_acct,
                role="DEBTOR",
                iban=silver_data.get('orgnl_tx_ref_dbtr_acct_id_iban'),
                account_type='CACC',
                currency=silver_data.get('orgnl_tx_ref_intr_bk_sttlm_ccy') or self.DEFAULT_CURRENCY,
            ))

        # Original Creditor Account
        creditor_acct = silver_data.get('orgnl_tx_ref_cdtr_acct_id_iban') or silver_data.get('orgnl_tx_ref_cdtr_acct_id_othr')
        if creditor_acct:
            entities.accounts.append(AccountData(
                account_number=creditor_acct,
                role="CREDITOR",
                iban=silver_data.get('orgnl_tx_ref_cdtr_acct_id_iban'),
                account_type='CACC',
                currency=silver_data.get('orgnl_tx_ref_intr_bk_sttlm_ccy') or self.DEFAULT_CURRENCY,
            ))

    def _extract_financial_institutions(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract financial institution entities from pacs.002 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import FinancialInstitutionData

        # Original Debtor Agent
        if silver_data.get('orgnl_tx_ref_dbtr_agt_bic'):
            bic = silver_data.get('orgnl_tx_ref_dbtr_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=f"FI_{bic}" if bic else None,
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Original Creditor Agent
        if silver_data.get('orgnl_tx_ref_cdtr_agt_bic'):
            bic = silver_data.get('orgnl_tx_ref_cdtr_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=f"FI_{bic}" if bic else None,
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Status Originator (if BIC present)
        if silver_data.get('sts_orgtr_bic'):
            bic = silver_data.get('sts_orgtr_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="STATUS_ORIGINATOR",
                name=silver_data.get('sts_orgtr_nm') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

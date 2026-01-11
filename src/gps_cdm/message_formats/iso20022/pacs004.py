"""ISO 20022 pacs.004 Parser and Extractor base classes.

pacs.004 (Payment Return) is used to return funds from a previous payment.
Key elements:
- OrgnlGrpInf: Original group information
- TxInf: Return transaction information including return reason

Systems using pacs.004:
- All ISO 20022-based payment systems for returns
- TARGET2, CHAPS, FEDNOW, FEDWIRE, NPP, etc.

Reference: ISO 20022 Message Definition Report - pacs.004.001.09
"""

from typing import Dict, Any, List, Optional
import logging

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor

logger = logging.getLogger(__name__)


class Pacs004Parser(BaseISO20022Parser):
    """Base parser for pacs.004 Payment Return messages.

    pacs.004 is used to return funds from a previous payment. The main elements:
    - GrpHdr: Group header with return message identification
    - OrgnlGrpInf: Reference to original payment group
    - TxInf: Return transaction details with reason

    pacs.004 structure:
    - Document
      - PmtRtr
        - GrpHdr (Group Header)
        - OrgnlGrpInf (Original Group Information)
        - TxInf (Transaction Information) [1..*]
    """

    ROOT_ELEMENT = "PmtRtr"
    MESSAGE_TYPE = "pacs.004"

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse pacs.004 Payment Return message.

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pacs.004 fields
        """
        root = self._parse_xml(xml_content)

        # Find the PmtRtr element
        pmt_rtr = self._find(root, self.ROOT_ELEMENT)
        if pmt_rtr is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                pmt_rtr = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pacs.004 message")

        return self._parse_payment_return(pmt_rtr)

    def _parse_payment_return(self, pmt_rtr) -> Dict[str, Any]:
        """Parse PmtRtr element.

        Args:
            pmt_rtr: PmtRtr element

        Returns:
            Dict with extracted fields
        """
        result = {
            'isISO20022': True,
            'messageTypeCode': 'pacs.004',
        }

        # Extract Group Header
        result.update(self._extract_group_header(pmt_rtr))

        # Extract Original Group Information
        orgnl_grp_inf = self._find(pmt_rtr, 'OrgnlGrpInf')
        if orgnl_grp_inf is not None:
            result.update(self._extract_original_group_info(orgnl_grp_inf))

        # Extract first Transaction Information
        tx_inf = self._find(pmt_rtr, 'TxInf')
        if tx_inf is not None:
            result.update(self._parse_return_tx_info(tx_inf))

        return result

    def _extract_original_group_info(self, orgnl_grp: 'ET.Element') -> Dict[str, Any]:
        """Extract OrgnlGrpInf element.

        Args:
            orgnl_grp: OrgnlGrpInf element

        Returns:
            Dict with original group fields
        """
        if orgnl_grp is None:
            return {}

        return {
            'originalMessageId': self._find_text(orgnl_grp, 'OrgnlMsgId'),
            'originalMessageNameId': self._find_text(orgnl_grp, 'OrgnlMsgNmId'),
            'originalCreationDateTime': self._find_text(orgnl_grp, 'OrgnlCreDtTm'),
        }

    def _parse_return_tx_info(self, tx_inf: 'ET.Element') -> Dict[str, Any]:
        """Parse TxInf element for pacs.004 return.

        Args:
            tx_inf: TxInf element

        Returns:
            Dict with extracted return transaction fields
        """
        result = {}

        # Return identification
        result['returnId'] = self._find_text(tx_inf, 'RtrId')

        # Original payment identification
        result['originalInstructionId'] = self._find_text(tx_inf, 'OrgnlInstrId')
        result['originalEndToEndId'] = self._find_text(tx_inf, 'OrgnlEndToEndId')
        result['originalTransactionId'] = self._find_text(tx_inf, 'OrgnlTxId')
        result['originalUETR'] = self._find_text(tx_inf, 'OrgnlUETR')
        result['originalClearingSystemRef'] = self._find_text(tx_inf, 'OrgnlClrSysRef')

        # Returned Interbank Settlement Amount
        amt_data = self._extract_amount(tx_inf, 'RtrdIntrBkSttlmAmt')
        result['returnedSettlementAmount'] = amt_data.get('amount')
        result['returnedSettlementCurrency'] = amt_data.get('currency')

        # Interbank Settlement Date
        result['interbankSettlementDate'] = self._find_text(tx_inf, 'IntrBkSttlmDt')

        # Settlement Priority
        result['settlementPriority'] = self._find_text(tx_inf, 'SttlmPrty')

        # Return Reason Information
        rtr_rsn_inf = self._find(tx_inf, 'RtrRsnInf')
        if rtr_rsn_inf:
            result['returnReasonCode'] = self._find_text(rtr_rsn_inf, 'Rsn/Cd')
            result['returnReasonProprietary'] = self._find_text(rtr_rsn_inf, 'Rsn/Prtry')
            result['returnAdditionalInfo'] = self._find_text(rtr_rsn_inf, 'AddtlInf')

            # Return Originator
            orgtr = self._find(rtr_rsn_inf, 'Orgtr')
            if orgtr:
                result['returnOriginatorName'] = self._find_text(orgtr, 'Nm')
                result['returnOriginatorBic'] = self._find_text(orgtr, 'Id/OrgId/AnyBIC')

        # Instructing Agent
        instg_agt = self._find(tx_inf, 'InstgAgt')
        if instg_agt:
            result.update(self._extract_financial_institution(instg_agt, 'instructingAgent'))

        # Instructed Agent
        instd_agt = self._find(tx_inf, 'InstdAgt')
        if instd_agt:
            result.update(self._extract_financial_institution(instd_agt, 'instructedAgent'))

        # Original Transaction Reference
        orgnl_tx_ref = self._find(tx_inf, 'OrgnlTxRef')
        if orgnl_tx_ref:
            result.update(self._extract_original_tx_reference(orgnl_tx_ref))

        return result

    def _extract_original_tx_reference(self, orgnl_tx_ref: 'ET.Element') -> Dict[str, Any]:
        """Extract OrgnlTxRef (Original Transaction Reference) element.

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

    # ==========================================================================
    # ISO PATH KEY NAMING METHODS (DOT-NOTATION)
    # ==========================================================================

    def parse_iso_paths(self, xml_content: str) -> Dict[str, Any]:
        """Parse pacs.004 message using full ISO path key naming.

        Returns keys in dot-notation format matching ISO 20022 element paths:
        - GrpHdr.MsgId, GrpHdr.CreDtTm
        - OrgnlGrpInf.OrgnlMsgId, OrgnlGrpInf.OrgnlMsgNmId
        - TxInf.RtrId, TxInf.OrgnlEndToEndId
        - TxInf.RtrRsnInf.Rsn.Cd
        - TxInf.OrgnlTxRef.Dbtr.Nm

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pacs.004 fields using full ISO path keys
        """
        root = self._parse_xml(xml_content)

        # Find the PmtRtr element
        pmt_rtr = self._find(root, self.ROOT_ELEMENT)
        if pmt_rtr is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                pmt_rtr = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pacs.004 message")

        result = {
            'isISO20022': True,
            'messageTypeCode': 'pacs.004',
        }

        # Extract Group Header
        result.update(self._extract_group_header_iso_path(pmt_rtr))

        # Extract Original Group Information
        orgnl_grp_inf = self._find(pmt_rtr, 'OrgnlGrpInf')
        if orgnl_grp_inf is not None:
            result.update(self._extract_original_group_info_iso_path(orgnl_grp_inf))

        # Extract first Transaction Information
        tx_inf = self._find(pmt_rtr, 'TxInf')
        if tx_inf is not None:
            result.update(self._parse_return_tx_info_iso_paths(tx_inf))

        return result

    def _extract_original_group_info_iso_path(self, orgnl_grp: 'ET.Element') -> Dict[str, Any]:
        """Extract OrgnlGrpInf element using ISO path keys.

        Args:
            orgnl_grp: OrgnlGrpInf element

        Returns:
            Dict with ISO path keys like 'OrgnlGrpInf.OrgnlMsgId'
        """
        if orgnl_grp is None:
            return {}

        prefix = 'OrgnlGrpInf'
        return {
            f'{prefix}.OrgnlMsgId': self._find_text(orgnl_grp, 'OrgnlMsgId'),
            f'{prefix}.OrgnlMsgNmId': self._find_text(orgnl_grp, 'OrgnlMsgNmId'),
            f'{prefix}.OrgnlCreDtTm': self._find_text(orgnl_grp, 'OrgnlCreDtTm'),
            f'{prefix}.OrgnlNbOfTxs': self._safe_int(self._find_text(orgnl_grp, 'OrgnlNbOfTxs')),
            f'{prefix}.OrgnlCtrlSum': self._safe_float(self._find_text(orgnl_grp, 'OrgnlCtrlSum')),
            f'{prefix}.GrpRtrRsn.RsnCd': self._find_text(orgnl_grp, 'RtrRsnInf/Rsn/Cd'),
        }

    def _parse_return_tx_info_iso_paths(self, tx_inf: 'ET.Element') -> Dict[str, Any]:
        """Parse TxInf element using ISO path keys.

        Args:
            tx_inf: TxInf element

        Returns:
            Dict with ISO path keys like 'TxInf.RtrId', 'TxInf.RtrRsnInf.Rsn.Cd'
        """
        result = {}
        prefix = 'TxInf'

        # Return identification
        result[f'{prefix}.RtrId'] = self._find_text(tx_inf, 'RtrId')

        # Original payment identification
        result[f'{prefix}.OrgnlInstrId'] = self._find_text(tx_inf, 'OrgnlInstrId')
        result[f'{prefix}.OrgnlEndToEndId'] = self._find_text(tx_inf, 'OrgnlEndToEndId')
        result[f'{prefix}.OrgnlTxId'] = self._find_text(tx_inf, 'OrgnlTxId')
        result[f'{prefix}.OrgnlUETR'] = self._find_text(tx_inf, 'OrgnlUETR')
        result[f'{prefix}.OrgnlClrSysRef'] = self._find_text(tx_inf, 'OrgnlClrSysRef')

        # Returned Interbank Settlement Amount
        result.update(self._extract_amount_iso_path(tx_inf, 'RtrdIntrBkSttlmAmt', prefix))

        # Interbank Settlement Date
        result[f'{prefix}.IntrBkSttlmDt'] = self._find_text(tx_inf, 'IntrBkSttlmDt')

        # Settlement Priority
        result[f'{prefix}.SttlmPrty'] = self._find_text(tx_inf, 'SttlmPrty')

        # Return Reason Information
        rtr_rsn_inf = self._find(tx_inf, 'RtrRsnInf')
        if rtr_rsn_inf:
            rsn_prefix = f'{prefix}.RtrRsnInf'
            result[f'{rsn_prefix}.Rsn.Cd'] = self._find_text(rtr_rsn_inf, 'Rsn/Cd')
            result[f'{rsn_prefix}.Rsn.Prtry'] = self._find_text(rtr_rsn_inf, 'Rsn/Prtry')
            result[f'{rsn_prefix}.AddtlInf'] = self._find_text(rtr_rsn_inf, 'AddtlInf')

            # Return Originator
            orgtr = self._find(rtr_rsn_inf, 'Orgtr')
            if orgtr:
                result[f'{rsn_prefix}.Orgtr.Nm'] = self._find_text(orgtr, 'Nm')
                result[f'{rsn_prefix}.Orgtr.Id.OrgId.AnyBIC'] = self._find_text(orgtr, 'Id/OrgId/AnyBIC')

        # Instructing Agent
        instg_agt = self._find(tx_inf, 'InstgAgt')
        if instg_agt:
            result.update(self._extract_financial_institution_iso_path(instg_agt, f'{prefix}.InstgAgt'))

        # Instructed Agent
        instd_agt = self._find(tx_inf, 'InstdAgt')
        if instd_agt:
            result.update(self._extract_financial_institution_iso_path(instd_agt, f'{prefix}.InstdAgt'))

        # Original Transaction Reference
        orgnl_tx_ref = self._find(tx_inf, 'OrgnlTxRef')
        if orgnl_tx_ref:
            result.update(self._extract_original_tx_reference_iso_path(orgnl_tx_ref))

        return result

    def _extract_original_tx_reference_iso_path(self, orgnl_tx_ref: 'ET.Element') -> Dict[str, Any]:
        """Extract OrgnlTxRef using ISO path keys.

        Args:
            orgnl_tx_ref: OrgnlTxRef element

        Returns:
            Dict with ISO path keys like 'TxInf.OrgnlTxRef.Dbtr.Nm'
        """
        if orgnl_tx_ref is None:
            return {}

        result = {}
        prefix = 'TxInf.OrgnlTxRef'

        # Original Amount
        result.update(self._extract_amount_iso_path(orgnl_tx_ref, 'IntrBkSttlmAmt', prefix))

        # Original Settlement Date
        result[f'{prefix}.IntrBkSttlmDt'] = self._find_text(orgnl_tx_ref, 'IntrBkSttlmDt')

        # Original Debtor
        dbtr = self._find(orgnl_tx_ref, 'Dbtr')
        if dbtr:
            result.update(self._extract_party_iso_path(dbtr, f'{prefix}.Dbtr'))

        # Original Debtor Account
        dbtr_acct = self._find(orgnl_tx_ref, 'DbtrAcct')
        if dbtr_acct:
            result.update(self._extract_account_iso_path(dbtr_acct, f'{prefix}.DbtrAcct'))

        # Original Debtor Agent
        dbtr_agt = self._find(orgnl_tx_ref, 'DbtrAgt')
        if dbtr_agt:
            result.update(self._extract_financial_institution_iso_path(dbtr_agt, f'{prefix}.DbtrAgt'))

        # Original Creditor
        cdtr = self._find(orgnl_tx_ref, 'Cdtr')
        if cdtr:
            result.update(self._extract_party_iso_path(cdtr, f'{prefix}.Cdtr'))

        # Original Creditor Account
        cdtr_acct = self._find(orgnl_tx_ref, 'CdtrAcct')
        if cdtr_acct:
            result.update(self._extract_account_iso_path(cdtr_acct, f'{prefix}.CdtrAcct'))

        # Original Creditor Agent
        cdtr_agt = self._find(orgnl_tx_ref, 'CdtrAgt')
        if cdtr_agt:
            result.update(self._extract_financial_institution_iso_path(cdtr_agt, f'{prefix}.CdtrAgt'))

        # Ultimate Debtor
        ultmt_dbtr = self._find(orgnl_tx_ref, 'UltmtDbtr')
        if ultmt_dbtr:
            result.update(self._extract_party_iso_path(ultmt_dbtr, f'{prefix}.UltmtDbtr'))

        # Ultimate Creditor
        ultmt_cdtr = self._find(orgnl_tx_ref, 'UltmtCdtr')
        if ultmt_cdtr:
            result.update(self._extract_party_iso_path(ultmt_cdtr, f'{prefix}.UltmtCdtr'))

        # Remittance Information
        rmt_inf = self._find(orgnl_tx_ref, 'RmtInf')
        if rmt_inf:
            result.update(self._extract_remittance_info_iso_path(rmt_inf, f'{prefix}.RmtInf'))

        return result


class Pacs004Extractor(BaseISO20022Extractor):
    """Base extractor for all pacs.004-based payment return messages.

    pacs.004 is used to return funds from a previous payment.
    Key differences from pacs.008:
    - Contains original transaction references
    - Has return reason codes
    - Amount is the returned amount (may be partial)

    Systems inheriting from this:
    - Target2Pacs004Extractor
    - ChapsPacs004Extractor
    - FednowPacs004Extractor
    - etc.
    """

    MESSAGE_TYPE: str = "pacs.004"
    SILVER_TABLE: str = "stg_iso20022_pacs004"
    PARSER_CLASS = Pacs004Parser
    DEFAULT_CURRENCY: str = "XXX"
    CLEARING_SYSTEM: str = None

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from parsed pacs.004 message.

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
            'grp_hdr_sttlm_mtd': trunc(msg_content.get('settlementMethod'), 10),

            # Instructing/Instructed Agents
            'instg_agt_bic': trunc(msg_content.get('instructingAgentBic'), 11),
            'instg_agt_nm': trunc(msg_content.get('instructingAgentName'), 140),
            'instd_agt_bic': trunc(msg_content.get('instructedAgentBic'), 11),
            'instd_agt_nm': trunc(msg_content.get('instructedAgentName'), 140),

            # Original Group Information
            'orgnl_grp_inf_orgnl_msg_id': trunc(msg_content.get('originalMessageId'), 35),
            'orgnl_grp_inf_orgnl_msg_nm_id': trunc(msg_content.get('originalMessageNameId'), 35),
            'orgnl_grp_inf_orgnl_cre_dt_tm': msg_content.get('originalCreationDateTime'),

            # Return Transaction Information
            'tx_inf_rtr_id': trunc(msg_content.get('returnId'), 35),
            'tx_inf_orgnl_instr_id': trunc(msg_content.get('originalInstructionId'), 35),
            'tx_inf_orgnl_end_to_end_id': trunc(msg_content.get('originalEndToEndId'), 35),
            'tx_inf_orgnl_tx_id': trunc(msg_content.get('originalTransactionId'), 35),
            'tx_inf_orgnl_uetr': msg_content.get('originalUETR'),
            'tx_inf_orgnl_clr_sys_ref': trunc(msg_content.get('originalClearingSystemRef'), 35),

            # Returned Amount
            'tx_inf_rtrd_intr_bk_sttlm_amt': msg_content.get('returnedSettlementAmount'),
            'tx_inf_rtrd_intr_bk_sttlm_ccy': msg_content.get('returnedSettlementCurrency'),
            'tx_inf_intr_bk_sttlm_dt': msg_content.get('interbankSettlementDate'),
            'tx_inf_sttlm_prty': trunc(msg_content.get('settlementPriority'), 10),

            # Return Reason
            'tx_inf_rtr_rsn_cd': trunc(msg_content.get('returnReasonCode'), 10),
            'tx_inf_rtr_rsn_prtry': trunc(msg_content.get('returnReasonProprietary'), 35),
            'tx_inf_rtr_addtl_inf': msg_content.get('returnAdditionalInfo'),
            'tx_inf_rtr_orgtr_nm': trunc(msg_content.get('returnOriginatorName'), 140),
            'tx_inf_rtr_orgtr_bic': trunc(msg_content.get('returnOriginatorBic'), 11),

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
            'grp_hdr_msg_id', 'grp_hdr_cre_dt_tm', 'grp_hdr_nb_of_txs', 'grp_hdr_sttlm_mtd',

            # Instructing/Instructed Agents
            'instg_agt_bic', 'instg_agt_nm', 'instd_agt_bic', 'instd_agt_nm',

            # Original Group Information
            'orgnl_grp_inf_orgnl_msg_id', 'orgnl_grp_inf_orgnl_msg_nm_id',
            'orgnl_grp_inf_orgnl_cre_dt_tm',

            # Return Transaction Information
            'tx_inf_rtr_id', 'tx_inf_orgnl_instr_id', 'tx_inf_orgnl_end_to_end_id',
            'tx_inf_orgnl_tx_id', 'tx_inf_orgnl_uetr', 'tx_inf_orgnl_clr_sys_ref',

            # Returned Amount
            'tx_inf_rtrd_intr_bk_sttlm_amt', 'tx_inf_rtrd_intr_bk_sttlm_ccy',
            'tx_inf_intr_bk_sttlm_dt', 'tx_inf_sttlm_prty',

            # Return Reason
            'tx_inf_rtr_rsn_cd', 'tx_inf_rtr_rsn_prtry', 'tx_inf_rtr_addtl_inf',
            'tx_inf_rtr_orgtr_nm', 'tx_inf_rtr_orgtr_bic',

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
        """Extract party entities from pacs.004 Silver record.

        In returns, the original debtor becomes creditor (receiving the return)
        and original creditor becomes debtor (returning funds).

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import PartyData

        # Original Debtor (receiving the returned funds - now effectively creditor)
        if silver_data.get('orgnl_tx_ref_dbtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('orgnl_tx_ref_dbtr_nm'),
                role="CREDITOR",  # Role reversed in return
                party_type='UNKNOWN',
            ))

        # Original Creditor (returning funds - now effectively debtor)
        if silver_data.get('orgnl_tx_ref_cdtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('orgnl_tx_ref_cdtr_nm'),
                role="DEBTOR",  # Role reversed in return
                party_type='UNKNOWN',
            ))

        # Return Originator
        if silver_data.get('tx_inf_rtr_orgtr_nm'):
            entities.parties.append(PartyData(
                name=silver_data.get('tx_inf_rtr_orgtr_nm'),
                role="RETURN_ORIGINATOR",
                party_type='UNKNOWN',
            ))

    def _extract_accounts(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract account entities from pacs.004 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import AccountData

        currency = silver_data.get('tx_inf_rtrd_intr_bk_sttlm_ccy') or self.DEFAULT_CURRENCY

        # Original Debtor Account (receiving return - now creditor account)
        debtor_acct = silver_data.get('orgnl_tx_ref_dbtr_acct_id_iban') or silver_data.get('orgnl_tx_ref_dbtr_acct_id_othr')
        if debtor_acct:
            entities.accounts.append(AccountData(
                account_number=debtor_acct,
                role="CREDITOR",  # Role reversed
                iban=silver_data.get('orgnl_tx_ref_dbtr_acct_id_iban'),
                account_type='CACC',
                currency=currency,
            ))

        # Original Creditor Account (returning - now debtor account)
        creditor_acct = silver_data.get('orgnl_tx_ref_cdtr_acct_id_iban') or silver_data.get('orgnl_tx_ref_cdtr_acct_id_othr')
        if creditor_acct:
            entities.accounts.append(AccountData(
                account_number=creditor_acct,
                role="DEBTOR",  # Role reversed
                iban=silver_data.get('orgnl_tx_ref_cdtr_acct_id_iban'),
                account_type='CACC',
                currency=currency,
            ))

    def _extract_financial_institutions(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract financial institution entities from pacs.004 Silver record.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import FinancialInstitutionData

        # Instructing Agent
        if silver_data.get('instg_agt_bic'):
            bic = silver_data.get('instg_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTING_AGENT",
                name=silver_data.get('instg_agt_nm') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Instructed Agent
        if silver_data.get('instd_agt_bic'):
            bic = silver_data.get('instd_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTED_AGENT",
                name=silver_data.get('instd_agt_nm') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Original Debtor Agent (now creditor agent in return flow)
        if silver_data.get('orgnl_tx_ref_dbtr_agt_bic'):
            bic = silver_data.get('orgnl_tx_ref_dbtr_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",  # Role reversed
                name=f"FI_{bic}" if bic else None,
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Original Creditor Agent (now debtor agent in return flow)
        if silver_data.get('orgnl_tx_ref_cdtr_agt_bic'):
            bic = silver_data.get('orgnl_tx_ref_cdtr_agt_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",  # Role reversed
                name=f"FI_{bic}" if bic else None,
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Return Originator (if BIC present)
        if silver_data.get('tx_inf_rtr_orgtr_bic'):
            bic = silver_data.get('tx_inf_rtr_orgtr_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="RETURN_ORIGINATOR",
                name=silver_data.get('tx_inf_rtr_orgtr_nm') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

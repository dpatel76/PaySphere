"""ISO 20022 pacs.009 Parser and Extractor base classes.

pacs.009 (FI Credit Transfer) is used for bank-to-bank transfers where both
the debtor and creditor are financial institutions. Key differences from pacs.008:
- Debtor/Creditor are FinInstnId elements (not regular party elements)
- Used for interbank settlements, liquidity management
- Different party structures than customer credit transfers

Systems using pacs.009:
- TARGET2 (Eurozone RTGS)
- FEDWIRE (for bank-to-bank transfers)
- CHIPS (for interbank transfers)

Reference: ISO 20022 Message Definition Report - pacs.009.001.08
"""

from typing import Dict, Any, List, Optional
import logging

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor

logger = logging.getLogger(__name__)


class Pacs009Parser(BaseISO20022Parser):
    """Base parser for pacs.009 FI Credit Transfer messages.

    pacs.009 is for financial institution-to-financial institution credit transfers.
    The main difference from pacs.008 is that Debtor and Creditor are financial
    institutions (identified by BIC/LEI) rather than regular parties.

    pacs.009 structure:
    - Document
      - FICdtTrf
        - GrpHdr (Group Header)
        - CdtTrfTxInf (Credit Transfer Transaction Information) [1..*]
    """

    ROOT_ELEMENT = "FICdtTrf"
    MESSAGE_TYPE = "pacs.009"

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse pacs.009 FI Credit Transfer message.

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pacs.009 fields
        """
        root = self._parse_xml(xml_content)

        # Find the FICdtTrf element
        fi_transfer = self._find(root, self.ROOT_ELEMENT)
        if fi_transfer is None:
            # Check if root IS the message element
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                fi_transfer = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pacs.009 message")

        return self._parse_fi_credit_transfer(fi_transfer)

    def _parse_fi_credit_transfer(self, fi_transfer) -> Dict[str, Any]:
        """Parse FICdtTrf element.

        Args:
            fi_transfer: FICdtTrf element

        Returns:
            Dict with extracted fields
        """
        result = {
            'isISO20022': True,
            'messageTypeCode': 'pacs.009',
        }

        # Extract Group Header
        result.update(self._extract_group_header(fi_transfer))

        # Extract first Credit Transfer Transaction
        cdt_trf_tx_inf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf_tx_inf is not None:
            result.update(self._parse_credit_transfer_tx(cdt_trf_tx_inf))

        return result

    def _parse_credit_transfer_tx(self, cdt_trf: 'ET.Element') -> Dict[str, Any]:
        """Parse CdtTrfTxInf element for pacs.009.

        pacs.009 has Debtor/Creditor as financial institutions, so the structure
        is different from pacs.008. The Dbtr/Cdtr elements contain FinInstnId.

        Args:
            cdt_trf: CdtTrfTxInf element

        Returns:
            Dict with extracted transaction fields
        """
        result = {}

        # Payment Identification
        pmt_id = self._find(cdt_trf, 'PmtId')
        if pmt_id:
            result.update(self._extract_payment_id(pmt_id))

        # Payment Type Information
        pmt_tp_inf = self._find(cdt_trf, 'PmtTpInf')
        if pmt_tp_inf:
            result.update(self._extract_payment_type_info(pmt_tp_inf))

        # Interbank Settlement Amount
        amt_data = self._extract_amount(cdt_trf, 'IntrBkSttlmAmt')
        result['amount'] = amt_data.get('amount')
        result['currency'] = amt_data.get('currency')

        # Interbank Settlement Date (transaction level)
        result['interbankSettlementDateTx'] = self._find_text(cdt_trf, 'IntrBkSttlmDt')

        # Settlement Priority
        result['settlementPriority'] = self._find_text(cdt_trf, 'SttlmPrty')

        # Settlement Time Indication
        result['settlementTimeRequest'] = self._find_text(cdt_trf, 'SttlmTmIndctn/CdtDtTm')

        # Charge Bearer
        result['chargeBearer'] = self._find_text(cdt_trf, 'ChrgBr')

        # Debtor (Financial Institution in pacs.009)
        dbtr = self._find(cdt_trf, 'Dbtr')
        if dbtr:
            result.update(self._extract_fi_party(dbtr, 'debtor'))

        # Debtor Account
        dbtr_acct = self._find(cdt_trf, 'DbtrAcct')
        if dbtr_acct:
            result.update(self._extract_account(dbtr_acct, 'debtorAccount'))

        # Debtor Agent
        dbtr_agt = self._find(cdt_trf, 'DbtrAgt')
        if dbtr_agt:
            result.update(self._extract_financial_institution(dbtr_agt, 'debtorAgent'))

        # Creditor (Financial Institution in pacs.009)
        cdtr = self._find(cdt_trf, 'Cdtr')
        if cdtr:
            result.update(self._extract_fi_party(cdtr, 'creditor'))

        # Creditor Account
        cdtr_acct = self._find(cdt_trf, 'CdtrAcct')
        if cdtr_acct:
            result.update(self._extract_account(cdtr_acct, 'creditorAccount'))

        # Creditor Agent
        cdtr_agt = self._find(cdt_trf, 'CdtrAgt')
        if cdtr_agt:
            result.update(self._extract_financial_institution(cdtr_agt, 'creditorAgent'))

        # Intermediary Agents
        intrmy_agt1 = self._find(cdt_trf, 'IntrmyAgt1')
        if intrmy_agt1:
            result.update(self._extract_financial_institution(intrmy_agt1, 'intermediaryAgent1'))

        # Underlying Customer Credit Transfer (if this is a cover payment)
        undrlg_cstmr = self._find(cdt_trf, 'UndrlygCstmrCdtTrf')
        if undrlg_cstmr:
            result['hasUnderlyingCustomerTransfer'] = True
            result.update(self._extract_underlying_customer_transfer(undrlg_cstmr))

        return result

    def _extract_fi_party(self, party_element, prefix: str) -> Dict[str, Any]:
        """Extract financial institution party (Dbtr/Cdtr in pacs.009).

        In pacs.009, the Debtor and Creditor are financial institutions,
        so they have FinInstnId structure directly.

        Args:
            party_element: Dbtr or Cdtr element
            prefix: Key prefix for result dict

        Returns:
            Dict with prefixed FI party fields
        """
        if party_element is None:
            return {}

        result = {}

        # Direct FinInstnId within Dbtr/Cdtr
        fin_instn_id = self._find(party_element, 'FinInstnId')
        if fin_instn_id is not None:
            result[f'{prefix}Bic'] = self._find_text(fin_instn_id, 'BICFI')
            result[f'{prefix}Lei'] = self._find_text(fin_instn_id, 'LEI')
            result[f'{prefix}Name'] = self._find_text(fin_instn_id, 'Nm')
            result[f'{prefix}ClearingSystemId'] = self._find_text(fin_instn_id, 'ClrSysMmbId/ClrSysId/Cd')
            result[f'{prefix}MemberId'] = self._find_text(fin_instn_id, 'ClrSysMmbId/MmbId')

            # Postal address
            pstl_adr = self._find(fin_instn_id, 'PstlAdr')
            if pstl_adr:
                result.update(self._extract_postal_address(pstl_adr, prefix))
        else:
            # Fallback: regular party structure
            result[f'{prefix}Name'] = self._find_text(party_element, 'Nm')

        return result

    def _extract_underlying_customer_transfer(self, undrlg: 'ET.Element') -> Dict[str, Any]:
        """Extract underlying customer credit transfer details.

        For cover payments, pacs.009 can include details of the underlying
        customer payment that this bank transfer is covering.

        Args:
            undrlg: UndrlygCstmrCdtTrf element

        Returns:
            Dict with underlying transfer fields
        """
        result = {}

        # Underlying amount
        amt_elem = self._find(undrlg, 'InstdAmt')
        if amt_elem is not None:
            result['underlyingAmount'] = self._safe_float(amt_elem.text)
            result['underlyingCurrency'] = amt_elem.get('Ccy')

        # Underlying debtor
        dbtr = self._find(undrlg, 'Dbtr')
        if dbtr:
            result['underlyingDebtorName'] = self._find_text(dbtr, 'Nm')

        # Underlying creditor
        cdtr = self._find(undrlg, 'Cdtr')
        if cdtr:
            result['underlyingCreditorName'] = self._find_text(cdtr, 'Nm')

        # Underlying remittance
        rmt_inf = self._find(undrlg, 'RmtInf')
        if rmt_inf:
            result['underlyingRemittance'] = self._find_text(rmt_inf, 'Ustrd')

        return result

    def parse_iso_paths(self, xml_content: str) -> Dict[str, Any]:
        """Parse pacs.009 message using full ISO path key naming.

        Returns keys using ISO 20022 element path notation:
        - GrpHdr.MsgId, GrpHdr.CreDtTm, GrpHdr.NbOfTxs
        - CdtTrfTxInf.PmtId.InstrId, CdtTrfTxInf.PmtId.EndToEndId
        - CdtTrfTxInf.Dbtr.FinInstnId.BICFI (pacs.009 specific - Dbtr is FI)
        - CdtTrfTxInf.Cdtr.FinInstnId.BICFI (pacs.009 specific - Cdtr is FI)
        - CdtTrfTxInf.DbtrAgt.FinInstnId.BICFI
        - CdtTrfTxInf.CdtrAgt.FinInstnId.BICFI

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with full ISO path keys
        """
        root = self._parse_xml(xml_content)

        # Find the FICdtTrf element
        fi_transfer = self._find(root, self.ROOT_ELEMENT)
        if fi_transfer is None:
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                fi_transfer = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pacs.009 message")

        result = {
            'isISO20022': True,
            'messageTypeCode': 'pacs.009',
        }

        # Extract Group Header using ISO paths
        result.update(self._extract_group_header_iso_path(fi_transfer))

        # Extract first Credit Transfer Transaction using ISO paths
        cdt_trf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf is not None:
            result.update(self._parse_credit_transfer_tx_iso_paths(cdt_trf))

        return result

    def _parse_credit_transfer_tx_iso_paths(self, cdt_trf) -> Dict[str, Any]:
        """Parse CdtTrfTxInf element using full ISO path keys.

        Args:
            cdt_trf: CdtTrfTxInf element

        Returns:
            Dict with full ISO path keys
        """
        result = {}
        prefix = 'CdtTrfTxInf'

        # Payment Identification
        pmt_id = self._find(cdt_trf, 'PmtId')
        if pmt_id:
            result.update(self._extract_payment_id_iso_path(pmt_id, f'{prefix}.PmtId'))

        # Payment Type Information
        pmt_tp_inf = self._find(cdt_trf, 'PmtTpInf')
        if pmt_tp_inf:
            result.update(self._extract_payment_type_info_iso_path(pmt_tp_inf, f'{prefix}.PmtTpInf'))

        # Interbank Settlement Amount
        result.update(self._extract_amount_iso_path(cdt_trf, 'IntrBkSttlmAmt', f'{prefix}.IntrBkSttlmAmt'))

        # Interbank Settlement Date (transaction level)
        result[f'{prefix}.IntrBkSttlmDt'] = self._find_text(cdt_trf, 'IntrBkSttlmDt')

        # Settlement Priority
        result[f'{prefix}.SttlmPrty'] = self._find_text(cdt_trf, 'SttlmPrty')

        # Charge Bearer
        result[f'{prefix}.ChrgBr'] = self._find_text(cdt_trf, 'ChrgBr')

        # Debtor (Financial Institution in pacs.009)
        dbtr = self._find(cdt_trf, 'Dbtr')
        if dbtr:
            result.update(self._extract_fi_party_iso_path(dbtr, f'{prefix}.Dbtr'))

        # Debtor Account
        dbtr_acct = self._find(cdt_trf, 'DbtrAcct')
        if dbtr_acct:
            result.update(self._extract_account_iso_path(dbtr_acct, f'{prefix}.DbtrAcct'))

        # Debtor Agent
        dbtr_agt = self._find(cdt_trf, 'DbtrAgt')
        if dbtr_agt:
            result.update(self._extract_financial_institution_iso_path(dbtr_agt, f'{prefix}.DbtrAgt'))

        # Creditor (Financial Institution in pacs.009)
        cdtr = self._find(cdt_trf, 'Cdtr')
        if cdtr:
            result.update(self._extract_fi_party_iso_path(cdtr, f'{prefix}.Cdtr'))

        # Creditor Account
        cdtr_acct = self._find(cdt_trf, 'CdtrAcct')
        if cdtr_acct:
            result.update(self._extract_account_iso_path(cdtr_acct, f'{prefix}.CdtrAcct'))

        # Creditor Agent
        cdtr_agt = self._find(cdt_trf, 'CdtrAgt')
        if cdtr_agt:
            result.update(self._extract_financial_institution_iso_path(cdtr_agt, f'{prefix}.CdtrAgt'))

        # Intermediary Agents
        intrmy_agt1 = self._find(cdt_trf, 'IntrmyAgt1')
        if intrmy_agt1:
            result.update(self._extract_financial_institution_iso_path(intrmy_agt1, f'{prefix}.IntrmyAgt1'))

        intrmy_agt2 = self._find(cdt_trf, 'IntrmyAgt2')
        if intrmy_agt2:
            result.update(self._extract_financial_institution_iso_path(intrmy_agt2, f'{prefix}.IntrmyAgt2'))

        # Purpose
        purp = self._find(cdt_trf, 'Purp')
        if purp:
            result[f'{prefix}.Purp.Cd'] = self._find_text(purp, 'Cd')
            result[f'{prefix}.Purp.Prtry'] = self._find_text(purp, 'Prtry')

        # Remittance Information
        rmt_inf = self._find(cdt_trf, 'RmtInf')
        if rmt_inf:
            result.update(self._extract_remittance_info_iso_path(rmt_inf, f'{prefix}.RmtInf'))

        # Underlying Customer Credit Transfer (for cover payments)
        undrlg = self._find(cdt_trf, 'UndrlygCstmrCdtTrf')
        if undrlg:
            result[f'{prefix}.UndrlygCstmrCdtTrf'] = True
            result.update(self._extract_underlying_iso_path(undrlg, f'{prefix}.UndrlygCstmrCdtTrf'))

        return result

    def _extract_fi_party_iso_path(self, party_element, path_prefix: str) -> Dict[str, Any]:
        """Extract financial institution party using ISO path keys.

        In pacs.009, Dbtr and Cdtr are financial institutions with FinInstnId.

        Args:
            party_element: Dbtr or Cdtr element
            path_prefix: ISO path prefix (e.g., 'CdtTrfTxInf.Dbtr')

        Returns:
            Dict with full ISO path keys
        """
        if party_element is None:
            return {}

        result = {}
        fin_instn_id = self._find(party_element, 'FinInstnId')
        if fin_instn_id is not None:
            fi_prefix = f'{path_prefix}.FinInstnId'
            result[f'{fi_prefix}.BICFI'] = self._find_text(fin_instn_id, 'BICFI')
            result[f'{fi_prefix}.LEI'] = self._find_text(fin_instn_id, 'LEI')
            result[f'{fi_prefix}.Nm'] = self._find_text(fin_instn_id, 'Nm')

            # Clearing System Member ID
            clr_sys = self._find(fin_instn_id, 'ClrSysMmbId')
            if clr_sys:
                result[f'{fi_prefix}.ClrSysMmbId.ClrSysId.Cd'] = self._find_text(clr_sys, 'ClrSysId/Cd')
                result[f'{fi_prefix}.ClrSysMmbId.MmbId'] = self._find_text(clr_sys, 'MmbId')

            # Postal address
            pstl_adr = self._find(fin_instn_id, 'PstlAdr')
            if pstl_adr:
                result[f'{fi_prefix}.PstlAdr.Ctry'] = self._find_text(pstl_adr, 'Ctry')
                result[f'{fi_prefix}.PstlAdr.TwnNm'] = self._find_text(pstl_adr, 'TwnNm')
                result[f'{fi_prefix}.PstlAdr.AdrLine'] = self._find_text(pstl_adr, 'AdrLine')

        return result

    def _extract_underlying_iso_path(self, undrlg, path_prefix: str) -> Dict[str, Any]:
        """Extract underlying customer credit transfer using ISO paths.

        Args:
            undrlg: UndrlygCstmrCdtTrf element
            path_prefix: ISO path prefix

        Returns:
            Dict with full ISO path keys
        """
        result = {}

        # Underlying amount
        amt_elem = self._find(undrlg, 'InstdAmt')
        if amt_elem is not None:
            result[f'{path_prefix}.InstdAmt'] = self._safe_float(amt_elem.text)
            result[f'{path_prefix}.InstdAmt@Ccy'] = amt_elem.get('Ccy')

        # Underlying debtor
        dbtr = self._find(undrlg, 'Dbtr')
        if dbtr:
            result[f'{path_prefix}.Dbtr.Nm'] = self._find_text(dbtr, 'Nm')

        # Underlying creditor
        cdtr = self._find(undrlg, 'Cdtr')
        if cdtr:
            result[f'{path_prefix}.Cdtr.Nm'] = self._find_text(cdtr, 'Nm')

        # Underlying remittance
        rmt_inf = self._find(undrlg, 'RmtInf')
        if rmt_inf:
            result[f'{path_prefix}.RmtInf.Ustrd'] = self._find_text(rmt_inf, 'Ustrd')

        return result


class Pacs009Extractor(BaseISO20022Extractor):
    """Base extractor for all pacs.009-based payment systems.

    pacs.009 is for FI-to-FI transfers where both parties are financial
    institutions. Key differences from Pacs008Extractor:
    - Debtor/Creditor are FIs (have BIC, not personal name/address)
    - May include underlying customer transfer details
    - Used for settlement, liquidity management

    Systems inheriting from this:
    - Target2Extractor
    - FedwirePacs009Extractor (for bank-to-bank Fedwire)
    - ChipsPacs009Extractor (for interbank CHIPS)
    """

    MESSAGE_TYPE: str = "pacs.009"
    SILVER_TABLE: str = "stg_pacs009"
    PARSER_CLASS = Pacs009Parser
    DEFAULT_CURRENCY: str = "EUR"  # TARGET2 default
    CLEARING_SYSTEM: str = None

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from parsed pacs.009 message.

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
            '_batch_id': batch_id,

            # Message identification
            'message_type': self.MESSAGE_TYPE,
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),

            # Payment identification
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),

            # Settlement
            'settlement_date': msg_content.get('interbankSettlementDate'),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),
            'settlement_priority': trunc(msg_content.get('settlementPriority'), 10),
            'clearing_system_code': trunc(msg_content.get('clearingSystemCode'), 10),

            # Amount
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or self.DEFAULT_CURRENCY,
            'charge_bearer': trunc(msg_content.get('chargeBearer'), 10),

            # Payment type
            'instruction_priority': trunc(msg_content.get('instructionPriority'), 10),
            'service_level': trunc(msg_content.get('serviceLevelCode'), 35),
            'local_instrument': trunc(msg_content.get('localInstrumentCode'), 35),

            # Instructing/Instructed Agents (header level)
            'instructing_agent_bic': trunc(msg_content.get('instructingAgentBic'), 11),
            'instructing_agent_name': trunc(msg_content.get('instructingAgentName'), 140),
            'instructing_agent_member_id': trunc(msg_content.get('instructingAgentMemberId'), 35),

            'instructed_agent_bic': trunc(msg_content.get('instructedAgentBic'), 11),
            'instructed_agent_name': trunc(msg_content.get('instructedAgentName'), 140),
            'instructed_agent_member_id': trunc(msg_content.get('instructedAgentMemberId'), 35),

            # Debtor FI (pacs.009 specific - debtor is an FI)
            'debtor_bic': trunc(msg_content.get('debtorBic'), 11),
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_lei': trunc(msg_content.get('debtorLei'), 20),
            'debtor_member_id': trunc(msg_content.get('debtorMemberId'), 35),
            'debtor_clearing_system_id': trunc(msg_content.get('debtorClearingSystemId'), 10),
            'debtor_country': trunc(msg_content.get('debtorCountry'), 2),

            # Debtor Account
            'debtor_account_iban': trunc(msg_content.get('debtorAccountIban'), 34),
            'debtor_account_other': trunc(msg_content.get('debtorAccountOther'), 34),

            # Debtor Agent
            'debtor_agent_bic': trunc(msg_content.get('debtorAgentBic'), 11),
            'debtor_agent_name': trunc(msg_content.get('debtorAgentName'), 140),
            'debtor_agent_member_id': trunc(msg_content.get('debtorAgentMemberId'), 35),

            # Creditor FI (pacs.009 specific - creditor is an FI)
            'creditor_bic': trunc(msg_content.get('creditorBic'), 11),
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_lei': trunc(msg_content.get('creditorLei'), 20),
            'creditor_member_id': trunc(msg_content.get('creditorMemberId'), 35),
            'creditor_clearing_system_id': trunc(msg_content.get('creditorClearingSystemId'), 10),
            'creditor_country': trunc(msg_content.get('creditorCountry'), 2),

            # Creditor Account
            'creditor_account_iban': trunc(msg_content.get('creditorAccountIban'), 34),
            'creditor_account_other': trunc(msg_content.get('creditorAccountOther'), 34),

            # Creditor Agent
            'creditor_agent_bic': trunc(msg_content.get('creditorAgentBic'), 11),
            'creditor_agent_name': trunc(msg_content.get('creditorAgentName'), 140),
            'creditor_agent_member_id': trunc(msg_content.get('creditorAgentMemberId'), 35),

            # Intermediary Agent
            'intermediary_agent_bic': trunc(msg_content.get('intermediaryAgent1Bic'), 11),
            'intermediary_agent_name': trunc(msg_content.get('intermediaryAgent1Name'), 140),
            'intermediary_agent_member_id': trunc(msg_content.get('intermediaryAgent1MemberId'), 35),

            # Underlying Customer Transfer (for cover payments)
            'has_underlying_customer_transfer': msg_content.get('hasUnderlyingCustomerTransfer', False),
            'underlying_amount': msg_content.get('underlyingAmount'),
            'underlying_currency': msg_content.get('underlyingCurrency'),
            'underlying_debtor_name': trunc(msg_content.get('underlyingDebtorName'), 140),
            'underlying_creditor_name': trunc(msg_content.get('underlyingCreditorName'), 140),
            'underlying_remittance': msg_content.get('underlyingRemittance'),

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
            'stg_id', 'raw_id', '_batch_id', 'message_type', 'message_id',

            # Timestamps
            'creation_date_time', 'settlement_date',

            # Payment identification
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr',

            # Settlement
            'settlement_method', 'settlement_priority', 'clearing_system_code',

            # Amount
            'amount', 'currency', 'charge_bearer',

            # Payment type
            'instruction_priority', 'service_level', 'local_instrument',

            # Instructing/Instructed Agents
            'instructing_agent_bic', 'instructing_agent_name', 'instructing_agent_member_id',
            'instructed_agent_bic', 'instructed_agent_name', 'instructed_agent_member_id',

            # Debtor FI
            'debtor_bic', 'debtor_name', 'debtor_lei', 'debtor_member_id',
            'debtor_clearing_system_id', 'debtor_country',

            # Debtor Account
            'debtor_account_iban', 'debtor_account_other',

            # Debtor Agent
            'debtor_agent_bic', 'debtor_agent_name', 'debtor_agent_member_id',

            # Creditor FI
            'creditor_bic', 'creditor_name', 'creditor_lei', 'creditor_member_id',
            'creditor_clearing_system_id', 'creditor_country',

            # Creditor Account
            'creditor_account_iban', 'creditor_account_other',

            # Creditor Agent
            'creditor_agent_bic', 'creditor_agent_name', 'creditor_agent_member_id',

            # Intermediary Agent
            'intermediary_agent_bic', 'intermediary_agent_name', 'intermediary_agent_member_id',

            # Underlying Customer Transfer
            'has_underlying_customer_transfer', 'underlying_amount', 'underlying_currency',
            'underlying_debtor_name', 'underlying_creditor_name', 'underlying_remittance',

            # Processing
            'processing_status',
        ]

    def _extract_parties(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract party entities from pacs.009 Silver record.

        In pacs.009, the debtor/creditor are financial institutions,
        so we create FI entities rather than party entities.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import PartyData

        # In pacs.009, debtor/creditor are FIs - we still create party records
        # but they represent financial institutions
        if silver_data.get('debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('debtor_name'),
                role="DEBTOR",
                party_type='FINANCIAL_INSTITUTION',
                identification_type='BIC' if silver_data.get('debtor_bic') else 'LEI' if silver_data.get('debtor_lei') else None,
                identification_number=silver_data.get('debtor_bic') or silver_data.get('debtor_lei'),
                country=silver_data.get('debtor_country'),
            ))

        if silver_data.get('creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('creditor_name'),
                role="CREDITOR",
                party_type='FINANCIAL_INSTITUTION',
                identification_type='BIC' if silver_data.get('creditor_bic') else 'LEI' if silver_data.get('creditor_lei') else None,
                identification_number=silver_data.get('creditor_bic') or silver_data.get('creditor_lei'),
                country=silver_data.get('creditor_country'),
            ))

        # Underlying customer parties (if cover payment)
        if silver_data.get('underlying_debtor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('underlying_debtor_name'),
                role="ULTIMATE_DEBTOR",
                party_type='UNKNOWN',
            ))

        if silver_data.get('underlying_creditor_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('underlying_creditor_name'),
                role="ULTIMATE_CREDITOR",
                party_type='UNKNOWN',
            ))

    def _extract_financial_institutions(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract financial institution entities from pacs.009 Silver record.

        In pacs.009, the debtor/creditor themselves are FIs, so we create
        FI entities for them in addition to the agents.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import FinancialInstitutionData

        # Debtor FI (the debtor in pacs.009 IS a financial institution)
        if silver_data.get('debtor_bic') or silver_data.get('debtor_member_id'):
            bic = silver_data.get('debtor_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR",
                name=silver_data.get('debtor_name'),
                bic=bic,
                lei=silver_data.get('debtor_lei'),
                clearing_code=silver_data.get('debtor_member_id'),
                clearing_system=silver_data.get('debtor_clearing_system_id') or self.CLEARING_SYSTEM,
                country=silver_data.get('debtor_country') or self._derive_country(bic, None),
            ))

        # Creditor FI (the creditor in pacs.009 IS a financial institution)
        if silver_data.get('creditor_bic') or silver_data.get('creditor_member_id'):
            bic = silver_data.get('creditor_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR",
                name=silver_data.get('creditor_name'),
                bic=bic,
                lei=silver_data.get('creditor_lei'),
                clearing_code=silver_data.get('creditor_member_id'),
                clearing_system=silver_data.get('creditor_clearing_system_id') or self.CLEARING_SYSTEM,
                country=silver_data.get('creditor_country') or self._derive_country(bic, None),
            ))

        # Debtor Agent
        if silver_data.get('debtor_agent_bic') or silver_data.get('debtor_agent_member_id'):
            bic = silver_data.get('debtor_agent_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=silver_data.get('debtor_agent_name'),
                bic=bic,
                clearing_code=silver_data.get('debtor_agent_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Creditor Agent
        if silver_data.get('creditor_agent_bic') or silver_data.get('creditor_agent_member_id'):
            bic = silver_data.get('creditor_agent_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=silver_data.get('creditor_agent_name'),
                bic=bic,
                clearing_code=silver_data.get('creditor_agent_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Instructing Agent
        if silver_data.get('instructing_agent_bic') or silver_data.get('instructing_agent_member_id'):
            bic = silver_data.get('instructing_agent_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTING_AGENT",
                name=silver_data.get('instructing_agent_name'),
                bic=bic,
                clearing_code=silver_data.get('instructing_agent_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Instructed Agent
        if silver_data.get('instructed_agent_bic') or silver_data.get('instructed_agent_member_id'):
            bic = silver_data.get('instructed_agent_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTED_AGENT",
                name=silver_data.get('instructed_agent_name'),
                bic=bic,
                clearing_code=silver_data.get('instructed_agent_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Intermediary Agent
        if silver_data.get('intermediary_agent_bic') or silver_data.get('intermediary_agent_member_id'):
            bic = silver_data.get('intermediary_agent_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY_AGENT1",
                name=silver_data.get('intermediary_agent_name'),
                bic=bic,
                clearing_code=silver_data.get('intermediary_agent_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

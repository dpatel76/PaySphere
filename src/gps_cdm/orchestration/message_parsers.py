"""
GPS CDM - Comprehensive Multi-Message Type Parsers
===================================================

Complete parsers for ALL supported payment message types (72+ standards):

ISO 20022 - Payments Initiation (pain):
- pain.001 - Customer Credit Transfer Initiation
- pain.002 - Payment Status Report
- pain.007 - Customer Payment Reversal
- pain.008 - Customer Direct Debit Initiation
- pain.013 - Creditor Payment Activation Request
- pain.014 - Creditor Payment Activation Request Status Report

ISO 20022 - Payments Clearing and Settlement (pacs):
- pacs.002 - FI Payment Status Report
- pacs.003 - FI Direct Debit
- pacs.004 - Payment Return
- pacs.007 - FI Payment Reversal
- pacs.008 - FI Customer Credit Transfer
- pacs.009 - FI Credit Transfer (Cover)
- pacs.028 - FI Positive Pay Response

ISO 20022 - Cash Management (camt):
- camt.026 - Unable to Apply
- camt.027 - Claim Non-Receipt
- camt.028 - Additional Payment Information
- camt.029 - Resolution of Investigation
- camt.052 - Account Report (Intraday)
- camt.053 - Account Statement
- camt.054 - Bank to Customer Debit Credit Notification
- camt.055 - Customer Payment Cancellation Request
- camt.056 - FI Payment Cancellation Request
- camt.057 - Notification to Receive
- camt.058 - Notification to Receive Cancellation
- camt.059 - Notification to Receive Status Report
- camt.060 - Account Reporting Request
- camt.086 - Bank Services Billing Statement
- camt.087 - Request for Duplicate

ISO 20022 - Account Management (acmt):
- acmt.001 - Account Opening Instruction
- acmt.002 - Account Opening Amendment
- acmt.003 - Account Modification Instruction
- acmt.005 - Account Management Status Report Request
- acmt.006 - Account Management Status Report
- acmt.007 - Account Opening Request

SWIFT MT Messages:
- MT103/MT103+ - Single Customer Credit Transfer
- MT200 - General Financial Institution Transfer (Own Account)
- MT201 - Multiple General Financial Institution Transfer
- MT202/MT202COV - General FI Transfer / Cover Payment
- MT203 - Multiple FI Transfer
- MT204 - Financial Markets Direct Debit
- MT205/MT205COV - FI Transfer Execution
- MT900 - Confirmation of Debit
- MT910 - Confirmation of Credit
- MT940 - Customer Statement
- MT942 - Interim Transaction Report
- MT950 - Statement Message

Domestic Payment Schemes:
- SEPA SCT (pain.001/pacs.008 based)
- SEPA SDD (pain.008/pacs.003 based)
- NACHA ACH (File format)
- Fedwire (Fixed-width format)
- CHIPS (Proprietary format)
- BACS/CHAPS/Faster Payments UK

Real-Time Payment Systems:
- FedNow (ISO 20022 based)
- RTP (ISO 20022 based)
- PIX (Brazilian instant payments)
- NPP (Australia New Payments Platform)
- UPI (India Unified Payments Interface)
- PayNow (Singapore)
- PromptPay (Thailand)
- InstaPay (Philippines)

RTGS Systems:
- TARGET2 (pacs.008/pacs.009 based)
- BOJNET (Bank of Japan)
- CNAPS (China National)
- MEPS+ (Singapore MAS)
- RTGS HK (Hong Kong CHATS)
- SARIE (Saudi Arabia)
- UAEFTS (UAE)
- KFTC (Korea)

Each parser extracts data into a standardized CDM structure.
"""

import xml.etree.ElementTree as ET
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MessageParser:
    """Base class for message parsers."""

    def __init__(self):
        self.result = self._init_result()

    def _init_result(self) -> Dict[str, Any]:
        """Initialize empty result structure."""
        return {
            "payment": {},
            "instruction": {},
            "debtor": {},
            "creditor": {},
            "debtor_account": {},
            "creditor_account": {},
            "debtor_agent": {},
            "creditor_agent": {},
            "intermediary_agents": [],
            "remittance": {},
            "regulatory": {},
            "tax": {},
            "ultimate_debtor": {},
            "ultimate_creditor": {},
            "charges": [],
            "status": {},
            "return_info": {},
            "entries": [],  # For statement messages
        }

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse message content. Override in subclasses."""
        raise NotImplementedError


class ISO20022Parser(MessageParser):
    """Parser for ISO 20022 XML messages."""

    def __init__(self):
        super().__init__()

    def _find_text(self, parent, path: str) -> Optional[str]:
        """Find element text using wildcard namespace."""
        if parent is None:
            return None
        tag = path.split('/')[-1]
        elem = parent.find('.//{*}' + tag)
        if elem is None:
            elem = parent.find('.//' + tag)
        return elem.text.strip() if elem is not None and elem.text else None

    def _find_attr(self, parent, path: str, attr: str) -> Optional[str]:
        """Find element attribute."""
        if parent is None:
            return None
        tag = path.split('/')[-1]
        elem = parent.find('.//{*}' + tag)
        if elem is None:
            elem = parent.find('.//' + tag)
        return elem.get(attr) if elem is not None else None

    def _find_elem(self, parent, tag: str):
        """Find element with wildcard namespace."""
        if parent is None:
            return None
        elem = parent.find('.//{*}' + tag)
        if elem is None:
            elem = parent.find('.//' + tag)
        return elem

    def _parse_party(self, elem, prefix: str = "") -> Dict[str, Any]:
        """Parse party information (Dbtr, Cdtr, etc.)."""
        if elem is None:
            return {}

        result = {
            "name": self._find_text(elem, 'Nm'),
            "country": self._find_text(elem, 'Ctry'),
            "address_line_1": self._find_text(elem, 'AdrLine'),
            "street_name": self._find_text(elem, 'StrtNm'),
            "building_number": self._find_text(elem, 'BldgNb'),
            "postal_code": self._find_text(elem, 'PstCd'),
            "town_name": self._find_text(elem, 'TwnNm'),
            "country_subdivision": self._find_text(elem, 'CtrySubDvsn'),
            "country_of_residence": self._find_text(elem, 'CtryOfRes'),
        }

        # Organization ID
        org_id = self._find_elem(elem, 'OrgId')
        if org_id is not None:
            result["bic"] = self._find_text(org_id, 'AnyBIC') or self._find_text(org_id, 'BICOrBEI')
            result["lei"] = self._find_text(org_id, 'LEI')
            result["other_id"] = self._find_text(org_id, 'Id')
            result["other_id_scheme"] = self._find_text(org_id, 'Cd')

        # Private ID (for individuals)
        prvt_id = self._find_elem(elem, 'PrvtId')
        if prvt_id is not None:
            result["date_of_birth"] = self._find_text(prvt_id, 'BirthDt')
            result["city_of_birth"] = self._find_text(prvt_id, 'CityOfBirth')
            result["country_of_birth"] = self._find_text(prvt_id, 'CtryOfBirth')
            result["national_id"] = self._find_text(prvt_id, 'Id')

        return {k: v for k, v in result.items() if v is not None}

    def _parse_account(self, elem) -> Dict[str, Any]:
        """Parse account information."""
        if elem is None:
            return {}

        result = {
            "iban": self._find_text(elem, 'IBAN'),
            "account_number": self._find_text(elem, 'Id'),
            "account_type": self._find_text(elem, 'Cd'),
            "currency": self._find_text(elem, 'Ccy'),
            "name": self._find_text(elem, 'Nm'),
        }

        return {k: v for k, v in result.items() if v is not None}

    def _parse_agent(self, elem) -> Dict[str, Any]:
        """Parse financial institution agent information."""
        if elem is None:
            return {}

        fin_instn = self._find_elem(elem, 'FinInstnId')
        if fin_instn is None:
            return {}

        result = {
            "bic": self._find_text(fin_instn, 'BICFI') or self._find_text(fin_instn, 'BIC'),
            "name": self._find_text(fin_instn, 'Nm'),
            "clearing_system_member_id": self._find_text(fin_instn, 'MmbId'),
            "clearing_system_code": self._find_text(fin_instn, 'Cd'),
            "country": self._find_text(fin_instn, 'Ctry'),
            "lei": self._find_text(fin_instn, 'LEI'),
        }

        brnch = self._find_elem(elem, 'BrnchId')
        if brnch is not None:
            result["branch_id"] = self._find_text(brnch, 'Id')
            result["branch_name"] = self._find_text(brnch, 'Nm')

        return {k: v for k, v in result.items() if v is not None}


class Pain001Parser(ISO20022Parser):
    """Parser for pain.001 - Customer Credit Transfer Initiation."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')
                self.result["payment"]["control_sum"] = self._find_text(grp_hdr, 'CtrlSum')

                init_pty = self._find_elem(grp_hdr, 'InitgPty')
                if init_pty is not None:
                    self.result["payment"]["initiating_party_name"] = self._find_text(init_pty, 'Nm')

            # Payment Information
            pmt_inf = self._find_elem(root, 'PmtInf')
            if pmt_inf is not None:
                self.result["instruction"]["payment_info_id"] = self._find_text(pmt_inf, 'PmtInfId')
                self.result["instruction"]["payment_method"] = self._find_text(pmt_inf, 'PmtMtd')
                self.result["instruction"]["batch_booking"] = self._find_text(pmt_inf, 'BtchBookg')
                self.result["instruction"]["requested_execution_date"] = (
                    self._find_text(pmt_inf, 'Dt') or self._find_text(pmt_inf, 'ReqdExctnDt')
                )
                self.result["instruction"]["charge_bearer"] = self._find_text(pmt_inf, 'ChrgBr')

                # Payment Type
                pmt_tp = self._find_elem(pmt_inf, 'PmtTpInf')
                if pmt_tp is not None:
                    self.result["instruction"]["priority"] = self._find_text(pmt_tp, 'InstrPrty')
                    self.result["instruction"]["service_level"] = self._find_text(pmt_tp, 'Cd')
                    self.result["instruction"]["local_instrument"] = self._find_text(pmt_tp, 'LclInstrm')
                    self.result["instruction"]["category_purpose"] = self._find_text(pmt_tp, 'CtgyPurp')

                # Debtor
                self.result["debtor"] = self._parse_party(self._find_elem(pmt_inf, 'Dbtr'))
                self.result["debtor_account"] = self._parse_account(self._find_elem(pmt_inf, 'DbtrAcct'))
                self.result["debtor_agent"] = self._parse_agent(self._find_elem(pmt_inf, 'DbtrAgt'))
                self.result["ultimate_debtor"] = self._parse_party(self._find_elem(pmt_inf, 'UltmtDbtr'))

            # Credit Transfer Transaction
            cdt_trf = self._find_elem(root, 'CdtTrfTxInf')
            if cdt_trf is not None:
                self._parse_credit_transfer(cdt_trf)

            # Determine cross-border
            self._set_cross_border_flag()

        except Exception as e:
            logger.error(f"Error parsing pain.001: {e}")

        return self.result

    def _parse_credit_transfer(self, cdt_trf):
        """Parse credit transfer transaction information."""
        # Payment IDs
        pmt_id = self._find_elem(cdt_trf, 'PmtId')
        if pmt_id is not None:
            self.result["instruction"]["instruction_id"] = self._find_text(pmt_id, 'InstrId')
            self.result["instruction"]["end_to_end_id"] = self._find_text(pmt_id, 'EndToEndId')
            self.result["instruction"]["uetr"] = self._find_text(pmt_id, 'UETR')

        # Amounts
        instd_amt = self._find_elem(cdt_trf, 'InstdAmt')
        if instd_amt is not None:
            self.result["instruction"]["instructed_amount"] = instd_amt.text
            self.result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

        # Exchange rate
        self.result["instruction"]["exchange_rate"] = self._find_text(cdt_trf, 'XchgRate')

        # Charge bearer override
        chrg_br = self._find_text(cdt_trf, 'ChrgBr')
        if chrg_br:
            self.result["instruction"]["charge_bearer"] = chrg_br

        # Creditor
        self.result["creditor"] = self._parse_party(self._find_elem(cdt_trf, 'Cdtr'))
        self.result["creditor_account"] = self._parse_account(self._find_elem(cdt_trf, 'CdtrAcct'))
        self.result["creditor_agent"] = self._parse_agent(self._find_elem(cdt_trf, 'CdtrAgt'))
        self.result["ultimate_creditor"] = self._parse_party(self._find_elem(cdt_trf, 'UltmtCdtr'))

        # Purpose
        purp = self._find_elem(cdt_trf, 'Purp')
        if purp is not None:
            self.result["instruction"]["purpose_code"] = self._find_text(purp, 'Cd')
            self.result["instruction"]["purpose_proprietary"] = self._find_text(purp, 'Prtry')

        # Remittance
        self._parse_remittance(self._find_elem(cdt_trf, 'RmtInf'))

        # Regulatory
        self._parse_regulatory(self._find_elem(cdt_trf, 'RgltryRptg'))

    def _parse_remittance(self, rmt_inf):
        """Parse remittance information."""
        if rmt_inf is None:
            return

        # Unstructured
        ustrd_list = rmt_inf.findall('.//{*}Ustrd')
        if ustrd_list:
            self.result["remittance"]["unstructured"] = [
                u.text for u in ustrd_list if u.text
            ]

        # Structured
        strd = self._find_elem(rmt_inf, 'Strd')
        if strd is not None:
            self.result["remittance"]["creditor_reference"] = self._find_text(strd, 'Ref')
            self.result["remittance"]["document_type"] = self._find_text(strd, 'Cd')
            self.result["remittance"]["document_number"] = self._find_text(strd, 'Nb')
            self.result["remittance"]["document_date"] = self._find_text(strd, 'RltdDt')

    def _parse_regulatory(self, rgltry):
        """Parse regulatory reporting."""
        if rgltry is None:
            return

        self.result["regulatory"]["indicator"] = self._find_text(rgltry, 'DbtCdtRptgInd')
        self.result["regulatory"]["authority_name"] = self._find_text(rgltry, 'Nm')
        self.result["regulatory"]["authority_country"] = self._find_text(rgltry, 'Ctry')
        self.result["regulatory"]["code"] = self._find_text(rgltry, 'Cd')
        self.result["regulatory"]["information"] = self._find_text(rgltry, 'Inf')

    def _set_cross_border_flag(self):
        """Determine if payment is cross-border."""
        debtor_country = (
            self.result["debtor"].get("country") or
            self.result["debtor_agent"].get("country")
        )
        creditor_country = (
            self.result["creditor"].get("country") or
            self.result["creditor_agent"].get("country")
        )
        if debtor_country and creditor_country:
            self.result["payment"]["cross_border"] = debtor_country != creditor_country


class Pacs008Parser(ISO20022Parser):
    """Parser for pacs.008 - FI to FI Customer Credit Transfer."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')
                self.result["payment"]["control_sum"] = self._find_text(grp_hdr, 'CtrlSum')

                # Settlement info
                sttlm = self._find_elem(grp_hdr, 'SttlmInf')
                if sttlm is not None:
                    self.result["instruction"]["settlement_method"] = self._find_text(sttlm, 'SttlmMtd')
                    self.result["instruction"]["clearing_system"] = self._find_text(sttlm, 'Cd')

                # Interbank settlement
                self.result["instruction"]["interbank_settlement_amount"] = self._find_text(grp_hdr, 'TtlIntrBkSttlmAmt')
                self.result["instruction"]["interbank_settlement_currency"] = self._find_attr(grp_hdr, 'TtlIntrBkSttlmAmt', 'Ccy')
                self.result["instruction"]["interbank_settlement_date"] = self._find_text(grp_hdr, 'IntrBkSttlmDt')

                # Payment Type
                pmt_tp = self._find_elem(grp_hdr, 'PmtTpInf')
                if pmt_tp is not None:
                    self.result["instruction"]["priority"] = self._find_text(pmt_tp, 'InstrPrty')
                    self.result["instruction"]["clearing_channel"] = self._find_text(pmt_tp, 'ClrChanl')
                    self.result["instruction"]["service_level"] = self._find_text(pmt_tp, 'Cd')

                # Instructing/Instructed agents
                self.result["payment"]["instructing_agent_bic"] = self._find_text(
                    self._find_elem(grp_hdr, 'InstgAgt'), 'BICFI'
                )
                self.result["payment"]["instructed_agent_bic"] = self._find_text(
                    self._find_elem(grp_hdr, 'InstdAgt'), 'BICFI'
                )

            # Credit Transfer Transaction (directly under FIToFICstmrCdtTrf)
            cdt_trf = self._find_elem(root, 'CdtTrfTxInf')
            if cdt_trf is not None:
                self._parse_credit_transfer(cdt_trf)

            self._set_cross_border_flag()

        except Exception as e:
            logger.error(f"Error parsing pacs.008: {e}")

        return self.result

    def _parse_credit_transfer(self, cdt_trf):
        """Parse pacs.008 credit transfer transaction."""
        # Payment IDs
        pmt_id = self._find_elem(cdt_trf, 'PmtId')
        if pmt_id is not None:
            self.result["instruction"]["instruction_id"] = self._find_text(pmt_id, 'InstrId')
            self.result["instruction"]["end_to_end_id"] = self._find_text(pmt_id, 'EndToEndId')
            self.result["instruction"]["transaction_id"] = self._find_text(pmt_id, 'TxId')
            self.result["instruction"]["uetr"] = self._find_text(pmt_id, 'UETR')
            self.result["instruction"]["clearing_system_reference"] = self._find_text(pmt_id, 'ClrSysRef')

        # Interbank settlement amount
        intrbnk_amt = self._find_elem(cdt_trf, 'IntrBkSttlmAmt')
        if intrbnk_amt is not None:
            self.result["instruction"]["interbank_settlement_amount"] = intrbnk_amt.text
            self.result["instruction"]["interbank_settlement_currency"] = intrbnk_amt.get('Ccy')

        # Instructed amount
        instd_amt = self._find_elem(cdt_trf, 'InstdAmt')
        if instd_amt is not None:
            self.result["instruction"]["instructed_amount"] = instd_amt.text
            self.result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

        # Exchange rate
        self.result["instruction"]["exchange_rate"] = self._find_text(cdt_trf, 'XchgRate')
        self.result["instruction"]["charge_bearer"] = self._find_text(cdt_trf, 'ChrgBr')

        # Settlement date at transaction level
        self.result["instruction"]["interbank_settlement_date"] = (
            self._find_text(cdt_trf, 'IntrBkSttlmDt') or
            self.result["instruction"].get("interbank_settlement_date")
        )

        # Charges
        for chrg in cdt_trf.findall('.//{*}ChrgsInf'):
            amt = self._find_elem(chrg, 'Amt')
            if amt is not None:
                self.result["charges"].append({
                    "amount": amt.text,
                    "currency": amt.get('Ccy'),
                    "agent_bic": self._find_text(chrg, 'BICFI'),
                })

        # Debtor
        self.result["debtor"] = self._parse_party(self._find_elem(cdt_trf, 'Dbtr'))
        self.result["debtor_account"] = self._parse_account(self._find_elem(cdt_trf, 'DbtrAcct'))
        self.result["debtor_agent"] = self._parse_agent(self._find_elem(cdt_trf, 'DbtrAgt'))

        # Creditor
        self.result["creditor"] = self._parse_party(self._find_elem(cdt_trf, 'Cdtr'))
        self.result["creditor_account"] = self._parse_account(self._find_elem(cdt_trf, 'CdtrAcct'))
        self.result["creditor_agent"] = self._parse_agent(self._find_elem(cdt_trf, 'CdtrAgt'))

        # Intermediary agents
        for i in range(1, 4):
            intm_agt = self._find_elem(cdt_trf, f'IntrmyAgt{i}')
            if intm_agt is not None:
                agent = self._parse_agent(intm_agt)
                agent["sequence"] = i
                self.result["intermediary_agents"].append(agent)

        # Purpose
        purp = self._find_elem(cdt_trf, 'Purp')
        if purp is not None:
            self.result["instruction"]["purpose_code"] = self._find_text(purp, 'Cd')

        # Remittance
        rmt_inf = self._find_elem(cdt_trf, 'RmtInf')
        if rmt_inf is not None:
            ustrd_list = rmt_inf.findall('.//{*}Ustrd')
            if ustrd_list:
                self.result["remittance"]["unstructured"] = [
                    u.text for u in ustrd_list if u.text
                ]
            strd = self._find_elem(rmt_inf, 'Strd')
            if strd is not None:
                self.result["remittance"]["creditor_reference"] = self._find_text(strd, 'Ref')

    def _set_cross_border_flag(self):
        """Determine if payment is cross-border."""
        debtor_country = (
            self.result["debtor"].get("country") or
            self.result["debtor_agent"].get("country")
        )
        creditor_country = (
            self.result["creditor"].get("country") or
            self.result["creditor_agent"].get("country")
        )
        if debtor_country and creditor_country:
            self.result["payment"]["cross_border"] = debtor_country != creditor_country


class Pain008Parser(ISO20022Parser):
    """Parser for pain.008 - Customer Direct Debit Initiation."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "DIRECT_DEBIT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')
                self.result["payment"]["control_sum"] = self._find_text(grp_hdr, 'CtrlSum')

            # Payment Information
            pmt_inf = self._find_elem(root, 'PmtInf')
            if pmt_inf is not None:
                self.result["instruction"]["payment_info_id"] = self._find_text(pmt_inf, 'PmtInfId')
                self.result["instruction"]["payment_method"] = self._find_text(pmt_inf, 'PmtMtd')
                self.result["instruction"]["batch_booking"] = self._find_text(pmt_inf, 'BtchBookg')
                self.result["instruction"]["requested_collection_date"] = self._find_text(pmt_inf, 'ReqdColltnDt')
                self.result["instruction"]["charge_bearer"] = self._find_text(pmt_inf, 'ChrgBr')

                # Payment Type
                pmt_tp = self._find_elem(pmt_inf, 'PmtTpInf')
                if pmt_tp is not None:
                    self.result["instruction"]["priority"] = self._find_text(pmt_tp, 'InstrPrty')
                    self.result["instruction"]["service_level"] = self._find_text(pmt_tp, 'Cd')
                    self.result["instruction"]["local_instrument"] = self._find_text(pmt_tp, 'LclInstrm')
                    self.result["instruction"]["sequence_type"] = self._find_text(pmt_tp, 'SeqTp')
                    self.result["instruction"]["category_purpose"] = self._find_text(pmt_tp, 'CtgyPurp')

                # Creditor (the one collecting the payment)
                self.result["creditor"] = self._parse_party(self._find_elem(pmt_inf, 'Cdtr'))
                self.result["creditor_account"] = self._parse_account(self._find_elem(pmt_inf, 'CdtrAcct'))
                self.result["creditor_agent"] = self._parse_agent(self._find_elem(pmt_inf, 'CdtrAgt'))

                # Creditor Scheme ID (for SEPA)
                cdtr_schme = self._find_elem(pmt_inf, 'CdtrSchmeId')
                if cdtr_schme is not None:
                    self.result["creditor"]["scheme_id"] = self._find_text(cdtr_schme, 'Id')

            # Direct Debit Transaction
            drct_dbt = self._find_elem(root, 'DrctDbtTxInf')
            if drct_dbt is not None:
                self._parse_direct_debit(drct_dbt)

            self._set_cross_border_flag()

        except Exception as e:
            logger.error(f"Error parsing pain.008: {e}")

        return self.result

    def _parse_direct_debit(self, drct_dbt):
        """Parse direct debit transaction information."""
        # Payment IDs
        pmt_id = self._find_elem(drct_dbt, 'PmtId')
        if pmt_id is not None:
            self.result["instruction"]["instruction_id"] = self._find_text(pmt_id, 'InstrId')
            self.result["instruction"]["end_to_end_id"] = self._find_text(pmt_id, 'EndToEndId')

        # Instructed Amount
        instd_amt = self._find_elem(drct_dbt, 'InstdAmt')
        if instd_amt is not None:
            self.result["instruction"]["instructed_amount"] = instd_amt.text
            self.result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

        # Mandate Related Information
        mndt = self._find_elem(drct_dbt, 'MndtRltdInf')
        if mndt is not None:
            self.result["instruction"]["mandate_id"] = self._find_text(mndt, 'MndtId')
            self.result["instruction"]["mandate_date_of_signature"] = self._find_text(mndt, 'DtOfSgntr')
            self.result["instruction"]["amendment_indicator"] = self._find_text(mndt, 'AmdmntInd')

        # Debtor (the one being debited)
        self.result["debtor"] = self._parse_party(self._find_elem(drct_dbt, 'Dbtr'))
        self.result["debtor_account"] = self._parse_account(self._find_elem(drct_dbt, 'DbtrAcct'))
        self.result["debtor_agent"] = self._parse_agent(self._find_elem(drct_dbt, 'DbtrAgt'))

        # Ultimate Parties
        self.result["ultimate_debtor"] = self._parse_party(self._find_elem(drct_dbt, 'UltmtDbtr'))
        self.result["ultimate_creditor"] = self._parse_party(self._find_elem(drct_dbt, 'UltmtCdtr'))

        # Purpose
        purp = self._find_elem(drct_dbt, 'Purp')
        if purp is not None:
            self.result["instruction"]["purpose_code"] = self._find_text(purp, 'Cd')

        # Remittance
        rmt_inf = self._find_elem(drct_dbt, 'RmtInf')
        if rmt_inf is not None:
            ustrd_list = rmt_inf.findall('.//{*}Ustrd')
            if ustrd_list:
                self.result["remittance"]["unstructured"] = [
                    u.text for u in ustrd_list if u.text
                ]

    def _set_cross_border_flag(self):
        """Determine if payment is cross-border."""
        debtor_country = (
            self.result["debtor"].get("country") or
            self.result["debtor_agent"].get("country")
        )
        creditor_country = (
            self.result["creditor"].get("country") or
            self.result["creditor_agent"].get("country")
        )
        if debtor_country and creditor_country:
            self.result["payment"]["cross_border"] = debtor_country != creditor_country


class Pacs004Parser(ISO20022Parser):
    """Parser for pacs.004 - Payment Return."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "RETURN"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')

                # Settlement
                sttlm = self._find_elem(grp_hdr, 'SttlmInf')
                if sttlm is not None:
                    self.result["instruction"]["settlement_method"] = self._find_text(sttlm, 'SttlmMtd')

            # Transaction Information
            tx_inf = self._find_elem(root, 'TxInf')
            if tx_inf is not None:
                self._parse_return_transaction(tx_inf)

        except Exception as e:
            logger.error(f"Error parsing pacs.004: {e}")

        return self.result

    def _parse_return_transaction(self, tx_inf):
        """Parse return transaction information."""
        # Return IDs
        rtr_id = self._find_elem(tx_inf, 'RtrId')
        if rtr_id is not None:
            self.result["instruction"]["return_id"] = rtr_id.text

        # Original references
        orgnl = self._find_elem(tx_inf, 'OrgnlGrpInf')
        if orgnl is not None:
            self.result["return_info"]["original_message_id"] = self._find_text(orgnl, 'OrgnlMsgId')
            self.result["return_info"]["original_message_name"] = self._find_text(orgnl, 'OrgnlMsgNmId')

        self.result["return_info"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
        self.result["return_info"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
        self.result["return_info"]["original_transaction_id"] = self._find_text(tx_inf, 'OrgnlTxId')
        self.result["return_info"]["original_uetr"] = self._find_text(tx_inf, 'OrgnlUETR')

        # Return Amount
        rtrd_amt = self._find_elem(tx_inf, 'RtrdIntrBkSttlmAmt')
        if rtrd_amt is not None:
            self.result["instruction"]["instructed_amount"] = rtrd_amt.text
            self.result["instruction"]["instructed_currency"] = rtrd_amt.get('Ccy')

        # Return Reason
        rsn = self._find_elem(tx_inf, 'RtrRsnInf')
        if rsn is not None:
            self.result["return_info"]["reason_code"] = self._find_text(rsn, 'Cd')
            self.result["return_info"]["reason_proprietary"] = self._find_text(rsn, 'Prtry')
            self.result["return_info"]["additional_info"] = self._find_text(rsn, 'AddtlInf')

        # Parties (reversed)
        self.result["debtor"] = self._parse_party(self._find_elem(tx_inf, 'RtrChain'))
        self.result["creditor"] = self._parse_party(self._find_elem(tx_inf, 'Cdtr'))
        self.result["debtor_agent"] = self._parse_agent(self._find_elem(tx_inf, 'DbtrAgt'))
        self.result["creditor_agent"] = self._parse_agent(self._find_elem(tx_inf, 'CdtrAgt'))


class Camt053Parser(ISO20022Parser):
    """Parser for camt.053 - Bank to Customer Statement."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "STATEMENT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Statement
            stmt = self._find_elem(root, 'Stmt')
            if stmt is not None:
                self._parse_statement(stmt)

        except Exception as e:
            logger.error(f"Error parsing camt.053: {e}")

        return self.result

    def _parse_statement(self, stmt):
        """Parse statement information."""
        self.result["instruction"]["statement_id"] = self._find_text(stmt, 'Id')
        self.result["instruction"]["sequence_number"] = self._find_text(stmt, 'ElctrncSeqNb')
        self.result["instruction"]["legal_sequence_number"] = self._find_text(stmt, 'LglSeqNb')
        self.result["instruction"]["creation_datetime"] = self._find_text(stmt, 'CreDtTm')
        self.result["instruction"]["from_date"] = self._find_text(stmt, 'FrDt')
        self.result["instruction"]["to_date"] = self._find_text(stmt, 'ToDt')

        # Account
        acct = self._find_elem(stmt, 'Acct')
        if acct is not None:
            self.result["debtor_account"] = self._parse_account(acct)
            # Account owner
            ownr = self._find_elem(acct, 'Ownr')
            if ownr is not None:
                self.result["debtor"] = self._parse_party(ownr)
            # Servicer
            svcr = self._find_elem(acct, 'Svcr')
            if svcr is not None:
                self.result["debtor_agent"] = self._parse_agent(svcr)

        # Balances
        balances = []
        for bal in stmt.findall('.//{*}Bal'):
            balance = {
                "type": self._find_text(bal, 'Cd'),
                "amount": self._find_text(bal, 'Amt'),
                "currency": self._find_attr(bal, 'Amt', 'Ccy'),
                "credit_debit": self._find_text(bal, 'CdtDbtInd'),
                "date": self._find_text(bal, 'Dt'),
            }
            balances.append({k: v for k, v in balance.items() if v})
        self.result["payment"]["balances"] = balances

        # Entries
        for ntry in stmt.findall('.//{*}Ntry'):
            entry = self._parse_entry(ntry)
            self.result["entries"].append(entry)

    def _parse_entry(self, ntry) -> Dict[str, Any]:
        """Parse statement entry."""
        entry = {
            "amount": self._find_text(ntry, 'Amt'),
            "currency": self._find_attr(ntry, 'Amt', 'Ccy'),
            "credit_debit": self._find_text(ntry, 'CdtDbtInd'),
            "status": self._find_text(ntry, 'Sts'),
            "booking_date": self._find_text(ntry, 'BookgDt'),
            "value_date": self._find_text(ntry, 'ValDt'),
            "reference": self._find_text(ntry, 'AcctSvcrRef'),
        }

        # Entry details
        dtls = self._find_elem(ntry, 'NtryDtls')
        if dtls is not None:
            tx_dtls = self._find_elem(dtls, 'TxDtls')
            if tx_dtls is not None:
                refs = self._find_elem(tx_dtls, 'Refs')
                if refs is not None:
                    entry["end_to_end_id"] = self._find_text(refs, 'EndToEndId')
                    entry["instruction_id"] = self._find_text(refs, 'InstrId')
                    entry["transaction_id"] = self._find_text(refs, 'TxId')

                # Related parties
                rltd_pties = self._find_elem(tx_dtls, 'RltdPties')
                if rltd_pties is not None:
                    dbtr = self._find_elem(rltd_pties, 'Dbtr')
                    if dbtr is not None:
                        entry["debtor_name"] = self._find_text(dbtr, 'Nm')
                    cdtr = self._find_elem(rltd_pties, 'Cdtr')
                    if cdtr is not None:
                        entry["creditor_name"] = self._find_text(cdtr, 'Nm')

                # Remittance
                rmt = self._find_elem(tx_dtls, 'RmtInf')
                if rmt is not None:
                    entry["remittance"] = self._find_text(rmt, 'Ustrd')

        return {k: v for k, v in entry.items() if v}


# =============================================================================
# Additional ISO 20022 PAIN Parsers
# =============================================================================

class Pain002Parser(ISO20022Parser):
    """Parser for pain.002 - Payment Status Report."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "STATUS_REPORT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Original Group Information
            orgnl = self._find_elem(root, 'OrgnlGrpInfAndSts')
            if orgnl is not None:
                self.result["status"]["original_message_id"] = self._find_text(orgnl, 'OrgnlMsgId')
                self.result["status"]["original_message_type"] = self._find_text(orgnl, 'OrgnlMsgNmId')
                self.result["status"]["group_status"] = self._find_text(orgnl, 'GrpSts')

            # Original Payment Information
            orgnl_pmt = self._find_elem(root, 'OrgnlPmtInfAndSts')
            if orgnl_pmt is not None:
                self.result["status"]["original_payment_info_id"] = self._find_text(orgnl_pmt, 'OrgnlPmtInfId')
                self.result["status"]["payment_info_status"] = self._find_text(orgnl_pmt, 'PmtInfSts')

                # Status reason
                sts_rsn = self._find_elem(orgnl_pmt, 'StsRsnInf')
                if sts_rsn is not None:
                    self.result["status"]["reason_code"] = self._find_text(sts_rsn, 'Cd')
                    self.result["status"]["reason_proprietary"] = self._find_text(sts_rsn, 'Prtry')
                    self.result["status"]["additional_info"] = self._find_text(sts_rsn, 'AddtlInf')

            # Transaction Information
            tx_inf = self._find_elem(root, 'TxInfAndSts')
            if tx_inf is not None:
                self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                self.result["status"]["transaction_status"] = self._find_text(tx_inf, 'TxSts')

        except Exception as e:
            logger.error(f"Error parsing pain.002: {e}")

        return self.result


class Pain007Parser(ISO20022Parser):
    """Parser for pain.007 - Customer Payment Reversal."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "REVERSAL"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')
                self.result["payment"]["control_sum"] = self._find_text(grp_hdr, 'CtrlSum')

            # Original Group Information
            orgnl = self._find_elem(root, 'OrgnlGrpInf')
            if orgnl is not None:
                self.result["return_info"]["original_message_id"] = self._find_text(orgnl, 'OrgnlMsgId')
                self.result["return_info"]["original_message_type"] = self._find_text(orgnl, 'OrgnlMsgNmId')

            # Original Payment Information
            orgnl_pmt = self._find_elem(root, 'OrgnlPmtInfAndRvsl')
            if orgnl_pmt is not None:
                self.result["return_info"]["original_payment_info_id"] = self._find_text(orgnl_pmt, 'OrgnlPmtInfId')

                # Reversal reason
                rvsl_rsn = self._find_elem(orgnl_pmt, 'RvslRsnInf')
                if rvsl_rsn is not None:
                    self.result["return_info"]["reason_code"] = self._find_text(rvsl_rsn, 'Cd')
                    self.result["return_info"]["additional_info"] = self._find_text(rvsl_rsn, 'AddtlInf')

            # Transaction Information
            tx_inf = self._find_elem(root, 'TxInf')
            if tx_inf is not None:
                self.result["instruction"]["reversal_id"] = self._find_text(tx_inf, 'RvslId')
                self.result["instruction"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                self.result["instruction"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')

                rvsd_amt = self._find_elem(tx_inf, 'RvsdInstdAmt')
                if rvsd_amt is not None:
                    self.result["instruction"]["instructed_amount"] = rvsd_amt.text
                    self.result["instruction"]["instructed_currency"] = rvsd_amt.get('Ccy')

        except Exception as e:
            logger.error(f"Error parsing pain.007: {e}")

        return self.result


class Pain013Parser(ISO20022Parser):
    """Parser for pain.013 - Creditor Payment Activation Request."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "CREDITOR_PAYMENT_ACTIVATION"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')
                self.result["payment"]["control_sum"] = self._find_text(grp_hdr, 'CtrlSum')

                init_pty = self._find_elem(grp_hdr, 'InitgPty')
                if init_pty is not None:
                    self.result["creditor"] = self._parse_party(init_pty)

            # Payment Activation Request
            pmt_act = self._find_elem(root, 'PmtActvtnReq')
            if pmt_act is not None:
                self.result["instruction"]["payment_activation_request_id"] = self._find_text(pmt_act, 'PmtActvtnReqId')
                self.result["instruction"]["requested_execution_date"] = self._find_text(pmt_act, 'ReqdExctnDt')

                # Creditor
                self.result["creditor"] = self._parse_party(self._find_elem(pmt_act, 'Cdtr'))
                self.result["creditor_account"] = self._parse_account(self._find_elem(pmt_act, 'CdtrAcct'))
                self.result["creditor_agent"] = self._parse_agent(self._find_elem(pmt_act, 'CdtrAgt'))

            # Credit Transfer Transaction
            cdt_trf = self._find_elem(root, 'CdtTrfTxInf')
            if cdt_trf is not None:
                pmt_id = self._find_elem(cdt_trf, 'PmtId')
                if pmt_id is not None:
                    self.result["instruction"]["instruction_id"] = self._find_text(pmt_id, 'InstrId')
                    self.result["instruction"]["end_to_end_id"] = self._find_text(pmt_id, 'EndToEndId')

                amt = self._find_elem(cdt_trf, 'Amt')
                if amt is not None:
                    instd_amt = self._find_elem(amt, 'InstdAmt')
                    if instd_amt is not None:
                        self.result["instruction"]["instructed_amount"] = instd_amt.text
                        self.result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

                self.result["debtor"] = self._parse_party(self._find_elem(cdt_trf, 'Dbtr'))
                self.result["debtor_account"] = self._parse_account(self._find_elem(cdt_trf, 'DbtrAcct'))
                self.result["debtor_agent"] = self._parse_agent(self._find_elem(cdt_trf, 'DbtrAgt'))

        except Exception as e:
            logger.error(f"Error parsing pain.013: {e}")

        return self.result


class Pain014Parser(ISO20022Parser):
    """Parser for pain.014 - Creditor Payment Activation Request Status Report."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACTIVATION_STATUS_REPORT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Original Group Information
            orgnl = self._find_elem(root, 'OrgnlGrpInfAndSts')
            if orgnl is not None:
                self.result["status"]["original_message_id"] = self._find_text(orgnl, 'OrgnlMsgId')
                self.result["status"]["original_message_type"] = self._find_text(orgnl, 'OrgnlMsgNmId')
                self.result["status"]["group_status"] = self._find_text(orgnl, 'GrpSts')

            # Original Payment Information
            orgnl_pmt = self._find_elem(root, 'OrgnlPmtInfAndSts')
            if orgnl_pmt is not None:
                self.result["status"]["original_payment_info_id"] = self._find_text(orgnl_pmt, 'OrgnlPmtActvtnReqId')
                self.result["status"]["payment_info_status"] = self._find_text(orgnl_pmt, 'PmtActvtnReqSts')

        except Exception as e:
            logger.error(f"Error parsing pain.014: {e}")

        return self.result


# =============================================================================
# Additional ISO 20022 PACS Parsers
# =============================================================================

class Pacs002Parser(ISO20022Parser):
    """Parser for pacs.002 - FI to FI Payment Status Report."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FI_STATUS_REPORT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["instructing_agent_bic"] = self._find_text(
                    self._find_elem(grp_hdr, 'InstgAgt'), 'BICFI'
                )
                self.result["payment"]["instructed_agent_bic"] = self._find_text(
                    self._find_elem(grp_hdr, 'InstdAgt'), 'BICFI'
                )

            # Original Group Information
            orgnl = self._find_elem(root, 'OrgnlGrpInfAndSts')
            if orgnl is not None:
                self.result["status"]["original_message_id"] = self._find_text(orgnl, 'OrgnlMsgId')
                self.result["status"]["original_message_type"] = self._find_text(orgnl, 'OrgnlMsgNmId')
                self.result["status"]["group_status"] = self._find_text(orgnl, 'GrpSts')

            # Transaction Information
            tx_inf = self._find_elem(root, 'TxInfAndSts')
            if tx_inf is not None:
                self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                self.result["status"]["original_transaction_id"] = self._find_text(tx_inf, 'OrgnlTxId')
                self.result["status"]["original_uetr"] = self._find_text(tx_inf, 'OrgnlUETR')
                self.result["status"]["transaction_status"] = self._find_text(tx_inf, 'TxSts')
                self.result["status"]["status_reason_code"] = self._find_text(tx_inf, 'Cd')
                self.result["status"]["acceptance_datetime"] = self._find_text(tx_inf, 'AccptncDtTm')

                # Charges
                for chrg in tx_inf.findall('.//{*}ChrgsInf'):
                    amt = self._find_elem(chrg, 'Amt')
                    if amt is not None:
                        self.result["charges"].append({
                            "amount": amt.text,
                            "currency": amt.get('Ccy'),
                            "agent_bic": self._find_text(chrg, 'BICFI'),
                        })

        except Exception as e:
            logger.error(f"Error parsing pacs.002: {e}")

        return self.result


class Pacs003Parser(ISO20022Parser):
    """Parser for pacs.003 - FI to FI Customer Direct Debit."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FI_DIRECT_DEBIT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')
                self.result["payment"]["control_sum"] = self._find_text(grp_hdr, 'CtrlSum')

                # Settlement
                sttlm = self._find_elem(grp_hdr, 'SttlmInf')
                if sttlm is not None:
                    self.result["instruction"]["settlement_method"] = self._find_text(sttlm, 'SttlmMtd')

            # Direct Debit Transaction
            dd_tx = self._find_elem(root, 'DrctDbtTxInf')
            if dd_tx is not None:
                # Payment IDs
                pmt_id = self._find_elem(dd_tx, 'PmtId')
                if pmt_id is not None:
                    self.result["instruction"]["instruction_id"] = self._find_text(pmt_id, 'InstrId')
                    self.result["instruction"]["end_to_end_id"] = self._find_text(pmt_id, 'EndToEndId')
                    self.result["instruction"]["transaction_id"] = self._find_text(pmt_id, 'TxId')

                # Interbank settlement
                intrbnk_amt = self._find_elem(dd_tx, 'IntrBkSttlmAmt')
                if intrbnk_amt is not None:
                    self.result["instruction"]["interbank_settlement_amount"] = intrbnk_amt.text
                    self.result["instruction"]["interbank_settlement_currency"] = intrbnk_amt.get('Ccy')

                self.result["instruction"]["interbank_settlement_date"] = self._find_text(dd_tx, 'IntrBkSttlmDt')

                # Instructed amount
                instd_amt = self._find_elem(dd_tx, 'InstdAmt')
                if instd_amt is not None:
                    self.result["instruction"]["instructed_amount"] = instd_amt.text
                    self.result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

                # Mandate
                mndt = self._find_elem(dd_tx, 'DrctDbtTx')
                if mndt is not None:
                    self.result["instruction"]["mandate_id"] = self._find_text(mndt, 'MndtId')
                    self.result["instruction"]["sequence_type"] = self._find_text(mndt, 'SeqTp')

                # Parties
                self.result["creditor"] = self._parse_party(self._find_elem(dd_tx, 'Cdtr'))
                self.result["creditor_account"] = self._parse_account(self._find_elem(dd_tx, 'CdtrAcct'))
                self.result["creditor_agent"] = self._parse_agent(self._find_elem(dd_tx, 'CdtrAgt'))
                self.result["debtor"] = self._parse_party(self._find_elem(dd_tx, 'Dbtr'))
                self.result["debtor_account"] = self._parse_account(self._find_elem(dd_tx, 'DbtrAcct'))
                self.result["debtor_agent"] = self._parse_agent(self._find_elem(dd_tx, 'DbtrAgt'))

        except Exception as e:
            logger.error(f"Error parsing pacs.003: {e}")

        return self.result


class Pacs007Parser(ISO20022Parser):
    """Parser for pacs.007 - FI to FI Payment Reversal."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FI_REVERSAL"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')

            # Original Group Information
            orgnl = self._find_elem(root, 'OrgnlGrpInf')
            if orgnl is not None:
                self.result["return_info"]["original_message_id"] = self._find_text(orgnl, 'OrgnlMsgId')
                self.result["return_info"]["original_message_type"] = self._find_text(orgnl, 'OrgnlMsgNmId')

            # Transaction Information
            tx_inf = self._find_elem(root, 'TxInf')
            if tx_inf is not None:
                self.result["instruction"]["reversal_id"] = self._find_text(tx_inf, 'RvslId')
                self.result["return_info"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                self.result["return_info"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                self.result["return_info"]["original_transaction_id"] = self._find_text(tx_inf, 'OrgnlTxId')
                self.result["return_info"]["original_uetr"] = self._find_text(tx_inf, 'OrgnlUETR')

                # Reversal amount
                rvsd_amt = self._find_elem(tx_inf, 'RvsdIntrBkSttlmAmt')
                if rvsd_amt is not None:
                    self.result["instruction"]["instructed_amount"] = rvsd_amt.text
                    self.result["instruction"]["instructed_currency"] = rvsd_amt.get('Ccy')

                # Reversal reason
                rvsl_rsn = self._find_elem(tx_inf, 'RvslRsnInf')
                if rvsl_rsn is not None:
                    self.result["return_info"]["reason_code"] = self._find_text(rvsl_rsn, 'Cd')
                    self.result["return_info"]["additional_info"] = self._find_text(rvsl_rsn, 'AddtlInf')

        except Exception as e:
            logger.error(f"Error parsing pacs.007: {e}")

        return self.result


class Pacs009Parser(ISO20022Parser):
    """Parser for pacs.009 - FI to FI Credit Transfer (Cover)."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FI_CREDIT_TRANSFER"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')
                self.result["payment"]["control_sum"] = self._find_text(grp_hdr, 'CtrlSum')

                # Settlement
                sttlm = self._find_elem(grp_hdr, 'SttlmInf')
                if sttlm is not None:
                    self.result["instruction"]["settlement_method"] = self._find_text(sttlm, 'SttlmMtd')
                    self.result["instruction"]["clearing_system"] = self._find_text(sttlm, 'Cd')

                # Instructing/Instructed agents
                self.result["payment"]["instructing_agent_bic"] = self._find_text(
                    self._find_elem(grp_hdr, 'InstgAgt'), 'BICFI'
                )
                self.result["payment"]["instructed_agent_bic"] = self._find_text(
                    self._find_elem(grp_hdr, 'InstdAgt'), 'BICFI'
                )

            # Credit Transfer Transaction
            cdt_trf = self._find_elem(root, 'CdtTrfTxInf')
            if cdt_trf is not None:
                # Payment IDs
                pmt_id = self._find_elem(cdt_trf, 'PmtId')
                if pmt_id is not None:
                    self.result["instruction"]["instruction_id"] = self._find_text(pmt_id, 'InstrId')
                    self.result["instruction"]["end_to_end_id"] = self._find_text(pmt_id, 'EndToEndId')
                    self.result["instruction"]["transaction_id"] = self._find_text(pmt_id, 'TxId')
                    self.result["instruction"]["uetr"] = self._find_text(pmt_id, 'UETR')

                # Interbank settlement
                intrbnk_amt = self._find_elem(cdt_trf, 'IntrBkSttlmAmt')
                if intrbnk_amt is not None:
                    self.result["instruction"]["interbank_settlement_amount"] = intrbnk_amt.text
                    self.result["instruction"]["interbank_settlement_currency"] = intrbnk_amt.get('Ccy')

                self.result["instruction"]["interbank_settlement_date"] = self._find_text(cdt_trf, 'IntrBkSttlmDt')

                # Debtor Agent
                self.result["debtor_agent"] = self._parse_agent(self._find_elem(cdt_trf, 'DbtrAgt'))

                # Creditor Agent
                self.result["creditor_agent"] = self._parse_agent(self._find_elem(cdt_trf, 'CdtrAgt'))

                # Intermediary agents
                for i in range(1, 4):
                    intm_agt = self._find_elem(cdt_trf, f'IntrmyAgt{i}')
                    if intm_agt is not None:
                        agent = self._parse_agent(intm_agt)
                        agent["sequence"] = i
                        self.result["intermediary_agents"].append(agent)

        except Exception as e:
            logger.error(f"Error parsing pacs.009: {e}")

        return self.result


class Pacs028Parser(ISO20022Parser):
    """Parser for pacs.028 - FI to FI Positive Pay Response."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "POSITIVE_PAY_RESPONSE"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Transaction Information
            tx_inf = self._find_elem(root, 'TxInf')
            if tx_inf is not None:
                self.result["status"]["status_id"] = self._find_text(tx_inf, 'StsId')
                self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                self.result["status"]["transaction_status"] = self._find_text(tx_inf, 'TxSts')

                # Amount verified
                vrfd_amt = self._find_elem(tx_inf, 'VrfdAmt')
                if vrfd_amt is not None:
                    self.result["instruction"]["instructed_amount"] = vrfd_amt.text
                    self.result["instruction"]["instructed_currency"] = vrfd_amt.get('Ccy')

        except Exception as e:
            logger.error(f"Error parsing pacs.028: {e}")

        return self.result


# =============================================================================
# Additional ISO 20022 CAMT Parsers
# =============================================================================

class Camt026Parser(ISO20022Parser):
    """Parser for camt.026 - Unable to Apply."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "UNABLE_TO_APPLY"

        try:
            root = ET.fromstring(content)

            # Assignment
            assgnmt = self._find_elem(root, 'Assgnmt')
            if assgnmt is not None:
                self.result["payment"]["message_id"] = self._find_text(assgnmt, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(assgnmt, 'CreDtTm')

            # Underlying
            undrlyg = self._find_elem(root, 'Undrlyg')
            if undrlyg is not None:
                tx_inf = self._find_elem(undrlyg, 'TxInf')
                if tx_inf is not None:
                    self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                    self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                    self.result["status"]["original_transaction_id"] = self._find_text(tx_inf, 'OrgnlTxId')
                    self.result["status"]["original_uetr"] = self._find_text(tx_inf, 'OrgnlUETR')

            # Justification
            jstfn = self._find_elem(root, 'Justfn')
            if jstfn is not None:
                self.result["status"]["reason_code"] = self._find_text(jstfn, 'Cd')
                self.result["status"]["additional_info"] = self._find_text(jstfn, 'AddtlInf')

        except Exception as e:
            logger.error(f"Error parsing camt.026: {e}")

        return self.result


class Camt027Parser(ISO20022Parser):
    """Parser for camt.027 - Claim Non-Receipt."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "CLAIM_NON_RECEIPT"

        try:
            root = ET.fromstring(content)

            # Assignment
            assgnmt = self._find_elem(root, 'Assgnmt')
            if assgnmt is not None:
                self.result["payment"]["message_id"] = self._find_text(assgnmt, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(assgnmt, 'CreDtTm')

            # Underlying
            undrlyg = self._find_elem(root, 'Undrlyg')
            if undrlyg is not None:
                tx_inf = self._find_elem(undrlyg, 'TxInf')
                if tx_inf is not None:
                    self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                    self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                    self.result["status"]["original_uetr"] = self._find_text(tx_inf, 'OrgnlUETR')

                    instd_amt = self._find_elem(tx_inf, 'InstdAmt')
                    if instd_amt is not None:
                        self.result["instruction"]["instructed_amount"] = instd_amt.text
                        self.result["instruction"]["instructed_currency"] = instd_amt.get('Ccy')

        except Exception as e:
            logger.error(f"Error parsing camt.027: {e}")

        return self.result


class Camt028Parser(ISO20022Parser):
    """Parser for camt.028 - Additional Payment Information."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ADDITIONAL_PAYMENT_INFO"

        try:
            root = ET.fromstring(content)

            # Assignment
            assgnmt = self._find_elem(root, 'Assgnmt')
            if assgnmt is not None:
                self.result["payment"]["message_id"] = self._find_text(assgnmt, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(assgnmt, 'CreDtTm')

            # Case
            case = self._find_elem(root, 'Case')
            if case is not None:
                self.result["status"]["case_id"] = self._find_text(case, 'Id')

            # Underlying
            undrlyg = self._find_elem(root, 'Undrlyg')
            if undrlyg is not None:
                tx_inf = self._find_elem(undrlyg, 'TxInf')
                if tx_inf is not None:
                    self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                    self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                    self.result["status"]["original_uetr"] = self._find_text(tx_inf, 'OrgnlUETR')

            # Information
            inf = self._find_elem(root, 'Inf')
            if inf is not None:
                self.result["status"]["additional_info"] = self._find_text(inf, 'Inf')

        except Exception as e:
            logger.error(f"Error parsing camt.028: {e}")

        return self.result


class Camt029Parser(ISO20022Parser):
    """Parser for camt.029 - Resolution of Investigation."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "RESOLUTION_OF_INVESTIGATION"

        try:
            root = ET.fromstring(content)

            # Assignment
            assgnmt = self._find_elem(root, 'Assgnmt')
            if assgnmt is not None:
                self.result["payment"]["message_id"] = self._find_text(assgnmt, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(assgnmt, 'CreDtTm')

            # Resolved Case
            rslvd = self._find_elem(root, 'RslvdCase')
            if rslvd is not None:
                self.result["status"]["resolved_case_id"] = self._find_text(rslvd, 'Id')

            # Status
            sts = self._find_elem(root, 'Sts')
            if sts is not None:
                self.result["status"]["confirmation"] = self._find_text(sts, 'Conf')

                # Cancellation Details
                cxl_dtls = self._find_elem(sts, 'CxlDtls')
                if cxl_dtls is not None:
                    self.result["status"]["original_instruction_id"] = self._find_text(cxl_dtls, 'OrgnlInstrId')
                    self.result["status"]["original_end_to_end_id"] = self._find_text(cxl_dtls, 'OrgnlEndToEndId')
                    self.result["status"]["original_uetr"] = self._find_text(cxl_dtls, 'OrgnlUETR')

        except Exception as e:
            logger.error(f"Error parsing camt.029: {e}")

        return self.result


class Camt052Parser(ISO20022Parser):
    """Parser for camt.052 - Bank to Customer Account Report (Intraday)."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_REPORT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Report
            rpt = self._find_elem(root, 'Rpt')
            if rpt is not None:
                self.result["instruction"]["report_id"] = self._find_text(rpt, 'Id')
                self.result["instruction"]["sequence_number"] = self._find_text(rpt, 'ElctrncSeqNb')
                self.result["instruction"]["creation_datetime"] = self._find_text(rpt, 'CreDtTm')
                self.result["instruction"]["from_datetime"] = self._find_text(rpt, 'FrToDt')

                # Account
                acct = self._find_elem(rpt, 'Acct')
                if acct is not None:
                    self.result["debtor_account"] = self._parse_account(acct)
                    ownr = self._find_elem(acct, 'Ownr')
                    if ownr is not None:
                        self.result["debtor"] = self._parse_party(ownr)

                # Balances
                balances = []
                for bal in rpt.findall('.//{*}Bal'):
                    balance = {
                        "type": self._find_text(bal, 'Cd'),
                        "amount": self._find_text(bal, 'Amt'),
                        "currency": self._find_attr(bal, 'Amt', 'Ccy'),
                        "credit_debit": self._find_text(bal, 'CdtDbtInd'),
                        "date": self._find_text(bal, 'Dt'),
                    }
                    balances.append({k: v for k, v in balance.items() if v})
                self.result["payment"]["balances"] = balances

                # Entries
                for ntry in rpt.findall('.//{*}Ntry'):
                    entry = self._parse_entry(ntry)
                    self.result["entries"].append(entry)

        except Exception as e:
            logger.error(f"Error parsing camt.052: {e}")

        return self.result

    def _parse_entry(self, ntry) -> Dict[str, Any]:
        """Parse report entry."""
        entry = {
            "amount": self._find_text(ntry, 'Amt'),
            "currency": self._find_attr(ntry, 'Amt', 'Ccy'),
            "credit_debit": self._find_text(ntry, 'CdtDbtInd'),
            "status": self._find_text(ntry, 'Sts'),
            "booking_date": self._find_text(ntry, 'BookgDt'),
            "value_date": self._find_text(ntry, 'ValDt'),
            "reference": self._find_text(ntry, 'AcctSvcrRef'),
        }
        return {k: v for k, v in entry.items() if v}


class Camt054Parser(ISO20022Parser):
    """Parser for camt.054 - Bank to Customer Debit Credit Notification."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "DEBIT_CREDIT_NOTIFICATION"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Notification
            ntfctn = self._find_elem(root, 'Ntfctn')
            if ntfctn is not None:
                self.result["instruction"]["notification_id"] = self._find_text(ntfctn, 'Id')
                self.result["instruction"]["creation_datetime"] = self._find_text(ntfctn, 'CreDtTm')

                # Account
                acct = self._find_elem(ntfctn, 'Acct')
                if acct is not None:
                    self.result["debtor_account"] = self._parse_account(acct)

                # Entries
                for ntry in ntfctn.findall('.//{*}Ntry'):
                    entry = {
                        "amount": self._find_text(ntry, 'Amt'),
                        "currency": self._find_attr(ntry, 'Amt', 'Ccy'),
                        "credit_debit": self._find_text(ntry, 'CdtDbtInd'),
                        "status": self._find_text(ntry, 'Sts'),
                        "booking_date": self._find_text(ntry, 'BookgDt'),
                        "value_date": self._find_text(ntry, 'ValDt'),
                    }

                    # Entry details
                    dtls = self._find_elem(ntry, 'NtryDtls')
                    if dtls is not None:
                        tx_dtls = self._find_elem(dtls, 'TxDtls')
                        if tx_dtls is not None:
                            refs = self._find_elem(tx_dtls, 'Refs')
                            if refs is not None:
                                entry["end_to_end_id"] = self._find_text(refs, 'EndToEndId')
                                entry["transaction_id"] = self._find_text(refs, 'TxId')

                    self.result["entries"].append({k: v for k, v in entry.items() if v})

        except Exception as e:
            logger.error(f"Error parsing camt.054: {e}")

        return self.result


class Camt055Parser(ISO20022Parser):
    """Parser for camt.055 - Customer Payment Cancellation Request."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "CUSTOMER_CANCELLATION_REQUEST"

        try:
            root = ET.fromstring(content)

            # Assignment
            assgnmt = self._find_elem(root, 'Assgnmt')
            if assgnmt is not None:
                self.result["payment"]["message_id"] = self._find_text(assgnmt, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(assgnmt, 'CreDtTm')

            # Underlying
            undrlyg = self._find_elem(root, 'Undrlyg')
            if undrlyg is not None:
                orgnl = self._find_elem(undrlyg, 'OrgnlPmtInfAndCxl')
                if orgnl is not None:
                    self.result["status"]["original_payment_info_id"] = self._find_text(orgnl, 'OrgnlPmtInfId')

                    tx_inf = self._find_elem(orgnl, 'TxInf')
                    if tx_inf is not None:
                        self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                        self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')

                        # Cancellation reason
                        cxl_rsn = self._find_elem(tx_inf, 'CxlRsnInf')
                        if cxl_rsn is not None:
                            self.result["status"]["reason_code"] = self._find_text(cxl_rsn, 'Cd')
                            self.result["status"]["additional_info"] = self._find_text(cxl_rsn, 'AddtlInf')

        except Exception as e:
            logger.error(f"Error parsing camt.055: {e}")

        return self.result


class Camt056Parser(ISO20022Parser):
    """Parser for camt.056 - FI to FI Payment Cancellation Request."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FI_CANCELLATION_REQUEST"

        try:
            root = ET.fromstring(content)

            # Assignment
            assgnmt = self._find_elem(root, 'Assgnmt')
            if assgnmt is not None:
                self.result["payment"]["message_id"] = self._find_text(assgnmt, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(assgnmt, 'CreDtTm')

            # Underlying
            undrlyg = self._find_elem(root, 'Undrlyg')
            if undrlyg is not None:
                tx_inf = self._find_elem(undrlyg, 'TxInf')
                if tx_inf is not None:
                    self.result["status"]["original_instruction_id"] = self._find_text(tx_inf, 'OrgnlInstrId')
                    self.result["status"]["original_end_to_end_id"] = self._find_text(tx_inf, 'OrgnlEndToEndId')
                    self.result["status"]["original_transaction_id"] = self._find_text(tx_inf, 'OrgnlTxId')
                    self.result["status"]["original_uetr"] = self._find_text(tx_inf, 'OrgnlUETR')

                    # Original amount
                    orgnl_amt = self._find_elem(tx_inf, 'OrgnlIntrBkSttlmAmt')
                    if orgnl_amt is not None:
                        self.result["instruction"]["instructed_amount"] = orgnl_amt.text
                        self.result["instruction"]["instructed_currency"] = orgnl_amt.get('Ccy')

                    # Cancellation reason
                    cxl_rsn = self._find_elem(tx_inf, 'CxlRsnInf')
                    if cxl_rsn is not None:
                        self.result["status"]["reason_code"] = self._find_text(cxl_rsn, 'Cd')
                        self.result["status"]["additional_info"] = self._find_text(cxl_rsn, 'AddtlInf')

        except Exception as e:
            logger.error(f"Error parsing camt.056: {e}")

        return self.result


class Camt057Parser(ISO20022Parser):
    """Parser for camt.057 - Notification to Receive."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "NOTIFICATION_TO_RECEIVE"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')
                self.result["payment"]["number_of_transactions"] = self._find_text(grp_hdr, 'NbOfTxs')

            # Notification
            ntfctn = self._find_elem(root, 'Ntfctn')
            if ntfctn is not None:
                self.result["instruction"]["notification_id"] = self._find_text(ntfctn, 'Id')
                self.result["instruction"]["expected_value_date"] = self._find_text(ntfctn, 'XpctdValDt')

                # Account
                acct = self._find_elem(ntfctn, 'Acct')
                if acct is not None:
                    self.result["creditor_account"] = self._parse_account(acct)

                # Debtor
                self.result["debtor"] = self._parse_party(self._find_elem(ntfctn, 'Dbtr'))
                self.result["debtor_agent"] = self._parse_agent(self._find_elem(ntfctn, 'DbtrAgt'))

                # Item
                itm = self._find_elem(ntfctn, 'Itm')
                if itm is not None:
                    self.result["instruction"]["item_id"] = self._find_text(itm, 'Id')
                    self.result["instruction"]["end_to_end_id"] = self._find_text(itm, 'EndToEndId')

                    amt = self._find_elem(itm, 'Amt')
                    if amt is not None:
                        self.result["instruction"]["instructed_amount"] = amt.text
                        self.result["instruction"]["instructed_currency"] = amt.get('Ccy')

        except Exception as e:
            logger.error(f"Error parsing camt.057: {e}")

        return self.result


class Camt058Parser(ISO20022Parser):
    """Parser for camt.058 - Notification to Receive Cancellation Advice."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "NOTIFICATION_CANCELLATION"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Original Notification
            orgnl = self._find_elem(root, 'OrgnlNtfctn')
            if orgnl is not None:
                self.result["status"]["original_notification_id"] = self._find_text(orgnl, 'OrgnlNtfctnId')
                self.result["status"]["original_item_id"] = self._find_text(orgnl, 'OrgnlItmId')
                self.result["status"]["cancellation_reason"] = self._find_text(orgnl, 'CxlRsnInf')

        except Exception as e:
            logger.error(f"Error parsing camt.058: {e}")

        return self.result


class Camt059Parser(ISO20022Parser):
    """Parser for camt.059 - Notification to Receive Status Report."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "NOTIFICATION_STATUS_REPORT"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Original Notification and Status
            orgnl = self._find_elem(root, 'OrgnlNtfctnAndSts')
            if orgnl is not None:
                self.result["status"]["original_notification_id"] = self._find_text(orgnl, 'OrgnlNtfctnId')
                self.result["status"]["notification_status"] = self._find_text(orgnl, 'NtfctnSts')

        except Exception as e:
            logger.error(f"Error parsing camt.059: {e}")

        return self.result


class Camt060Parser(ISO20022Parser):
    """Parser for camt.060 - Account Reporting Request."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_REPORTING_REQUEST"

        try:
            root = ET.fromstring(content)

            # Group Header
            grp_hdr = self._find_elem(root, 'GrpHdr')
            if grp_hdr is not None:
                self.result["payment"]["message_id"] = self._find_text(grp_hdr, 'MsgId')
                self.result["payment"]["creation_datetime"] = self._find_text(grp_hdr, 'CreDtTm')

            # Reporting Request
            rptg_req = self._find_elem(root, 'RptgReq')
            if rptg_req is not None:
                self.result["instruction"]["request_id"] = self._find_text(rptg_req, 'Id')
                self.result["instruction"]["requested_execution_date"] = self._find_text(rptg_req, 'ReqdExctnDt')
                self.result["instruction"]["report_type"] = self._find_text(rptg_req, 'Cd')

                # Account
                acct = self._find_elem(rptg_req, 'Acct')
                if acct is not None:
                    self.result["debtor_account"] = self._parse_account(acct)

        except Exception as e:
            logger.error(f"Error parsing camt.060: {e}")

        return self.result


class Camt086Parser(ISO20022Parser):
    """Parser for camt.086 - Bank Services Billing Statement."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "BILLING_STATEMENT"

        try:
            root = ET.fromstring(content)

            # Billing Statement
            bllg_stmt = self._find_elem(root, 'BllgStmt')
            if bllg_stmt is not None:
                self.result["instruction"]["statement_id"] = self._find_text(bllg_stmt, 'StmtId')
                self.result["instruction"]["from_date"] = self._find_text(bllg_stmt, 'FrToDt')
                self.result["payment"]["creation_datetime"] = self._find_text(bllg_stmt, 'CreDtTm')

                # Billing Statement Group
                bllg_grp = self._find_elem(bllg_stmt, 'BllgGrp')
                if bllg_grp is not None:
                    # Parse service entries
                    for svc in bllg_grp.findall('.//{*}SvcChrgDtl'):
                        entry = {
                            "service_id": self._find_text(svc, 'SvcId'),
                            "service_type": self._find_text(svc, 'Tp'),
                            "amount": self._find_text(svc, 'Amt'),
                            "currency": self._find_attr(svc, 'Amt', 'Ccy'),
                        }
                        self.result["entries"].append({k: v for k, v in entry.items() if v})

        except Exception as e:
            logger.error(f"Error parsing camt.086: {e}")

        return self.result


class Camt087Parser(ISO20022Parser):
    """Parser for camt.087 - Request for Duplicate."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "REQUEST_FOR_DUPLICATE"

        try:
            root = ET.fromstring(content)

            # Assignment
            assgnmt = self._find_elem(root, 'Assgnmt')
            if assgnmt is not None:
                self.result["payment"]["message_id"] = self._find_text(assgnmt, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(assgnmt, 'CreDtTm')

            # Request for Duplicate
            req = self._find_elem(root, 'ReqForDplct')
            if req is not None:
                # Payment Instruction Reference
                pmt_ref = self._find_elem(req, 'PmtInstrRef')
                if pmt_ref is not None:
                    self.result["status"]["original_message_id"] = self._find_text(pmt_ref, 'MsgId')
                    self.result["status"]["original_message_type"] = self._find_text(pmt_ref, 'MsgNm')
                    self.result["status"]["original_instruction_id"] = self._find_text(pmt_ref, 'InstrId')
                    self.result["status"]["original_end_to_end_id"] = self._find_text(pmt_ref, 'EndToEndId')

        except Exception as e:
            logger.error(f"Error parsing camt.087: {e}")

        return self.result


# =============================================================================
# ISO 20022 ACMT Parsers (Account Management)
# =============================================================================

class Acmt001Parser(ISO20022Parser):
    """Parser for acmt.001 - Account Opening Instruction."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_OPENING"

        try:
            root = ET.fromstring(content)

            # Message Identification
            msg_id = self._find_elem(root, 'MsgId')
            if msg_id is not None:
                self.result["payment"]["message_id"] = self._find_text(msg_id, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(msg_id, 'CreDtTm')

            # Account Details
            acct_dtls = self._find_elem(root, 'AcctDtls')
            if acct_dtls is not None:
                self.result["debtor_account"]["account_type"] = self._find_text(acct_dtls, 'Cd')
                self.result["debtor_account"]["currency"] = self._find_text(acct_dtls, 'Ccy')
                self.result["debtor_account"]["name"] = self._find_text(acct_dtls, 'Nm')

            # Account Parties
            acct_pties = self._find_elem(root, 'AcctPties')
            if acct_pties is not None:
                # Principal Account Owner
                prncpl = self._find_elem(acct_pties, 'PrncplAcctOwnr')
                if prncpl is not None:
                    self.result["debtor"] = self._parse_party(prncpl)

                # Account Servicer
                svcr = self._find_elem(acct_pties, 'AcctSvcr')
                if svcr is not None:
                    self.result["debtor_agent"] = self._parse_agent(svcr)

        except Exception as e:
            logger.error(f"Error parsing acmt.001: {e}")

        return self.result


class Acmt002Parser(ISO20022Parser):
    """Parser for acmt.002 - Account Opening Amendment."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_AMENDMENT"

        try:
            root = ET.fromstring(content)

            # Message Identification
            msg_id = self._find_elem(root, 'MsgId')
            if msg_id is not None:
                self.result["payment"]["message_id"] = self._find_text(msg_id, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(msg_id, 'CreDtTm')

            # Amendment Details
            amdmnt = self._find_elem(root, 'AcctOpngAmdmntDtls')
            if amdmnt is not None:
                self.result["instruction"]["amendment_id"] = self._find_text(amdmnt, 'AmdmntId')

                acct = self._find_elem(amdmnt, 'Acct')
                if acct is not None:
                    self.result["debtor_account"] = self._parse_account(acct)

        except Exception as e:
            logger.error(f"Error parsing acmt.002: {e}")

        return self.result


class Acmt003Parser(ISO20022Parser):
    """Parser for acmt.003 - Account Modification Instruction."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_MODIFICATION"

        try:
            root = ET.fromstring(content)

            # Message Identification
            msg_id = self._find_elem(root, 'MsgId')
            if msg_id is not None:
                self.result["payment"]["message_id"] = self._find_text(msg_id, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(msg_id, 'CreDtTm')

            # Modification Details
            mod = self._find_elem(root, 'AcctModDtls')
            if mod is not None:
                acct_id = self._find_elem(mod, 'AcctId')
                if acct_id is not None:
                    self.result["debtor_account"] = self._parse_account(acct_id)

                # Modified Account Details
                mod_dtls = self._find_elem(mod, 'ModfdAcctDtls')
                if mod_dtls is not None:
                    self.result["instruction"]["modified_name"] = self._find_text(mod_dtls, 'Nm')
                    self.result["instruction"]["modified_currency"] = self._find_text(mod_dtls, 'Ccy')

        except Exception as e:
            logger.error(f"Error parsing acmt.003: {e}")

        return self.result


class Acmt005Parser(ISO20022Parser):
    """Parser for acmt.005 - Account Management Status Report Request."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_STATUS_REQUEST"

        try:
            root = ET.fromstring(content)

            # Message Identification
            msg_id = self._find_elem(root, 'MsgId')
            if msg_id is not None:
                self.result["payment"]["message_id"] = self._find_text(msg_id, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(msg_id, 'CreDtTm')

            # Request Details
            req = self._find_elem(root, 'ReqDtls')
            if req is not None:
                self.result["instruction"]["original_message_id"] = self._find_text(req, 'OrgnlMsgId')

        except Exception as e:
            logger.error(f"Error parsing acmt.005: {e}")

        return self.result


class Acmt006Parser(ISO20022Parser):
    """Parser for acmt.006 - Account Management Status Report."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_STATUS_REPORT"

        try:
            root = ET.fromstring(content)

            # Message Identification
            msg_id = self._find_elem(root, 'MsgId')
            if msg_id is not None:
                self.result["payment"]["message_id"] = self._find_text(msg_id, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(msg_id, 'CreDtTm')

            # Report Details
            rpt = self._find_elem(root, 'AcctMgmtStsRpt')
            if rpt is not None:
                self.result["status"]["status"] = self._find_text(rpt, 'Sts')
                self.result["status"]["original_message_id"] = self._find_text(rpt, 'OrgnlMsgId')

                # Reason
                rsn = self._find_elem(rpt, 'StsRsn')
                if rsn is not None:
                    self.result["status"]["reason_code"] = self._find_text(rsn, 'Cd')

        except Exception as e:
            logger.error(f"Error parsing acmt.006: {e}")

        return self.result


class Acmt007Parser(ISO20022Parser):
    """Parser for acmt.007 - Account Opening Request."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACCOUNT_OPENING_REQUEST"

        try:
            root = ET.fromstring(content)

            # Message Identification
            msg_id = self._find_elem(root, 'MsgId')
            if msg_id is not None:
                self.result["payment"]["message_id"] = self._find_text(msg_id, 'Id')
                self.result["payment"]["creation_datetime"] = self._find_text(msg_id, 'CreDtTm')

            # Account Details
            acct_dtls = self._find_elem(root, 'AcctDtls')
            if acct_dtls is not None:
                self.result["debtor_account"]["account_type"] = self._find_text(acct_dtls, 'Cd')
                self.result["debtor_account"]["currency"] = self._find_text(acct_dtls, 'Ccy')

            # Account Parties
            acct_pties = self._find_elem(root, 'AcctPties')
            if acct_pties is not None:
                ownr = self._find_elem(acct_pties, 'AcctOwnr')
                if ownr is not None:
                    self.result["debtor"] = self._parse_party(ownr)

        except Exception as e:
            logger.error(f"Error parsing acmt.007: {e}")

        return self.result


class MT103Parser(MessageParser):
    """Parser for SWIFT MT103 - Single Customer Credit Transfer."""

    # Field tag patterns
    FIELD_PATTERNS = {
        '20': r':20:(.+)',           # Transaction Reference
        '23B': r':23B:(.+)',         # Bank Operation Code
        '32A': r':32A:(\d{6})(\w{3})(\d+[,.]?\d*)',  # Value Date/Currency/Amount
        '33B': r':33B:(\w{3})(\d+[,.]?\d*)',        # Currency/Instructed Amount
        '36': r':36:(\d+[,.]?\d*)',   # Exchange Rate
        '50K': r':50K:(.+?)(?=:\d|$)',  # Ordering Customer (K)
        '50A': r':50A:(.+?)(?=:\d|$)',  # Ordering Customer (A)
        '50F': r':50F:(.+?)(?=:\d|$)',  # Ordering Customer (F)
        '52A': r':52A:(.+?)(?=:\d|$)',  # Ordering Institution
        '52D': r':52D:(.+?)(?=:\d|$)',  # Ordering Institution (D)
        '53A': r':53A:(.+?)(?=:\d|$)',  # Sender's Correspondent
        '53B': r':53B:(.+?)(?=:\d|$)',  # Sender's Correspondent (B)
        '54A': r':54A:(.+?)(?=:\d|$)',  # Receiver's Correspondent
        '56A': r':56A:(.+?)(?=:\d|$)',  # Intermediary
        '57A': r':57A:(.+?)(?=:\d|$)',  # Account With Institution
        '57D': r':57D:(.+?)(?=:\d|$)',  # Account With Institution (D)
        '59': r':59:(.+?)(?=:\d|$)',    # Beneficiary Customer
        '59A': r':59A:(.+?)(?=:\d|$)',  # Beneficiary Customer (A)
        '59F': r':59F:(.+?)(?=:\d|$)',  # Beneficiary Customer (F)
        '70': r':70:(.+?)(?=:\d|$)',    # Remittance Information
        '71A': r':71A:(.+)',           # Details of Charges
        '71F': r':71F:(\w{3})(\d+[,.]?\d*)',  # Sender's Charges
        '71G': r':71G:(\w{3})(\d+[,.]?\d*)',  # Receiver's Charges
        '72': r':72:(.+?)(?=:\d|$)',    # Sender to Receiver Info
        '77B': r':77B:(.+?)(?=:\d|$)',  # Regulatory Reporting
    }

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()

        try:
            # Normalize line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')

            # Parse header blocks
            self._parse_headers(content)

            # Parse text block (Block 4)
            block4_match = re.search(r'\{4:(.+?)\}', content, re.DOTALL)
            if block4_match:
                self._parse_block4(block4_match.group(1))
            else:
                # Try parsing as raw text
                self._parse_block4(content)

            self._set_cross_border_flag()

        except Exception as e:
            logger.error(f"Error parsing MT103: {e}")

        return self.result

    def _parse_headers(self, content: str):
        """Parse header blocks."""
        # Block 1 - Basic Header
        block1 = re.search(r'\{1:([^}]+)\}', content)
        if block1:
            header = block1.group(1)
            if len(header) >= 12:
                self.result["payment"]["sender_bic"] = header[3:15] if len(header) >= 15 else header[3:12]

        # Block 2 - Application Header
        block2 = re.search(r'\{2:([^}]+)\}', content)
        if block2:
            header = block2.group(1)
            if header.startswith('I'):
                # Input header
                if len(header) >= 15:
                    self.result["payment"]["receiver_bic"] = header[4:16]
                if len(header) >= 16:
                    priority = header[16:17] if len(header) > 16 else 'N'
                    self.result["instruction"]["priority"] = {
                        'N': 'NORM', 'U': 'HIGH', 'S': 'HIGH'
                    }.get(priority, 'NORM')

        # Block 3 - User Header
        block3 = re.search(r'\{3:(.+?)\}', content, re.DOTALL)
        if block3:
            user_header = block3.group(1)
            # UETR
            uetr_match = re.search(r'\{121:([^}]+)\}', user_header)
            if uetr_match:
                self.result["instruction"]["uetr"] = uetr_match.group(1)
            # MUR (Message User Reference)
            mur_match = re.search(r'\{108:([^}]+)\}', user_header)
            if mur_match:
                self.result["instruction"]["instruction_id"] = mur_match.group(1)

    def _parse_block4(self, block4: str):
        """Parse text block (Block 4)."""
        # :20: Transaction Reference
        match = re.search(r':20:(.+?)(?:\n|$)', block4)
        if match:
            self.result["instruction"]["end_to_end_id"] = match.group(1).strip()

        # :23B: Bank Operation Code
        match = re.search(r':23B:(.+?)(?:\n|$)', block4)
        if match:
            self.result["instruction"]["bank_operation_code"] = match.group(1).strip()

        # :32A: Value Date/Currency/Amount
        match = re.search(r':32A:(\d{6})(\w{3})(\d+[,.]?\d*)', block4)
        if match:
            date_str = match.group(1)
            self.result["instruction"]["value_date"] = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
            self.result["instruction"]["interbank_settlement_currency"] = match.group(2)
            self.result["instruction"]["interbank_settlement_amount"] = match.group(3).replace(',', '.')
            # Also set as instructed amount if not present
            self.result["instruction"]["instructed_currency"] = match.group(2)
            self.result["instruction"]["instructed_amount"] = match.group(3).replace(',', '.')

        # :33B: Original Instructed Amount
        match = re.search(r':33B:(\w{3})(\d+[,.]?\d*)', block4)
        if match:
            self.result["instruction"]["instructed_currency"] = match.group(1)
            self.result["instruction"]["instructed_amount"] = match.group(2).replace(',', '.')

        # :36: Exchange Rate
        match = re.search(r':36:(\d+[,.]?\d*)', block4)
        if match:
            self.result["instruction"]["exchange_rate"] = match.group(1).replace(',', '.')

        # :50: Ordering Customer (Debtor)
        self._parse_party_field(block4, ['50K', '50A', '50F'], self.result["debtor"], self.result["debtor_account"])

        # :52: Ordering Institution (Debtor Agent)
        self._parse_institution_field(block4, ['52A', '52D'], self.result["debtor_agent"])

        # :53: Sender's Correspondent (Intermediary 1)
        agent1 = {}
        self._parse_institution_field(block4, ['53A', '53B'], agent1)
        if agent1:
            agent1["sequence"] = 1
            self.result["intermediary_agents"].append(agent1)

        # :54: Receiver's Correspondent (Intermediary 2)
        agent2 = {}
        self._parse_institution_field(block4, ['54A', '54B'], agent2)
        if agent2:
            agent2["sequence"] = 2
            self.result["intermediary_agents"].append(agent2)

        # :56: Intermediary Institution
        agent3 = {}
        self._parse_institution_field(block4, ['56A', '56D'], agent3)
        if agent3:
            agent3["sequence"] = 3
            self.result["intermediary_agents"].append(agent3)

        # :57: Account With Institution (Creditor Agent)
        self._parse_institution_field(block4, ['57A', '57D'], self.result["creditor_agent"])

        # :59: Beneficiary Customer (Creditor)
        self._parse_party_field(block4, ['59', '59A', '59F'], self.result["creditor"], self.result["creditor_account"])

        # :70: Remittance Information
        match = re.search(r':70:(.+?)(?=:\d{2}[A-Z]?:|$)', block4, re.DOTALL)
        if match:
            lines = match.group(1).strip().split('\n')
            self.result["remittance"]["unstructured"] = [l.strip() for l in lines if l.strip()]

        # :71A: Details of Charges
        match = re.search(r':71A:(.+?)(?:\n|$)', block4)
        if match:
            code = match.group(1).strip()
            self.result["instruction"]["charge_bearer"] = {
                'OUR': 'DEBT', 'BEN': 'CRED', 'SHA': 'SHAR'
            }.get(code, code)

        # :71F: Sender's Charges
        for match in re.finditer(r':71F:(\w{3})(\d+[,.]?\d*)', block4):
            self.result["charges"].append({
                "type": "SENDER",
                "currency": match.group(1),
                "amount": match.group(2).replace(',', '.'),
            })

        # :71G: Receiver's Charges
        match = re.search(r':71G:(\w{3})(\d+[,.]?\d*)', block4)
        if match:
            self.result["charges"].append({
                "type": "RECEIVER",
                "currency": match.group(1),
                "amount": match.group(2).replace(',', '.'),
            })

        # :72: Sender to Receiver Information
        match = re.search(r':72:(.+?)(?=:\d{2}[A-Z]?:|$)', block4, re.DOTALL)
        if match:
            lines = match.group(1).strip().split('\n')
            self.result["instruction"]["sender_to_receiver_info"] = '\n'.join(
                l.strip() for l in lines if l.strip()
            )

        # :77B: Regulatory Reporting
        match = re.search(r':77B:(.+?)(?=:\d{2}[A-Z]?:|$)', block4, re.DOTALL)
        if match:
            self.result["regulatory"]["information"] = match.group(1).strip()

    def _parse_party_field(self, block4: str, tags: List[str], party: Dict, account: Dict):
        """Parse party fields like :50K:, :59:."""
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                content = match.group(1).strip()
                lines = content.split('\n')

                # First line might be account number
                if lines and lines[0].startswith('/'):
                    account["account_number"] = lines[0][1:].strip()
                    lines = lines[1:]

                # For 'A' option, extract BIC
                if tag.endswith('A') and lines:
                    bic_line = lines[0].strip()
                    if len(bic_line) >= 8:
                        party["bic"] = bic_line[:11] if len(bic_line) >= 11 else bic_line[:8]
                        lines = lines[1:]

                # Remaining lines are name and address
                if lines:
                    party["name"] = lines[0].strip()
                    if len(lines) > 1:
                        party["address_line_1"] = '\n'.join(l.strip() for l in lines[1:])

                break

    def _parse_institution_field(self, block4: str, tags: List[str], agent: Dict):
        """Parse institution fields like :52A:, :57A:."""
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                content = match.group(1).strip()
                lines = content.split('\n')

                # First line might be account
                if lines and lines[0].startswith('/'):
                    agent["account_number"] = lines[0][1:].strip()
                    lines = lines[1:]

                # For 'A' option, first line is BIC
                if tag.endswith('A') and lines:
                    bic_line = lines[0].strip()
                    if len(bic_line) >= 8:
                        agent["bic"] = bic_line[:11] if len(bic_line) >= 11 else bic_line[:8]
                elif tag.endswith('D') and lines:
                    # 'D' option is name and address
                    agent["name"] = lines[0].strip()
                    if len(lines) > 1:
                        agent["address_line_1"] = '\n'.join(l.strip() for l in lines[1:])

                break

    def _set_cross_border_flag(self):
        """Determine if payment is cross-border based on BICs."""
        sender_bic = self.result["payment"].get("sender_bic", "")
        receiver_bic = self.result["payment"].get("receiver_bic", "")

        if len(sender_bic) >= 6 and len(receiver_bic) >= 6:
            sender_country = sender_bic[4:6]
            receiver_country = receiver_bic[4:6]
            self.result["payment"]["cross_border"] = sender_country != receiver_country


# =============================================================================
# Additional SWIFT MT Parsers
# =============================================================================

class MT200Parser(MessageParser):
    """Parser for MT200 - Financial Institution Transfer for Own Account."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FI_OWN_ACCOUNT_TRANSFER"

        try:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            self._parse_headers(content)

            block4_match = re.search(r'\{4:(.+?)\}', content, re.DOTALL)
            block4 = block4_match.group(1) if block4_match else content

            # :20: Transaction Reference
            match = re.search(r':20:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["end_to_end_id"] = match.group(1).strip()

            # :32A: Value Date/Currency/Amount
            match = re.search(r':32A:(\d{6})(\w{3})(\d+[,.]?\d*)', block4)
            if match:
                date_str = match.group(1)
                self.result["instruction"]["value_date"] = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
                self.result["instruction"]["instructed_currency"] = match.group(2)
                self.result["instruction"]["instructed_amount"] = match.group(3).replace(',', '.')

            # :53: Sender's Correspondent
            self._parse_institution(block4, ['53A', '53B', '53D'], self.result["debtor_agent"])

            # :56: Intermediary
            agent = {}
            self._parse_institution(block4, ['56A', '56D'], agent)
            if agent:
                agent["sequence"] = 1
                self.result["intermediary_agents"].append(agent)

            # :57: Account With Institution
            self._parse_institution(block4, ['57A', '57D'], self.result["creditor_agent"])

        except Exception as e:
            logger.error(f"Error parsing MT200: {e}")

        return self.result

    def _parse_headers(self, content: str):
        """Parse SWIFT header blocks."""
        block1 = re.search(r'\{1:([^}]+)\}', content)
        if block1 and len(block1.group(1)) >= 12:
            self.result["payment"]["sender_bic"] = block1.group(1)[3:15] if len(block1.group(1)) >= 15 else block1.group(1)[3:12]

        block2 = re.search(r'\{2:([^}]+)\}', content)
        if block2 and block2.group(1).startswith('I') and len(block2.group(1)) >= 15:
            self.result["payment"]["receiver_bic"] = block2.group(1)[4:16]

    def _parse_institution(self, block4: str, tags: List[str], agent: Dict):
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                content = match.group(1).strip()
                lines = content.split('\n')
                if lines and lines[0].startswith('/'):
                    agent["account_number"] = lines[0][1:].strip()
                    lines = lines[1:]
                if tag.endswith('A') and lines:
                    bic_line = lines[0].strip()
                    if len(bic_line) >= 8:
                        agent["bic"] = bic_line[:11] if len(bic_line) >= 11 else bic_line[:8]
                break


class MT202Parser(MessageParser):
    """Parser for MT202 - General Financial Institution Transfer."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FI_TRANSFER"

        try:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            self._parse_headers(content)

            block4_match = re.search(r'\{4:(.+?)\}', content, re.DOTALL)
            block4 = block4_match.group(1) if block4_match else content

            # :20: Transaction Reference
            match = re.search(r':20:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["end_to_end_id"] = match.group(1).strip()

            # :21: Related Reference
            match = re.search(r':21:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["related_reference"] = match.group(1).strip()

            # :32A: Value Date/Currency/Amount
            match = re.search(r':32A:(\d{6})(\w{3})(\d+[,.]?\d*)', block4)
            if match:
                date_str = match.group(1)
                self.result["instruction"]["value_date"] = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
                self.result["instruction"]["instructed_currency"] = match.group(2)
                self.result["instruction"]["instructed_amount"] = match.group(3).replace(',', '.')

            # :52: Ordering Institution
            self._parse_institution(block4, ['52A', '52D'], self.result["debtor_agent"])

            # :53: Sender's Correspondent
            agent1 = {}
            self._parse_institution(block4, ['53A', '53B'], agent1)
            if agent1:
                agent1["sequence"] = 1
                self.result["intermediary_agents"].append(agent1)

            # :54: Receiver's Correspondent
            agent2 = {}
            self._parse_institution(block4, ['54A', '54B'], agent2)
            if agent2:
                agent2["sequence"] = 2
                self.result["intermediary_agents"].append(agent2)

            # :56: Intermediary
            agent3 = {}
            self._parse_institution(block4, ['56A', '56D'], agent3)
            if agent3:
                agent3["sequence"] = 3
                self.result["intermediary_agents"].append(agent3)

            # :57: Account With Institution
            self._parse_institution(block4, ['57A', '57D'], self.result["creditor_agent"])

            # :58: Beneficiary Institution
            beneficiary_agent = {}
            self._parse_institution(block4, ['58A', '58D'], beneficiary_agent)
            if beneficiary_agent:
                self.result["creditor"]["bic"] = beneficiary_agent.get("bic")
                self.result["creditor"]["name"] = beneficiary_agent.get("name")

            # :72: Sender to Receiver Information
            match = re.search(r':72:(.+?)(?=:\d{2}[A-Z]?:|$)', block4, re.DOTALL)
            if match:
                self.result["instruction"]["sender_to_receiver_info"] = match.group(1).strip()

        except Exception as e:
            logger.error(f"Error parsing MT202: {e}")

        return self.result

    def _parse_headers(self, content: str):
        block1 = re.search(r'\{1:([^}]+)\}', content)
        if block1 and len(block1.group(1)) >= 12:
            self.result["payment"]["sender_bic"] = block1.group(1)[3:15] if len(block1.group(1)) >= 15 else block1.group(1)[3:12]
        block2 = re.search(r'\{2:([^}]+)\}', content)
        if block2 and block2.group(1).startswith('I') and len(block2.group(1)) >= 15:
            self.result["payment"]["receiver_bic"] = block2.group(1)[4:16]

    def _parse_institution(self, block4: str, tags: List[str], agent: Dict):
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                content = match.group(1).strip()
                lines = content.split('\n')
                if lines and lines[0].startswith('/'):
                    agent["account_number"] = lines[0][1:].strip()
                    lines = lines[1:]
                if tag.endswith('A') and lines:
                    bic_line = lines[0].strip()
                    if len(bic_line) >= 8:
                        agent["bic"] = bic_line[:11] if len(bic_line) >= 11 else bic_line[:8]
                elif tag.endswith('D') and lines:
                    agent["name"] = lines[0].strip()
                break


class MT202COVParser(MT202Parser):
    """Parser for MT202COV - Cover Payment."""

    def parse(self, content: str) -> Dict[str, Any]:
        # First parse as standard MT202
        result = super().parse(content)
        result["instruction"]["payment_type"] = "COVER_PAYMENT"

        try:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            block4_match = re.search(r'\{4:(.+?)\}', content, re.DOTALL)
            block4 = block4_match.group(1) if block4_match else content

            # MT202COV has additional underlying customer credit transfer details
            # :50: Ordering Customer
            self._parse_party_field(block4, ['50K', '50A', '50F'], result["debtor"], result.get("debtor_account", {}))

            # :59: Beneficiary Customer
            self._parse_party_field(block4, ['59', '59A', '59F'], result["creditor"], result.get("creditor_account", {}))

            # :70: Remittance Information
            match = re.search(r':70:(.+?)(?=:\d{2}[A-Z]?:|$)', block4, re.DOTALL)
            if match:
                lines = match.group(1).strip().split('\n')
                result["remittance"]["unstructured"] = [l.strip() for l in lines if l.strip()]

        except Exception as e:
            logger.error(f"Error parsing MT202COV additional fields: {e}")

        return result

    def _parse_party_field(self, block4: str, tags: List[str], party: Dict, account: Dict):
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                content = match.group(1).strip()
                lines = content.split('\n')
                if lines and lines[0].startswith('/'):
                    account["account_number"] = lines[0][1:].strip()
                    lines = lines[1:]
                if lines:
                    party["name"] = lines[0].strip()
                break


class MT900Parser(MessageParser):
    """Parser for MT900 - Confirmation of Debit."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "DEBIT_CONFIRMATION"

        try:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            self._parse_headers(content)

            block4_match = re.search(r'\{4:(.+?)\}', content, re.DOTALL)
            block4 = block4_match.group(1) if block4_match else content

            # :20: Transaction Reference
            match = re.search(r':20:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["end_to_end_id"] = match.group(1).strip()

            # :21: Related Reference
            match = re.search(r':21:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["related_reference"] = match.group(1).strip()

            # :25: Account Identification
            match = re.search(r':25:(.+?)(?:\n|$)', block4)
            if match:
                self.result["debtor_account"]["account_number"] = match.group(1).strip()

            # :32A: Value Date/Currency/Amount
            match = re.search(r':32A:(\d{6})(\w{3})(\d+[,.]?\d*)', block4)
            if match:
                date_str = match.group(1)
                self.result["instruction"]["value_date"] = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
                self.result["instruction"]["instructed_currency"] = match.group(2)
                self.result["instruction"]["instructed_amount"] = match.group(3).replace(',', '.')

            # :52: Ordering Institution
            self._parse_institution(block4, ['52A', '52D'], self.result["debtor_agent"])

        except Exception as e:
            logger.error(f"Error parsing MT900: {e}")

        return self.result

    def _parse_headers(self, content: str):
        block1 = re.search(r'\{1:([^}]+)\}', content)
        if block1 and len(block1.group(1)) >= 12:
            self.result["payment"]["sender_bic"] = block1.group(1)[3:15] if len(block1.group(1)) >= 15 else block1.group(1)[3:12]

    def _parse_institution(self, block4: str, tags: List[str], agent: Dict):
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                content = match.group(1).strip()
                lines = content.split('\n')
                if tag.endswith('A') and lines:
                    bic_line = lines[0].strip()
                    if len(bic_line) >= 8:
                        agent["bic"] = bic_line[:11] if len(bic_line) >= 11 else bic_line[:8]
                break


class MT910Parser(MessageParser):
    """Parser for MT910 - Confirmation of Credit."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "CREDIT_CONFIRMATION"

        try:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            self._parse_headers(content)

            block4_match = re.search(r'\{4:(.+?)\}', content, re.DOTALL)
            block4 = block4_match.group(1) if block4_match else content

            # :20: Transaction Reference
            match = re.search(r':20:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["end_to_end_id"] = match.group(1).strip()

            # :21: Related Reference
            match = re.search(r':21:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["related_reference"] = match.group(1).strip()

            # :25: Account Identification
            match = re.search(r':25:(.+?)(?:\n|$)', block4)
            if match:
                self.result["creditor_account"]["account_number"] = match.group(1).strip()

            # :32A: Value Date/Currency/Amount
            match = re.search(r':32A:(\d{6})(\w{3})(\d+[,.]?\d*)', block4)
            if match:
                date_str = match.group(1)
                self.result["instruction"]["value_date"] = f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}"
                self.result["instruction"]["instructed_currency"] = match.group(2)
                self.result["instruction"]["instructed_amount"] = match.group(3).replace(',', '.')

            # :50: Ordering Customer
            self._parse_party(block4, ['50K', '50A', '50F'], self.result["debtor"])

            # :52: Ordering Institution
            self._parse_institution(block4, ['52A', '52D'], self.result["debtor_agent"])

        except Exception as e:
            logger.error(f"Error parsing MT910: {e}")

        return self.result

    def _parse_headers(self, content: str):
        block1 = re.search(r'\{1:([^}]+)\}', content)
        if block1 and len(block1.group(1)) >= 12:
            self.result["payment"]["sender_bic"] = block1.group(1)[3:15] if len(block1.group(1)) >= 15 else block1.group(1)[3:12]

    def _parse_party(self, block4: str, tags: List[str], party: Dict):
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                lines = match.group(1).strip().split('\n')
                if lines:
                    party["name"] = lines[0].strip() if not lines[0].startswith('/') else (lines[1].strip() if len(lines) > 1 else None)
                break

    def _parse_institution(self, block4: str, tags: List[str], agent: Dict):
        for tag in tags:
            pattern = rf':{tag}:(.+?)(?=:\d{{2}}[A-Z]?:|$)'
            match = re.search(pattern, block4, re.DOTALL)
            if match:
                content = match.group(1).strip()
                lines = content.split('\n')
                if tag.endswith('A') and lines:
                    bic_line = lines[0].strip()
                    if len(bic_line) >= 8:
                        agent["bic"] = bic_line[:11] if len(bic_line) >= 11 else bic_line[:8]
                break


class MT940Parser(MessageParser):
    """Parser for MT940 - Customer Statement Message."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "CUSTOMER_STATEMENT"

        try:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            self._parse_headers(content)

            block4_match = re.search(r'\{4:(.+?)\}', content, re.DOTALL)
            block4 = block4_match.group(1) if block4_match else content

            # :20: Transaction Reference
            match = re.search(r':20:(.+?)(?:\n|$)', block4)
            if match:
                self.result["payment"]["message_id"] = match.group(1).strip()

            # :25: Account Identification
            match = re.search(r':25:(.+?)(?:\n|$)', block4)
            if match:
                self.result["debtor_account"]["account_number"] = match.group(1).strip()

            # :28C: Statement Number
            match = re.search(r':28C:(.+?)(?:\n|$)', block4)
            if match:
                self.result["instruction"]["statement_number"] = match.group(1).strip()

            # :60F: Opening Balance
            match = re.search(r':60F:([CD])(\d{6})(\w{3})(\d+[,.]?\d*)', block4)
            if match:
                self.result["payment"]["opening_balance"] = {
                    "credit_debit": "CREDIT" if match.group(1) == 'C' else "DEBIT",
                    "date": f"20{match.group(2)[:2]}-{match.group(2)[2:4]}-{match.group(2)[4:6]}",
                    "currency": match.group(3),
                    "amount": match.group(4).replace(',', '.'),
                }

            # :62F: Closing Balance
            match = re.search(r':62F:([CD])(\d{6})(\w{3})(\d+[,.]?\d*)', block4)
            if match:
                self.result["payment"]["closing_balance"] = {
                    "credit_debit": "CREDIT" if match.group(1) == 'C' else "DEBIT",
                    "date": f"20{match.group(2)[:2]}-{match.group(2)[2:4]}-{match.group(2)[4:6]}",
                    "currency": match.group(3),
                    "amount": match.group(4).replace(',', '.'),
                }

            # :61: Statement Lines
            for match in re.finditer(r':61:(\d{6})(\d{4})?([CD])([A-Z]?)(\d+[,.]?\d*)([A-Z]\d{3})(.+?)(?=:61:|:62|:64|:86:|$)', block4, re.DOTALL):
                entry = {
                    "value_date": f"20{match.group(1)[:2]}-{match.group(1)[2:4]}-{match.group(1)[4:6]}",
                    "credit_debit": "CREDIT" if match.group(3) == 'C' else "DEBIT",
                    "amount": match.group(5).replace(',', '.'),
                    "transaction_type": match.group(6),
                    "reference": match.group(7).strip().split('\n')[0] if match.group(7) else None,
                }
                self.result["entries"].append({k: v for k, v in entry.items() if v})

        except Exception as e:
            logger.error(f"Error parsing MT940: {e}")

        return self.result

    def _parse_headers(self, content: str):
        block1 = re.search(r'\{1:([^}]+)\}', content)
        if block1 and len(block1.group(1)) >= 12:
            self.result["payment"]["sender_bic"] = block1.group(1)[3:15] if len(block1.group(1)) >= 15 else block1.group(1)[3:12]


class MT942Parser(MT940Parser):
    """Parser for MT942 - Interim Transaction Report."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "INTERIM_REPORT"
        return result


class MT950Parser(MT940Parser):
    """Parser for MT950 - Statement Message."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "STATEMENT_MESSAGE"
        return result


# =============================================================================
# Domestic Payment Scheme Parsers
# =============================================================================

class SEPASCTParser(Pain001Parser):
    """Parser for SEPA Credit Transfer (SCT) - Based on pain.001."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "SEPA_CREDIT_TRANSFER"
        result["instruction"]["local_instrument"] = "SEPA"
        result["instruction"]["clearing_system"] = "SEPA"
        return result


class SEPASDDParser(Pain008Parser):
    """Parser for SEPA Direct Debit (SDD) - Based on pain.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "SEPA_DIRECT_DEBIT"
        result["instruction"]["local_instrument"] = "SEPA"
        result["instruction"]["clearing_system"] = "SEPA"
        return result


class NACHAACHParser(MessageParser):
    """Parser for NACHA ACH file format."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "ACH"
        self.result["instruction"]["clearing_system"] = "NACHA"

        try:
            lines = content.strip().split('\n')

            for line in lines:
                if len(line) < 94:
                    continue

                record_type = line[0:1]

                if record_type == '1':  # File Header
                    self.result["payment"]["message_id"] = line[13:23].strip()
                    self.result["payment"]["creation_datetime"] = line[23:33].strip()
                    self.result["debtor_agent"]["routing_number"] = line[3:13].strip()

                elif record_type == '5':  # Batch Header
                    self.result["instruction"]["batch_number"] = line[87:94].strip()
                    self.result["instruction"]["service_class_code"] = line[1:4].strip()
                    self.result["debtor"]["name"] = line[4:20].strip()
                    self.result["instruction"]["company_entry_description"] = line[63:73].strip()
                    self.result["instruction"]["effective_entry_date"] = line[69:75].strip()

                elif record_type == '6':  # Entry Detail
                    entry = {
                        "transaction_code": line[1:3].strip(),
                        "receiving_dfi_id": line[3:11].strip(),
                        "check_digit": line[11:12].strip(),
                        "dfi_account_number": line[12:29].strip(),
                        "amount": str(int(line[29:39].strip()) / 100) if line[29:39].strip() else None,
                        "individual_id": line[39:54].strip(),
                        "individual_name": line[54:76].strip(),
                        "trace_number": line[79:94].strip(),
                    }
                    self.result["entries"].append({k: v for k, v in entry.items() if v})

                elif record_type == '9':  # File Control
                    self.result["payment"]["number_of_transactions"] = line[13:21].strip()
                    total_debit = line[31:43].strip()
                    total_credit = line[43:55].strip()
                    if total_debit:
                        self.result["payment"]["total_debit"] = str(int(total_debit) / 100)
                    if total_credit:
                        self.result["payment"]["total_credit"] = str(int(total_credit) / 100)

        except Exception as e:
            logger.error(f"Error parsing NACHA ACH: {e}")

        return self.result


class FedwireParser(MessageParser):
    """Parser for Fedwire message format."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "FEDWIRE"
        self.result["instruction"]["clearing_system"] = "FEDWIRE"

        try:
            # Fedwire uses tag-value format {tag}value
            # Common tags: {1500} Sender, {1510} Sender Reference, {2000} Amount, etc.

            # Amount
            match = re.search(r'\{2000\}(\d+)', content)
            if match:
                self.result["instruction"]["instructed_amount"] = str(int(match.group(1)) / 100)
                self.result["instruction"]["instructed_currency"] = "USD"

            # Sender reference
            match = re.search(r'\{1510\}(.+?)(?=\{|$)', content)
            if match:
                self.result["instruction"]["end_to_end_id"] = match.group(1).strip()

            # Sender ABA
            match = re.search(r'\{3100\}(\d{9})', content)
            if match:
                self.result["debtor_agent"]["routing_number"] = match.group(1)

            # Sender Name
            match = re.search(r'\{3400\}(.+?)(?=\{|$)', content)
            if match:
                self.result["debtor_agent"]["name"] = match.group(1).strip()

            # Receiver ABA
            match = re.search(r'\{3200\}(\d{9})', content)
            if match:
                self.result["creditor_agent"]["routing_number"] = match.group(1)

            # Receiver Name
            match = re.search(r'\{3600\}(.+?)(?=\{|$)', content)
            if match:
                self.result["creditor_agent"]["name"] = match.group(1).strip()

            # Beneficiary
            match = re.search(r'\{4200\}(.+?)(?=\{|$)', content)
            if match:
                self.result["creditor"]["name"] = match.group(1).strip()

            # Originator
            match = re.search(r'\{5000\}(.+?)(?=\{|$)', content)
            if match:
                self.result["debtor"]["name"] = match.group(1).strip()

            # Business Function Code
            match = re.search(r'\{3500\}([A-Z]{3})', content)
            if match:
                self.result["instruction"]["business_function_code"] = match.group(1)

        except Exception as e:
            logger.error(f"Error parsing Fedwire: {e}")

        return self.result


class CHIPSParser(MessageParser):
    """Parser for CHIPS (Clearing House Interbank Payments System) messages."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "CHIPS"
        self.result["instruction"]["clearing_system"] = "CHIPS"

        try:
            # CHIPS uses similar tag format
            # UID
            match = re.search(r'UID:(\d+)', content)
            if match:
                self.result["instruction"]["end_to_end_id"] = match.group(1)

            # Amount
            match = re.search(r'AMT:(\d+)', content)
            if match:
                self.result["instruction"]["instructed_amount"] = str(int(match.group(1)) / 100)
                self.result["instruction"]["instructed_currency"] = "USD"

            # Sending Participant
            match = re.search(r'SPRT:(\d{4})', content)
            if match:
                self.result["debtor_agent"]["chips_participant_id"] = match.group(1)

            # Receiving Participant
            match = re.search(r'RPRT:(\d{4})', content)
            if match:
                self.result["creditor_agent"]["chips_participant_id"] = match.group(1)

        except Exception as e:
            logger.error(f"Error parsing CHIPS: {e}")

        return self.result


class BACSParser(Pain001Parser):
    """Parser for UK BACS - Based on pain.001."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "BACS"
        result["instruction"]["clearing_system"] = "BACS"
        return result


class CHAPSParser(Pacs008Parser):
    """Parser for UK CHAPS - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "CHAPS"
        result["instruction"]["clearing_system"] = "CHAPS"
        return result


class FasterPaymentsParser(Pacs008Parser):
    """Parser for UK Faster Payments - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "FASTER_PAYMENTS"
        result["instruction"]["clearing_system"] = "FPS"
        return result


# =============================================================================
# Real-Time Payment System Parsers
# =============================================================================

class FedNowParser(Pacs008Parser):
    """Parser for FedNow instant payments - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "FEDNOW"
        result["instruction"]["clearing_system"] = "FEDNOW"
        result["instruction"]["instant_payment"] = True
        return result


class RTPParser(Pacs008Parser):
    """Parser for TCH RTP (Real-Time Payments) - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "RTP"
        result["instruction"]["clearing_system"] = "TCH_RTP"
        result["instruction"]["instant_payment"] = True
        return result


class PIXParser(MessageParser):
    """Parser for Brazilian PIX instant payments."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "PIX"
        self.result["instruction"]["clearing_system"] = "PIX"
        self.result["instruction"]["instant_payment"] = True

        try:
            # PIX uses JSON format
            import json
            data = json.loads(content)

            # Transaction ID
            self.result["instruction"]["end_to_end_id"] = data.get("endToEndId", data.get("txId"))

            # Amount
            if "valor" in data:
                self.result["instruction"]["instructed_amount"] = str(data["valor"]["original"])
                self.result["instruction"]["instructed_currency"] = "BRL"

            # Debtor (Pagador)
            if "pagador" in data:
                pagador = data["pagador"]
                self.result["debtor"]["name"] = pagador.get("nome")
                self.result["debtor"]["national_id"] = pagador.get("cpf") or pagador.get("cnpj")

            # Creditor (Recebedor)
            if "recebedor" in data:
                recebedor = data["recebedor"]
                self.result["creditor"]["name"] = recebedor.get("nome")
                self.result["creditor"]["national_id"] = recebedor.get("cpf") or recebedor.get("cnpj")

            # PIX Key
            self.result["creditor_account"]["pix_key"] = data.get("chave")

        except json.JSONDecodeError:
            # Fall back to XML parsing if not JSON
            try:
                root = ET.fromstring(content)
                # Parse as ISO 20022 XML
                iso_parser = Pacs008Parser()
                return iso_parser.parse(content)
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error parsing PIX: {e}")

        return self.result


class NPPParser(Pacs008Parser):
    """Parser for Australian NPP (New Payments Platform) - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "NPP"
        result["instruction"]["clearing_system"] = "NPP_AUSTRALIA"
        result["instruction"]["instant_payment"] = True
        return result


class UPIParser(MessageParser):
    """Parser for India UPI (Unified Payments Interface)."""

    def parse(self, content: str) -> Dict[str, Any]:
        self.result = self._init_result()
        self.result["instruction"]["payment_type"] = "UPI"
        self.result["instruction"]["clearing_system"] = "UPI"
        self.result["instruction"]["instant_payment"] = True

        try:
            # UPI typically uses XML format
            root = ET.fromstring(content)

            # Transaction ID
            txn_id = root.find('.//TxnId') or root.find('.//txnId')
            if txn_id is not None:
                self.result["instruction"]["end_to_end_id"] = txn_id.text

            # Amount
            amount = root.find('.//Amount') or root.find('.//amount')
            if amount is not None:
                self.result["instruction"]["instructed_amount"] = amount.text
                self.result["instruction"]["instructed_currency"] = "INR"

            # Payer VPA
            payer = root.find('.//Payer') or root.find('.//payer')
            if payer is not None:
                self.result["debtor"]["upi_id"] = payer.get('addr') or payer.text
                name = payer.find('.//Name') or payer.find('.//name')
                if name is not None:
                    self.result["debtor"]["name"] = name.text

            # Payee VPA
            payee = root.find('.//Payee') or root.find('.//payee')
            if payee is not None:
                self.result["creditor"]["upi_id"] = payee.get('addr') or payee.text
                name = payee.find('.//Name') or payee.find('.//name')
                if name is not None:
                    self.result["creditor"]["name"] = name.text

        except Exception as e:
            logger.error(f"Error parsing UPI: {e}")

        return self.result


class PayNowParser(Pacs008Parser):
    """Parser for Singapore PayNow - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "PAYNOW"
        result["instruction"]["clearing_system"] = "PAYNOW_SG"
        result["instruction"]["instant_payment"] = True
        return result


class PromptPayParser(Pacs008Parser):
    """Parser for Thailand PromptPay - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "PROMPTPAY"
        result["instruction"]["clearing_system"] = "PROMPTPAY_TH"
        result["instruction"]["instant_payment"] = True
        return result


class InstaPayParser(Pacs008Parser):
    """Parser for Philippines InstaPay - Based on pacs.008."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "INSTAPAY"
        result["instruction"]["clearing_system"] = "INSTAPAY_PH"
        result["instruction"]["instant_payment"] = True
        return result


# =============================================================================
# RTGS System Parsers
# =============================================================================

class TARGET2Parser(Pacs009Parser):
    """Parser for TARGET2 (Trans-European RTGS) - Based on pacs.009."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "TARGET2"
        result["instruction"]["clearing_system"] = "TARGET2"
        result["instruction"]["rtgs"] = True
        return result


class BOJNETParser(Pacs009Parser):
    """Parser for BOJ-NET (Bank of Japan Financial Network) - Based on pacs.009."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "BOJNET"
        result["instruction"]["clearing_system"] = "BOJNET"
        result["instruction"]["rtgs"] = True
        return result


class CNAPSParser(Pacs008Parser):
    """Parser for CNAPS (China National Advanced Payment System)."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "CNAPS"
        result["instruction"]["clearing_system"] = "CNAPS"
        result["instruction"]["rtgs"] = True
        return result


class MEPSPlusParser(Pacs009Parser):
    """Parser for MEPS+ (Singapore MAS Electronic Payment System)."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "MEPS_PLUS"
        result["instruction"]["clearing_system"] = "MEPS_PLUS_SG"
        result["instruction"]["rtgs"] = True
        return result


class RTGSHKParser(Pacs009Parser):
    """Parser for RTGS Hong Kong (CHATS)."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "RTGS_HK"
        result["instruction"]["clearing_system"] = "CHATS"
        result["instruction"]["rtgs"] = True
        return result


class SARIEParser(Pacs009Parser):
    """Parser for SARIE (Saudi Arabian Riyal Interbank Express)."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "SARIE"
        result["instruction"]["clearing_system"] = "SARIE"
        result["instruction"]["rtgs"] = True
        return result


class UAEFTSParser(Pacs009Parser):
    """Parser for UAEFTS (UAE Funds Transfer System)."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "UAEFTS"
        result["instruction"]["clearing_system"] = "UAEFTS"
        result["instruction"]["rtgs"] = True
        return result


class KFTCParser(Pacs009Parser):
    """Parser for KFTC (Korea Financial Telecommunications)."""

    def parse(self, content: str) -> Dict[str, Any]:
        result = super().parse(content)
        result["instruction"]["payment_type"] = "KFTC"
        result["instruction"]["clearing_system"] = "KFTC"
        result["instruction"]["rtgs"] = True
        return result


# Message Type Registry - Comprehensive coverage of 72+ payment standards
MESSAGE_PARSERS = {
    # =========================================================================
    # ISO 20022 - Payments Initiation (pain)
    # =========================================================================
    "pain.001": Pain001Parser,
    "pain.001.001.03": Pain001Parser,
    "pain.001.001.09": Pain001Parser,
    "pain.001.001.11": Pain001Parser,
    "pain.002": Pain002Parser,
    "pain.002.001.03": Pain002Parser,
    "pain.002.001.10": Pain002Parser,
    "pain.007": Pain007Parser,
    "pain.007.001.05": Pain007Parser,
    "pain.008": Pain008Parser,
    "pain.008.001.02": Pain008Parser,
    "pain.008.001.08": Pain008Parser,
    "pain.013": Pain013Parser,
    "pain.013.001.07": Pain013Parser,
    "pain.014": Pain014Parser,
    "pain.014.001.07": Pain014Parser,

    # =========================================================================
    # ISO 20022 - Payments Clearing and Settlement (pacs)
    # =========================================================================
    "pacs.002": Pacs002Parser,
    "pacs.002.001.10": Pacs002Parser,
    "pacs.003": Pacs003Parser,
    "pacs.003.001.08": Pacs003Parser,
    "pacs.004": Pacs004Parser,
    "pacs.004.001.09": Pacs004Parser,
    "pacs.007": Pacs007Parser,
    "pacs.007.001.10": Pacs007Parser,
    "pacs.008": Pacs008Parser,
    "pacs.008.001.08": Pacs008Parser,
    "pacs.008.001.10": Pacs008Parser,
    "pacs.009": Pacs009Parser,
    "pacs.009.001.08": Pacs009Parser,
    "pacs.028": Pacs028Parser,
    "pacs.028.001.03": Pacs028Parser,

    # =========================================================================
    # ISO 20022 - Cash Management (camt)
    # =========================================================================
    "camt.026": Camt026Parser,
    "camt.026.001.07": Camt026Parser,
    "camt.027": Camt027Parser,
    "camt.027.001.07": Camt027Parser,
    "camt.028": Camt028Parser,
    "camt.028.001.09": Camt028Parser,
    "camt.029": Camt029Parser,
    "camt.029.001.09": Camt029Parser,
    "camt.052": Camt052Parser,
    "camt.052.001.08": Camt052Parser,
    "camt.053": Camt053Parser,
    "camt.053.001.08": Camt053Parser,
    "camt.054": Camt054Parser,
    "camt.054.001.08": Camt054Parser,
    "camt.055": Camt055Parser,
    "camt.055.001.08": Camt055Parser,
    "camt.056": Camt056Parser,
    "camt.056.001.08": Camt056Parser,
    "camt.057": Camt057Parser,
    "camt.057.001.06": Camt057Parser,
    "camt.058": Camt058Parser,
    "camt.058.001.06": Camt058Parser,
    "camt.059": Camt059Parser,
    "camt.059.001.06": Camt059Parser,
    "camt.060": Camt060Parser,
    "camt.060.001.05": Camt060Parser,
    "camt.086": Camt086Parser,
    "camt.086.001.03": Camt086Parser,
    "camt.087": Camt087Parser,
    "camt.087.001.06": Camt087Parser,

    # =========================================================================
    # ISO 20022 - Account Management (acmt)
    # =========================================================================
    "acmt.001": Acmt001Parser,
    "acmt.001.001.08": Acmt001Parser,
    "acmt.002": Acmt002Parser,
    "acmt.002.001.07": Acmt002Parser,
    "acmt.003": Acmt003Parser,
    "acmt.003.001.07": Acmt003Parser,
    "acmt.005": Acmt005Parser,
    "acmt.005.001.06": Acmt005Parser,
    "acmt.006": Acmt006Parser,
    "acmt.006.001.07": Acmt006Parser,
    "acmt.007": Acmt007Parser,
    "acmt.007.001.04": Acmt007Parser,

    # =========================================================================
    # SWIFT MT Messages - ALL DECOMMISSIONED by SWIFT Nov 2025
    # Use ISO 20022 equivalents: MT103→pacs.008, MT202→pacs.009, MT940/MT950→camt.053
    # =========================================================================

    # =========================================================================
    # Domestic Payment Schemes
    # =========================================================================
    # SEPA (Europe)
    "sepa_sct": SEPASCTParser,
    "sepa.sct": SEPASCTParser,
    "SEPA_SCT": SEPASCTParser,
    "sepa_credit_transfer": SEPASCTParser,
    "sepa_sdd": SEPASDDParser,
    "sepa.sdd": SEPASDDParser,
    "SEPA_SDD": SEPASDDParser,
    "sepa_direct_debit": SEPASDDParser,

    # US Payment Schemes
    "nacha": NACHAACHParser,
    "nacha_ach": NACHAACHParser,
    "NACHA_ACH": NACHAACHParser,
    "ach": NACHAACHParser,
    "ACH": NACHAACHParser,
    "fedwire": FedwireParser,
    "Fedwire": FedwireParser,
    "FEDWIRE": FedwireParser,
    "chips": CHIPSParser,
    "CHIPS": CHIPSParser,

    # UK Payment Schemes
    "bacs": BACSParser,
    "BACS": BACSParser,
    "chaps": CHAPSParser,
    "CHAPS": CHAPSParser,
    "fps": FasterPaymentsParser,
    "FPS": FasterPaymentsParser,
    "faster_payments": FasterPaymentsParser,
    "FASTER_PAYMENTS": FasterPaymentsParser,

    # =========================================================================
    # Real-Time Payment Systems
    # =========================================================================
    # US Real-Time
    "fednow": FedNowParser,
    "FedNow": FedNowParser,
    "FEDNOW": FedNowParser,
    "rtp": RTPParser,
    "RTP": RTPParser,
    "tch_rtp": RTPParser,

    # Brazil
    "pix": PIXParser,
    "PIX": PIXParser,

    # Australia
    "npp": NPPParser,
    "NPP": NPPParser,
    "osko": NPPParser,

    # India
    "upi": UPIParser,
    "UPI": UPIParser,
    "imps": UPIParser,
    "IMPS": UPIParser,

    # Singapore
    "paynow": PayNowParser,
    "PayNow": PayNowParser,
    "PAYNOW": PayNowParser,

    # Thailand
    "promptpay": PromptPayParser,
    "PromptPay": PromptPayParser,
    "PROMPTPAY": PromptPayParser,

    # Philippines
    "instapay": InstaPayParser,
    "InstaPay": InstaPayParser,
    "INSTAPAY": InstaPayParser,

    # =========================================================================
    # RTGS Systems
    # =========================================================================
    # Europe
    "target2": TARGET2Parser,
    "TARGET2": TARGET2Parser,
    "t2": TARGET2Parser,

    # Japan
    "bojnet": BOJNETParser,
    "BOJNET": BOJNETParser,
    "boj_net": BOJNETParser,

    # China
    "cnaps": CNAPSParser,
    "CNAPS": CNAPSParser,
    "hvps": CNAPSParser,
    "beps": CNAPSParser,

    # Singapore
    "meps": MEPSPlusParser,
    "MEPS": MEPSPlusParser,
    "meps_plus": MEPSPlusParser,
    "MEPS_PLUS": MEPSPlusParser,

    # Hong Kong
    "rtgs_hk": RTGSHKParser,
    "RTGS_HK": RTGSHKParser,
    "chats": RTGSHKParser,
    "CHATS": RTGSHKParser,

    # Saudi Arabia
    "sarie": SARIEParser,
    "SARIE": SARIEParser,

    # UAE
    "uaefts": UAEFTSParser,
    "UAEFTS": UAEFTSParser,

    # Korea
    "kftc": KFTCParser,
    "KFTC": KFTCParser,
    "bok_wire": KFTCParser,
    "BOK_WIRE": KFTCParser,
}


def get_parser_for_message_type(message_type: str) -> Optional[MessageParser]:
    """Get appropriate parser for message type."""
    # Normalize message type
    msg_type = message_type.lower().replace("_", ".").replace("-", ".")

    # Try exact match first
    parser_class = MESSAGE_PARSERS.get(message_type)
    if parser_class:
        return parser_class()

    # Try lowercase
    parser_class = MESSAGE_PARSERS.get(msg_type)
    if parser_class:
        return parser_class()

    # Try prefix match
    for key, parser_class in MESSAGE_PARSERS.items():
        if msg_type.startswith(key.lower()):
            return parser_class()

    # Default to Pain001Parser for unknown types
    logger.warning(f"Unknown message type '{message_type}', using Pain001Parser as default")
    return Pain001Parser()


def parse_message(content: str, message_type: str) -> Dict[str, Any]:
    """
    Parse a payment message and extract CDM fields.

    Args:
        content: Raw message content (XML or SWIFT MT)
        message_type: Message type identifier (e.g., "pain.001", "MT103")

    Returns:
        Dictionary with parsed CDM entities
    """
    parser = get_parser_for_message_type(message_type)
    return parser.parse(content)

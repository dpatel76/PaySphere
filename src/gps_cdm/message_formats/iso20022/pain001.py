"""ISO 20022 pain.001 Parser and Extractor base classes.

pain.001 (Customer Credit Transfer Initiation) is the message type used when
a customer initiates a payment request to their bank. Key characteristics:
- Customer → Bank communication (initiation, not interbank transfer)
- Contains payment instructions with debtor/creditor details
- Used for batch processing of multiple payments
- Different from pacs.008 which is for interbank transfers

Systems using pain.001 or its variants:
- SEPA Credit Transfer (European payments)
- Generic ISO 20022 payment initiation
- Bank proprietary implementations

Reference: ISO 20022 Message Definition Report - pain.001.001.09
"""

from typing import Dict, Any, List, Optional
import json
import logging

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor

logger = logging.getLogger(__name__)


class Pain001Parser(BaseISO20022Parser):
    """Base parser for pain.001 Customer Credit Transfer Initiation messages.

    pain.001 structure:
    - Document
      - CstmrCdtTrfInitn
        - GrpHdr (Group Header)
        - PmtInf (Payment Information) [1..*]
          - CdtTrfTxInf (Credit Transfer Transaction Info) [1..*]

    Note: pain.001 differs from pacs.008 in that:
    - It's a customer→bank message, not bank→bank
    - It has a PmtInf (Payment Information) wrapper
    - The initiating party is specified in GrpHdr
    """

    ROOT_ELEMENT = "CstmrCdtTrfInitn"
    MESSAGE_TYPE = "pain.001"

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse pain.001 Customer Credit Transfer Initiation message.

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pain.001 fields
        """
        root = self._parse_xml(xml_content)

        # Find the CstmrCdtTrfInitn element
        initn = self._find(root, self.ROOT_ELEMENT)
        if initn is None:
            # Check if root IS the message element
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                initn = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pain.001 message")

        return self._parse_customer_credit_transfer(initn)

    def _parse_customer_credit_transfer(self, initn) -> Dict[str, Any]:
        """Parse CstmrCdtTrfInitn element.

        Args:
            initn: CstmrCdtTrfInitn element

        Returns:
            Dict with extracted fields
        """
        result = {
            'isISO20022': True,
            'messageTypeCode': 'pain.001',
        }

        # Extract Group Header (pain.001 specific)
        result.update(self._extract_pain001_group_header(initn))

        # Extract first Payment Information block
        pmt_inf = self._find(initn, 'PmtInf')
        if pmt_inf is not None:
            result.update(self._parse_payment_info(pmt_inf))

        return result

    def _extract_pain001_group_header(self, initn) -> Dict[str, Any]:
        """Extract Group Header specific to pain.001.

        pain.001 GrpHdr contains:
        - MsgId: Message identification
        - CreDtTm: Creation date/time
        - NbOfTxs: Number of transactions
        - CtrlSum: Control sum (total amount)
        - InitgPty: Initiating Party (unique to pain.001)

        Args:
            initn: CstmrCdtTrfInitn element

        Returns:
            Dict with extracted header fields
        """
        result = {}
        grp_hdr = self._find(initn, 'GrpHdr')

        if grp_hdr is None:
            return result

        # Core identification
        result['messageId'] = self._find_text(grp_hdr, 'MsgId')
        result['creationDateTime'] = self._find_text(grp_hdr, 'CreDtTm')
        result['numberOfTransactions'] = self._safe_int(self._find_text(grp_hdr, 'NbOfTxs'))
        result['controlSum'] = self._safe_float(self._find_text(grp_hdr, 'CtrlSum'))

        # Initiating Party (specific to pain.001)
        initg_pty = self._find(grp_hdr, 'InitgPty')
        if initg_pty:
            result.update(self._extract_party(initg_pty, 'initiatingParty'))

        return result

    def _parse_payment_info(self, pmt_inf) -> Dict[str, Any]:
        """Parse PmtInf (Payment Information) element.

        PmtInf is the main container in pain.001 containing:
        - PmtInfId: Payment information identification
        - PmtMtd: Payment method (TRF=Transfer, CHK=Cheque)
        - BtchBookg: Batch booking indicator
        - ReqdExctnDt: Requested execution date
        - Dbtr/DbtrAcct/DbtrAgt: Debtor information (shared across all txs)
        - CdtTrfTxInf: Credit transfer transactions [1..*]

        Args:
            pmt_inf: PmtInf element

        Returns:
            Dict with payment info fields
        """
        result = {}

        # Payment Information identification
        result['paymentInfoId'] = self._find_text(pmt_inf, 'PmtInfId')
        result['paymentMethod'] = self._find_text(pmt_inf, 'PmtMtd')
        result['batchBooking'] = self._find_text(pmt_inf, 'BtchBookg') == 'true'

        # Requested Execution Date (may be nested or direct)
        req_exctn = self._find(pmt_inf, 'ReqdExctnDt')
        if req_exctn is not None:
            result['requestedExecutionDate'] = (
                self._find_text(req_exctn, 'Dt') or
                req_exctn.text
            )

        # Payment Type Information
        pmt_tp_inf = self._find(pmt_inf, 'PmtTpInf')
        if pmt_tp_inf:
            result.update(self._extract_payment_type_info(pmt_tp_inf))

        # Debtor (shared across all transactions in this PmtInf)
        dbtr = self._find(pmt_inf, 'Dbtr')
        if dbtr:
            result.update(self._extract_party(dbtr, 'debtor'))

        # Debtor Account
        dbtr_acct = self._find(pmt_inf, 'DbtrAcct')
        if dbtr_acct:
            result.update(self._extract_account(dbtr_acct, 'debtorAccount'))

        # Debtor Agent
        dbtr_agt = self._find(pmt_inf, 'DbtrAgt')
        if dbtr_agt:
            result.update(self._extract_financial_institution(dbtr_agt, 'debtorAgent'))

        # Charge Bearer (at PmtInf level)
        result['chargeBearer'] = self._find_text(pmt_inf, 'ChrgBr')

        # Ultimate Debtor (if present at PmtInf level)
        ultmt_dbtr = self._find(pmt_inf, 'UltmtDbtr')
        if ultmt_dbtr:
            result.update(self._extract_party(ultmt_dbtr, 'ultimateDebtor'))

        # Extract first Credit Transfer Transaction
        cdt_trf_tx_inf = self._find(pmt_inf, 'CdtTrfTxInf')
        if cdt_trf_tx_inf is not None:
            result.update(self._parse_credit_transfer_tx(cdt_trf_tx_inf))

        return result

    def _parse_credit_transfer_tx(self, cdt_trf: 'ET.Element') -> Dict[str, Any]:
        """Parse CdtTrfTxInf element within pain.001.

        Args:
            cdt_trf: CdtTrfTxInf element

        Returns:
            Dict with transaction fields
        """
        result = {}

        # Payment Identification
        pmt_id = self._find(cdt_trf, 'PmtId')
        if pmt_id:
            result['instructionId'] = self._find_text(pmt_id, 'InstrId')
            result['endToEndId'] = self._find_text(pmt_id, 'EndToEndId')
            result['uetr'] = self._find_text(pmt_id, 'UETR')

        # Payment Type Information (if at transaction level)
        pmt_tp_inf = self._find(cdt_trf, 'PmtTpInf')
        if pmt_tp_inf:
            tx_type_info = self._extract_payment_type_info(pmt_tp_inf)
            # Only add if not already set from PmtInf level
            for key, value in tx_type_info.items():
                if key not in result or result[key] is None:
                    result[key] = value

        # Amount (pain.001 uses Amt/InstdAmt structure)
        amt = self._find(cdt_trf, 'Amt')
        if amt:
            instd_amt = self._find(amt, 'InstdAmt')
            if instd_amt is not None:
                result['amount'] = self._safe_float(instd_amt.text)
                result['currency'] = instd_amt.get('Ccy')

            # Equivalent Amount (for cross-currency)
            eqvt_amt = self._find(amt, 'EqvtAmt')
            if eqvt_amt:
                result['equivalentAmount'] = self._safe_float(self._find_text(eqvt_amt, 'Amt'))
                result['equivalentCurrency'] = self._find_text(eqvt_amt, 'CcyOfTrf')

        # Exchange Rate
        result['exchangeRate'] = self._safe_float(self._find_text(cdt_trf, 'XchgRateInf/XchgRate'))

        # Charge Bearer (at transaction level)
        tx_chrg_br = self._find_text(cdt_trf, 'ChrgBr')
        if tx_chrg_br:
            result['chargeBearer'] = tx_chrg_br

        # Creditor Agent
        cdtr_agt = self._find(cdt_trf, 'CdtrAgt')
        if cdtr_agt:
            result.update(self._extract_financial_institution(cdtr_agt, 'creditorAgent'))

        # Creditor
        cdtr = self._find(cdt_trf, 'Cdtr')
        if cdtr:
            result.update(self._extract_party(cdtr, 'creditor'))

        # Creditor Account
        cdtr_acct = self._find(cdt_trf, 'CdtrAcct')
        if cdtr_acct:
            result.update(self._extract_account(cdtr_acct, 'creditorAccount'))

        # Ultimate Creditor
        ultmt_cdtr = self._find(cdt_trf, 'UltmtCdtr')
        if ultmt_cdtr:
            result.update(self._extract_party(ultmt_cdtr, 'ultimateCreditor'))

        # Intermediary Agent(s)
        intrmy_agt1 = self._find(cdt_trf, 'IntrmyAgt1')
        if intrmy_agt1:
            result.update(self._extract_financial_institution(intrmy_agt1, 'intermediaryAgent1'))

        # Purpose
        purp = self._find(cdt_trf, 'Purp')
        if purp:
            result['purposeCode'] = self._find_text(purp, 'Cd')
            result['purposeProprietary'] = self._find_text(purp, 'Prtry')

        # Remittance Information
        rmt_inf = self._find(cdt_trf, 'RmtInf')
        if rmt_inf:
            result.update(self._extract_remittance_info(rmt_inf))

        # Regulatory Reporting
        rgltry_rptg = self._find(cdt_trf, 'RgltryRptg')
        if rgltry_rptg:
            result.update(self._extract_regulatory_reporting(rgltry_rptg))

        return result


class Pain001Extractor(BaseISO20022Extractor):
    """Base extractor for pain.001 Customer Credit Transfer Initiation.

    Systems inheriting from this:
    - SepaExtractor (SEPA Credit Transfer)
    - Generic ISO 20022 pain.001

    Key differences from Pacs008Extractor:
    - Has InitiatingParty (customer who requested the payment)
    - Has Payment Information wrapper (PmtInf)
    - Payment method field (TRF, CHK, etc.)
    - Batch booking indicator
    """

    MESSAGE_TYPE: str = "pain.001"
    SILVER_TABLE: str = "stg_pain001"
    PARSER_CLASS = Pain001Parser
    DEFAULT_CURRENCY: str = "EUR"
    CLEARING_SYSTEM: str = None

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from parsed pain.001 message.

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

            # Message Header
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'number_of_transactions': msg_content.get('numberOfTransactions'),
            'control_sum': msg_content.get('controlSum'),

            # Initiating Party (unique to pain.001)
            'initiating_party_name': trunc(msg_content.get('initiatingPartyName'), 140),
            'initiating_party_id': trunc(msg_content.get('initiatingPartyOtherId') or msg_content.get('initiatingPartyLei'), 35),
            'initiating_party_id_type': trunc(msg_content.get('initiatingPartyOtherIdScheme'), 35),
            'initiating_party_country': trunc(msg_content.get('initiatingPartyCountry'), 2),

            # Payment Information
            'payment_info_id': trunc(msg_content.get('paymentInfoId'), 35),
            'payment_method': trunc(msg_content.get('paymentMethod'), 3),
            'batch_booking': msg_content.get('batchBooking'),
            'requested_execution_date': msg_content.get('requestedExecutionDate'),

            # Payment Type
            'instruction_priority': trunc(msg_content.get('instructionPriority'), 10),
            'service_level': trunc(msg_content.get('serviceLevelCode'), 35),
            'local_instrument': trunc(msg_content.get('localInstrumentCode'), 35),
            'category_purpose': trunc(msg_content.get('categoryPurposeCode'), 35),

            # Charge Bearer
            'charge_bearer': trunc(msg_content.get('chargeBearer'), 10),

            # Transaction IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'uetr': msg_content.get('uetr'),

            # Amounts
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency') or self.DEFAULT_CURRENCY,
            'equivalent_amount': msg_content.get('equivalentAmount'),
            'equivalent_currency': msg_content.get('equivalentCurrency'),
            'exchange_rate': msg_content.get('exchangeRate'),

            # Debtor
            'debtor_name': trunc(msg_content.get('debtorName'), 140),
            'debtor_street_name': trunc(msg_content.get('debtorStreetName'), 70),
            'debtor_building_number': trunc(msg_content.get('debtorBuildingNumber'), 16),
            'debtor_post_code': trunc(msg_content.get('debtorPostCode'), 16),
            'debtor_town_name': trunc(msg_content.get('debtorTownName'), 35),
            'debtor_country_sub_division': trunc(msg_content.get('debtorCountrySubDivision'), 35),
            'debtor_country': trunc(msg_content.get('debtorCountry'), 2),
            'debtor_id': trunc(msg_content.get('debtorOtherId') or msg_content.get('debtorLei'), 35),
            'debtor_id_type': trunc(msg_content.get('debtorOtherIdScheme'), 35),

            # Debtor Account
            'debtor_account_iban': trunc(msg_content.get('debtorAccountIban'), 34),
            'debtor_account_other': trunc(msg_content.get('debtorAccountOther'), 34),
            'debtor_account_type': trunc(msg_content.get('debtorAccountType'), 10),
            'debtor_account_currency': msg_content.get('debtorAccountCurrency'),

            # Debtor Agent
            'debtor_agent_bic': trunc(msg_content.get('debtorAgentBic'), 11),
            'debtor_agent_name': trunc(msg_content.get('debtorAgentName'), 140),
            'debtor_agent_clearing_system': trunc(msg_content.get('debtorAgentClearingSystemId'), 10),
            'debtor_agent_member_id': trunc(msg_content.get('debtorAgentMemberId'), 35),
            'debtor_agent_country': trunc(msg_content.get('debtorAgentCountry'), 2),

            # Creditor
            'creditor_name': trunc(msg_content.get('creditorName'), 140),
            'creditor_street_name': trunc(msg_content.get('creditorStreetName'), 70),
            'creditor_building_number': trunc(msg_content.get('creditorBuildingNumber'), 16),
            'creditor_post_code': trunc(msg_content.get('creditorPostCode'), 16),
            'creditor_town_name': trunc(msg_content.get('creditorTownName'), 35),
            'creditor_country_sub_division': trunc(msg_content.get('creditorCountrySubDivision'), 35),
            'creditor_country': trunc(msg_content.get('creditorCountry'), 2),
            'creditor_id': trunc(msg_content.get('creditorOtherId') or msg_content.get('creditorLei'), 35),
            'creditor_id_type': trunc(msg_content.get('creditorOtherIdScheme'), 35),

            # Creditor Account
            'creditor_account_iban': trunc(msg_content.get('creditorAccountIban'), 34),
            'creditor_account_other': trunc(msg_content.get('creditorAccountOther'), 34),
            'creditor_account_type': trunc(msg_content.get('creditorAccountType'), 10),
            'creditor_account_currency': msg_content.get('creditorAccountCurrency'),

            # Creditor Agent
            'creditor_agent_bic': trunc(msg_content.get('creditorAgentBic'), 11),
            'creditor_agent_name': trunc(msg_content.get('creditorAgentName'), 140),
            'creditor_agent_clearing_system': trunc(msg_content.get('creditorAgentClearingSystemId'), 10),
            'creditor_agent_member_id': trunc(msg_content.get('creditorAgentMemberId'), 35),
            'creditor_agent_country': trunc(msg_content.get('creditorAgentCountry'), 2),

            # Ultimate Parties
            'ultimate_debtor_name': trunc(msg_content.get('ultimateDebtorName'), 140),
            'ultimate_debtor_id': trunc(msg_content.get('ultimateDebtorOtherId') or msg_content.get('ultimateDebtorLei'), 35),
            'ultimate_debtor_id_type': trunc(msg_content.get('ultimateDebtorOtherIdScheme'), 35),

            'ultimate_creditor_name': trunc(msg_content.get('ultimateCreditorName'), 140),
            'ultimate_creditor_id': trunc(msg_content.get('ultimateCreditorOtherId') or msg_content.get('ultimateCreditorLei'), 35),
            'ultimate_creditor_id_type': trunc(msg_content.get('ultimateCreditorOtherIdScheme'), 35),

            # Purpose
            'purpose_code': trunc(msg_content.get('purposeCode'), 10),
            'purpose_proprietary': trunc(msg_content.get('purposeProprietary'), 35),

            # Remittance
            'remittance_unstructured': msg_content.get('remittanceUnstructured'),
            'referred_doc_type': trunc(msg_content.get('referredDocumentType'), 10),
            'referred_doc_number': trunc(msg_content.get('referredDocumentNumber'), 35),
            'referred_doc_date': msg_content.get('referredDocumentDate'),
            'creditor_reference': trunc(msg_content.get('creditorReference'), 35),

            # Regulatory Reporting
            'regulatory_reporting_indicator': trunc(msg_content.get('regulatoryReportingIndicator'), 10),
            'regulatory_authority_country': trunc(msg_content.get('regulatoryAuthorityCountry'), 2),
            'regulatory_code': trunc(msg_content.get('regulatoryCode'), 10),

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
            'stg_id', 'raw_id', '_batch_id', 'message_id',

            # Timestamps & counts
            'creation_date_time', 'number_of_transactions', 'control_sum',

            # Initiating Party (pain.001 specific)
            'initiating_party_name', 'initiating_party_id',
            'initiating_party_id_type', 'initiating_party_country',

            # Payment Information
            'payment_info_id', 'payment_method', 'batch_booking', 'requested_execution_date',

            # Payment Type
            'instruction_priority', 'service_level', 'local_instrument', 'category_purpose',

            # Charge Bearer
            'charge_bearer',

            # Transaction IDs
            'instruction_id', 'end_to_end_id', 'uetr',

            # Amounts
            'amount', 'currency', 'equivalent_amount', 'equivalent_currency', 'exchange_rate',

            # Debtor
            'debtor_name', 'debtor_street_name', 'debtor_building_number',
            'debtor_post_code', 'debtor_town_name', 'debtor_country_sub_division',
            'debtor_country', 'debtor_id', 'debtor_id_type',

            # Debtor Account
            'debtor_account_iban', 'debtor_account_other',
            'debtor_account_type', 'debtor_account_currency',

            # Debtor Agent
            'debtor_agent_bic', 'debtor_agent_name',
            'debtor_agent_clearing_system', 'debtor_agent_member_id', 'debtor_agent_country',

            # Creditor
            'creditor_name', 'creditor_street_name', 'creditor_building_number',
            'creditor_post_code', 'creditor_town_name', 'creditor_country_sub_division',
            'creditor_country', 'creditor_id', 'creditor_id_type',

            # Creditor Account
            'creditor_account_iban', 'creditor_account_other',
            'creditor_account_type', 'creditor_account_currency',

            # Creditor Agent
            'creditor_agent_bic', 'creditor_agent_name',
            'creditor_agent_clearing_system', 'creditor_agent_member_id', 'creditor_agent_country',

            # Ultimate Parties
            'ultimate_debtor_name', 'ultimate_debtor_id', 'ultimate_debtor_id_type',
            'ultimate_creditor_name', 'ultimate_creditor_id', 'ultimate_creditor_id_type',

            # Purpose
            'purpose_code', 'purpose_proprietary',

            # Remittance
            'remittance_unstructured', 'referred_doc_type', 'referred_doc_number',
            'referred_doc_date', 'creditor_reference',

            # Regulatory
            'regulatory_reporting_indicator', 'regulatory_authority_country', 'regulatory_code',

            # Processing
            'processing_status',
        ]

    def _extract_parties(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract party entities from pain.001 Silver record.

        Adds initiating party handling unique to pain.001.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import PartyData

        # Initiating Party (unique to pain.001)
        if silver_data.get('initiating_party_name'):
            entities.parties.append(PartyData(
                name=silver_data.get('initiating_party_name'),
                role="INITIATING_PARTY",
                party_type='ORGANIZATION' if silver_data.get('initiating_party_id') else 'UNKNOWN',
                country=silver_data.get('initiating_party_country'),
                identification_type=silver_data.get('initiating_party_id_type'),
                identification_number=silver_data.get('initiating_party_id'),
            ))

        # Call parent for standard debtor/creditor
        super()._extract_parties(silver_data, entities)

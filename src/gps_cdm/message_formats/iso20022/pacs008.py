"""ISO 20022 pacs.008 Parser and Extractor base classes.

pacs.008 (FI to FI Customer Credit Transfer) is used by:
- FEDWIRE (US Fed, migrated March 2025)
- CHIPS (US clearing, migrated November 2023)
- CHAPS (UK high-value)
- FPS (UK Faster Payments)
- FEDNOW (US instant)
- RTP (US real-time, TCH)
- NPP (Australia)
- MEPS+ (Singapore)
- UAEFTS (UAE)
- RTGS_HK (Hong Kong)
- INSTAPAY (Philippines)

Each system implements the base pacs.008 schema with their own usage guidelines.
System-specific extractors inherit from Pacs008Extractor and override only
what's different for their clearing network.

Reference: ISO 20022 Message Definition Report - pacs.008.001.08
"""

from typing import Dict, Any, List, Optional
import logging

from .base_parser import BaseISO20022Parser
from .base_extractor import BaseISO20022Extractor

logger = logging.getLogger(__name__)


class Pacs008Parser(BaseISO20022Parser):
    """Base parser for pacs.008 FI to FI Customer Credit Transfer messages.

    Extracts all standard pacs.008 elements. System-specific parsers inherit
    from this class and may add additional extraction logic.

    pacs.008 structure:
    - Document
      - FIToFICstmrCdtTrf
        - GrpHdr (Group Header)
        - CdtTrfTxInf (Credit Transfer Transaction Information) [1..*]
    """

    # Root element for pacs.008 messages
    ROOT_ELEMENT = "FIToFICstmrCdtTrf"
    MESSAGE_TYPE = "pacs.008"

    def parse(self, xml_content: str) -> Dict[str, Any]:
        """Parse pacs.008 FI to FI Customer Credit Transfer message.

        Args:
            xml_content: Raw XML string

        Returns:
            Dict with all extracted pacs.008 fields
        """
        root = self._parse_xml(xml_content)

        # Find the FIToFICstmrCdtTrf element
        fi_transfer = self._find(root, self.ROOT_ELEMENT)
        if fi_transfer is None:
            # Check if root IS the message element
            root_tag = self._strip_ns(root.tag)
            if root_tag == self.ROOT_ELEMENT:
                fi_transfer = root
            else:
                raise ValueError(f"Cannot find {self.ROOT_ELEMENT} element in pacs.008 message")

        return self._parse_fi_to_fi_transfer(fi_transfer)

    def _parse_fi_to_fi_transfer(self, fi_transfer) -> Dict[str, Any]:
        """Parse FIToFICstmrCdtTrf element.

        Args:
            fi_transfer: FIToFICstmrCdtTrf element

        Returns:
            Dict with extracted fields
        """
        result = {
            'isISO20022': True,
            'messageTypeCode': 'pacs.008',
        }

        # Extract Group Header
        result.update(self._extract_group_header(fi_transfer))

        # Extract first Credit Transfer Transaction (for single-transaction messages)
        # Multi-transaction handling done at higher level
        cdt_trf_tx_inf = self._find(fi_transfer, 'CdtTrfTxInf')
        if cdt_trf_tx_inf is not None:
            result.update(self._parse_credit_transfer_tx(cdt_trf_tx_inf))

        return result

    def _parse_credit_transfer_tx(self, cdt_trf: 'ET.Element') -> Dict[str, Any]:
        """Parse CdtTrfTxInf (Credit Transfer Transaction Information) element.

        This is the main transaction-level element containing:
        - PmtId: Payment identification
        - PmtTpInf: Payment type information
        - IntrBkSttlmAmt: Interbank settlement amount
        - Dbtr/DbtrAcct/DbtrAgt: Debtor information
        - Cdtr/CdtrAcct/CdtrAgt: Creditor information
        - IntrmyAgt1/2/3: Intermediary agents
        - RmtInf: Remittance information

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

        # Charge Bearer
        result['chargeBearer'] = self._find_text(cdt_trf, 'ChrgBr')

        # Instructed Amount (if different from settlement amount)
        instd_amt = self._extract_amount(cdt_trf, 'InstdAmt')
        if instd_amt.get('amount'):
            result['instructedAmount'] = instd_amt.get('amount')
            result['instructedCurrency'] = instd_amt.get('currency')

        # Exchange Rate
        result['exchangeRate'] = self._safe_float(self._find_text(cdt_trf, 'XchgRate'))

        # Debtor Agent
        dbtr_agt = self._find(cdt_trf, 'DbtrAgt')
        if dbtr_agt:
            result.update(self._extract_financial_institution(dbtr_agt, 'debtorAgent'))

        # Debtor
        dbtr = self._find(cdt_trf, 'Dbtr')
        if dbtr:
            result.update(self._extract_party(dbtr, 'debtor'))

        # Debtor Account
        dbtr_acct = self._find(cdt_trf, 'DbtrAcct')
        if dbtr_acct:
            result.update(self._extract_account(dbtr_acct, 'debtorAccount'))

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

        # Ultimate Debtor (if present)
        ultmt_dbtr = self._find(cdt_trf, 'UltmtDbtr')
        if ultmt_dbtr:
            result.update(self._extract_party(ultmt_dbtr, 'ultimateDebtor'))

        # Ultimate Creditor (if present)
        ultmt_cdtr = self._find(cdt_trf, 'UltmtCdtr')
        if ultmt_cdtr:
            result.update(self._extract_party(ultmt_cdtr, 'ultimateCreditor'))

        # Intermediary Agents
        intrmy_agt1 = self._find(cdt_trf, 'IntrmyAgt1')
        if intrmy_agt1:
            result.update(self._extract_financial_institution(intrmy_agt1, 'intermediaryAgent1'))

        intrmy_agt2 = self._find(cdt_trf, 'IntrmyAgt2')
        if intrmy_agt2:
            result.update(self._extract_financial_institution(intrmy_agt2, 'intermediaryAgent2'))

        intrmy_agt3 = self._find(cdt_trf, 'IntrmyAgt3')
        if intrmy_agt3:
            result.update(self._extract_financial_institution(intrmy_agt3, 'intermediaryAgent3'))

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

        # Related Remittance Information
        rltd_rmt_inf = self._find(cdt_trf, 'RltdRmtInf')
        if rltd_rmt_inf:
            result['relatedRemittanceType'] = self._find_text(rltd_rmt_inf, 'RmtId')

        return result


class Pacs008Extractor(BaseISO20022Extractor):
    """Base extractor for all pacs.008-based payment systems.

    System-specific extractors (FedwireExtractor, ChipsExtractor, ChapsExtractor, etc.)
    inherit from this class and override only what's different for their system.

    Common pacs.008 patterns:
    - Same GrpHdr structure
    - Same CdtTrfTxInf structure
    - Same party/account/agent extraction
    - Different clearing system codes and defaults
    """

    # Subclasses override these
    MESSAGE_TYPE: str = "pacs.008"
    SILVER_TABLE: str = "stg_iso20022_pacs008"  # Shared ISO 20022 pacs.008 table
    PARSER_CLASS = Pacs008Parser
    DEFAULT_CURRENCY: str = "XXX"
    CLEARING_SYSTEM: str = None

    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from parsed pacs.008 message.

        This extracts the standard pacs.008 fields. System-specific extractors
        can call this via super() and then add/override fields.

        Args:
            msg_content: Parsed message content
            raw_id: Reference to Bronze record
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            Dict with all fields for Silver staging table
        """
        trunc = self.trunc

        # Start with common fields
        silver = self._extract_common_silver_fields(msg_content, raw_id, stg_id, batch_id)

        # Add pacs.008 specific fields
        silver.update({
            # Settlement
            'settlement_priority': trunc(msg_content.get('settlementPriority'), 10),
            'settlement_method': trunc(msg_content.get('settlementMethod'), 10),
            'clearing_system_code': trunc(msg_content.get('clearingSystemCode'), 10),

            # Charge bearer
            'charge_bearer': trunc(msg_content.get('chargeBearer'), 10),

            # Exchange rate (for cross-currency)
            'exchange_rate': msg_content.get('exchangeRate'),
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency'),

            # Instructing/Instructed Agents (header level)
            'instructing_agent_bic': trunc(msg_content.get('instructingAgentBic'), 11),
            'instructing_agent_name': trunc(msg_content.get('instructingAgentName'), 140),
            'instructing_agent_member_id': trunc(msg_content.get('instructingAgentMemberId'), 35),
            'instructing_agent_lei': trunc(msg_content.get('instructingAgentLei'), 20),

            'instructed_agent_bic': trunc(msg_content.get('instructedAgentBic'), 11),
            'instructed_agent_name': trunc(msg_content.get('instructedAgentName'), 140),
            'instructed_agent_member_id': trunc(msg_content.get('instructedAgentMemberId'), 35),
            'instructed_agent_lei': trunc(msg_content.get('instructedAgentLei'), 20),

            # Ultimate parties
            'ultimate_debtor_name': trunc(msg_content.get('ultimateDebtorName'), 140),
            'ultimate_debtor_lei': trunc(msg_content.get('ultimateDebtorLei'), 20),
            'ultimate_debtor_country': trunc(msg_content.get('ultimateDebtorCountry'), 2),

            'ultimate_creditor_name': trunc(msg_content.get('ultimateCreditorName'), 140),
            'ultimate_creditor_lei': trunc(msg_content.get('ultimateCreditorLei'), 20),
            'ultimate_creditor_country': trunc(msg_content.get('ultimateCreditorCountry'), 2),

            # Intermediary Agents
            'intermediary_agent1_bic': trunc(msg_content.get('intermediaryAgent1Bic'), 11),
            'intermediary_agent1_name': trunc(msg_content.get('intermediaryAgent1Name'), 140),
            'intermediary_agent1_member_id': trunc(msg_content.get('intermediaryAgent1MemberId'), 35),

            'intermediary_agent2_bic': trunc(msg_content.get('intermediaryAgent2Bic'), 11),
            'intermediary_agent2_name': trunc(msg_content.get('intermediaryAgent2Name'), 140),
            'intermediary_agent2_member_id': trunc(msg_content.get('intermediaryAgent2MemberId'), 35),

            # Purpose
            'purpose_code': trunc(msg_content.get('purposeCode'), 10),
            'purpose_proprietary': trunc(msg_content.get('purposeProprietary'), 35),

            # Regulatory Reporting
            'regulatory_reporting_indicator': trunc(msg_content.get('regulatoryReportingIndicator'), 10),
            'regulatory_authority_name': trunc(msg_content.get('regulatoryAuthorityName'), 140),
            'regulatory_authority_country': trunc(msg_content.get('regulatoryAuthorityCountry'), 2),
            'regulatory_code': trunc(msg_content.get('regulatoryCode'), 10),
            'regulatory_info': trunc(msg_content.get('regulatoryInfo'), 140),

            # Structured remittance
            'referred_doc_type': trunc(msg_content.get('referredDocumentType'), 10),
            'referred_doc_number': trunc(msg_content.get('referredDocumentNumber'), 35),
            'referred_doc_date': msg_content.get('referredDocumentDate'),
            'referred_doc_amount': msg_content.get('referredDocumentAmount'),
            'referred_doc_currency': msg_content.get('referredDocumentCurrency'),
            'creditor_reference_type': trunc(msg_content.get('creditorReferenceType'), 10),
        })

        return silver

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        This is the standard pacs.008 Silver column list. System-specific
        extractors may override to add format-specific columns.

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
            'settlement_priority', 'settlement_method', 'clearing_system_code',

            # Amount
            'amount', 'currency', 'instructed_amount', 'instructed_currency',
            'exchange_rate', 'charge_bearer',

            # Payment type
            'instruction_priority', 'service_level', 'local_instrument', 'category_purpose',

            # Instructing/Instructed Agents
            'instructing_agent_bic', 'instructing_agent_name',
            'instructing_agent_member_id', 'instructing_agent_lei',
            'instructed_agent_bic', 'instructed_agent_name',
            'instructed_agent_member_id', 'instructed_agent_lei',

            # Debtor
            'debtor_name', 'debtor_street_name', 'debtor_building_number',
            'debtor_post_code', 'debtor_town_name', 'debtor_country_sub_division',
            'debtor_country', 'debtor_lei',

            # Debtor Account
            'debtor_account_iban', 'debtor_account_other',
            'debtor_account_type', 'debtor_account_currency',

            # Debtor Agent
            'debtor_agent_bic', 'debtor_agent_name',
            'debtor_agent_clearing_system_id', 'debtor_agent_member_id',

            # Creditor
            'creditor_name', 'creditor_street_name', 'creditor_building_number',
            'creditor_post_code', 'creditor_town_name', 'creditor_country_sub_division',
            'creditor_country', 'creditor_lei',

            # Creditor Account
            'creditor_account_iban', 'creditor_account_other',
            'creditor_account_type', 'creditor_account_currency',

            # Creditor Agent
            'creditor_agent_bic', 'creditor_agent_name',
            'creditor_agent_clearing_system_id', 'creditor_agent_member_id',

            # Ultimate parties
            'ultimate_debtor_name', 'ultimate_debtor_lei', 'ultimate_debtor_country',
            'ultimate_creditor_name', 'ultimate_creditor_lei', 'ultimate_creditor_country',

            # Intermediary Agents
            'intermediary_agent1_bic', 'intermediary_agent1_name', 'intermediary_agent1_member_id',
            'intermediary_agent2_bic', 'intermediary_agent2_name', 'intermediary_agent2_member_id',

            # Purpose
            'purpose_code', 'purpose_proprietary',

            # Regulatory reporting
            'regulatory_reporting_indicator', 'regulatory_authority_name',
            'regulatory_authority_country', 'regulatory_code', 'regulatory_info',

            # Remittance
            'remittance_unstructured', 'creditor_reference',
            'referred_doc_type', 'referred_doc_number', 'referred_doc_date',
            'referred_doc_amount', 'referred_doc_currency', 'creditor_reference_type',

            # Processing
            'processing_status',
        ]

    def _extract_parties(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract party entities from pacs.008 Silver record.

        Overrides base to add pacs.008 field name mapping.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        # Call parent implementation for standard debtor/creditor
        super()._extract_parties(silver_data, entities)

    def _extract_financial_institutions(self, silver_data: Dict[str, Any], entities) -> None:
        """Extract financial institution entities from pacs.008 Silver record.

        Overrides base to handle pacs.008 specific agent fields including
        intermediary agents.

        Args:
            silver_data: Silver record dict
            entities: GoldEntities to populate
        """
        from ..base import FinancialInstitutionData

        # Debtor Agent
        if silver_data.get('debtor_agent_bic') or silver_data.get('debtor_agent_member_id'):
            entities.financial_institutions.append(self._create_debtor_agent(silver_data))

        # Creditor Agent
        if silver_data.get('creditor_agent_bic') or silver_data.get('creditor_agent_member_id'):
            entities.financial_institutions.append(self._create_creditor_agent(silver_data))

        # Instructing Agent (header level)
        if silver_data.get('instructing_agent_bic') or silver_data.get('instructing_agent_member_id'):
            bic = silver_data.get('instructing_agent_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTING_AGENT",
                name=silver_data.get('instructing_agent_name') or (f"FI_{bic}" if bic else None),
                bic=bic,
                lei=silver_data.get('instructing_agent_lei'),
                clearing_code=silver_data.get('instructing_agent_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Instructed Agent (header level)
        if silver_data.get('instructed_agent_bic') or silver_data.get('instructed_agent_member_id'):
            bic = silver_data.get('instructed_agent_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INSTRUCTED_AGENT",
                name=silver_data.get('instructed_agent_name') or (f"FI_{bic}" if bic else None),
                bic=bic,
                lei=silver_data.get('instructed_agent_lei'),
                clearing_code=silver_data.get('instructed_agent_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Intermediary Agent 1
        if silver_data.get('intermediary_agent1_bic') or silver_data.get('intermediary_agent1_member_id'):
            bic = silver_data.get('intermediary_agent1_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY_AGENT1",
                name=silver_data.get('intermediary_agent1_name') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_code=silver_data.get('intermediary_agent1_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

        # Intermediary Agent 2
        if silver_data.get('intermediary_agent2_bic') or silver_data.get('intermediary_agent2_member_id'):
            bic = silver_data.get('intermediary_agent2_bic')
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY_AGENT2",
                name=silver_data.get('intermediary_agent2_name') or (f"FI_{bic}" if bic else None),
                bic=bic,
                clearing_code=silver_data.get('intermediary_agent2_member_id'),
                clearing_system=self.CLEARING_SYSTEM,
                country=self._derive_country(bic, None),
            ))

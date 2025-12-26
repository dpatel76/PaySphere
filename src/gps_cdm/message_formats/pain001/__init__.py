"""ISO 20022 pain.001 (Customer Credit Transfer Initiation) Extractor."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..base import (
    BaseExtractor,
    ExtractorRegistry,
    GoldEntities,
    PartyData,
    AccountData,
    FinancialInstitutionData,
)


class Pain001Extractor(BaseExtractor):
    """Extractor for ISO 20022 pain.001 messages."""

    MESSAGE_TYPE = "pain.001"
    SILVER_TABLE = "stg_pain001"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw pain.001 content."""
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
        """Extract all Silver layer fields from pain.001 message."""
        trunc = self.trunc

        # Extract nested objects
        initiating_party = msg_content.get('initiatingParty', {})
        pmt_info = msg_content.get('paymentInformation', {})
        debtor = msg_content.get('debtor', {})
        debtor_account = msg_content.get('debtorAccount', {})
        debtor_agent = msg_content.get('debtorAgent', {})
        creditor = msg_content.get('creditor', {})
        creditor_account = msg_content.get('creditorAccount', {})
        creditor_agent = msg_content.get('creditorAgent', {})
        ultimate_debtor = msg_content.get('ultimateDebtor', {})
        ultimate_creditor = msg_content.get('ultimateCreditor', {})
        remittance_info = msg_content.get('remittanceInformation', {})
        structured_remit = remittance_info.get('structured', {}) if remittance_info else {}
        regulatory = msg_content.get('regulatoryReporting', {})

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header (msg_id matches table schema)
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'number_of_transactions': msg_content.get('numberOfTransactions'),
            'control_sum': msg_content.get('controlSum'),

            # Initiating Party
            'initiating_party_name': trunc(initiating_party.get('name'), 140),
            'initiating_party_id': trunc(initiating_party.get('id'), 35),
            'initiating_party_id_type': trunc(initiating_party.get('idType'), 35),
            'initiating_party_country': initiating_party.get('country'),

            # Payment Information
            'payment_info_id': trunc(pmt_info.get('paymentInfoId'), 35),
            'payment_method': pmt_info.get('paymentMethod'),
            'batch_booking': pmt_info.get('batchBooking'),
            'requested_execution_date': pmt_info.get('requestedExecutionDate'),
            'service_level': trunc(pmt_info.get('serviceLevel'), 35),
            'local_instrument': trunc(pmt_info.get('localInstrument'), 35),
            'category_purpose': trunc(pmt_info.get('categoryPurpose'), 35),

            # Debtor (column names match table: debtor_street_name, debtor_town_name)
            'debtor_name': trunc(debtor.get('name'), 140),
            'debtor_street_name': trunc(debtor.get('streetName'), 70),
            'debtor_building_number': trunc(debtor.get('buildingNumber'), 16),
            'debtor_postal_code': trunc(debtor.get('postalCode'), 16),
            'debtor_town_name': trunc(debtor.get('townName'), 35),
            'debtor_country_sub_division': trunc(debtor.get('countrySubDivision'), 35),
            'debtor_country': debtor.get('country'),
            'debtor_id': trunc(debtor.get('id'), 35),
            'debtor_id_type': trunc(debtor.get('idType'), 35),

            # Debtor Account (includes debtor_account_other)
            'debtor_account_iban': trunc(debtor_account.get('iban'), 34),
            'debtor_account_other': trunc(debtor_account.get('other') or debtor_account.get('accountNumber'), 34),
            'debtor_account_currency': debtor_account.get('currency'),
            'debtor_account_type': trunc(debtor_account.get('accountType'), 35),

            # Debtor Agent
            'debtor_agent_bic': debtor_agent.get('bic'),
            'debtor_agent_name': trunc(debtor_agent.get('name'), 140),
            'debtor_agent_clearing_system': trunc(debtor_agent.get('clearingSystem'), 35),
            'debtor_agent_member_id': trunc(debtor_agent.get('memberId'), 35),
            'debtor_agent_country': debtor_agent.get('country'),

            # Instruction
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'uetr': msg_content.get('uetr'),

            # Amounts
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency'),
            'equivalent_amount': msg_content.get('equivalentAmount'),
            'equivalent_currency': msg_content.get('equivalentCurrency'),
            'exchange_rate': msg_content.get('exchangeRate'),

            # Creditor Agent
            'creditor_agent_bic': creditor_agent.get('bic'),
            'creditor_agent_name': trunc(creditor_agent.get('name'), 140),
            'creditor_agent_clearing_system': trunc(creditor_agent.get('clearingSystem'), 35),
            'creditor_agent_member_id': trunc(creditor_agent.get('memberId'), 35),
            'creditor_agent_country': creditor_agent.get('country'),

            # Creditor (column names match table: creditor_street_name, creditor_town_name)
            'creditor_name': trunc(creditor.get('name'), 140),
            'creditor_street_name': trunc(creditor.get('streetName'), 70),
            'creditor_building_number': trunc(creditor.get('buildingNumber'), 16),
            'creditor_postal_code': trunc(creditor.get('postalCode'), 16),
            'creditor_town_name': trunc(creditor.get('townName'), 35),
            'creditor_country_sub_division': trunc(creditor.get('countrySubDivision'), 35),
            'creditor_country': creditor.get('country'),
            'creditor_id': trunc(creditor.get('id'), 35),
            'creditor_id_type': trunc(creditor.get('idType'), 35),

            # Creditor Account
            'creditor_account_iban': trunc(creditor_account.get('iban'), 34),
            'creditor_account_other': trunc(creditor_account.get('other') or creditor_account.get('accountNumber'), 34),
            'creditor_account_currency': creditor_account.get('currency'),
            'creditor_account_type': trunc(creditor_account.get('accountType'), 10),

            # Ultimate Parties
            'ultimate_debtor_name': trunc(ultimate_debtor.get('name'), 140),
            'ultimate_debtor_id': trunc(ultimate_debtor.get('id'), 35),
            'ultimate_debtor_id_type': trunc(ultimate_debtor.get('idType'), 35),
            'ultimate_creditor_name': trunc(ultimate_creditor.get('name'), 140),
            'ultimate_creditor_id': trunc(ultimate_creditor.get('id'), 35),
            'ultimate_creditor_id_type': trunc(ultimate_creditor.get('idType'), 35),

            # Purpose & Charges
            'purpose_code': msg_content.get('purposeCode'),
            'purpose_proprietary': msg_content.get('purposeProprietary'),
            'charge_bearer': msg_content.get('chargeBearer'),

            # Remittance Information (table uses single columns, not broken out)
            'remittance_information': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,
            'structured_remittance': json.dumps(structured_remit) if structured_remit else None,

            # Regulatory Reporting (table uses single JSON column)
            'regulatory_reporting': json.dumps(regulatory) if regulatory else None,
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT.

        Column order matches silver.stg_pain001 table schema exactly.
        Note: _processed_at has a default, so we don't include it.
        """
        return [
            # Core identifiers
            'stg_id', 'raw_id', 'msg_id',
            # Message header
            'creation_date_time', 'number_of_transactions', 'control_sum',
            # Initiating party
            'initiating_party_name', 'initiating_party_id',
            # Payment info
            'payment_info_id', 'payment_method', 'batch_booking', 'requested_execution_date',
            # Debtor
            'debtor_name', 'debtor_street_name', 'debtor_building_number', 'debtor_postal_code',
            'debtor_town_name', 'debtor_country', 'debtor_id', 'debtor_id_type',
            # Debtor account
            'debtor_account_iban', 'debtor_account_other', 'debtor_account_currency',
            # Debtor agent
            'debtor_agent_bic', 'debtor_agent_name', 'debtor_agent_clearing_system', 'debtor_agent_member_id',
            # Instruction
            'instruction_id', 'end_to_end_id', 'uetr',
            # Amounts
            'instructed_amount', 'instructed_currency', 'equivalent_amount', 'equivalent_currency',
            # Creditor agent
            'creditor_agent_bic', 'creditor_agent_name', 'creditor_agent_clearing_system', 'creditor_agent_member_id',
            # Creditor
            'creditor_name', 'creditor_street_name', 'creditor_building_number', 'creditor_postal_code',
            'creditor_town_name', 'creditor_country', 'creditor_id', 'creditor_id_type',
            # Creditor account
            'creditor_account_iban', 'creditor_account_other', 'creditor_account_currency',
            # Purpose & charges
            'purpose_code', 'purpose_proprietary', 'charge_bearer',
            # Remittance & regulatory
            'remittance_information', 'structured_remittance', 'regulatory_reporting',
            # Batch info
            '_batch_id',
            # Extended fields (added later)
            'initiating_party_id_type', 'initiating_party_country',
            'service_level', 'local_instrument', 'category_purpose',
            'debtor_country_sub_division', 'debtor_account_type', 'debtor_agent_country',
            'exchange_rate',
            'creditor_country_sub_division', 'creditor_account_type', 'creditor_agent_country',
            'ultimate_debtor_name', 'ultimate_debtor_id', 'ultimate_debtor_id_type',
            'ultimate_creditor_name', 'ultimate_creditor_id', 'ultimate_creditor_id_type',
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
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from pain.001 message."""
        entities = GoldEntities()

        # Extract nested objects
        debtor = msg_content.get('debtor', {})
        creditor = msg_content.get('creditor', {})
        debtor_account = msg_content.get('debtorAccount', {})
        creditor_account = msg_content.get('creditorAccount', {})
        debtor_agent = msg_content.get('debtorAgent', {})
        creditor_agent = msg_content.get('creditorAgent', {})
        ultimate_debtor = msg_content.get('ultimateDebtor', {})
        ultimate_creditor = msg_content.get('ultimateCreditor', {})
        pmt_info = msg_content.get('paymentInformation', {})

        # Debtor Party
        if debtor.get('name'):
            entities.parties.append(PartyData(
                name=debtor.get('name'),
                role="DEBTOR",
                party_type='ORGANIZATION' if debtor.get('id') else 'UNKNOWN',
                street_name=debtor.get('streetName'),
                building_number=debtor.get('buildingNumber'),
                post_code=debtor.get('postalCode'),
                town_name=debtor.get('townName'),
                country_sub_division=debtor.get('countrySubDivision'),
                country=debtor.get('country'),
                identification_type=debtor.get('idType'),
                identification_number=debtor.get('id'),
            ))

        # Creditor Party
        if creditor.get('name'):
            entities.parties.append(PartyData(
                name=creditor.get('name'),
                role="CREDITOR",
                party_type='ORGANIZATION' if creditor.get('id') else 'UNKNOWN',
                street_name=creditor.get('streetName'),
                building_number=creditor.get('buildingNumber'),
                post_code=creditor.get('postalCode'),
                town_name=creditor.get('townName'),
                country_sub_division=creditor.get('countrySubDivision'),
                country=creditor.get('country'),
                identification_type=creditor.get('idType'),
                identification_number=creditor.get('id'),
            ))

        # Ultimate Debtor Party
        if ultimate_debtor.get('name'):
            entities.parties.append(PartyData(
                name=ultimate_debtor.get('name'),
                role="ULTIMATE_DEBTOR",
                party_type='UNKNOWN',
                identification_type=ultimate_debtor.get('idType'),
                identification_number=ultimate_debtor.get('id'),
            ))

        # Ultimate Creditor Party
        if ultimate_creditor.get('name'):
            entities.parties.append(PartyData(
                name=ultimate_creditor.get('name'),
                role="ULTIMATE_CREDITOR",
                party_type='UNKNOWN',
                identification_type=ultimate_creditor.get('idType'),
                identification_number=ultimate_creditor.get('id'),
            ))

        # Debtor Account
        if debtor_account.get('iban') or debtor_account.get('accountNumber'):
            entities.accounts.append(AccountData(
                account_number=debtor_account.get('iban') or debtor_account.get('accountNumber'),
                role="DEBTOR",
                iban=debtor_account.get('iban'),
                account_type=debtor_account.get('accountType', 'CACC'),
                currency=debtor_account.get('currency', 'XXX'),
            ))

        # Creditor Account
        if creditor_account.get('iban') or creditor_account.get('accountNumber'):
            entities.accounts.append(AccountData(
                account_number=creditor_account.get('iban') or creditor_account.get('accountNumber'),
                role="CREDITOR",
                iban=creditor_account.get('iban'),
                account_type=creditor_account.get('accountType', 'CACC'),
                currency=creditor_account.get('currency', 'XXX'),
            ))

        # Debtor Agent
        if debtor_agent.get('bic') or debtor_agent.get('memberId'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=debtor_agent.get('name'),
                bic=debtor_agent.get('bic'),
                lei=debtor_agent.get('lei'),
                clearing_code=debtor_agent.get('memberId'),
                clearing_system=debtor_agent.get('clearingSystem'),
                country=debtor_agent.get('country', 'XX'),
            ))

        # Creditor Agent
        if creditor_agent.get('bic') or creditor_agent.get('memberId'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=creditor_agent.get('name'),
                bic=creditor_agent.get('bic'),
                lei=creditor_agent.get('lei'),
                clearing_code=creditor_agent.get('memberId'),
                clearing_system=creditor_agent.get('clearingSystem'),
                country=creditor_agent.get('country', 'XX'),
            ))

        # Payment instruction fields
        entities.service_level = pmt_info.get('serviceLevel')
        entities.local_instrument = pmt_info.get('localInstrument')
        entities.category_purpose = pmt_info.get('categoryPurpose')
        entities.exchange_rate = msg_content.get('exchangeRate')

        return entities


# Register the extractor
ExtractorRegistry.register('pain.001', Pain001Extractor())
ExtractorRegistry.register('pain_001', Pain001Extractor())
ExtractorRegistry.register('pain001', Pain001Extractor())

"""ISO 20022 pacs.008 (FI to FI Customer Credit Transfer) Extractor."""

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


class Pacs008Extractor(BaseExtractor):
    """Extractor for ISO 20022 pacs.008 messages."""

    MESSAGE_TYPE = "pacs.008"
    SILVER_TABLE = "stg_pacs008"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw pacs.008 content."""
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
        """Extract all Silver layer fields from pacs.008 message."""
        trunc = self.trunc

        # Extract nested objects
        instructing_agent = msg_content.get('instructingAgent', {})
        instructed_agent = msg_content.get('instructedAgent', {})
        pmt_type_info = msg_content.get('paymentTypeInformation', {})
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

        # Charges can be an array
        charges = msg_content.get('chargesInformation', [])
        charge_amount = charges[0].get('amount') if charges and len(charges) > 0 else None
        charge_currency = charges[0].get('currency') if charges and len(charges) > 0 else None

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            '_ingested_at': datetime.utcnow(),

            # Message Header
            'message_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'number_of_transactions': msg_content.get('numberOfTransactions'),
            'total_interbank_settlement_amount': msg_content.get('totalInterbankSettlementAmount'),
            'interbank_settlement_currency': msg_content.get('interbankSettlementCurrency'),
            'interbank_settlement_date': msg_content.get('interbankSettlementDate'),
            'settlement_method': msg_content.get('settlementMethod'),
            'clearing_system': trunc(msg_content.get('clearingSystem'), 35),

            # Instructing/Instructed Agents
            'instructing_agent_bic': instructing_agent.get('bic'),
            'instructing_agent_name': trunc(instructing_agent.get('name'), 140),
            'instructing_agent_lei': trunc(instructing_agent.get('lei'), 20),
            'instructing_agent_country': instructing_agent.get('country'),
            'instructed_agent_bic': instructed_agent.get('bic'),
            'instructed_agent_name': trunc(instructed_agent.get('name'), 140),
            'instructed_agent_lei': trunc(instructed_agent.get('lei'), 20),
            'instructed_agent_country': instructed_agent.get('country'),

            # Payment Type Information
            'instruction_priority': pmt_type_info.get('instructionPriority'),
            'clearing_channel': trunc(pmt_type_info.get('clearingChannel'), 35),
            'service_level': trunc(pmt_type_info.get('serviceLevel'), 35),
            'local_instrument': trunc(pmt_type_info.get('localInstrument'), 35),
            'category_purpose': trunc(pmt_type_info.get('categoryPurpose'), 35),

            # Transaction IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),
            'clearing_system_reference': trunc(msg_content.get('clearingSystemReference'), 35),

            # Amounts
            'interbank_settlement_amount': msg_content.get('interbankSettlementAmount'),
            'interbank_settlement_amount_currency': msg_content.get('interbankSettlementAmountCurrency'),
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency'),
            'exchange_rate': msg_content.get('exchangeRate'),
            'charge_bearer': msg_content.get('chargeBearer'),
            'charge_amount': charge_amount,
            'charge_currency': charge_currency,

            # Debtor
            'debtor_name': trunc(debtor.get('name'), 140),
            'debtor_street_name': trunc(debtor.get('streetName'), 70),
            'debtor_building_number': trunc(debtor.get('buildingNumber'), 16),
            'debtor_postal_code': trunc(debtor.get('postalCode'), 16),
            'debtor_town_name': trunc(debtor.get('townName'), 35),
            'debtor_country_sub_division': trunc(debtor.get('countrySubDivision'), 35),
            'debtor_country': debtor.get('country'),
            'debtor_id': trunc(debtor.get('id'), 35),
            'debtor_id_type': trunc(debtor.get('idType'), 35),

            # Debtor Account
            'debtor_account_iban': trunc(debtor_account.get('iban'), 34),
            'debtor_account_currency': debtor_account.get('currency'),
            'debtor_account_type': trunc(debtor_account.get('accountType'), 10),

            # Debtor Agent
            'debtor_agent_bic': debtor_agent.get('bic'),
            'debtor_agent_name': trunc(debtor_agent.get('name'), 140),
            'debtor_agent_clearing_system_member_id': trunc(debtor_agent.get('clearingSystemMemberId'), 35),
            'debtor_agent_lei': trunc(debtor_agent.get('lei'), 20),

            # Creditor Agent
            'creditor_agent_bic': creditor_agent.get('bic'),
            'creditor_agent_name': trunc(creditor_agent.get('name'), 140),
            'creditor_agent_clearing_system_member_id': trunc(creditor_agent.get('clearingSystemMemberId'), 35),
            'creditor_agent_lei': trunc(creditor_agent.get('lei'), 20),

            # Creditor
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
            'creditor_account_currency': creditor_account.get('currency'),
            'creditor_account_type': trunc(creditor_account.get('accountType'), 10),

            # Ultimate Parties
            'ultimate_debtor_name': trunc(ultimate_debtor.get('name'), 140),
            'ultimate_debtor_id': trunc(ultimate_debtor.get('id'), 35),
            'ultimate_debtor_id_type': trunc(ultimate_debtor.get('idType'), 35),
            'ultimate_creditor_name': trunc(ultimate_creditor.get('name'), 140),
            'ultimate_creditor_id': trunc(ultimate_creditor.get('id'), 35),
            'ultimate_creditor_id_type': trunc(ultimate_creditor.get('idType'), 35),

            # Purpose
            'purpose_code': msg_content.get('purposeCode'),

            # Remittance Information
            'remittance_unstructured': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,
            'remittance_creditor_ref': trunc(structured_remit.get('creditorReference'), 35),
            'remittance_doc_type': trunc(structured_remit.get('documentType'), 35),
            'remittance_doc_number': trunc(structured_remit.get('documentNumber'), 35),
            'remittance_doc_date': structured_remit.get('documentDate'),

            # Regulatory Reporting
            'regulatory_indicator': regulatory.get('indicator'),
            'regulatory_authority_name': trunc(regulatory.get('authorityName'), 140),
            'regulatory_authority_country': regulatory.get('authorityCountry'),
            'regulatory_code': trunc(regulatory.get('code'), 10),
            'regulatory_amount': regulatory.get('amount'),
            'regulatory_currency': regulatory.get('currency'),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id', '_ingested_at',
            'message_id', 'creation_date_time', 'number_of_transactions',
            'total_interbank_settlement_amount', 'interbank_settlement_currency',
            'interbank_settlement_date', 'settlement_method', 'clearing_system',
            'instructing_agent_bic', 'instructing_agent_name', 'instructing_agent_lei', 'instructing_agent_country',
            'instructed_agent_bic', 'instructed_agent_name', 'instructed_agent_lei', 'instructed_agent_country',
            'instruction_priority', 'clearing_channel', 'service_level', 'local_instrument', 'category_purpose',
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr', 'clearing_system_reference',
            'interbank_settlement_amount', 'interbank_settlement_amount_currency',
            'instructed_amount', 'instructed_currency', 'exchange_rate',
            'charge_bearer', 'charge_amount', 'charge_currency',
            'debtor_name', 'debtor_street_name', 'debtor_building_number', 'debtor_postal_code',
            'debtor_town_name', 'debtor_country_sub_division', 'debtor_country', 'debtor_id', 'debtor_id_type',
            'debtor_account_iban', 'debtor_account_currency', 'debtor_account_type',
            'debtor_agent_bic', 'debtor_agent_name', 'debtor_agent_clearing_system_member_id', 'debtor_agent_lei',
            'creditor_agent_bic', 'creditor_agent_name', 'creditor_agent_clearing_system_member_id', 'creditor_agent_lei',
            'creditor_name', 'creditor_street_name', 'creditor_building_number', 'creditor_postal_code',
            'creditor_town_name', 'creditor_country_sub_division', 'creditor_country', 'creditor_id', 'creditor_id_type',
            'creditor_account_iban', 'creditor_account_currency', 'creditor_account_type',
            'ultimate_debtor_name', 'ultimate_debtor_id', 'ultimate_debtor_id_type',
            'ultimate_creditor_name', 'ultimate_creditor_id', 'ultimate_creditor_id_type',
            'purpose_code',
            'remittance_unstructured', 'remittance_creditor_ref', 'remittance_doc_type',
            'remittance_doc_number', 'remittance_doc_date',
            'regulatory_indicator', 'regulatory_authority_name', 'regulatory_authority_country',
            'regulatory_code', 'regulatory_amount', 'regulatory_currency',
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
        """Extract Gold layer entities from pacs.008 message."""
        entities = GoldEntities()

        # Extract nested objects
        instructing_agent = msg_content.get('instructingAgent', {})
        instructed_agent = msg_content.get('instructedAgent', {})
        pmt_type_info = msg_content.get('paymentTypeInformation', {})
        debtor = msg_content.get('debtor', {})
        debtor_account = msg_content.get('debtorAccount', {})
        debtor_agent = msg_content.get('debtorAgent', {})
        creditor = msg_content.get('creditor', {})
        creditor_account = msg_content.get('creditorAccount', {})
        creditor_agent = msg_content.get('creditorAgent', {})
        ultimate_debtor = msg_content.get('ultimateDebtor', {})
        ultimate_creditor = msg_content.get('ultimateCreditor', {})

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

        # Instructing Agent (Debtor Agent)
        if instructing_agent.get('bic') or debtor_agent.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=instructing_agent.get('name') or debtor_agent.get('name'),
                bic=instructing_agent.get('bic') or debtor_agent.get('bic'),
                lei=instructing_agent.get('lei') or debtor_agent.get('lei'),
                clearing_code=debtor_agent.get('clearingSystemMemberId'),
                country=instructing_agent.get('country', 'XX'),
            ))

        # Instructed Agent (Creditor Agent)
        if instructed_agent.get('bic') or creditor_agent.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=instructed_agent.get('name') or creditor_agent.get('name'),
                bic=instructed_agent.get('bic') or creditor_agent.get('bic'),
                lei=instructed_agent.get('lei') or creditor_agent.get('lei'),
                clearing_code=creditor_agent.get('clearingSystemMemberId'),
                country=instructed_agent.get('country', 'XX'),
            ))

        # Payment instruction fields
        entities.service_level = pmt_type_info.get('serviceLevel')
        entities.local_instrument = pmt_type_info.get('localInstrument')
        entities.category_purpose = pmt_type_info.get('categoryPurpose')
        entities.exchange_rate = msg_content.get('exchangeRate')

        return entities


# Register the extractor
ExtractorRegistry.register('pacs.008', Pacs008Extractor())
ExtractorRegistry.register('pacs_008', Pacs008Extractor())
ExtractorRegistry.register('pacs008', Pacs008Extractor())

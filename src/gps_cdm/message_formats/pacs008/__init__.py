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
        """Extract all Silver layer fields from pacs.008 message - matches DB schema exactly."""
        trunc = self.trunc

        # Extract nested objects
        instructing_agent = msg_content.get('instructingAgent', {}) or {}
        instructed_agent = msg_content.get('instructedAgent', {}) or {}
        pmt_type_info = msg_content.get('paymentTypeInformation', {}) or {}
        debtor = msg_content.get('debtor', {}) or {}
        debtor_account = msg_content.get('debtorAccount', {}) or {}
        debtor_agent = msg_content.get('debtorAgent', {}) or {}
        creditor = msg_content.get('creditor', {}) or {}
        creditor_account = msg_content.get('creditorAccount', {}) or {}
        creditor_agent = msg_content.get('creditorAgent', {}) or {}
        ultimate_debtor = msg_content.get('ultimateDebtor', {}) or {}
        ultimate_creditor = msg_content.get('ultimateCreditor', {}) or {}
        remittance_info = msg_content.get('remittanceInformation', {}) or {}
        structured_remit = remittance_info.get('structured', {}) if remittance_info else {}
        regulatory = msg_content.get('regulatoryReporting', {}) or {}

        # Charges can be an array
        charges = msg_content.get('chargesInformation', [])
        charges_amount = charges[0].get('amount') if charges and len(charges) > 0 else None
        charges_currency = charges[0].get('currency') if charges and len(charges) > 0 else None

        # Build debtor/creditor address from components
        debtor_address_parts = [
            debtor.get('streetName'),
            debtor.get('buildingNumber'),
            debtor.get('townName'),
            debtor.get('postalCode'),
            debtor.get('countrySubDivision'),
        ]
        debtor_address = ', '.join([p for p in debtor_address_parts if p])

        creditor_address_parts = [
            creditor.get('streetName'),
            creditor.get('buildingNumber'),
            creditor.get('townName'),
            creditor.get('postalCode'),
            creditor.get('countrySubDivision'),
        ]
        creditor_address = ', '.join([p for p in creditor_address_parts if p])

        # Structured remittance as JSON
        structured_remittance = json.dumps(structured_remit) if structured_remit else None

        # Regulatory reporting as JSON
        regulatory_reporting = json.dumps(regulatory) if regulatory else None

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,

            # Message Header - uses 'msg_id' not 'message_id'
            'msg_id': trunc(msg_content.get('messageId'), 35),
            'creation_date_time': msg_content.get('creationDateTime'),
            'number_of_transactions': msg_content.get('numberOfTransactions'),
            'settlement_method': msg_content.get('settlementMethod'),
            'clearing_system': trunc(msg_content.get('clearingSystem'), 35),
            'interbank_settlement_date': msg_content.get('interbankSettlementDate'),
            'total_interbank_settlement_amount': msg_content.get('totalInterbankSettlementAmount'),
            'total_interbank_settlement_currency': msg_content.get('totalInterbankSettlementCurrency') or msg_content.get('interbankSettlementCurrency'),

            # Instructing/Instructed Agents
            'instructing_agent_bic': instructing_agent.get('bic'),
            'instructed_agent_bic': instructed_agent.get('bic'),

            # Transaction IDs
            'instruction_id': trunc(msg_content.get('instructionId'), 35),
            'end_to_end_id': trunc(msg_content.get('endToEndId'), 35),
            'transaction_id': trunc(msg_content.get('transactionId'), 35),
            'uetr': msg_content.get('uetr'),
            'clearing_system_reference': trunc(msg_content.get('clearingSystemReference'), 35),

            # Amounts
            'interbank_settlement_amount': msg_content.get('interbankSettlementAmount'),
            'interbank_settlement_currency': msg_content.get('interbankSettlementAmountCurrency') or msg_content.get('interbankSettlementCurrency'),
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency'),
            'exchange_rate': msg_content.get('exchangeRate'),
            'charge_bearer': msg_content.get('chargeBearer'),
            'charges_amount': charges_amount,
            'charges_currency': charges_currency,

            # Debtor
            'debtor_name': trunc(debtor.get('name'), 140),
            'debtor_address': trunc(debtor_address, 140) if debtor_address else None,
            'debtor_country': debtor.get('country'),
            'debtor_account_iban': trunc(debtor_account.get('iban'), 34),
            'debtor_agent_bic': debtor_agent.get('bic'),

            # Creditor
            'creditor_name': trunc(creditor.get('name'), 140),
            'creditor_address': trunc(creditor_address, 140) if creditor_address else None,
            'creditor_country': creditor.get('country'),
            'creditor_account_iban': trunc(creditor_account.get('iban'), 34),
            'creditor_agent_bic': creditor_agent.get('bic'),

            # Purpose
            'purpose_code': msg_content.get('purposeCode'),

            # Remittance Information - single column 'remittance_info'
            'remittance_info': trunc(remittance_info.get('unstructured'), 140) if remittance_info else None,

            # Ultimate Parties
            'ultimate_debtor_name': trunc(ultimate_debtor.get('name'), 140),
            'ultimate_creditor_name': trunc(ultimate_creditor.get('name'), 140),

            # Intermediary Agents
            'intermediary_agent_1_bic': msg_content.get('intermediaryAgent1', {}).get('bic') if msg_content.get('intermediaryAgent1') else None,
            'intermediary_agent_2_bic': msg_content.get('intermediaryAgent2', {}).get('bic') if msg_content.get('intermediaryAgent2') else None,
            'intermediary_agent_3_bic': msg_content.get('intermediaryAgent3', {}).get('bic') if msg_content.get('intermediaryAgent3') else None,

            # Structured remittance and regulatory as JSON
            'structured_remittance': structured_remittance,
            'regulatory_reporting': regulatory_reporting,

            # Extended agent fields
            'instructing_agent_name': trunc(instructing_agent.get('name'), 140),
            'instructing_agent_lei': trunc(instructing_agent.get('lei'), 20),
            'instructing_agent_country': instructing_agent.get('country'),
            'instructed_agent_name': trunc(instructed_agent.get('name'), 140),
            'instructed_agent_lei': trunc(instructed_agent.get('lei'), 20),
            'instructed_agent_country': instructed_agent.get('country'),

            # Payment Type Information
            'instruction_priority': pmt_type_info.get('instructionPriority'),
            'clearing_channel': trunc(pmt_type_info.get('clearingChannel'), 35),
            'service_level': trunc(pmt_type_info.get('serviceLevel'), 35),
            'local_instrument': trunc(pmt_type_info.get('localInstrument'), 35),
            'category_purpose': trunc(pmt_type_info.get('categoryPurpose'), 35),

            # Debtor address components
            'debtor_street_name': trunc(debtor.get('streetName'), 70),
            'debtor_building_number': trunc(debtor.get('buildingNumber'), 16),
            'debtor_postal_code': trunc(debtor.get('postalCode'), 16),
            'debtor_town_name': trunc(debtor.get('townName'), 35),
            'debtor_country_sub_division': trunc(debtor.get('countrySubDivision'), 35),
            'debtor_id': trunc(debtor.get('id'), 35),
            'debtor_id_type': trunc(debtor.get('idType'), 35),
            'debtor_account_currency': debtor_account.get('currency'),
            'debtor_account_type': trunc(debtor_account.get('accountType'), 10),
            'debtor_agent_name': trunc(debtor_agent.get('name'), 140),
            'debtor_agent_clearing_member_id': trunc(debtor_agent.get('clearingSystemMemberId'), 35),
            'debtor_agent_lei': trunc(debtor_agent.get('lei'), 20),

            # Creditor Agent extended
            'creditor_agent_name': trunc(creditor_agent.get('name'), 140),
            'creditor_agent_clearing_member_id': trunc(creditor_agent.get('clearingSystemMemberId'), 35),
            'creditor_agent_lei': trunc(creditor_agent.get('lei'), 20),

            # Creditor address components
            'creditor_street_name': trunc(creditor.get('streetName'), 70),
            'creditor_building_number': trunc(creditor.get('buildingNumber'), 16),
            'creditor_postal_code': trunc(creditor.get('postalCode'), 16),
            'creditor_town_name': trunc(creditor.get('townName'), 35),
            'creditor_country_sub_division': trunc(creditor.get('countrySubDivision'), 35),
            'creditor_id': trunc(creditor.get('id'), 35),
            'creditor_id_type': trunc(creditor.get('idType'), 35),
            'creditor_account_currency': creditor_account.get('currency'),
            'creditor_account_type': trunc(creditor_account.get('accountType'), 10),

            # Ultimate parties IDs
            'ultimate_debtor_id': trunc(ultimate_debtor.get('id'), 35),
            'ultimate_debtor_id_type': trunc(ultimate_debtor.get('idType'), 35),
            'ultimate_creditor_id': trunc(ultimate_creditor.get('id'), 35),
            'ultimate_creditor_id_type': trunc(ultimate_creditor.get('idType'), 35),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT - matches DB schema exactly."""
        return [
            'stg_id', 'raw_id', '_batch_id',
            # Message header
            'msg_id', 'creation_date_time', 'number_of_transactions',
            'settlement_method', 'clearing_system', 'interbank_settlement_date',
            'total_interbank_settlement_amount', 'total_interbank_settlement_currency',
            # Agents
            'instructing_agent_bic', 'instructed_agent_bic',
            # Transaction IDs
            'instruction_id', 'end_to_end_id', 'transaction_id', 'uetr', 'clearing_system_reference',
            # Amounts
            'interbank_settlement_amount', 'interbank_settlement_currency',
            'instructed_amount', 'instructed_currency', 'exchange_rate',
            'charge_bearer', 'charges_amount', 'charges_currency',
            # Debtor
            'debtor_name', 'debtor_address', 'debtor_country',
            'debtor_account_iban', 'debtor_agent_bic',
            # Creditor
            'creditor_name', 'creditor_address', 'creditor_country',
            'creditor_account_iban', 'creditor_agent_bic',
            # Purpose and remittance
            'purpose_code', 'remittance_info',
            # Ultimate parties
            'ultimate_debtor_name', 'ultimate_creditor_name',
            # Intermediary agents
            'intermediary_agent_1_bic', 'intermediary_agent_2_bic', 'intermediary_agent_3_bic',
            # JSON columns
            'structured_remittance', 'regulatory_reporting',
            # Extended agent info
            'instructing_agent_name', 'instructing_agent_lei', 'instructing_agent_country',
            'instructed_agent_name', 'instructed_agent_lei', 'instructed_agent_country',
            # Payment type info
            'instruction_priority', 'clearing_channel', 'service_level', 'local_instrument', 'category_purpose',
            # Debtor details
            'debtor_street_name', 'debtor_building_number', 'debtor_postal_code',
            'debtor_town_name', 'debtor_country_sub_division',
            'debtor_id', 'debtor_id_type',
            'debtor_account_currency', 'debtor_account_type',
            'debtor_agent_name', 'debtor_agent_clearing_member_id', 'debtor_agent_lei',
            # Creditor agent details
            'creditor_agent_name', 'creditor_agent_clearing_member_id', 'creditor_agent_lei',
            # Creditor details
            'creditor_street_name', 'creditor_building_number', 'creditor_postal_code',
            'creditor_town_name', 'creditor_country_sub_division',
            'creditor_id', 'creditor_id_type',
            'creditor_account_currency', 'creditor_account_type',
            # Ultimate party IDs
            'ultimate_debtor_id', 'ultimate_debtor_id_type',
            'ultimate_creditor_id', 'ultimate_creditor_id_type',
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
                account_type=debtor_account.get('accountType') or 'CACC',
                currency=debtor_account.get('currency') or 'XXX',
            ))

        # Creditor Account
        if creditor_account.get('iban') or creditor_account.get('accountNumber'):
            entities.accounts.append(AccountData(
                account_number=creditor_account.get('iban') or creditor_account.get('accountNumber'),
                role="CREDITOR",
                iban=creditor_account.get('iban'),
                account_type=creditor_account.get('accountType') or 'CACC',
                currency=creditor_account.get('currency') or 'XXX',
            ))

        # Instructing Agent (Debtor Agent)
        if instructing_agent.get('bic') or debtor_agent.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=instructing_agent.get('name') or debtor_agent.get('name'),
                bic=instructing_agent.get('bic') or debtor_agent.get('bic'),
                lei=instructing_agent.get('lei') or debtor_agent.get('lei'),
                clearing_code=debtor_agent.get('clearingSystemMemberId'),
                country=instructing_agent.get('country') or 'XX',
            ))

        # Instructed Agent (Creditor Agent)
        if instructed_agent.get('bic') or creditor_agent.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=instructed_agent.get('name') or creditor_agent.get('name'),
                bic=instructed_agent.get('bic') or creditor_agent.get('bic'),
                lei=instructed_agent.get('lei') or creditor_agent.get('lei'),
                clearing_code=creditor_agent.get('clearingSystemMemberId'),
                country=instructed_agent.get('country') or 'XX',
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

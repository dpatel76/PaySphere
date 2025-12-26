"""Fedwire (US RTGS) Extractor."""

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


class FedwireExtractor(BaseExtractor):
    """Extractor for Fedwire messages."""

    MESSAGE_TYPE = "FEDWIRE"
    SILVER_TABLE = "stg_fedwire"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw Fedwire content."""
        msg_id = raw_content.get('messageId', '') or raw_content.get('imad', '')
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
        """Extract all Silver layer fields from Fedwire message."""
        trunc = self.trunc

        # Extract nested objects
        sender = msg_content.get('sender', {})
        sender_addr = sender.get('address', {}) if sender else {}
        receiver = msg_content.get('receiver', {})
        receiver_addr = receiver.get('address', {}) if receiver else {}
        originator = msg_content.get('originator', {})
        originator_addr = originator.get('address', {}) if originator else {}
        beneficiary = msg_content.get('beneficiary', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        beneficiary_bank = msg_content.get('beneficiaryBank', {})
        instructing_bank = msg_content.get('instructingBank', {})
        intermediary_bank = msg_content.get('intermediaryBank', {})

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            '_ingested_at': datetime.utcnow(),

            # Message Header
            'message_id': trunc(msg_content.get('messageId'), 35),
            'type_code': trunc(msg_content.get('typeCode'), 4),
            'subtype_code': trunc(msg_content.get('subtypeCode'), 4),
            'imad': trunc(msg_content.get('imad'), 22),
            'omad': trunc(msg_content.get('omad'), 22),
            'input_cycle_date': msg_content.get('inputCycleDate'),
            'input_source': trunc(msg_content.get('inputSource'), 8),
            'input_sequence_number': trunc(msg_content.get('inputSequenceNumber'), 6),

            # Amount & Currency
            'amount': msg_content.get('amount'),
            'currency': msg_content.get('currency', 'USD'),
            'instructed_amount': msg_content.get('instructedAmount'),
            'instructed_currency': msg_content.get('instructedCurrency', 'USD'),

            # References
            'sender_reference': trunc(msg_content.get('senderReference'), 16),
            'previous_message_id': trunc(msg_content.get('previousMessageId'), 22),
            'business_function_code': trunc(msg_content.get('businessFunctionCode'), 3),
            'beneficiary_reference': trunc(msg_content.get('beneficiaryReference'), 16),

            # Sender FI
            'sender_routing_number': trunc(sender.get('routingNumber'), 9),
            'sender_name': trunc(sender.get('name'), 140),
            'sender_short_name': trunc(sender.get('shortName'), 35),
            'sender_bic': sender.get('bic'),
            'sender_lei': trunc(sender.get('lei'), 20),
            'sender_address_line1': trunc(sender_addr.get('line1'), 140),
            'sender_address_line2': trunc(sender_addr.get('line2'), 140),
            'sender_city': trunc(sender_addr.get('city'), 35),
            'sender_state': trunc(sender_addr.get('state'), 2),
            'sender_zip_code': trunc(sender_addr.get('zipCode'), 10),
            'sender_country': sender_addr.get('country', 'US'),

            # Receiver FI
            'receiver_routing_number': trunc(receiver.get('routingNumber'), 9),
            'receiver_name': trunc(receiver.get('name'), 140),
            'receiver_short_name': trunc(receiver.get('shortName'), 35),
            'receiver_bic': receiver.get('bic'),
            'receiver_lei': trunc(receiver.get('lei'), 20),
            'receiver_address_line1': trunc(receiver_addr.get('line1'), 140),
            'receiver_address_line2': trunc(receiver_addr.get('line2'), 140),
            'receiver_city': trunc(receiver_addr.get('city'), 35),
            'receiver_state': trunc(receiver_addr.get('state'), 2),
            'receiver_zip_code': trunc(receiver_addr.get('zipCode'), 10),
            'receiver_country': receiver_addr.get('country', 'US'),

            # Originator
            'originator_name': trunc(originator.get('name'), 140),
            'originator_account_number': trunc(originator.get('accountNumber'), 35),
            'originator_address_line1': trunc(originator_addr.get('line1'), 140),
            'originator_address_line2': trunc(originator_addr.get('line2'), 140),
            'originator_city': trunc(originator_addr.get('city'), 35),
            'originator_state': trunc(originator_addr.get('state'), 2),
            'originator_zip_code': trunc(originator_addr.get('zipCode'), 10),
            'originator_country': originator_addr.get('country', 'US'),
            'originator_identifier': trunc(originator.get('identifier'), 35),
            'originator_identifier_type': trunc(originator.get('identifierType'), 10),

            # Originator Option F (additional party info)
            'originator_option_f': trunc(msg_content.get('originatorOptionF'), 140),

            # Beneficiary
            'beneficiary_name': trunc(beneficiary.get('name'), 140),
            'beneficiary_account_number': trunc(beneficiary.get('accountNumber'), 35),
            'beneficiary_address_line1': trunc(beneficiary_addr.get('line1'), 140),
            'beneficiary_address_line2': trunc(beneficiary_addr.get('line2'), 140),
            'beneficiary_city': trunc(beneficiary_addr.get('city'), 35),
            'beneficiary_state': trunc(beneficiary_addr.get('state'), 2),
            'beneficiary_zip_code': trunc(beneficiary_addr.get('zipCode'), 10),
            'beneficiary_country': beneficiary_addr.get('country', 'US'),
            'beneficiary_identifier': trunc(beneficiary.get('identifier'), 35),
            'beneficiary_identifier_type': trunc(beneficiary.get('identifierType'), 10),

            # Beneficiary Bank
            'beneficiary_bank_routing_number': trunc(beneficiary_bank.get('routingNumber'), 9),
            'beneficiary_bank_name': trunc(beneficiary_bank.get('name'), 140),
            'beneficiary_bank_bic': beneficiary_bank.get('bic'),

            # Instructing Bank
            'instructing_bank_routing_number': trunc(instructing_bank.get('routingNumber'), 9),
            'instructing_bank_name': trunc(instructing_bank.get('name'), 140),

            # Intermediary Bank
            'intermediary_bank_routing_number': trunc(intermediary_bank.get('routingNumber'), 9) if intermediary_bank else None,
            'intermediary_bank_name': trunc(intermediary_bank.get('name'), 140) if intermediary_bank else None,

            # Info Fields
            'originator_to_beneficiary_info': trunc(msg_content.get('originatorToBeneficiaryInfo'), 140),
            'fi_to_fi_info': trunc(msg_content.get('fiToFiInfo'), 210),
            'charge_details': trunc(msg_content.get('chargeDetails'), 3),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id', '_ingested_at',
            'message_id', 'type_code', 'subtype_code', 'imad', 'omad',
            'input_cycle_date', 'input_source', 'input_sequence_number',
            'amount', 'currency', 'instructed_amount', 'instructed_currency',
            'sender_reference', 'previous_message_id', 'business_function_code', 'beneficiary_reference',
            'sender_routing_number', 'sender_name', 'sender_short_name', 'sender_bic', 'sender_lei',
            'sender_address_line1', 'sender_address_line2', 'sender_city', 'sender_state',
            'sender_zip_code', 'sender_country',
            'receiver_routing_number', 'receiver_name', 'receiver_short_name', 'receiver_bic', 'receiver_lei',
            'receiver_address_line1', 'receiver_address_line2', 'receiver_city', 'receiver_state',
            'receiver_zip_code', 'receiver_country',
            'originator_name', 'originator_account_number',
            'originator_address_line1', 'originator_address_line2',
            'originator_city', 'originator_state', 'originator_zip_code', 'originator_country',
            'originator_identifier', 'originator_identifier_type', 'originator_option_f',
            'beneficiary_name', 'beneficiary_account_number',
            'beneficiary_address_line1', 'beneficiary_address_line2',
            'beneficiary_city', 'beneficiary_state', 'beneficiary_zip_code', 'beneficiary_country',
            'beneficiary_identifier', 'beneficiary_identifier_type',
            'beneficiary_bank_routing_number', 'beneficiary_bank_name', 'beneficiary_bank_bic',
            'instructing_bank_routing_number', 'instructing_bank_name',
            'intermediary_bank_routing_number', 'intermediary_bank_name',
            'originator_to_beneficiary_info', 'fi_to_fi_info', 'charge_details',
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
        """Extract Gold layer entities from Fedwire message."""
        entities = GoldEntities()

        # Extract nested objects
        sender = msg_content.get('sender', {})
        sender_addr = sender.get('address', {}) if sender else {}
        receiver = msg_content.get('receiver', {})
        receiver_addr = receiver.get('address', {}) if receiver else {}
        originator = msg_content.get('originator', {})
        originator_addr = originator.get('address', {}) if originator else {}
        beneficiary = msg_content.get('beneficiary', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        beneficiary_bank = msg_content.get('beneficiaryBank', {})
        intermediary_bank = msg_content.get('intermediaryBank', {})

        # Originator (Debtor Party)
        if originator.get('name'):
            entities.parties.append(PartyData(
                name=originator.get('name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                street_name=originator_addr.get('line1'),
                town_name=originator_addr.get('city'),
                post_code=originator_addr.get('zipCode'),
                country_sub_division=originator_addr.get('state'),
                country=originator_addr.get('country', 'US'),
                identification_type=originator.get('identifierType'),
                identification_number=originator.get('identifier'),
            ))

        # Beneficiary (Creditor Party)
        if beneficiary.get('name'):
            entities.parties.append(PartyData(
                name=beneficiary.get('name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                street_name=beneficiary_addr.get('line1'),
                town_name=beneficiary_addr.get('city'),
                post_code=beneficiary_addr.get('zipCode'),
                country_sub_division=beneficiary_addr.get('state'),
                country=beneficiary_addr.get('country', 'US'),
                identification_type=beneficiary.get('identifierType'),
                identification_number=beneficiary.get('identifier'),
            ))

        # Originator Account (Debtor Account)
        if originator.get('accountNumber'):
            entities.accounts.append(AccountData(
                account_number=originator.get('accountNumber'),
                role="DEBTOR",
                account_type='CACC',
                currency=msg_content.get('currency', 'USD'),
            ))

        # Beneficiary Account (Creditor Account)
        if beneficiary.get('accountNumber'):
            entities.accounts.append(AccountData(
                account_number=beneficiary.get('accountNumber'),
                role="CREDITOR",
                account_type='CACC',
                currency=msg_content.get('currency', 'USD'),
            ))

        # Sender FI (Debtor Agent)
        if sender.get('routingNumber'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=sender.get('name'),
                short_name=sender.get('shortName'),
                bic=sender.get('bic'),
                lei=sender.get('lei'),
                clearing_code=sender.get('routingNumber'),
                clearing_system='USABA',
                address_line1=sender_addr.get('line1'),
                town_name=sender_addr.get('city'),
                country=sender_addr.get('country', 'US'),
            ))

        # Receiver FI / Beneficiary Bank (Creditor Agent)
        if receiver.get('routingNumber') or beneficiary_bank.get('routingNumber'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=receiver.get('name') or beneficiary_bank.get('name'),
                short_name=receiver.get('shortName'),
                bic=receiver.get('bic') or beneficiary_bank.get('bic'),
                lei=receiver.get('lei'),
                clearing_code=receiver.get('routingNumber') or beneficiary_bank.get('routingNumber'),
                clearing_system='USABA',
                address_line1=receiver_addr.get('line1'),
                town_name=receiver_addr.get('city'),
                country=receiver_addr.get('country', 'US'),
            ))

        # Intermediary Bank
        if intermediary_bank and intermediary_bank.get('routingNumber'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                name=intermediary_bank.get('name'),
                clearing_code=intermediary_bank.get('routingNumber'),
                clearing_system='USABA',
                country='US',
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('FEDWIRE', FedwireExtractor())
ExtractorRegistry.register('fedwire', FedwireExtractor())

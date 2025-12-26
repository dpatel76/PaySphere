"""SWIFT MT103 (Single Customer Credit Transfer) Extractor."""

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


class MT103Extractor(BaseExtractor):
    """Extractor for SWIFT MT103 messages."""

    MESSAGE_TYPE = "MT103"
    SILVER_TABLE = "stg_mt103"

    # =========================================================================
    # BRONZE EXTRACTION
    # =========================================================================

    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw MT103 content."""
        msg_id = raw_content.get('transactionReferenceNumber', '') or raw_content.get('senderReference', '')
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
        """Extract all Silver layer fields from MT103 message."""
        trunc = self.trunc

        # Extract nested objects
        ordering_cust = msg_content.get('orderingCustomer', {})
        ordering_cust_addr = ordering_cust.get('address', {}) if ordering_cust else {}
        ordering_inst = msg_content.get('orderingInstitution', {})
        senders_corr = msg_content.get('sendersCorrespondent', {})
        receivers_corr = msg_content.get('receiversCorrespondent', {})
        intermediary = msg_content.get('intermediaryInstitution', {})
        acct_with_inst = msg_content.get('accountWithInstitution', {})
        beneficiary = msg_content.get('beneficiaryCustomer', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        details_of_charges = msg_content.get('detailsOfCharges', {})
        regulatory = msg_content.get('regulatoryReporting', {})

        # Instruction codes can be an array - join them
        instruction_codes = msg_content.get('instructionCode', [])
        if isinstance(instruction_codes, list):
            instruction_code_str = ','.join(str(c) for c in instruction_codes[:4])
        else:
            instruction_code_str = str(instruction_codes) if instruction_codes else None

        return {
            'stg_id': stg_id,
            'raw_id': raw_id,
            '_batch_id': batch_id,
            '_ingested_at': datetime.utcnow(),

            # Message References
            'sender_reference': trunc(msg_content.get('senderReference'), 16),
            'transaction_reference_number': trunc(msg_content.get('transactionReferenceNumber'), 16),
            'bank_operation_code': trunc(msg_content.get('bankOperationCode'), 4),
            'instruction_code': trunc(instruction_code_str, 35),

            # Dates
            'value_date': msg_content.get('valueDate'),
            'currency_code': msg_content.get('currencyCode'),

            # Amount
            'amount': msg_content.get('amount'),

            # Ordering Customer (Field 50)
            'ordering_customer_name': trunc(ordering_cust.get('name'), 140),
            'ordering_customer_account': trunc(ordering_cust.get('account'), 35),
            'ordering_customer_address': trunc(ordering_cust_addr.get('streetName'), 140),
            'ordering_customer_country': ordering_cust_addr.get('country'),
            'ordering_customer_party_id': trunc(ordering_cust.get('partyIdentifier'), 35),
            'ordering_customer_national_id': trunc(ordering_cust.get('nationalId'), 35),

            # Ordering Institution (Field 52)
            'ordering_institution_bic': ordering_inst.get('bic'),
            'ordering_institution_name': trunc(ordering_inst.get('name'), 140),
            'ordering_institution_clearing_code': trunc(ordering_inst.get('clearingCode'), 35),
            'ordering_institution_country': ordering_inst.get('country'),

            # Sender's Correspondent (Field 53)
            'senders_correspondent_bic': senders_corr.get('bic'),
            'senders_correspondent_account': trunc(senders_corr.get('account'), 35),
            'senders_correspondent_name': trunc(senders_corr.get('name'), 140),

            # Receiver's Correspondent (Field 54)
            'receivers_correspondent_bic': receivers_corr.get('bic'),
            'receivers_correspondent_account': trunc(receivers_corr.get('account'), 35),
            'receivers_correspondent_name': trunc(receivers_corr.get('name'), 140),

            # Intermediary Institution (Field 56)
            'intermediary_institution_bic': intermediary.get('bic'),
            'intermediary_institution_name': trunc(intermediary.get('name'), 140),
            'intermediary_institution_country': intermediary.get('country'),

            # Account With Institution (Field 57)
            'account_with_institution_bic': acct_with_inst.get('bic'),
            'account_with_institution_name': trunc(acct_with_inst.get('name'), 140),
            'account_with_institution_country': acct_with_inst.get('country'),

            # Beneficiary Customer (Field 59)
            'beneficiary_name': trunc(beneficiary.get('name'), 140),
            'beneficiary_account': trunc(beneficiary.get('account'), 35),
            'beneficiary_address': trunc(beneficiary_addr.get('streetName'), 140),
            'beneficiary_country': beneficiary_addr.get('country'),
            'beneficiary_party_id': trunc(beneficiary.get('partyIdentifier'), 35),

            # Remittance Information (Field 70)
            'remittance_information': trunc(msg_content.get('remittanceInformation'), 140),

            # Details of Charges (Field 71)
            'details_of_charges': trunc(details_of_charges.get('chargeBearer') if isinstance(details_of_charges, dict) else details_of_charges, 3),

            # Sender to Receiver Information (Field 72)
            'sender_to_receiver_information': trunc(msg_content.get('senderToReceiverInformation'), 210),

            # Regulatory Reporting (Field 77B)
            'regulatory_reporting': trunc(regulatory.get('code') if isinstance(regulatory, dict) else regulatory, 140),
        }

    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        return [
            'stg_id', 'raw_id', '_batch_id', '_ingested_at',
            'sender_reference', 'transaction_reference_number', 'bank_operation_code', 'instruction_code',
            'value_date', 'currency_code', 'amount',
            'ordering_customer_name', 'ordering_customer_account', 'ordering_customer_address',
            'ordering_customer_country', 'ordering_customer_party_id', 'ordering_customer_national_id',
            'ordering_institution_bic', 'ordering_institution_name', 'ordering_institution_clearing_code',
            'ordering_institution_country',
            'senders_correspondent_bic', 'senders_correspondent_account', 'senders_correspondent_name',
            'receivers_correspondent_bic', 'receivers_correspondent_account', 'receivers_correspondent_name',
            'intermediary_institution_bic', 'intermediary_institution_name', 'intermediary_institution_country',
            'account_with_institution_bic', 'account_with_institution_name', 'account_with_institution_country',
            'beneficiary_name', 'beneficiary_account', 'beneficiary_address', 'beneficiary_country',
            'beneficiary_party_id',
            'remittance_information', 'details_of_charges', 'sender_to_receiver_information',
            'regulatory_reporting',
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
        """Extract Gold layer entities from MT103 message."""
        entities = GoldEntities()

        # Extract nested objects
        ordering_cust = msg_content.get('orderingCustomer', {})
        ordering_cust_addr = ordering_cust.get('address', {}) if ordering_cust else {}
        ordering_inst = msg_content.get('orderingInstitution', {})
        beneficiary = msg_content.get('beneficiaryCustomer', {})
        beneficiary_addr = beneficiary.get('address', {}) if beneficiary else {}
        acct_with_inst = msg_content.get('accountWithInstitution', {})
        intermediary = msg_content.get('intermediaryInstitution', {})

        # Ordering Customer (Debtor)
        if ordering_cust.get('name'):
            entities.parties.append(PartyData(
                name=ordering_cust.get('name'),
                role="DEBTOR",
                party_type='UNKNOWN',
                street_name=ordering_cust_addr.get('streetName'),
                building_number=ordering_cust_addr.get('buildingNumber'),
                post_code=ordering_cust_addr.get('postalCode'),
                town_name=ordering_cust_addr.get('townName'),
                country_sub_division=ordering_cust_addr.get('countrySubDivision'),
                country=ordering_cust_addr.get('country'),
                identification_type='CUST' if ordering_cust.get('partyIdentifier') else ('NATL' if ordering_cust.get('nationalId') else None),
                identification_number=ordering_cust.get('partyIdentifier') or ordering_cust.get('nationalId'),
            ))

        # Beneficiary Customer (Creditor)
        if beneficiary.get('name'):
            entities.parties.append(PartyData(
                name=beneficiary.get('name'),
                role="CREDITOR",
                party_type='UNKNOWN',
                street_name=beneficiary_addr.get('streetName'),
                building_number=beneficiary_addr.get('buildingNumber'),
                post_code=beneficiary_addr.get('postalCode'),
                town_name=beneficiary_addr.get('townName'),
                country_sub_division=beneficiary_addr.get('countrySubDivision'),
                country=beneficiary_addr.get('country'),
                identification_type='CUST' if beneficiary.get('partyIdentifier') else None,
                identification_number=beneficiary.get('partyIdentifier'),
            ))

        # Ordering Customer Account (Debtor Account)
        if ordering_cust.get('account'):
            entities.accounts.append(AccountData(
                account_number=ordering_cust.get('account'),
                role="DEBTOR",
                account_type='UNKNOWN',
                currency=msg_content.get('currencyCode', 'XXX'),
            ))

        # Beneficiary Account (Creditor Account)
        if beneficiary.get('account'):
            entities.accounts.append(AccountData(
                account_number=beneficiary.get('account'),
                role="CREDITOR",
                account_type='UNKNOWN',
                currency=msg_content.get('currencyCode', 'XXX'),
            ))

        # Ordering Institution (Debtor Agent)
        if ordering_inst.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="DEBTOR_AGENT",
                name=ordering_inst.get('name'),
                bic=ordering_inst.get('bic'),
                clearing_code=ordering_inst.get('clearingCode'),
                country=ordering_inst.get('country', 'XX'),
            ))

        # Account With Institution (Creditor Agent)
        if acct_with_inst.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="CREDITOR_AGENT",
                name=acct_with_inst.get('name'),
                bic=acct_with_inst.get('bic'),
                country=acct_with_inst.get('country', 'XX'),
            ))

        # Intermediary Institution
        if intermediary.get('bic'):
            entities.financial_institutions.append(FinancialInstitutionData(
                role="INTERMEDIARY",
                name=intermediary.get('name'),
                bic=intermediary.get('bic'),
                country=intermediary.get('country', 'XX'),
            ))

        return entities


# Register the extractor
ExtractorRegistry.register('MT103', MT103Extractor())
ExtractorRegistry.register('mt103', MT103Extractor())
ExtractorRegistry.register('103', MT103Extractor())

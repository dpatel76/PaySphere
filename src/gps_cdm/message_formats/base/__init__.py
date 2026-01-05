"""Base classes for message format extractors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json
import logging

logger = logging.getLogger(__name__)


def trunc(value: Optional[str], max_length: int) -> Optional[str]:
    """Truncate string value to max_length."""
    if value is None:
        return None
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length]
    return value


# =============================================================================
# DATA CLASSES FOR GOLD ENTITIES
# =============================================================================

@dataclass
class PartyData:
    """Standardized party data for Gold layer persistence."""
    name: str
    party_type: str = "UNKNOWN"
    role: str = "UNKNOWN"  # DEBTOR, CREDITOR, ULTIMATE_DEBTOR, ULTIMATE_CREDITOR
    street_name: Optional[str] = None
    building_number: Optional[str] = None
    post_code: Optional[str] = None
    town_name: Optional[str] = None
    country_sub_division: Optional[str] = None
    country: Optional[str] = None
    identification_type: Optional[str] = None
    identification_number: Optional[str] = None


@dataclass
class AccountData:
    """Standardized account data for Gold layer persistence."""
    account_number: str
    role: str = "UNKNOWN"  # DEBTOR, CREDITOR
    iban: Optional[str] = None
    account_type: str = "UNKNOWN"
    currency: str = "XXX"


@dataclass
class FinancialInstitutionData:
    """Standardized FI data for Gold layer persistence."""
    role: str  # DEBTOR_AGENT, CREDITOR_AGENT, INTERMEDIARY
    name: Optional[str] = None
    short_name: Optional[str] = None
    bic: Optional[str] = None
    lei: Optional[str] = None
    clearing_code: Optional[str] = None
    clearing_system: Optional[str] = None
    address_line1: Optional[str] = None
    town_name: Optional[str] = None
    country: str = "XX"


@dataclass
class GoldEntities:
    """Container for all extracted Gold entities from a message."""
    parties: List[PartyData] = field(default_factory=list)
    accounts: List[AccountData] = field(default_factory=list)
    financial_institutions: List[FinancialInstitutionData] = field(default_factory=list)

    # Payment instruction fields
    service_level: Optional[str] = None
    local_instrument: Optional[str] = None
    category_purpose: Optional[str] = None
    exchange_rate: Optional[float] = None


# =============================================================================
# EXTENSION DATA CLASSES (Scheme-specific)
# =============================================================================

@dataclass
class FedwireExtension:
    """FEDWIRE-specific payment attributes."""
    wire_type_code: Optional[str] = None
    wire_subtype_code: Optional[str] = None
    imad: Optional[str] = None
    omad: Optional[str] = None
    previous_imad: Optional[str] = None
    fi_to_fi_info: Optional[str] = None
    beneficiary_reference: Optional[str] = None
    input_cycle_date: Optional[str] = None
    input_sequence_number: Optional[str] = None
    input_source: Optional[str] = None
    originator_id_type: Optional[str] = None
    originator_option_f: Optional[str] = None
    beneficiary_id_type: Optional[str] = None
    charges: Optional[str] = None


@dataclass
class AchExtension:
    """NACHA ACH-specific payment attributes."""
    immediate_destination: Optional[str] = None
    immediate_origin: Optional[str] = None
    file_creation_date: Optional[str] = None
    file_creation_time: Optional[str] = None
    file_id_modifier: Optional[str] = None
    standard_entry_class: Optional[str] = None
    company_entry_description: Optional[str] = None
    batch_number: Optional[int] = None
    originator_status_code: Optional[str] = None
    transaction_code: Optional[str] = None
    originating_dfi_id: Optional[str] = None
    receiving_dfi_id: Optional[str] = None
    individual_id: Optional[str] = None
    discretionary_data: Optional[str] = None
    addenda_indicator: Optional[str] = None
    addenda_type: Optional[str] = None
    addenda_info: Optional[str] = None
    return_reason_code: Optional[str] = None
    original_entry_trace: Optional[str] = None
    date_of_death: Optional[str] = None
    original_receiving_dfi: Optional[str] = None


@dataclass
class SepaExtension:
    """SEPA-specific payment attributes."""
    sepa_message_type: Optional[str] = None
    sepa_scheme: Optional[str] = None
    settlement_method: Optional[str] = None
    mandate_id: Optional[str] = None
    mandate_date: Optional[str] = None
    sequence_type: Optional[str] = None
    creditor_scheme_id: Optional[str] = None
    amendment_indicator: bool = False
    original_mandate_id: Optional[str] = None


@dataclass
class SwiftExtension:
    """SWIFT MT-specific payment attributes."""
    swift_message_type: Optional[str] = None
    sender_bic: Optional[str] = None
    receiver_bic: Optional[str] = None
    message_priority: Optional[str] = None
    senders_correspondent_bic: Optional[str] = None
    senders_correspondent_account: Optional[str] = None
    receivers_correspondent_bic: Optional[str] = None
    receivers_correspondent_account: Optional[str] = None
    ordering_institution_bic: Optional[str] = None
    account_with_institution_bic: Optional[str] = None
    sender_charges_amount: Optional[float] = None
    sender_charges_currency: Optional[str] = None
    sender_to_receiver_information: Optional[str] = None
    instruction_codes: Optional[str] = None


@dataclass
class RtpExtension:
    """TCH RTP-specific payment attributes."""
    rtp_message_type: Optional[str] = None
    debtor_agent_rtn: Optional[str] = None
    creditor_agent_rtn: Optional[str] = None
    rfp_reference: Optional[str] = None
    rfp_expiry_datetime: Optional[str] = None


@dataclass
class Iso20022Extension:
    """ISO 20022-specific payment attributes."""
    message_definition: Optional[str] = None
    message_namespace: Optional[str] = None
    payment_info_id: Optional[str] = None
    initiating_party_name: Optional[str] = None
    initiating_party_id: Optional[str] = None
    instruction_priority: Optional[str] = None
    clearing_channel: Optional[str] = None
    regulatory_reporting_code: Optional[str] = None
    creditor_reference: Optional[str] = None


# =============================================================================
# GOLD ENTITY PERSISTER (Common across all message formats)
# =============================================================================

class GoldEntityPersister:
    """
    Common persistence logic for Gold layer entities.

    This class handles INSERT statements for all Gold tables, ensuring
    consistent persistence across all message formats.
    """

    @staticmethod
    def persist_party(
        cursor,
        party: PartyData,
        message_type: str,
        stg_id: str,
        source_system: str = "GPS_CDM"
    ) -> str:
        """Persist a party to gold.cdm_party and return the party_id."""
        party_id = f"party_{uuid.uuid4().hex[:12]}"

        cursor.execute("""
            INSERT INTO gold.cdm_party (
                party_id, party_type, name,
                street_name, building_number, post_code, town_name,
                country_sub_division, country,
                identification_type, identification_number,
                source_system, source_message_type, source_stg_id,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (party_id) DO NOTHING
        """, (
            party_id,
            party.party_type,
            party.name,
            party.street_name,
            party.building_number,
            party.post_code,
            party.town_name,
            party.country_sub_division,
            party.country,
            party.identification_type,
            party.identification_number,
            source_system,
            message_type,
            stg_id,
        ))

        return party_id

    @staticmethod
    def persist_account(
        cursor,
        account: AccountData,
        owner_id: Optional[str],
        message_type: str,
        stg_id: str,
        source_system: str = "GPS_CDM"
    ) -> str:
        """Persist an account to gold.cdm_account and return the account_id."""
        account_id = f"acct_{uuid.uuid4().hex[:12]}"

        cursor.execute("""
            INSERT INTO gold.cdm_account (
                account_id, account_number, iban, account_type, currency,
                owner_id, account_status,
                source_system, source_message_type, source_stg_id,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (account_id) DO NOTHING
        """, (
            account_id,
            account.account_number,
            account.iban,
            account.account_type,
            account.currency,
            owner_id,
            'ACTIVE',
            source_system,
            message_type,
            stg_id,
        ))

        return account_id

    @staticmethod
    def persist_financial_institution(
        cursor,
        fi: FinancialInstitutionData,
        source_system: str = "GPS_CDM"
    ) -> str:
        """Persist a FI to gold.cdm_financial_institution and return the fi_id."""
        fi_id = f"fi_{uuid.uuid4().hex[:12]}"
        inst_name = fi.name or f"FI_{fi.bic or fi.clearing_code}"

        cursor.execute("""
            INSERT INTO gold.cdm_financial_institution (
                fi_id, institution_name, short_name, bic, lei,
                national_clearing_code, national_clearing_system,
                address_line1, town_name, country,
                source_system, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (fi_id) DO NOTHING
        """, (
            fi_id,
            inst_name,
            fi.short_name,
            fi.bic,
            fi.lei,
            fi.clearing_code,
            fi.clearing_system,
            fi.address_line1,
            fi.town_name,
            fi.country,
            source_system,
        ))

        return fi_id

    @classmethod
    def persist_all_entities(
        cls,
        cursor,
        entities: GoldEntities,
        message_type: str,
        stg_id: str,
        source_system: str = "GPS_CDM"
    ) -> Dict[str, Optional[str]]:
        """
        Persist all extracted Gold entities and return a dict of entity IDs.

        Returns:
            Dict with keys like 'debtor_id', 'creditor_id', 'debtor_account_id', etc.
        """
        entity_ids = {
            'debtor_id': None,
            'debtor_account_id': None,
            'debtor_agent_id': None,
            'creditor_id': None,
            'creditor_account_id': None,
            'creditor_agent_id': None,
            'intermediary_agent1_id': None,
            'intermediary_agent2_id': None,
            'ultimate_debtor_id': None,
            'ultimate_creditor_id': None,
        }

        # Persist parties
        for party in entities.parties:
            if party.name:
                party_id = cls.persist_party(cursor, party, message_type, stg_id, source_system)

                if party.role == "DEBTOR":
                    entity_ids['debtor_id'] = party_id
                elif party.role == "CREDITOR":
                    entity_ids['creditor_id'] = party_id
                elif party.role == "ULTIMATE_DEBTOR":
                    entity_ids['ultimate_debtor_id'] = party_id
                elif party.role == "ULTIMATE_CREDITOR":
                    entity_ids['ultimate_creditor_id'] = party_id

        # Persist accounts
        for account in entities.accounts:
            if account.account_number:
                owner_id = entity_ids.get('debtor_id') if account.role == "DEBTOR" else entity_ids.get('creditor_id')
                account_id = cls.persist_account(cursor, account, owner_id, message_type, stg_id, source_system)

                if account.role == "DEBTOR":
                    entity_ids['debtor_account_id'] = account_id
                elif account.role == "CREDITOR":
                    entity_ids['creditor_account_id'] = account_id

        # Persist financial institutions
        for fi in entities.financial_institutions:
            if fi.bic or fi.clearing_code:
                fi_id = cls.persist_financial_institution(cursor, fi, source_system)

                if fi.role == "DEBTOR_AGENT":
                    entity_ids['debtor_agent_id'] = fi_id
                elif fi.role == "CREDITOR_AGENT":
                    entity_ids['creditor_agent_id'] = fi_id
                elif fi.role == "INTERMEDIARY":
                    entity_ids['intermediary_agent1_id'] = fi_id

        return entity_ids

    # =========================================================================
    # EXTENSION TABLE PERSISTERS
    # =========================================================================

    @staticmethod
    def persist_fedwire_extension(
        cursor,
        instruction_id: str,
        ext: 'FedwireExtension'
    ) -> str:
        """Persist FEDWIRE extension data."""
        extension_id = f"fwext_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO gold.cdm_payment_extension_fedwire (
                extension_id, instruction_id,
                wire_type_code, wire_subtype_code, imad, omad, previous_imad,
                fi_to_fi_info, beneficiary_reference,
                input_cycle_date, input_sequence_number, input_source,
                originator_id_type, originator_option_f, beneficiary_id_type, charges
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (instruction_id) DO UPDATE SET
                wire_type_code = EXCLUDED.wire_type_code,
                wire_subtype_code = EXCLUDED.wire_subtype_code
        """, (
            extension_id, instruction_id,
            ext.wire_type_code, ext.wire_subtype_code, ext.imad, ext.omad, ext.previous_imad,
            ext.fi_to_fi_info, ext.beneficiary_reference,
            ext.input_cycle_date, ext.input_sequence_number, ext.input_source,
            ext.originator_id_type, ext.originator_option_f, ext.beneficiary_id_type, ext.charges
        ))
        return extension_id

    @staticmethod
    def persist_ach_extension(
        cursor,
        instruction_id: str,
        ext: 'AchExtension'
    ) -> str:
        """Persist ACH extension data."""
        extension_id = f"achext_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO gold.cdm_payment_extension_ach (
                extension_id, instruction_id,
                immediate_destination, immediate_origin, file_creation_date, file_creation_time, file_id_modifier,
                standard_entry_class, company_entry_description, batch_number, originator_status_code,
                transaction_code, originating_dfi_id, receiving_dfi_id, individual_id, discretionary_data,
                addenda_indicator, addenda_type, addenda_info,
                return_reason_code, original_entry_trace, date_of_death, original_receiving_dfi
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (instruction_id) DO UPDATE SET
                standard_entry_class = EXCLUDED.standard_entry_class,
                transaction_code = EXCLUDED.transaction_code
        """, (
            extension_id, instruction_id,
            trunc(ext.immediate_destination, 50), trunc(ext.immediate_origin, 50),
            trunc(ext.file_creation_date, 10), trunc(ext.file_creation_time, 4), trunc(ext.file_id_modifier, 1),
            trunc(ext.standard_entry_class, 3), trunc(ext.company_entry_description, 100),
            trunc(ext.batch_number, 20), trunc(ext.originator_status_code, 1),
            trunc(ext.transaction_code, 2), trunc(ext.originating_dfi_id, 20), trunc(ext.receiving_dfi_id, 20),
            trunc(ext.individual_id, 50), trunc(ext.discretionary_data, 2),
            trunc(ext.addenda_indicator, 1), trunc(ext.addenda_type, 2), trunc(ext.addenda_info, 500),
            trunc(ext.return_reason_code, 3), trunc(ext.original_entry_trace, 30),
            trunc(ext.date_of_death, 10), trunc(ext.original_receiving_dfi, 20)
        ))
        return extension_id

    @staticmethod
    def persist_sepa_extension(
        cursor,
        instruction_id: str,
        ext: 'SepaExtension'
    ) -> str:
        """Persist SEPA extension data."""
        extension_id = f"sepaext_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO gold.cdm_payment_extension_sepa (
                extension_id, instruction_id,
                sepa_message_type, sepa_scheme, settlement_method,
                mandate_id, mandate_date, sequence_type, creditor_scheme_id,
                amendment_indicator, original_mandate_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (instruction_id) DO UPDATE SET
                sepa_scheme = EXCLUDED.sepa_scheme,
                mandate_id = EXCLUDED.mandate_id
        """, (
            extension_id, instruction_id,
            ext.sepa_message_type, ext.sepa_scheme, ext.settlement_method,
            ext.mandate_id, ext.mandate_date, ext.sequence_type, ext.creditor_scheme_id,
            ext.amendment_indicator, ext.original_mandate_id
        ))
        return extension_id

    @staticmethod
    def persist_swift_extension(
        cursor,
        instruction_id: str,
        ext: 'SwiftExtension'
    ) -> str:
        """Persist SWIFT MT extension data."""
        extension_id = f"swiftext_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO gold.cdm_payment_extension_swift (
                extension_id, instruction_id,
                swift_message_type, sender_bic, receiver_bic, message_priority,
                senders_correspondent_bic, senders_correspondent_account,
                receivers_correspondent_bic, receivers_correspondent_account,
                ordering_institution_bic, account_with_institution_bic,
                sender_charges_amount, sender_charges_currency,
                sender_to_receiver_information, instruction_codes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (instruction_id) DO UPDATE SET
                swift_message_type = EXCLUDED.swift_message_type,
                sender_bic = EXCLUDED.sender_bic
        """, (
            extension_id, instruction_id,
            ext.swift_message_type, ext.sender_bic, ext.receiver_bic, ext.message_priority,
            ext.senders_correspondent_bic, ext.senders_correspondent_account,
            ext.receivers_correspondent_bic, ext.receivers_correspondent_account,
            ext.ordering_institution_bic, ext.account_with_institution_bic,
            ext.sender_charges_amount, ext.sender_charges_currency,
            ext.sender_to_receiver_information, ext.instruction_codes
        ))
        return extension_id

    @staticmethod
    def persist_rtp_extension(
        cursor,
        instruction_id: str,
        ext: 'RtpExtension'
    ) -> str:
        """Persist RTP extension data."""
        extension_id = f"rtpext_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO gold.cdm_payment_extension_rtp (
                extension_id, instruction_id,
                rtp_message_type, debtor_agent_rtn, creditor_agent_rtn,
                rfp_reference, rfp_expiry_datetime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (instruction_id) DO UPDATE SET
                rtp_message_type = EXCLUDED.rtp_message_type
        """, (
            extension_id, instruction_id,
            ext.rtp_message_type, ext.debtor_agent_rtn, ext.creditor_agent_rtn,
            ext.rfp_reference, ext.rfp_expiry_datetime
        ))
        return extension_id

    @staticmethod
    def persist_iso20022_extension(
        cursor,
        instruction_id: str,
        ext: 'Iso20022Extension'
    ) -> str:
        """Persist ISO 20022 extension data."""
        extension_id = f"isoext_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO gold.cdm_payment_extension_iso20022 (
                extension_id, instruction_id,
                message_definition, message_namespace, payment_info_id,
                initiating_party_name, initiating_party_id,
                instruction_priority, clearing_channel,
                regulatory_reporting_code, creditor_reference
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (instruction_id) DO UPDATE SET
                message_definition = EXCLUDED.message_definition
        """, (
            extension_id, instruction_id,
            ext.message_definition, ext.message_namespace, ext.payment_info_id,
            ext.initiating_party_name, ext.initiating_party_id,
            ext.instruction_priority, ext.clearing_channel,
            ext.regulatory_reporting_code, ext.creditor_reference
        ))
        return extension_id

    @classmethod
    def persist_extension(
        cls,
        cursor,
        instruction_id: str,
        message_type: str,
        staging_record: Dict[str, Any]
    ) -> Optional[str]:
        """
        Persist scheme-specific extension data based on message type.

        Args:
            cursor: Database cursor
            instruction_id: The payment instruction ID
            message_type: Message type (FEDWIRE, ACH, SEPA, MT103, RTP, pain.001, etc.)
            staging_record: Silver staging record with extracted fields

        Returns:
            Extension ID if created, None otherwise
        """
        msg_type_upper = message_type.upper()

        if msg_type_upper == 'FEDWIRE':
            ext = FedwireExtension(
                wire_type_code=staging_record.get('type_code'),
                wire_subtype_code=staging_record.get('subtype_code'),
                imad=staging_record.get('imad'),
                omad=staging_record.get('omad'),
                previous_imad=staging_record.get('previous_imad'),
                fi_to_fi_info=staging_record.get('fi_to_fi_info'),
                beneficiary_reference=staging_record.get('beneficiary_reference'),
                input_cycle_date=staging_record.get('input_cycle_date'),
                input_sequence_number=staging_record.get('input_sequence_number'),
                input_source=staging_record.get('input_source'),
                originator_id_type=staging_record.get('originator_id_type'),
                originator_option_f=staging_record.get('originator_option_f'),
                beneficiary_id_type=staging_record.get('beneficiary_id_type'),
                charges=staging_record.get('charges'),
            )
            return cls.persist_fedwire_extension(cursor, instruction_id, ext)

        elif msg_type_upper == 'ACH':
            ext = AchExtension(
                immediate_destination=staging_record.get('immediate_destination'),
                immediate_origin=staging_record.get('immediate_origin'),
                file_creation_date=staging_record.get('file_creation_date'),
                file_creation_time=staging_record.get('file_creation_time'),
                file_id_modifier=staging_record.get('file_id_modifier'),
                standard_entry_class=staging_record.get('standard_entry_class'),
                company_entry_description=staging_record.get('company_entry_description'),
                batch_number=staging_record.get('batch_number'),
                originator_status_code=staging_record.get('originator_status_code'),
                transaction_code=staging_record.get('transaction_code'),
                originating_dfi_id=staging_record.get('originating_dfi_id'),
                receiving_dfi_id=staging_record.get('receiving_dfi_id'),
                individual_id=staging_record.get('individual_id'),
                discretionary_data=staging_record.get('discretionary_data'),
                addenda_indicator=staging_record.get('addenda_indicator'),
                addenda_type=staging_record.get('addenda_type'),
                addenda_info=staging_record.get('addenda_info'),
                return_reason_code=staging_record.get('return_reason_code'),
                original_entry_trace=staging_record.get('original_entry_trace'),
                date_of_death=staging_record.get('date_of_death'),
                original_receiving_dfi=staging_record.get('original_receiving_dfi'),
            )
            return cls.persist_ach_extension(cursor, instruction_id, ext)

        elif msg_type_upper == 'SEPA':
            ext = SepaExtension(
                sepa_message_type=staging_record.get('sepa_message_type'),
                sepa_scheme=staging_record.get('sepa_scheme'),
                settlement_method=staging_record.get('settlement_method'),
                mandate_id=staging_record.get('mandate_id'),
                mandate_date=staging_record.get('mandate_date'),
                sequence_type=staging_record.get('sequence_type'),
                creditor_scheme_id=staging_record.get('creditor_id'),
            )
            return cls.persist_sepa_extension(cursor, instruction_id, ext)

        elif msg_type_upper in ('MT103', 'MT202', 'MT202COV'):
            ext = SwiftExtension(
                swift_message_type=staging_record.get('message_type'),
                sender_bic=staging_record.get('sender_bic'),
                receiver_bic=staging_record.get('receiver_bic'),
                message_priority=staging_record.get('priority'),
                senders_correspondent_bic=staging_record.get('senders_correspondent_bic'),
                senders_correspondent_account=staging_record.get('senders_correspondent_account'),
                receivers_correspondent_bic=staging_record.get('receivers_correspondent_bic'),
                receivers_correspondent_account=staging_record.get('receivers_correspondent_account'),
                ordering_institution_bic=staging_record.get('ordering_institution_bic'),
                account_with_institution_bic=staging_record.get('account_with_institution_bic'),
                sender_to_receiver_information=staging_record.get('sender_to_receiver_information'),
                instruction_codes=staging_record.get('instruction_code'),
            )
            return cls.persist_swift_extension(cursor, instruction_id, ext)

        elif msg_type_upper == 'RTP':
            ext = RtpExtension(
                rtp_message_type=staging_record.get('rtp_message_type'),
                debtor_agent_rtn=staging_record.get('debtor_agent_id'),
                creditor_agent_rtn=staging_record.get('creditor_agent_id'),
            )
            return cls.persist_rtp_extension(cursor, instruction_id, ext)

        elif msg_type_upper.startswith('PAIN.') or msg_type_upper.startswith('PACS.'):
            ext = Iso20022Extension(
                message_definition=message_type,
                payment_info_id=staging_record.get('payment_info_id'),
                initiating_party_name=staging_record.get('initiating_party_name'),
                initiating_party_id=staging_record.get('initiating_party_id'),
                instruction_priority=staging_record.get('instruction_priority'),
                creditor_reference=staging_record.get('creditor_reference'),
            )
            return cls.persist_iso20022_extension(cursor, instruction_id, ext)

        return None


# =============================================================================
# BASE EXTRACTOR CLASS
# =============================================================================

class BaseExtractor(ABC):
    """Base class for all message format extractors."""

    # Override in subclasses
    MESSAGE_TYPE: str = "UNKNOWN"
    SILVER_TABLE: str = "stg_unknown"

    @classmethod
    def trunc(cls, val: Any, max_len: int) -> Optional[str]:
        """Truncate string to maximum length."""
        if val is None:
            return None
        if len(str(val)) > max_len:
            return str(val)[:max_len]
        return str(val) if val else None

    @abstractmethod
    def extract_bronze(self, raw_content: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
        """Extract Bronze layer record from raw content.

        Args:
            raw_content: Raw message content from source
            batch_id: Processing batch identifier

        Returns:
            Dict with raw_id, message_type, and raw_content for Bronze table
        """
        pass

    @abstractmethod
    def extract_silver(
        self,
        msg_content: Dict[str, Any],
        raw_id: str,
        stg_id: str,
        batch_id: str
    ) -> Dict[str, Any]:
        """Extract Silver layer record from message content.

        Args:
            msg_content: Parsed message content
            raw_id: Reference to Bronze record
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            Dict with all fields for Silver staging table
        """
        pass

    @abstractmethod
    def get_silver_columns(self) -> List[str]:
        """Return ordered list of Silver table columns for INSERT."""
        pass

    @abstractmethod
    def get_silver_values(self, silver_record: Dict[str, Any]) -> tuple:
        """Return ordered tuple of values for Silver table INSERT."""
        pass

    @abstractmethod
    def extract_gold_entities(
        self,
        msg_content: Dict[str, Any],
        stg_id: str,
        batch_id: str
    ) -> GoldEntities:
        """Extract Gold layer entities from message content.

        Each message format extractor implements this to extract
        parties, accounts, and FIs in a standardized format.
        The GoldEntityPersister handles the actual INSERT statements.

        Args:
            msg_content: Parsed message content
            stg_id: Silver staging record ID
            batch_id: Processing batch identifier

        Returns:
            GoldEntities container with all extracted entities
        """
        pass

    def generate_stg_id(self) -> str:
        """Generate unique staging ID."""
        return str(uuid.uuid4())

    def generate_raw_id(self, msg_id: Optional[str] = None) -> str:
        """Generate unique raw record ID."""
        if msg_id:
            return f"raw_{msg_id}_{uuid.uuid4().hex[:8]}"
        return f"raw_{uuid.uuid4().hex}"


# =============================================================================
# EXTRACTOR REGISTRY
# =============================================================================

class ExtractorRegistry:
    """Registry for message format extractors."""

    _extractors: Dict[str, BaseExtractor] = {}

    @classmethod
    def register(cls, message_type: str, extractor: BaseExtractor) -> None:
        """Register an extractor for a message type."""
        cls._extractors[message_type.lower()] = extractor
        logger.info(f"Registered extractor for message type: {message_type}")

    @classmethod
    def get(cls, message_type: str) -> Optional[BaseExtractor]:
        """Get extractor for a message type."""
        # Normalize message type
        normalized = message_type.lower().replace('.', '_').replace('-', '_')
        return cls._extractors.get(normalized) or cls._extractors.get(message_type.lower())

    @classmethod
    def list_types(cls) -> List[str]:
        """List all registered message types."""
        return list(cls._extractors.keys())

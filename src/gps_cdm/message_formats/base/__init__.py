"""Base classes for message format extractors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json
import logging

logger = logging.getLogger(__name__)


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

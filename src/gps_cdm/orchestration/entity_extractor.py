"""
GPS CDM - Entity Extraction Processor
=====================================

Extracts normalized entities (Party, Account, Financial Institution) from
staging data based on YAML entity mappings.

This module bridges Silver → Gold transformation for reference data,
ensuring proper normalization and deduplication.

Usage:
    extractor = EntityExtractor(db_connection, mapping_config)
    results = extractor.extract_from_staging(staging_records, batch_id)

    # Results contain:
    # - parties: List of extracted/matched party records
    # - accounts: List of extracted/matched account records
    # - financial_institutions: List of extracted/matched FI records
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from gps_cdm.ingestion.core.models import MappingConfig, EntityMapping
from gps_cdm.orchestration.deduplication import ReferenceDataDeduplicator, DeduplicationResult


@dataclass
class ExtractedEntity:
    """Represents an extracted entity ready for persistence."""
    entity_type: str  # "party", "account", "financial_institution"
    entity_id: str
    role: str  # "debtor", "creditor", "debtor_agent", etc.
    is_new: bool  # True if newly created, False if matched existing
    data: Dict[str, Any]
    source_stg_id: str
    match_info: Optional[DeduplicationResult] = None


@dataclass
class ExtractionResult:
    """Result of entity extraction from staging records."""
    batch_id: str
    parties: List[ExtractedEntity] = field(default_factory=list)
    accounts: List[ExtractedEntity] = field(default_factory=list)
    financial_institutions: List[ExtractedEntity] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def total_extracted(self) -> int:
        return len(self.parties) + len(self.accounts) + len(self.financial_institutions)

    @property
    def new_entities(self) -> int:
        return (
            sum(1 for p in self.parties if p.is_new) +
            sum(1 for a in self.accounts if a.is_new) +
            sum(1 for f in self.financial_institutions if f.is_new)
        )


class EntityExtractor:
    """
    Extracts normalized entities from staging data.

    Uses YAML entity mappings to identify which staging columns
    map to which entity attributes, then extracts and deduplicates.
    """

    def __init__(
        self,
        db_connection=None,
        deduplicator: Optional[ReferenceDataDeduplicator] = None,
        source_system: str = "GPS_CDM",
    ):
        """
        Initialize entity extractor.

        Args:
            db_connection: Database connection for persistence
            deduplicator: Optional pre-configured deduplicator
            source_system: Source system identifier for lineage
        """
        self.db = db_connection
        self.deduplicator = deduplicator or ReferenceDataDeduplicator(db_connection)
        self.source_system = source_system

    def extract_from_staging(
        self,
        staging_records: List[Dict[str, Any]],
        mapping_config: MappingConfig,
        batch_id: str,
    ) -> ExtractionResult:
        """
        Extract entities from staging records based on mapping configuration.

        Args:
            staging_records: List of staging table records (as dicts)
            mapping_config: Mapping configuration with entity mappings
            batch_id: Batch identifier for lineage

        Returns:
            ExtractionResult with all extracted entities
        """
        result = ExtractionResult(batch_id=batch_id)

        for record in staging_records:
            stg_id = record.get("stg_id", str(uuid.uuid4()))

            # Extract parties
            if mapping_config.party_mappings:
                for party_mapping in mapping_config.party_mappings:
                    try:
                        party = self._extract_party(record, party_mapping, stg_id)
                        if party:
                            result.parties.append(party)
                    except Exception as e:
                        result.errors.append({
                            "entity_type": "party",
                            "role": party_mapping.role,
                            "stg_id": stg_id,
                            "error": str(e),
                        })

            # Extract accounts
            if mapping_config.account_mappings:
                for account_mapping in mapping_config.account_mappings:
                    try:
                        account = self._extract_account(record, account_mapping, stg_id)
                        if account:
                            result.accounts.append(account)
                    except Exception as e:
                        result.errors.append({
                            "entity_type": "account",
                            "role": account_mapping.role,
                            "stg_id": stg_id,
                            "error": str(e),
                        })

            # Extract financial institutions
            if mapping_config.fi_mappings:
                for fi_mapping in mapping_config.fi_mappings:
                    try:
                        fi = self._extract_financial_institution(record, fi_mapping, stg_id)
                        if fi:
                            result.financial_institutions.append(fi)
                    except Exception as e:
                        result.errors.append({
                            "entity_type": "financial_institution",
                            "role": fi_mapping.role,
                            "stg_id": stg_id,
                            "error": str(e),
                        })

        return result

    def _extract_party(
        self,
        record: Dict[str, Any],
        mapping: EntityMapping,
        stg_id: str,
    ) -> Optional[ExtractedEntity]:
        """Extract a party entity from a staging record."""
        # Build party data from mapping fields
        data = {}
        prefix = mapping.source_prefix or ""

        for field_mapping in mapping.fields:
            source_col = f"{prefix}{field_mapping.source}" if prefix else field_mapping.source
            value = record.get(source_col)
            if value is not None and value != "":
                data[field_mapping.target] = value

        # Skip if no meaningful data
        if not data.get("name"):
            return None

        # Determine party type
        party_type = data.get("party_type", "UNKNOWN")
        if not party_type or party_type == "UNKNOWN":
            # Infer from data
            if data.get("date_of_birth") or data.get("place_of_birth"):
                party_type = "INDIVIDUAL"
            elif data.get("lei") or data.get("registration_number"):
                party_type = "ORGANIZATION"
            else:
                party_type = "UNKNOWN"
        data["party_type"] = party_type

        # Get country
        country = data.get("country", "XX")

        # Check for duplicates
        dedup_result = self.deduplicator.find_party(
            name=data.get("name", ""),
            country=country,
            party_type=party_type,
            lei=data.get("lei"),
            bic=data.get("bic"),
            registration_number=data.get("registration_number"),
        )

        if dedup_result.is_duplicate:
            # Use existing party
            return ExtractedEntity(
                entity_type="party",
                entity_id=dedup_result.existing_id,
                role=mapping.role,
                is_new=False,
                data=data,
                source_stg_id=stg_id,
                match_info=dedup_result,
            )
        else:
            # Create new party
            party_id = str(uuid.uuid4())
            data["party_id"] = party_id
            data["source_system"] = self.source_system
            data["source_stg_id"] = stg_id

            # Register in deduplicator cache
            self.deduplicator.register_party(
                party_id=party_id,
                name=data.get("name", ""),
                country=country,
                party_type=party_type,
                lei=data.get("lei"),
                bic=data.get("bic"),
                registration_number=data.get("registration_number"),
            )

            return ExtractedEntity(
                entity_type="party",
                entity_id=party_id,
                role=mapping.role,
                is_new=True,
                data=data,
                source_stg_id=stg_id,
            )

    def _extract_account(
        self,
        record: Dict[str, Any],
        mapping: EntityMapping,
        stg_id: str,
    ) -> Optional[ExtractedEntity]:
        """Extract an account entity from a staging record."""
        data = {}
        prefix = mapping.source_prefix or ""

        for field_mapping in mapping.fields:
            source_col = f"{prefix}{field_mapping.source}" if prefix else field_mapping.source
            value = record.get(source_col)
            if value is not None and value != "":
                data[field_mapping.target] = value

        # Need at least account number or IBAN
        if not data.get("account_number") and not data.get("iban"):
            return None

        # Check for duplicates
        dedup_result = self.deduplicator.find_account(
            account_number=data.get("account_number", ""),
            owner_id=data.get("owner_id"),
            iban=data.get("iban"),
        )

        if dedup_result.is_duplicate:
            return ExtractedEntity(
                entity_type="account",
                entity_id=dedup_result.existing_id,
                role=mapping.role,
                is_new=False,
                data=data,
                source_stg_id=stg_id,
                match_info=dedup_result,
            )
        else:
            account_id = str(uuid.uuid4())
            data["account_id"] = account_id
            data["source_system"] = self.source_system
            data["source_stg_id"] = stg_id

            self.deduplicator.register_account(
                account_id=account_id,
                account_number=data.get("account_number", ""),
                owner_id=data.get("owner_id"),
                iban=data.get("iban"),
            )

            return ExtractedEntity(
                entity_type="account",
                entity_id=account_id,
                role=mapping.role,
                is_new=True,
                data=data,
                source_stg_id=stg_id,
            )

    def _extract_financial_institution(
        self,
        record: Dict[str, Any],
        mapping: EntityMapping,
        stg_id: str,
    ) -> Optional[ExtractedEntity]:
        """Extract a financial institution entity from a staging record."""
        data = {}
        prefix = mapping.source_prefix or ""

        for field_mapping in mapping.fields:
            source_col = f"{prefix}{field_mapping.source}" if prefix else field_mapping.source
            value = record.get(source_col)
            if value is not None and value != "":
                data[field_mapping.target] = value

        # Need at least BIC, LEI, or clearing code
        if not data.get("bic") and not data.get("lei") and not data.get("national_clearing_code"):
            return None

        # Check for duplicates
        dedup_result = self.deduplicator.find_financial_institution(
            bic=data.get("bic"),
            lei=data.get("lei"),
            clearing_code=data.get("national_clearing_code"),
            clearing_system=data.get("national_clearing_system"),
            country=data.get("country"),
        )

        if dedup_result.is_duplicate:
            return ExtractedEntity(
                entity_type="financial_institution",
                entity_id=dedup_result.existing_id,
                role=mapping.role,
                is_new=False,
                data=data,
                source_stg_id=stg_id,
                match_info=dedup_result,
            )
        else:
            fi_id = str(uuid.uuid4())
            data["fi_id"] = fi_id
            data["source_system"] = self.source_system

            # Set institution_name from BIC if not provided
            if not data.get("institution_name") and data.get("bic"):
                data["institution_name"] = f"FI_{data['bic']}"

            self.deduplicator.register_financial_institution(
                fi_id=fi_id,
                bic=data.get("bic"),
                lei=data.get("lei"),
                clearing_code=data.get("national_clearing_code"),
                clearing_system=data.get("national_clearing_system"),
                country=data.get("country"),
            )

            return ExtractedEntity(
                entity_type="financial_institution",
                entity_id=fi_id,
                role=mapping.role,
                is_new=True,
                data=data,
                source_stg_id=stg_id,
            )

    def persist_entities(
        self,
        result: ExtractionResult,
        source_message_type: str,
    ) -> Dict[str, int]:
        """
        Persist extracted entities to the database.

        Args:
            result: Extraction result with entities
            source_message_type: Source message type for lineage

        Returns:
            Dict with counts of inserted entities
        """
        if not self.db:
            raise ValueError("Database connection required for persistence")

        counts = {"parties": 0, "accounts": 0, "financial_institutions": 0}
        cursor = self.db.cursor()

        try:
            # Insert new parties
            for party in result.parties:
                if party.is_new:
                    self._insert_party(cursor, party, source_message_type)
                    counts["parties"] += 1

            # Insert new accounts
            for account in result.accounts:
                if account.is_new:
                    self._insert_account(cursor, account, source_message_type)
                    counts["accounts"] += 1

            # Insert new financial institutions
            for fi in result.financial_institutions:
                if fi.is_new:
                    self._insert_financial_institution(cursor, fi, source_message_type)
                    counts["financial_institutions"] += 1

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise
        finally:
            cursor.close()

        return counts

    def _insert_party(self, cursor, entity: ExtractedEntity, source_message_type: str):
        """Insert a party record."""
        data = entity.data

        # Determine identification type and number
        # Use explicit identification_type if provided, otherwise infer from lei field
        id_type = data.get("identification_type")
        id_number = data.get("lei")  # lei field holds the identifier value

        if not id_type and id_number:
            # Default to LEI if we have an identifier but no type
            id_type = "LEI"

        if not id_number and data.get("registration_number"):
            id_type = "REG"
            id_number = data.get("registration_number")

        sql = """
            INSERT INTO gold.cdm_party (
                party_id, party_type, name,
                identification_type, identification_number, identification_country,
                registration_number, registration_country,
                street_name, building_number, post_code, town_name,
                country_sub_division, country,
                date_of_birth, place_of_birth, nationality,
                source_system, source_message_type, source_stg_id,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT (party_id) DO NOTHING
        """
        cursor.execute(sql, (
            data.get("party_id"),
            data.get("party_type", "UNKNOWN"),
            data.get("name"),
            id_type,
            id_number,
            data.get("country"),  # identification_country
            data.get("registration_number"),
            data.get("country"),  # registration_country
            data.get("street_name"),
            data.get("building_number"),
            data.get("post_code"),
            data.get("town_name"),
            data.get("country_sub_division"),
            data.get("country", "XX"),
            data.get("date_of_birth"),
            data.get("place_of_birth"),
            data.get("nationality"),
            self.source_system,
            source_message_type,
            entity.source_stg_id,
        ))

    def _insert_account(self, cursor, entity: ExtractedEntity, source_message_type: str):
        """Insert an account record."""
        data = entity.data
        sql = """
            INSERT INTO gold.cdm_account (
                account_id, account_number, iban,
                account_type, currency, owner_id,
                account_status,
                source_system, source_message_type, source_stg_id,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s,
                %s, %s, %s,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT (account_id) DO NOTHING
        """
        cursor.execute(sql, (
            data.get("account_id"),
            data.get("account_number", "UNKNOWN"),
            data.get("iban"),
            data.get("account_type", "UNKNOWN"),
            data.get("currency", "XXX"),
            data.get("owner_id"),
            data.get("account_status", "ACTIVE"),
            self.source_system,
            source_message_type,
            entity.source_stg_id,
        ))

    def _insert_financial_institution(self, cursor, entity: ExtractedEntity, source_message_type: str):
        """Insert a financial institution record."""
        data = entity.data
        sql = """
            INSERT INTO gold.cdm_financial_institution (
                fi_id, institution_name, bic, lei,
                national_clearing_code, national_clearing_system,
                country,
                source_system,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s,
                %s,
                %s,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT (fi_id) DO NOTHING
        """
        cursor.execute(sql, (
            data.get("fi_id"),
            data.get("institution_name", "Unknown Institution"),
            data.get("bic"),
            data.get("lei"),
            data.get("national_clearing_code"),
            data.get("national_clearing_system"),
            data.get("country", "XX"),
            self.source_system,
        ))


def get_entity_ids_for_instruction(
    extraction_result: ExtractionResult,
) -> Dict[str, Optional[str]]:
    """
    Get entity IDs to link to payment instruction.

    Returns dict with debtor_id, creditor_id, debtor_agent_id, creditor_agent_id,
    debtor_account_id, creditor_account_id.
    """
    ids = {
        "debtor_id": None,
        "creditor_id": None,
        "debtor_agent_id": None,
        "creditor_agent_id": None,
        "debtor_account_id": None,
        "creditor_account_id": None,
    }

    # Map parties by role
    for party in extraction_result.parties:
        if party.role == "debtor":
            ids["debtor_id"] = party.entity_id
        elif party.role == "creditor":
            ids["creditor_id"] = party.entity_id

    # Map accounts by role
    for account in extraction_result.accounts:
        if account.role == "debtor_account":
            ids["debtor_account_id"] = account.entity_id
        elif account.role == "creditor_account":
            ids["creditor_account_id"] = account.entity_id

    # Map FIs by role
    for fi in extraction_result.financial_institutions:
        if fi.role in ("debtor_agent", "instructing_agent"):
            ids["debtor_agent_id"] = fi.entity_id
        elif fi.role in ("creditor_agent", "instructed_agent"):
            ids["creditor_agent_id"] = fi.entity_id

    return ids

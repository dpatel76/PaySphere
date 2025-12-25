"""
GPS CDM - Reference Data Deduplication Service
===============================================

Provides deduplication logic for reference data entities (party, account, FI)
to prevent duplicate inserts when the same entity appears in multiple messages.

Uses natural keys for matching:
- Party: name + country + party_type, or LEI, or registration_number
- Account: account_number + owner_id, or IBAN
- Financial Institution: BIC, or national_clearing_code + country

Supports:
- Exact match (find existing)
- Fuzzy match (optional, for name variations)
- Upsert pattern (update if exists, insert if not)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import hashlib


@dataclass
class DeduplicationResult:
    """Result of deduplication check."""
    is_duplicate: bool
    existing_id: Optional[str] = None
    match_type: Optional[str] = None  # "exact", "lei", "bic", "fuzzy"
    confidence: float = 1.0
    matched_on: Optional[List[str]] = None


class ReferenceDataDeduplicator:
    """
    Deduplicates reference data entities across messages.

    Maintains a cache of seen entities and uses natural keys
    to identify duplicates.

    Usage:
        dedup = ReferenceDataDeduplicator(db_connection)

        # Check if party exists
        result = dedup.find_party(
            name="John Doe",
            country="US",
            party_type="INDIVIDUAL"
        )

        if result.is_duplicate:
            party_id = result.existing_id
        else:
            party_id = insert_new_party(...)
            dedup.register_party(party_id, name, country, party_type)
    """

    def __init__(self, db_connection=None, enable_fuzzy: bool = False):
        """
        Initialize deduplicator.

        Args:
            db_connection: Database connection for persistence lookups
            enable_fuzzy: Enable fuzzy matching for names (slower but catches variations)
        """
        self.db = db_connection
        self.enable_fuzzy = enable_fuzzy

        # In-memory cache for fast lookups within batch
        self._party_cache: Dict[str, str] = {}  # natural_key -> party_id
        self._account_cache: Dict[str, str] = {}
        self._fi_cache: Dict[str, str] = {}

    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison."""
        if not name:
            return ""
        return " ".join(name.upper().strip().split())

    def _make_party_key(
        self,
        name: str,
        country: str,
        party_type: str,
        lei: Optional[str] = None,
        bic: Optional[str] = None,
        registration_number: Optional[str] = None,
    ) -> str:
        """Create natural key for party deduplication."""
        # Prefer strong identifiers
        if lei:
            return f"LEI:{lei.upper()}"
        if bic:
            return f"BIC:{bic.upper()}"
        if registration_number:
            return f"REG:{registration_number.upper()}:{country.upper()}"

        # Fall back to name-based key
        norm_name = self._normalize_name(name)
        return f"NAME:{norm_name}:{country.upper()}:{party_type.upper()}"

    def _make_account_key(
        self,
        account_number: str,
        owner_id: Optional[str] = None,
        iban: Optional[str] = None,
    ) -> str:
        """Create natural key for account deduplication."""
        if iban:
            return f"IBAN:{iban.upper().replace(' ', '')}"
        if owner_id:
            return f"ACCT:{account_number}:{owner_id}"
        return f"ACCT:{account_number}"

    def _make_fi_key(
        self,
        bic: Optional[str] = None,
        lei: Optional[str] = None,
        clearing_code: Optional[str] = None,
        clearing_system: Optional[str] = None,
        country: Optional[str] = None,
    ) -> str:
        """Create natural key for financial institution deduplication."""
        if bic:
            return f"BIC:{bic.upper()}"
        if lei:
            return f"LEI:{lei.upper()}"
        if clearing_code and country:
            system = clearing_system or "DEFAULT"
            return f"CLEARING:{clearing_code}:{system}:{country.upper()}"
        return None

    def find_party(
        self,
        name: str,
        country: str,
        party_type: str,
        lei: Optional[str] = None,
        bic: Optional[str] = None,
        registration_number: Optional[str] = None,
    ) -> DeduplicationResult:
        """
        Find existing party matching the given attributes.

        Args:
            name: Party name
            country: Country code
            party_type: INDIVIDUAL or ORGANIZATION
            lei: Legal Entity Identifier (if available)
            bic: BIC code (if available)
            registration_number: Company registration number

        Returns:
            DeduplicationResult indicating if duplicate exists
        """
        natural_key = self._make_party_key(
            name, country, party_type, lei, bic, registration_number
        )

        # Check cache first
        if natural_key in self._party_cache:
            match_type = natural_key.split(":")[0].lower()
            return DeduplicationResult(
                is_duplicate=True,
                existing_id=self._party_cache[natural_key],
                match_type=match_type,
                confidence=1.0,
                matched_on=[natural_key.split(":")[0]],
            )

        # Check database if connection available
        if self.db:
            existing_id = self._db_find_party(
                name, country, party_type, lei, bic, registration_number
            )
            if existing_id:
                # Cache for future lookups
                self._party_cache[natural_key] = existing_id
                return DeduplicationResult(
                    is_duplicate=True,
                    existing_id=existing_id,
                    match_type="db_lookup",
                    confidence=1.0,
                )

        return DeduplicationResult(is_duplicate=False)

    def _db_find_party(
        self,
        name: str,
        country: str,
        party_type: str,
        lei: Optional[str] = None,
        bic: Optional[str] = None,
        registration_number: Optional[str] = None,
    ) -> Optional[str]:
        """Find party in database using natural keys."""
        if not self.db:
            return None

        # Build query with priority: LEI > Registration > Name
        # Note: Schema uses identification_type/identification_number for LEI
        conditions = []
        params = []

        if lei:
            conditions.append("identification_type = 'LEI' AND identification_number = %s")
            params.append(lei.upper())
        elif registration_number:
            conditions.append("registration_number = %s AND country = %s")
            params.extend([registration_number.upper(), country.upper()])
        else:
            # Name-based matching
            norm_name = self._normalize_name(name)
            conditions.append(
                "UPPER(TRIM(name)) = %s AND UPPER(country) = %s AND UPPER(party_type) = %s"
            )
            params.extend([norm_name, country.upper(), party_type.upper()])

        query = f"""
            SELECT party_id FROM gold.cdm_party
            WHERE ({' OR '.join(conditions)})
            AND is_current = true
            LIMIT 1
        """

        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception:
            return None

    def register_party(
        self,
        party_id: str,
        name: str,
        country: str,
        party_type: str,
        lei: Optional[str] = None,
        bic: Optional[str] = None,
        registration_number: Optional[str] = None,
    ) -> None:
        """Register a newly inserted party in the cache."""
        natural_key = self._make_party_key(
            name, country, party_type, lei, bic, registration_number
        )
        self._party_cache[natural_key] = party_id

    def find_account(
        self,
        account_number: str,
        owner_id: Optional[str] = None,
        iban: Optional[str] = None,
    ) -> DeduplicationResult:
        """Find existing account matching the given attributes."""
        natural_key = self._make_account_key(account_number, owner_id, iban)

        if natural_key in self._account_cache:
            return DeduplicationResult(
                is_duplicate=True,
                existing_id=self._account_cache[natural_key],
                match_type="cache",
            )

        if self.db:
            existing_id = self._db_find_account(account_number, owner_id, iban)
            if existing_id:
                self._account_cache[natural_key] = existing_id
                return DeduplicationResult(
                    is_duplicate=True,
                    existing_id=existing_id,
                    match_type="db_lookup",
                )

        return DeduplicationResult(is_duplicate=False)

    def _db_find_account(
        self,
        account_number: str,
        owner_id: Optional[str] = None,
        iban: Optional[str] = None,
    ) -> Optional[str]:
        """Find account in database."""
        if not self.db:
            return None

        conditions = []
        params = []

        if iban:
            conditions.append("iban = %s")
            params.append(iban.upper().replace(" ", ""))
        elif owner_id:
            conditions.append("account_number = %s AND owner_id = %s")
            params.extend([account_number, owner_id])
        else:
            conditions.append("account_number = %s")
            params.append(account_number)

        query = f"""
            SELECT account_id FROM gold.cdm_account
            WHERE {' OR '.join(conditions)}
            AND is_current = true
            LIMIT 1
        """

        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception:
            return None

    def register_account(
        self,
        account_id: str,
        account_number: str,
        owner_id: Optional[str] = None,
        iban: Optional[str] = None,
    ) -> None:
        """Register a newly inserted account in the cache."""
        natural_key = self._make_account_key(account_number, owner_id, iban)
        self._account_cache[natural_key] = account_id

    def find_financial_institution(
        self,
        bic: Optional[str] = None,
        lei: Optional[str] = None,
        clearing_code: Optional[str] = None,
        clearing_system: Optional[str] = None,
        country: Optional[str] = None,
    ) -> DeduplicationResult:
        """Find existing financial institution."""
        natural_key = self._make_fi_key(
            bic, lei, clearing_code, clearing_system, country
        )

        if not natural_key:
            return DeduplicationResult(is_duplicate=False)

        if natural_key in self._fi_cache:
            return DeduplicationResult(
                is_duplicate=True,
                existing_id=self._fi_cache[natural_key],
                match_type="cache",
            )

        if self.db:
            existing_id = self._db_find_fi(
                bic, lei, clearing_code, clearing_system, country
            )
            if existing_id:
                self._fi_cache[natural_key] = existing_id
                return DeduplicationResult(
                    is_duplicate=True,
                    existing_id=existing_id,
                    match_type="db_lookup",
                )

        return DeduplicationResult(is_duplicate=False)

    def _db_find_fi(
        self,
        bic: Optional[str] = None,
        lei: Optional[str] = None,
        clearing_code: Optional[str] = None,
        clearing_system: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Optional[str]:
        """Find financial institution in database."""
        if not self.db:
            return None

        conditions = []
        params = []

        if bic:
            conditions.append("bic = %s")
            params.append(bic.upper())
        if lei:
            conditions.append("lei = %s")
            params.append(lei.upper())
        if clearing_code and country:
            cond = "national_clearing_code = %s AND country = %s"
            if clearing_system:
                cond += " AND national_clearing_system = %s"
                params.append(clearing_system)
            conditions.append(cond)
            params.extend([clearing_code, country.upper()])

        if not conditions:
            return None

        query = f"""
            SELECT fi_id FROM gold.cdm_financial_institution
            WHERE {' OR '.join(conditions)}
            AND is_current = true
            LIMIT 1
        """

        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception:
            return None

    def register_financial_institution(
        self,
        fi_id: str,
        bic: Optional[str] = None,
        lei: Optional[str] = None,
        clearing_code: Optional[str] = None,
        clearing_system: Optional[str] = None,
        country: Optional[str] = None,
    ) -> None:
        """Register a newly inserted FI in the cache."""
        natural_key = self._make_fi_key(
            bic, lei, clearing_code, clearing_system, country
        )
        if natural_key:
            self._fi_cache[natural_key] = fi_id

    def clear_cache(self) -> None:
        """Clear all caches (call between batches)."""
        self._party_cache.clear()
        self._account_cache.clear()
        self._fi_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "party_cache_size": len(self._party_cache),
            "account_cache_size": len(self._account_cache),
            "fi_cache_size": len(self._fi_cache),
        }


def create_upsert_sql(
    table: str,
    columns: List[str],
    conflict_columns: List[str],
    update_columns: Optional[List[str]] = None,
) -> str:
    """
    Generate PostgreSQL UPSERT (INSERT ... ON CONFLICT) SQL.

    Args:
        table: Target table name
        columns: All columns to insert
        conflict_columns: Columns for conflict detection
        update_columns: Columns to update on conflict (None = do nothing)

    Returns:
        SQL statement string
    """
    col_list = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    conflict_list = ", ".join(conflict_columns)

    if update_columns:
        updates = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_columns])
        return f"""
            INSERT INTO {table} ({col_list})
            VALUES ({placeholders})
            ON CONFLICT ({conflict_list})
            DO UPDATE SET {updates}, updated_at = CURRENT_TIMESTAMP
            RETURNING *
        """
    else:
        return f"""
            INSERT INTO {table} ({col_list})
            VALUES ({placeholders})
            ON CONFLICT ({conflict_list})
            DO NOTHING
            RETURNING *
        """

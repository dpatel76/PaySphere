"""
GPS CDM - Reconciliation Service
=================================

Reconciles source (Bronze) records with target (Gold) records to ensure
data integrity across the medallion pipeline. Identifies mismatches,
orphans, and data drift.

Usage:
    recon = ReconciliationService(db_connection)

    # Run reconciliation for a batch
    result = recon.reconcile_batch(batch_id)

    # Get mismatches
    mismatches = recon.get_mismatches(batch_id)

    # Get orphan records (Bronze without Gold)
    orphans = recon.get_orphans(direction="bronze")
"""

import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class MatchStatus(str, Enum):
    """Reconciliation match status."""
    MATCHED = "MATCHED"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISMATCHED = "MISMATCHED"
    BRONZE_ONLY = "BRONZE_ONLY"
    GOLD_ONLY = "GOLD_ONLY"
    MULTIPLE_MATCHES = "MULTIPLE_MATCHES"


class InvestigationStatus(str, Enum):
    """Investigation status for mismatches."""
    NOT_INVESTIGATED = "NOT_INVESTIGATED"
    INVESTIGATING = "INVESTIGATING"
    INVESTIGATED = "INVESTIGATED"
    REQUIRES_ACTION = "REQUIRES_ACTION"


class ResolutionAction(str, Enum):
    """Resolution action for mismatches."""
    ACCEPTED = "ACCEPTED"
    CORRECTED = "CORRECTED"
    REJECTED = "REJECTED"
    REPROCESSED = "REPROCESSED"
    MANUAL_FIX = "MANUAL_FIX"


@dataclass
class FieldComparison:
    """Comparison result for a single field."""
    field_name: str
    bronze_value: Any
    gold_value: Any
    matched: bool
    transformation_expected: bool = False


@dataclass
class RecordReconciliation:
    """Reconciliation result for a single record."""
    recon_id: str
    bronze_raw_id: str
    silver_stg_id: Optional[str]
    gold_instruction_id: Optional[str]
    match_status: str
    field_comparisons: List[FieldComparison]
    mismatched_fields: List[str]
    match_rate: float  # Percentage of fields that matched


@dataclass
class ReconciliationRunResult:
    """Result of a reconciliation run."""
    recon_run_id: str
    batch_id: Optional[str]
    status: str
    total_source_records: int
    total_target_records: int
    matched_count: int
    partial_match_count: int
    mismatched_count: int
    source_only_count: int
    target_only_count: int
    match_rate: float
    started_at: datetime
    completed_at: Optional[datetime] = None


# Fields to compare between Bronze/Silver and Gold
# Format: (bronze_field, gold_field, is_key_field, allow_transformation)
RECONCILIATION_FIELDS = [
    # Key fields (must match exactly)
    ("end_to_end_id", "end_to_end_id", True, False),
    ("uetr", "uetr", True, False),

    # Amount fields (compare with tolerance)
    ("instructed_amount", "instructed_amount", False, False),
    ("instructed_currency", "instructed_currency", False, False),

    # Party fields (may have transformations)
    ("debtor_name", "debtor_name", False, True),
    ("creditor_name", "creditor_name", False, True),

    # Date fields
    ("creation_date_time", "creation_datetime", False, True),
    ("requested_execution_date", "execution_date", False, True),

    # Other fields
    ("charge_bearer", "charge_bearer", False, False),
]


class ReconciliationService:
    """
    Reconciles Bronze source with Gold target.

    Compares key fields between source and target records,
    identifies mismatches, and provides investigation/resolution workflow.
    """

    def __init__(self, db_connection):
        """
        Initialize the reconciliation service.

        Args:
            db_connection: Database connection (psycopg2 or compatible)
        """
        self.db = db_connection

    def start_reconciliation_run(
        self,
        batch_id: Optional[str] = None,
        initiated_by: Optional[str] = None,
    ) -> str:
        """Start a new reconciliation run."""
        recon_run_id = str(uuid.uuid4())

        sql = """
            INSERT INTO observability.obs_reconciliation_runs (
                recon_run_id, batch_id, status, initiated_by, started_at
            ) VALUES (%s, %s, 'RUNNING', %s, CURRENT_TIMESTAMP)
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (recon_run_id, batch_id, initiated_by))
            self.db.commit()
            return recon_run_id
        finally:
            cursor.close()

    def complete_reconciliation_run(
        self,
        recon_run_id: str,
        result: ReconciliationRunResult,
    ):
        """Complete a reconciliation run with results."""
        sql = """
            UPDATE observability.obs_reconciliation_runs
            SET status = %s,
                completed_at = CURRENT_TIMESTAMP,
                total_source_records = %s,
                total_target_records = %s,
                matched_count = %s,
                partial_match_count = %s,
                mismatched_count = %s,
                source_only_count = %s,
                target_only_count = %s,
                match_rate = %s
            WHERE recon_run_id = %s
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                result.status,
                result.total_source_records,
                result.total_target_records,
                result.matched_count,
                result.partial_match_count,
                result.mismatched_count,
                result.source_only_count,
                result.target_only_count,
                result.match_rate,
                recon_run_id,
            ))
            self.db.commit()
        finally:
            cursor.close()

    def reconcile_batch(
        self,
        batch_id: str,
        initiated_by: Optional[str] = None,
    ) -> ReconciliationRunResult:
        """
        Reconcile all records in a batch.

        Compares Bronze source records with their corresponding Gold targets.

        Args:
            batch_id: Batch identifier
            initiated_by: User or system initiating reconciliation

        Returns:
            ReconciliationRunResult with summary statistics
        """
        recon_run_id = self.start_reconciliation_run(batch_id, initiated_by)

        result = ReconciliationRunResult(
            recon_run_id=recon_run_id,
            batch_id=batch_id,
            status="RUNNING",
            total_source_records=0,
            total_target_records=0,
            matched_count=0,
            partial_match_count=0,
            mismatched_count=0,
            source_only_count=0,
            target_only_count=0,
            match_rate=0.0,
            started_at=datetime.now(),
        )

        try:
            # Get source records (Bronze → Silver chain)
            source_records = self._get_source_records(batch_id)
            result.total_source_records = len(source_records)

            # Get target records (Gold)
            target_records = self._get_target_records(batch_id)
            result.total_target_records = len(target_records)

            # Build target lookup by key
            target_by_key = self._build_target_lookup(target_records)

            # Reconcile each source record
            for source in source_records:
                record_result = self._reconcile_record(
                    source, target_by_key, recon_run_id, batch_id
                )

                if record_result.match_status == MatchStatus.MATCHED.value:
                    result.matched_count += 1
                elif record_result.match_status == MatchStatus.PARTIAL_MATCH.value:
                    result.partial_match_count += 1
                elif record_result.match_status == MatchStatus.MISMATCHED.value:
                    result.mismatched_count += 1
                elif record_result.match_status == MatchStatus.BRONZE_ONLY.value:
                    result.source_only_count += 1
                elif record_result.match_status == MatchStatus.MULTIPLE_MATCHES.value:
                    result.mismatched_count += 1

                # Store reconciliation result
                self._store_reconciliation_result(record_result, recon_run_id, batch_id)

                # Update Gold record reconciliation status
                if record_result.gold_instruction_id:
                    self._update_gold_recon_status(
                        record_result.gold_instruction_id,
                        record_result.match_status
                    )

            # Check for Gold records without Bronze (shouldn't happen normally)
            result.target_only_count = self._count_gold_only_records(batch_id, target_by_key)

            # Calculate match rate
            if result.total_source_records > 0:
                result.match_rate = (
                    (result.matched_count + result.partial_match_count)
                    / result.total_source_records * 100
                )

            result.status = "COMPLETED"
            result.completed_at = datetime.now()

        except Exception as e:
            result.status = "FAILED"
            raise
        finally:
            self.complete_reconciliation_run(recon_run_id, result)

        return result

    def _get_source_records(self, batch_id: str) -> List[Dict]:
        """Get Bronze/Silver source records for reconciliation."""
        sql = """
            SELECT
                b.raw_id,
                b.message_type,
                s.stg_id,
                s.end_to_end_id,
                s.uetr,
                s.instructed_amount,
                s.instructed_currency,
                s.debtor_name,
                s.creditor_name,
                s.creation_date_time,
                s.requested_execution_date,
                s.charge_bearer,
                s.gold_instruction_id
            FROM bronze.raw_payment_messages b
            LEFT JOIN silver.stg_pain001 s ON b.silver_stg_id = s.stg_id
            WHERE b._batch_id = %s
              AND b.processing_status = 'PROCESSED'
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (batch_id,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def _get_target_records(self, batch_id: str) -> List[Dict]:
        """Get Gold target records for reconciliation."""
        sql = """
            SELECT
                instruction_id,
                payment_id,
                end_to_end_id,
                uetr,
                instructed_amount,
                instructed_currency,
                debtor_id,
                creditor_id,
                creation_datetime,
                requested_execution_date,
                charge_bearer,
                source_stg_id,
                lineage_batch_id
            FROM gold.cdm_payment_instruction
            WHERE lineage_batch_id = %s
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (batch_id,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def _build_target_lookup(self, target_records: List[Dict]) -> Dict[str, List[Dict]]:
        """Build lookup dictionary for target records by key."""
        lookup = {}
        for record in target_records:
            # Use end_to_end_id as primary key
            key = record.get('end_to_end_id')
            if key:
                if key not in lookup:
                    lookup[key] = []
                lookup[key].append(record)

            # Also index by source_stg_id
            stg_key = record.get('source_stg_id')
            if stg_key:
                stg_lookup_key = f"stg:{stg_key}"
                if stg_lookup_key not in lookup:
                    lookup[stg_lookup_key] = []
                lookup[stg_lookup_key].append(record)

        return lookup

    def _reconcile_record(
        self,
        source: Dict,
        target_lookup: Dict[str, List[Dict]],
        recon_run_id: str,
        batch_id: str,
    ) -> RecordReconciliation:
        """Reconcile a single source record with target."""
        recon_id = str(uuid.uuid4())
        bronze_raw_id = source.get('raw_id')
        silver_stg_id = source.get('stg_id')
        end_to_end_id = source.get('end_to_end_id')

        # Find matching target
        targets = []
        if end_to_end_id:
            targets = target_lookup.get(end_to_end_id, [])
        if not targets and silver_stg_id:
            targets = target_lookup.get(f"stg:{silver_stg_id}", [])

        if not targets:
            # No target found
            return RecordReconciliation(
                recon_id=recon_id,
                bronze_raw_id=bronze_raw_id,
                silver_stg_id=silver_stg_id,
                gold_instruction_id=None,
                match_status=MatchStatus.BRONZE_ONLY.value,
                field_comparisons=[],
                mismatched_fields=[],
                match_rate=0.0,
            )

        if len(targets) > 1:
            # Multiple matches
            return RecordReconciliation(
                recon_id=recon_id,
                bronze_raw_id=bronze_raw_id,
                silver_stg_id=silver_stg_id,
                gold_instruction_id=targets[0].get('instruction_id'),
                match_status=MatchStatus.MULTIPLE_MATCHES.value,
                field_comparisons=[],
                mismatched_fields=['MULTIPLE_GOLD_RECORDS'],
                match_rate=0.0,
            )

        target = targets[0]
        gold_instruction_id = target.get('instruction_id')

        # Compare fields
        comparisons = []
        mismatched_fields = []
        matched_count = 0
        total_count = 0

        for bronze_field, gold_field, is_key, allow_transform in RECONCILIATION_FIELDS:
            source_value = source.get(bronze_field)
            target_value = target.get(gold_field)

            # Normalize values for comparison
            matched = self._compare_values(source_value, target_value, allow_transform)

            if matched:
                matched_count += 1
            else:
                mismatched_fields.append(bronze_field)

            total_count += 1

            comparisons.append(FieldComparison(
                field_name=bronze_field,
                bronze_value=source_value,
                gold_value=target_value,
                matched=matched,
                transformation_expected=allow_transform,
            ))

        match_rate = (matched_count / total_count * 100) if total_count > 0 else 0

        # Determine match status
        if match_rate == 100:
            match_status = MatchStatus.MATCHED.value
        elif match_rate >= 80:
            match_status = MatchStatus.PARTIAL_MATCH.value
        else:
            match_status = MatchStatus.MISMATCHED.value

        return RecordReconciliation(
            recon_id=recon_id,
            bronze_raw_id=bronze_raw_id,
            silver_stg_id=silver_stg_id,
            gold_instruction_id=gold_instruction_id,
            match_status=match_status,
            field_comparisons=comparisons,
            mismatched_fields=mismatched_fields,
            match_rate=match_rate,
        )

    def _compare_values(
        self,
        source_value: Any,
        target_value: Any,
        allow_transform: bool = False,
    ) -> bool:
        """Compare two values with optional transformation tolerance."""
        # Handle None/NULL
        if source_value is None and target_value is None:
            return True
        if source_value is None or target_value is None:
            return False

        # Normalize strings
        if isinstance(source_value, str) and isinstance(target_value, str):
            source_norm = source_value.strip().upper()
            target_norm = target_value.strip().upper()
            return source_norm == target_norm

        # Compare numbers with tolerance
        if isinstance(source_value, (int, float, Decimal)) and \
           isinstance(target_value, (int, float, Decimal)):
            try:
                diff = abs(float(source_value) - float(target_value))
                return diff < 0.01  # Allow small rounding differences
            except (TypeError, ValueError):
                return False

        # Compare dates (may have different formats)
        if allow_transform:
            try:
                source_str = str(source_value)[:10]  # YYYY-MM-DD
                target_str = str(target_value)[:10]
                return source_str == target_str
            except Exception:
                pass

        # Default comparison
        return str(source_value) == str(target_value)

    def _store_reconciliation_result(
        self,
        result: RecordReconciliation,
        recon_run_id: str,
        batch_id: str,
    ):
        """Store reconciliation result in database."""
        # Convert field comparisons to JSON
        field_comparisons = {}
        for comp in result.field_comparisons:
            field_comparisons[comp.field_name] = {
                "bronze": str(comp.bronze_value) if comp.bronze_value else None,
                "gold": str(comp.gold_value) if comp.gold_value else None,
                "matched": comp.matched,
            }

        sql = """
            INSERT INTO observability.obs_reconciliation_results (
                recon_id, recon_run_id, batch_id,
                bronze_raw_id, silver_stg_id, gold_instruction_id,
                match_status,
                field_comparisons, mismatched_fields,
                total_fields_compared, fields_matched,
                reconciled_at
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s,
                %s, %s,
                %s, %s,
                CURRENT_TIMESTAMP
            )
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                result.recon_id,
                recon_run_id,
                batch_id,
                result.bronze_raw_id,
                result.silver_stg_id,
                result.gold_instruction_id,
                result.match_status,
                json.dumps(field_comparisons),
                result.mismatched_fields,
                len(result.field_comparisons),
                len([c for c in result.field_comparisons if c.matched]),
            ))
            self.db.commit()
        finally:
            cursor.close()

    def _update_gold_recon_status(self, instruction_id: str, status: str):
        """Update reconciliation status on Gold record."""
        recon_status = "MATCHED" if status in ("MATCHED", "PARTIAL_MATCH") else "MISMATCHED"

        sql = """
            UPDATE gold.cdm_payment_instruction
            SET reconciliation_status = %s,
                reconciled_at = CURRENT_TIMESTAMP
            WHERE instruction_id = %s
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (recon_status, instruction_id))
            self.db.commit()
        finally:
            cursor.close()

    def _count_gold_only_records(
        self,
        batch_id: str,
        target_lookup: Dict[str, List[Dict]],
    ) -> int:
        """Count Gold records that don't have a Bronze source."""
        # This is unusual - Gold records should always come from Bronze
        # But we check anyway for data integrity
        sql = """
            SELECT COUNT(*)
            FROM gold.cdm_payment_instruction g
            WHERE g.lineage_batch_id = %s
              AND NOT EXISTS (
                  SELECT 1 FROM silver.stg_pain001 s
                  WHERE s.stg_id = g.source_stg_id
              )
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (batch_id,))
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    def get_mismatches(
        self,
        batch_id: Optional[str] = None,
        status: Optional[str] = None,
        investigation_status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get reconciliation mismatches with filters."""
        conditions = ["match_status NOT IN ('MATCHED')"]
        params = []

        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)
        if status:
            conditions.append("match_status = %s")
            params.append(status)
        if investigation_status:
            conditions.append("investigation_status = %s")
            params.append(investigation_status)

        sql = f"""
            SELECT recon_id, recon_run_id, batch_id,
                   bronze_raw_id, silver_stg_id, gold_instruction_id,
                   match_status, field_comparisons, mismatched_fields,
                   investigation_status, investigation_notes,
                   resolution_action, resolution_notes,
                   reconciled_at
            FROM observability.obs_reconciliation_results
            WHERE {' AND '.join(conditions)}
            ORDER BY reconciled_at DESC
            LIMIT %s
        """
        params.append(limit)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def get_orphans(
        self,
        direction: str = "bronze",
        batch_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get orphan records.

        Args:
            direction: "bronze" for Bronze without Gold, "gold" for Gold without Bronze
            batch_id: Optional batch filter
            limit: Max records to return
        """
        if direction == "bronze":
            # Bronze records that didn't make it to Gold
            sql = """
                SELECT
                    b.raw_id,
                    b.message_type,
                    b.processing_status,
                    b.processing_error,
                    s.stg_id,
                    s.processing_status as silver_status,
                    s.gold_instruction_id,
                    b._batch_id as batch_id
                FROM bronze.raw_payment_messages b
                LEFT JOIN silver.stg_pain001 s ON b.silver_stg_id = s.stg_id
                WHERE (s.gold_instruction_id IS NULL OR s.stg_id IS NULL)
            """
            if batch_id:
                sql += " AND b._batch_id = %s"
            sql += " ORDER BY b.ingestion_timestamp DESC LIMIT %s"
        else:
            # Gold records without Bronze source (shouldn't happen)
            sql = """
                SELECT
                    g.instruction_id,
                    g.end_to_end_id,
                    g.source_stg_id,
                    g.lineage_batch_id as batch_id
                FROM gold.cdm_payment_instruction g
                LEFT JOIN silver.stg_pain001 s ON g.source_stg_id = s.stg_id
                WHERE s.stg_id IS NULL
            """
            if batch_id:
                sql += " AND g.lineage_batch_id = %s"
            sql += " ORDER BY g.created_at DESC LIMIT %s"

        params = []
        if batch_id:
            params.append(batch_id)
        params.append(limit)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def investigate_mismatch(
        self,
        recon_id: str,
        notes: str,
        investigated_by: str,
        status: str = InvestigationStatus.INVESTIGATED.value,
    ) -> bool:
        """Mark a mismatch as investigated."""
        sql = """
            UPDATE observability.obs_reconciliation_results
            SET investigation_status = %s,
                investigation_notes = %s,
                investigated_by = %s,
                investigated_at = CURRENT_TIMESTAMP
            WHERE recon_id = %s
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (status, notes, investigated_by, recon_id))
            self.db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def resolve_mismatch(
        self,
        recon_id: str,
        action: str,
        notes: str,
        resolved_by: str,
    ) -> bool:
        """Resolve a mismatch with an action."""
        sql = """
            UPDATE observability.obs_reconciliation_results
            SET resolution_action = %s,
                resolution_notes = %s,
                resolved_by = %s,
                resolved_at = CURRENT_TIMESTAMP,
                investigation_status = %s
            WHERE recon_id = %s
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                action, notes, resolved_by,
                InvestigationStatus.INVESTIGATED.value,
                recon_id
            ))
            self.db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def accept_mismatch(
        self,
        recon_id: str,
        notes: str,
        accepted_by: str,
    ) -> bool:
        """Accept a mismatch as valid (e.g., expected transformation)."""
        return self.resolve_mismatch(
            recon_id,
            ResolutionAction.ACCEPTED.value,
            notes,
            accepted_by
        )

    def get_reconciliation_summary(
        self,
        batch_id: Optional[str] = None,
        hours_back: int = 24,
    ) -> Dict:
        """Get summary statistics for reconciliation."""
        base_condition = "reconciled_at > NOW() - INTERVAL '%s hours'"
        params = [hours_back]

        if batch_id:
            base_condition += " AND batch_id = %s"
            params.append(batch_id)

        cursor = self.db.cursor()
        try:
            # Get counts by status
            cursor.execute(f"""
                SELECT match_status, COUNT(*)
                FROM observability.obs_reconciliation_results
                WHERE {base_condition}
                GROUP BY match_status
            """, params)
            status_counts = dict(cursor.fetchall())

            # Get counts by investigation status
            cursor.execute(f"""
                SELECT investigation_status, COUNT(*)
                FROM observability.obs_reconciliation_results
                WHERE {base_condition}
                GROUP BY investigation_status
            """, params)
            investigation_counts = dict(cursor.fetchall())

            total = sum(status_counts.values())
            matched = status_counts.get('MATCHED', 0) + status_counts.get('PARTIAL_MATCH', 0)

            return {
                "total_records": total,
                "matched": matched,
                "match_rate": (matched / total * 100) if total > 0 else 0,
                "by_status": status_counts,
                "by_investigation": investigation_counts,
                "needs_investigation": status_counts.get('MISMATCHED', 0) +
                                       status_counts.get('BRONZE_ONLY', 0),
            }
        finally:
            cursor.close()

    def get_run_history(
        self,
        batch_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """Get reconciliation run history."""
        conditions = ["1=1"]
        params = []

        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)

        sql = f"""
            SELECT recon_run_id, batch_id, status,
                   total_source_records, total_target_records,
                   matched_count, mismatched_count, source_only_count,
                   match_rate, started_at, completed_at, initiated_by
            FROM observability.obs_reconciliation_runs
            WHERE {' AND '.join(conditions)}
            ORDER BY started_at DESC
            LIMIT %s
        """
        params.append(limit)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

"""
GPS CDM - Pipeline Reprocessor
===============================

Handles re-processing of failed or updated records through the pipeline.
Supports individual record re-processing, batch re-processing, and
update-and-reprocess workflows.

Usage:
    reprocessor = PipelineReprocessor(db_connection)

    # Re-process a single failed record
    result = reprocessor.reprocess_bronze_record(raw_id)

    # Re-process all failed records in a batch
    batch_result = reprocessor.reprocess_failed_batch(batch_id)

    # Update a record and re-process
    result = reprocessor.update_and_reprocess("silver", "stg_pain001", stg_id, updates)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ReprocessStatus(str, Enum):
    """Reprocessing status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class ReprocessResult:
    """Result of reprocessing a single record."""
    record_id: str
    source_layer: str
    status: str
    promoted_to_layer: Optional[str] = None
    new_record_id: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class BatchReprocessResult:
    """Result of batch reprocessing."""
    batch_id: str
    total_records: int
    success_count: int
    failed_count: int
    skipped_count: int
    results: List[ReprocessResult] = field(default_factory=list)
    duration_seconds: float = 0.0


class PipelineReprocessor:
    """
    Handles re-processing of records through the medallion pipeline.

    Supports:
    - Re-processing failed records
    - Re-processing records after data correction
    - Update-and-reprocess workflows
    - Batch re-processing
    """

    def __init__(
        self,
        db_connection,
        exception_manager=None,
        dq_validator=None,
    ):
        """
        Initialize the reprocessor.

        Args:
            db_connection: Database connection
            exception_manager: Optional ExceptionManager instance
            dq_validator: Optional DataQualityValidator instance
        """
        self.db = db_connection
        self.exception_manager = exception_manager
        self.dq_validator = dq_validator

    def reprocess_bronze_record(
        self,
        raw_id: str,
        force: bool = False,
    ) -> ReprocessResult:
        """
        Re-process a Bronze record through Silver → Gold.

        Args:
            raw_id: Bronze record ID
            force: Re-process even if already processed successfully

        Returns:
            ReprocessResult with outcome
        """
        start_time = datetime.now()

        # Get the bronze record
        bronze_record = self._get_bronze_record(raw_id)
        if not bronze_record:
            return ReprocessResult(
                record_id=raw_id,
                source_layer="bronze",
                status=ReprocessStatus.FAILED.value,
                error_message="Bronze record not found",
            )

        # Check if already processed
        if bronze_record.get('processing_status') == 'PROCESSED' and not force:
            if bronze_record.get('silver_stg_id'):
                return ReprocessResult(
                    record_id=raw_id,
                    source_layer="bronze",
                    status=ReprocessStatus.SKIPPED.value,
                    promoted_to_layer="silver",
                    new_record_id=bronze_record.get('silver_stg_id'),
                )

        try:
            # Update status to reprocessing
            self._update_bronze_status(raw_id, "REPROCESSING")

            # Parse and promote to Silver
            stg_id = self._promote_bronze_to_silver(bronze_record)

            if stg_id:
                # Update bronze with silver link
                self._update_bronze_status(
                    raw_id, "PROCESSED",
                    silver_stg_id=stg_id
                )

                # Now promote Silver to Gold
                instruction_id = self._promote_silver_to_gold(stg_id)

                if instruction_id:
                    # Update silver with gold link
                    self._update_silver_status(
                        stg_id, "PROCESSED",
                        gold_instruction_id=instruction_id
                    )

                    duration = (datetime.now() - start_time).total_seconds()
                    return ReprocessResult(
                        record_id=raw_id,
                        source_layer="bronze",
                        status=ReprocessStatus.SUCCESS.value,
                        promoted_to_layer="gold",
                        new_record_id=instruction_id,
                        duration_seconds=duration,
                    )
                else:
                    duration = (datetime.now() - start_time).total_seconds()
                    return ReprocessResult(
                        record_id=raw_id,
                        source_layer="bronze",
                        status=ReprocessStatus.SUCCESS.value,
                        promoted_to_layer="silver",
                        new_record_id=stg_id,
                        duration_seconds=duration,
                    )
            else:
                self._update_bronze_status(raw_id, "FAILED", "Failed to promote to Silver")
                return ReprocessResult(
                    record_id=raw_id,
                    source_layer="bronze",
                    status=ReprocessStatus.FAILED.value,
                    error_message="Failed to promote to Silver",
                )

        except Exception as e:
            self._update_bronze_status(raw_id, "FAILED", str(e))
            if self.exception_manager:
                self.exception_manager.log_exception_from_error(
                    batch_id=bronze_record.get('_batch_id', 'REPROCESS'),
                    source_layer="bronze",
                    source_table="raw_payment_messages",
                    source_record_id=raw_id,
                    error=e,
                    target_layer="silver"
                )
            return ReprocessResult(
                record_id=raw_id,
                source_layer="bronze",
                status=ReprocessStatus.FAILED.value,
                error_message=str(e),
            )

    def reprocess_silver_record(
        self,
        stg_id: str,
        force: bool = False,
    ) -> ReprocessResult:
        """
        Re-process a Silver record to Gold.

        Args:
            stg_id: Silver staging record ID
            force: Re-process even if already processed

        Returns:
            ReprocessResult with outcome
        """
        start_time = datetime.now()

        # Get silver record
        silver_record = self._get_silver_record(stg_id)
        if not silver_record:
            return ReprocessResult(
                record_id=stg_id,
                source_layer="silver",
                status=ReprocessStatus.FAILED.value,
                error_message="Silver record not found",
            )

        # Check if already processed
        if silver_record.get('processing_status') == 'PROCESSED' and not force:
            if silver_record.get('gold_instruction_id'):
                return ReprocessResult(
                    record_id=stg_id,
                    source_layer="silver",
                    status=ReprocessStatus.SKIPPED.value,
                    promoted_to_layer="gold",
                    new_record_id=silver_record.get('gold_instruction_id'),
                )

        try:
            # Update status
            self._update_silver_status(stg_id, "REPROCESSING")

            # Run DQ validation if validator available
            if self.dq_validator:
                dq_result = self.dq_validator.revalidate_record(
                    "silver", "stg_pain001", stg_id,
                    silver_record.get('_batch_id', 'REPROCESS')
                )
                if not dq_result.passed:
                    self._update_silver_status(stg_id, "FAILED", "DQ validation failed")
                    return ReprocessResult(
                        record_id=stg_id,
                        source_layer="silver",
                        status=ReprocessStatus.FAILED.value,
                        error_message=f"DQ validation failed: score={dq_result.overall_score}",
                    )

            # Promote to Gold
            instruction_id = self._promote_silver_to_gold(stg_id)

            if instruction_id:
                self._update_silver_status(
                    stg_id, "PROCESSED",
                    gold_instruction_id=instruction_id
                )
                duration = (datetime.now() - start_time).total_seconds()
                return ReprocessResult(
                    record_id=stg_id,
                    source_layer="silver",
                    status=ReprocessStatus.SUCCESS.value,
                    promoted_to_layer="gold",
                    new_record_id=instruction_id,
                    duration_seconds=duration,
                )
            else:
                self._update_silver_status(stg_id, "FAILED", "Failed to promote to Gold")
                return ReprocessResult(
                    record_id=stg_id,
                    source_layer="silver",
                    status=ReprocessStatus.FAILED.value,
                    error_message="Failed to promote to Gold",
                )

        except Exception as e:
            self._update_silver_status(stg_id, "FAILED", str(e))
            return ReprocessResult(
                record_id=stg_id,
                source_layer="silver",
                status=ReprocessStatus.FAILED.value,
                error_message=str(e),
            )

    def reprocess_failed_batch(
        self,
        batch_id: str,
        layer: Optional[str] = None,
        limit: int = 100,
    ) -> BatchReprocessResult:
        """
        Re-process all failed records in a batch.

        Args:
            batch_id: Batch identifier
            layer: Specific layer to reprocess (None for all)
            limit: Maximum records to reprocess

        Returns:
            BatchReprocessResult with summary
        """
        start_time = datetime.now()

        result = BatchReprocessResult(
            batch_id=batch_id,
            total_records=0,
            success_count=0,
            failed_count=0,
            skipped_count=0,
        )

        # Get failed records
        failed_records = self._get_failed_records(batch_id, layer, limit)
        result.total_records = len(failed_records)

        for record in failed_records:
            record_layer = record.get('layer')
            record_id = record.get('record_id')

            if record_layer == 'bronze':
                record_result = self.reprocess_bronze_record(record_id, force=True)
            elif record_layer == 'silver':
                record_result = self.reprocess_silver_record(record_id, force=True)
            else:
                continue

            result.results.append(record_result)

            if record_result.status == ReprocessStatus.SUCCESS.value:
                result.success_count += 1
            elif record_result.status == ReprocessStatus.FAILED.value:
                result.failed_count += 1
            else:
                result.skipped_count += 1

        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        return result

    def reprocess_dq_failures(
        self,
        batch_id: Optional[str] = None,
        limit: int = 100,
    ) -> BatchReprocessResult:
        """
        Re-process records that failed DQ validation.

        Useful after data correction to re-validate.
        """
        start_time = datetime.now()

        result = BatchReprocessResult(
            batch_id=batch_id or "DQ_REPROCESS",
            total_records=0,
            success_count=0,
            failed_count=0,
            skipped_count=0,
        )

        # Get DQ failed records
        dq_failures = self._get_dq_failed_records(batch_id, limit)
        result.total_records = len(dq_failures)

        for record in dq_failures:
            layer = record.get('layer')
            record_id = record.get('record_id')

            if layer == 'silver':
                record_result = self.reprocess_silver_record(record_id, force=True)
            else:
                continue

            result.results.append(record_result)

            if record_result.status == ReprocessStatus.SUCCESS.value:
                result.success_count += 1
            elif record_result.status == ReprocessStatus.FAILED.value:
                result.failed_count += 1
            else:
                result.skipped_count += 1

        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        return result

    def update_and_reprocess(
        self,
        layer: str,
        table_name: str,
        record_id: str,
        updates: Dict[str, Any],
        reprocess: bool = True,
    ) -> Tuple[bool, Optional[ReprocessResult]]:
        """
        Update a record and optionally re-process through pipeline.

        Args:
            layer: Layer of the record (bronze, silver)
            table_name: Table name
            record_id: Record ID
            updates: Dictionary of field updates
            reprocess: Whether to re-process after update

        Returns:
            Tuple of (update_success, reprocess_result)
        """
        # Perform the update
        update_success = self._update_record(layer, table_name, record_id, updates)

        if not update_success:
            return False, None

        if not reprocess:
            return True, None

        # Re-process
        if layer == 'bronze':
            result = self.reprocess_bronze_record(record_id, force=True)
        elif layer == 'silver':
            result = self.reprocess_silver_record(record_id, force=True)
        else:
            return True, None

        return True, result

    def _get_bronze_record(self, raw_id: str) -> Optional[Dict]:
        """Get a bronze record by ID."""
        sql = "SELECT * FROM bronze.raw_payment_messages WHERE raw_id = %s"
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (raw_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            cursor.close()

    def _get_silver_record(self, stg_id: str) -> Optional[Dict]:
        """Get a silver record by ID."""
        sql = "SELECT * FROM silver.stg_pain001 WHERE stg_id = %s"
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (stg_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            cursor.close()

    def _update_bronze_status(
        self,
        raw_id: str,
        status: str,
        error: Optional[str] = None,
        silver_stg_id: Optional[str] = None,
    ):
        """Update bronze record status."""
        sql = """
            UPDATE bronze.raw_payment_messages
            SET processing_status = %s,
                processing_error = %s,
                processing_attempts = processing_attempts + 1,
                last_processed_at = CURRENT_TIMESTAMP,
                silver_stg_id = COALESCE(%s, silver_stg_id),
                promoted_to_silver_at = CASE WHEN %s IS NOT NULL THEN CURRENT_TIMESTAMP ELSE promoted_to_silver_at END
            WHERE raw_id = %s
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (status, error, silver_stg_id, silver_stg_id, raw_id))
            self.db.commit()
        finally:
            cursor.close()

    def _update_silver_status(
        self,
        stg_id: str,
        status: str,
        error: Optional[str] = None,
        gold_instruction_id: Optional[str] = None,
    ):
        """Update silver record status."""
        sql = """
            UPDATE silver.stg_pain001
            SET processing_status = %s,
                processing_error = %s,
                gold_instruction_id = COALESCE(%s, gold_instruction_id),
                promoted_to_gold_at = CASE WHEN %s IS NOT NULL THEN CURRENT_TIMESTAMP ELSE promoted_to_gold_at END
            WHERE stg_id = %s
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (status, error, gold_instruction_id, gold_instruction_id, stg_id))
            self.db.commit()
        finally:
            cursor.close()

    def _get_failed_records(
        self,
        batch_id: str,
        layer: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get failed records from a batch."""
        records = []

        if layer is None or layer == 'bronze':
            cursor = self.db.cursor()
            try:
                cursor.execute("""
                    SELECT raw_id as record_id, 'bronze' as layer
                    FROM bronze.raw_payment_messages
                    WHERE _batch_id = %s
                      AND (processing_status = 'FAILED' OR
                           (processing_status = 'PROCESSED' AND silver_stg_id IS NULL))
                    LIMIT %s
                """, (batch_id, limit))
                columns = [desc[0] for desc in cursor.description]
                records.extend([dict(zip(columns, row)) for row in cursor.fetchall()])
            finally:
                cursor.close()

        if layer is None or layer == 'silver':
            cursor = self.db.cursor()
            try:
                cursor.execute("""
                    SELECT stg_id as record_id, 'silver' as layer
                    FROM silver.stg_pain001
                    WHERE _batch_id = %s
                      AND (processing_status = 'FAILED' OR
                           (processing_status = 'PROCESSED' AND gold_instruction_id IS NULL))
                    LIMIT %s
                """, (batch_id, limit))
                columns = [desc[0] for desc in cursor.description]
                records.extend([dict(zip(columns, row)) for row in cursor.fetchall()])
            finally:
                cursor.close()

        return records[:limit]

    def _get_dq_failed_records(
        self,
        batch_id: Optional[str],
        limit: int = 100,
    ) -> List[Dict]:
        """Get records with DQ failures."""
        sql = """
            SELECT stg_id as record_id, 'silver' as layer
            FROM silver.stg_pain001
            WHERE dq_status = 'FAILED'
        """
        params = []
        if batch_id:
            sql += " AND _batch_id = %s"
            params.append(batch_id)
        sql += " LIMIT %s"
        params.append(limit)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def _update_record(
        self,
        layer: str,
        table_name: str,
        record_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """Update a record with given field values."""
        table_map = {
            ('bronze', 'raw_payment_messages'): ('bronze.raw_payment_messages', 'raw_id'),
            ('silver', 'stg_pain001'): ('silver.stg_pain001', 'stg_id'),
        }

        full_table, id_col = table_map.get((layer, table_name), (None, None))
        if not full_table or not updates:
            return False

        # Build SET clause
        set_parts = []
        params = []
        for field, value in updates.items():
            # Whitelist allowed fields for security
            if self._is_updatable_field(layer, field):
                set_parts.append(f"{field} = %s")
                params.append(value)

        if not set_parts:
            return False

        sql = f"""
            UPDATE {full_table}
            SET {', '.join(set_parts)}
            WHERE {id_col} = %s
        """
        params.append(record_id)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            self.db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def _is_updatable_field(self, layer: str, field: str) -> bool:
        """Check if a field can be updated (security whitelist)."""
        # Define updatable fields per layer
        updatable = {
            'bronze': {
                'raw_content', 'message_type', 'processing_status',
            },
            'silver': {
                'debtor_name', 'creditor_name', 'debtor_country', 'creditor_country',
                'instructed_amount', 'instructed_currency', 'charge_bearer',
                'debtor_agent_bic', 'creditor_agent_bic',
                'debtor_account_iban', 'creditor_account_iban',
                'processing_status', 'dq_status',
            },
        }
        return field in updatable.get(layer, set())

    def _promote_bronze_to_silver(self, bronze_record: Dict) -> Optional[str]:
        """
        Promote a bronze record to silver.

        This is a simplified version - in production, this would
        call the actual parsing logic.
        """
        # For now, just return the existing silver_stg_id if present
        # In real implementation, this would parse the raw content
        return bronze_record.get('silver_stg_id')

    def _promote_silver_to_gold(self, stg_id: str) -> Optional[str]:
        """
        Promote a silver record to gold.

        This is a simplified version - in production, this would
        call the actual transformation logic.
        """
        # Check if already promoted
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                SELECT gold_instruction_id FROM silver.stg_pain001
                WHERE stg_id = %s
            """, (stg_id,))
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]
            return None
        finally:
            cursor.close()


# Helper functions for common reprocessing scenarios

def reprocess_exceptions(
    db_connection,
    batch_id: Optional[str] = None,
    exception_type: Optional[str] = None,
    limit: int = 100,
) -> BatchReprocessResult:
    """
    Re-process records from exceptions.

    This is a convenience function that combines ExceptionManager
    and PipelineReprocessor.
    """
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    exc_manager = ExceptionManager(db_connection)
    reprocessor = PipelineReprocessor(db_connection, exc_manager)

    # Get retryable exceptions
    exceptions = exc_manager.get_retryable_exceptions(limit=limit)

    result = BatchReprocessResult(
        batch_id=batch_id or "EXCEPTION_REPROCESS",
        total_records=len(exceptions),
        success_count=0,
        failed_count=0,
        skipped_count=0,
    )

    for exc in exceptions:
        source_layer = exc.get('source_layer')
        record_id = exc.get('source_record_id')

        if source_layer == 'bronze':
            record_result = reprocessor.reprocess_bronze_record(record_id, force=True)
        elif source_layer == 'silver':
            record_result = reprocessor.reprocess_silver_record(record_id, force=True)
        else:
            continue

        result.results.append(record_result)

        if record_result.status == ReprocessStatus.SUCCESS.value:
            result.success_count += 1
            # Auto-resolve the exception
            exc_manager.resolve_exception(
                exc.get('exception_id'),
                "Auto-resolved via reprocessing",
                "SYSTEM"
            )
        else:
            result.failed_count += 1
            # Schedule next retry
            exc_manager.schedule_retry(exc.get('exception_id'))

    return result

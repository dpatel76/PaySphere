"""
GPS CDM - Exception Manager
============================

Centralized exception tracking and management across the medallion pipeline.
Provides logging, querying, resolution, and retry functionality for processing
exceptions at Bronze, Silver, and Gold layers.

Usage:
    manager = ExceptionManager(db_connection)

    # Log an exception
    exc_id = manager.log_exception(
        batch_id="abc123",
        source_layer="bronze",
        source_table="raw_payment_messages",
        source_record_id="raw-001",
        exception_type="PARSE_ERROR",
        exception_message="Invalid XML structure"
    )

    # Get exceptions
    exceptions = manager.get_exceptions(batch_id="abc123", status="NEW")

    # Resolve
    manager.resolve_exception(exc_id, "Fixed XML", "admin")
"""

import uuid
import json
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ExceptionType(str, Enum):
    """Types of processing exceptions."""
    PARSE_ERROR = "PARSE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TRANSFORM_ERROR = "TRANSFORM_ERROR"
    DQ_FAILURE = "DQ_FAILURE"
    MAPPING_ERROR = "MAPPING_ERROR"
    DB_ERROR = "DB_ERROR"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


class ExceptionSeverity(str, Enum):
    """Exception severity levels."""
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ExceptionStatus(str, Enum):
    """Exception resolution status."""
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"
    AUTO_RESOLVED = "AUTO_RESOLVED"


@dataclass
class ProcessingException:
    """Represents a processing exception."""
    exception_id: str
    batch_id: str
    source_layer: str
    source_table: str
    source_record_id: str
    exception_type: str
    exception_message: str
    severity: str = "ERROR"
    status: str = "NEW"
    target_layer: Optional[str] = None
    target_table: Optional[str] = None
    exception_code: Optional[str] = None
    exception_details: Optional[Dict] = None
    stack_trace: Optional[str] = None
    field_name: Optional[str] = None
    field_value: Optional[str] = None
    expected_value: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    can_retry: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ExceptionSummary:
    """Summary of exceptions for a batch or system-wide."""
    total: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_layer: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_status: Dict[str, int] = field(default_factory=dict)
    new_count: int = 0
    resolved_count: int = 0
    critical_count: int = 0
    retryable_count: int = 0


class ExceptionManager:
    """
    Manages processing exceptions across the pipeline.

    Provides centralized logging, querying, and resolution of exceptions
    that occur during Bronze → Silver → Gold transformations.
    """

    def __init__(self, db_connection):
        """
        Initialize the exception manager.

        Args:
            db_connection: Database connection (psycopg2 or compatible)
        """
        self.db = db_connection

    def log_exception(
        self,
        batch_id: str,
        source_layer: str,
        source_table: str,
        source_record_id: str,
        exception_type: str,
        exception_message: str,
        target_layer: Optional[str] = None,
        target_table: Optional[str] = None,
        exception_code: Optional[str] = None,
        exception_details: Optional[Dict] = None,
        stack_trace: Optional[str] = None,
        field_name: Optional[str] = None,
        field_value: Optional[str] = None,
        expected_value: Optional[str] = None,
        severity: str = "ERROR",
        pipeline_run_id: Optional[str] = None,
        can_retry: bool = True,
        max_retries: int = 3,
    ) -> str:
        """
        Log a processing exception.

        Args:
            batch_id: Batch identifier
            source_layer: Layer where exception occurred (bronze, silver, gold)
            source_table: Table name where exception occurred
            source_record_id: ID of the record that caused the exception
            exception_type: Type of exception (PARSE_ERROR, VALIDATION_ERROR, etc.)
            exception_message: Human-readable error message
            target_layer: Target layer the record was trying to reach
            target_table: Target table name
            exception_code: Error code (e.g., AM01 for amount errors)
            exception_details: Additional details as JSON
            stack_trace: Full stack trace if available
            field_name: Specific field that caused the error
            field_value: Actual value that caused the error
            expected_value: Expected value or format
            severity: WARNING, ERROR, or CRITICAL
            pipeline_run_id: Optional pipeline run identifier
            can_retry: Whether this exception can be retried
            max_retries: Maximum number of retry attempts

        Returns:
            exception_id of the logged exception
        """
        exception_id = str(uuid.uuid4())

        sql = """
            INSERT INTO observability.obs_processing_exceptions (
                exception_id, batch_id, pipeline_run_id,
                source_layer, source_table, source_record_id,
                target_layer, target_table,
                exception_type, exception_code, exception_message,
                exception_details, stack_trace,
                field_name, field_value, expected_value,
                severity, status, can_retry, max_retries,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                exception_id, batch_id, pipeline_run_id,
                source_layer, source_table, source_record_id,
                target_layer, target_table,
                exception_type, exception_code, exception_message,
                json.dumps(exception_details) if exception_details else None,
                stack_trace,
                field_name, str(field_value) if field_value is not None else None,
                expected_value,
                severity, ExceptionStatus.NEW.value, can_retry, max_retries,
            ))
            self.db.commit()
            return exception_id
        except Exception as e:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def log_exception_from_error(
        self,
        batch_id: str,
        source_layer: str,
        source_table: str,
        source_record_id: str,
        error: Exception,
        exception_type: str = None,
        target_layer: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Log an exception from a Python Exception object.

        Automatically extracts message and stack trace.
        """
        return self.log_exception(
            batch_id=batch_id,
            source_layer=source_layer,
            source_table=source_table,
            source_record_id=source_record_id,
            exception_type=exception_type or ExceptionType.UNKNOWN.value,
            exception_message=str(error),
            stack_trace=traceback.format_exc(),
            target_layer=target_layer,
            **kwargs
        )

    def get_exception(self, exception_id: str) -> Optional[ProcessingException]:
        """Get a single exception by ID."""
        sql = """
            SELECT * FROM observability.obs_processing_exceptions
            WHERE exception_id = %s
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (exception_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))
                return ProcessingException(**{
                    k: v for k, v in data.items()
                    if k in ProcessingException.__dataclass_fields__
                })
            return None
        finally:
            cursor.close()

    def get_exceptions(
        self,
        batch_id: Optional[str] = None,
        source_layer: Optional[str] = None,
        source_record_id: Optional[str] = None,
        exception_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        can_retry: Optional[bool] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:
        """
        Get exceptions with filters.

        Returns list of exception dictionaries.
        """
        conditions = ["1=1"]
        params = []

        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)
        if source_layer:
            conditions.append("source_layer = %s")
            params.append(source_layer)
        if source_record_id:
            conditions.append("source_record_id = %s")
            params.append(source_record_id)
        if exception_type:
            conditions.append("exception_type = %s")
            params.append(exception_type)
        if severity:
            conditions.append("severity = %s")
            params.append(severity)
        if status:
            conditions.append("status = %s")
            params.append(status)
        if can_retry is not None:
            conditions.append("can_retry = %s")
            params.append(can_retry)
        if created_after:
            conditions.append("created_at >= %s")
            params.append(created_after)
        if created_before:
            conditions.append("created_at <= %s")
            params.append(created_before)

        sql = f"""
            SELECT * FROM observability.obs_processing_exceptions
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def get_exception_summary(
        self,
        batch_id: Optional[str] = None,
        hours_back: int = 24,
    ) -> ExceptionSummary:
        """
        Get summary statistics for exceptions.

        Args:
            batch_id: Filter by batch (None for all)
            hours_back: Include exceptions from last N hours

        Returns:
            ExceptionSummary with counts by various dimensions
        """
        summary = ExceptionSummary()

        base_condition = "created_at > NOW() - INTERVAL '%s hours'"
        params = [hours_back]

        if batch_id:
            base_condition += " AND batch_id = %s"
            params.append(batch_id)

        cursor = self.db.cursor()
        try:
            # Total count
            cursor.execute(f"""
                SELECT COUNT(*) FROM observability.obs_processing_exceptions
                WHERE {base_condition}
            """, params)
            summary.total = cursor.fetchone()[0]

            # By type
            cursor.execute(f"""
                SELECT exception_type, COUNT(*)
                FROM observability.obs_processing_exceptions
                WHERE {base_condition}
                GROUP BY exception_type
            """, params)
            summary.by_type = dict(cursor.fetchall())

            # By layer
            cursor.execute(f"""
                SELECT source_layer, COUNT(*)
                FROM observability.obs_processing_exceptions
                WHERE {base_condition}
                GROUP BY source_layer
            """, params)
            summary.by_layer = dict(cursor.fetchall())

            # By severity
            cursor.execute(f"""
                SELECT severity, COUNT(*)
                FROM observability.obs_processing_exceptions
                WHERE {base_condition}
                GROUP BY severity
            """, params)
            summary.by_severity = dict(cursor.fetchall())

            # By status
            cursor.execute(f"""
                SELECT status, COUNT(*)
                FROM observability.obs_processing_exceptions
                WHERE {base_condition}
                GROUP BY status
            """, params)
            summary.by_status = dict(cursor.fetchall())

            # Specific counts
            summary.new_count = summary.by_status.get('NEW', 0)
            summary.resolved_count = summary.by_status.get('RESOLVED', 0)
            summary.critical_count = summary.by_severity.get('CRITICAL', 0)

            # Retryable count
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM observability.obs_processing_exceptions
                WHERE {base_condition}
                  AND can_retry = true
                  AND status NOT IN ('RESOLVED', 'IGNORED')
                  AND retry_count < max_retries
            """, params)
            summary.retryable_count = cursor.fetchone()[0]

            return summary
        finally:
            cursor.close()

    def acknowledge_exception(
        self,
        exception_id: str,
        notes: Optional[str] = None,
        acknowledged_by: Optional[str] = None,
    ) -> bool:
        """Mark an exception as acknowledged."""
        sql = """
            UPDATE observability.obs_processing_exceptions
            SET status = %s,
                resolution_notes = COALESCE(%s, resolution_notes),
                updated_at = CURRENT_TIMESTAMP
            WHERE exception_id = %s
              AND status = %s
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                ExceptionStatus.ACKNOWLEDGED.value,
                notes,
                exception_id,
                ExceptionStatus.NEW.value
            ))
            self.db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def resolve_exception(
        self,
        exception_id: str,
        resolution_notes: str,
        resolved_by: str,
        status: str = None,
    ) -> bool:
        """
        Mark an exception as resolved.

        Args:
            exception_id: Exception to resolve
            resolution_notes: How it was resolved
            resolved_by: Who resolved it
            status: Resolution status (defaults to RESOLVED)
        """
        sql = """
            UPDATE observability.obs_processing_exceptions
            SET status = %s,
                resolution_notes = %s,
                resolved_by = %s,
                resolved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE exception_id = %s
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                status or ExceptionStatus.RESOLVED.value,
                resolution_notes,
                resolved_by,
                exception_id
            ))
            self.db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def ignore_exception(
        self,
        exception_id: str,
        reason: str,
        ignored_by: str,
    ) -> bool:
        """Mark an exception as ignored (won't be retried)."""
        return self.resolve_exception(
            exception_id,
            resolution_notes=f"IGNORED: {reason}",
            resolved_by=ignored_by,
            status=ExceptionStatus.IGNORED.value
        )

    def schedule_retry(
        self,
        exception_id: str,
        retry_at: Optional[datetime] = None,
        delay_seconds: int = 300,
    ) -> bool:
        """
        Schedule an exception for retry.

        Args:
            exception_id: Exception to retry
            retry_at: When to retry (default: now + delay_seconds)
            delay_seconds: Delay in seconds if retry_at not specified
        """
        if not retry_at:
            retry_at = datetime.now() + timedelta(seconds=delay_seconds)

        sql = """
            UPDATE observability.obs_processing_exceptions
            SET retry_count = retry_count + 1,
                last_retry_at = CURRENT_TIMESTAMP,
                next_retry_at = %s,
                status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE exception_id = %s
              AND can_retry = true
              AND retry_count < max_retries
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                retry_at,
                ExceptionStatus.IN_PROGRESS.value,
                exception_id
            ))
            self.db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def get_retryable_exceptions(
        self,
        source_layer: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get exceptions that are due for retry."""
        conditions = [
            "can_retry = true",
            "status NOT IN ('RESOLVED', 'IGNORED')",
            "retry_count < max_retries",
            "(next_retry_at IS NULL OR next_retry_at <= CURRENT_TIMESTAMP)"
        ]
        params = []

        if source_layer:
            conditions.append("source_layer = %s")
            params.append(source_layer)

        sql = f"""
            SELECT * FROM observability.obs_processing_exceptions
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at ASC
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

    def update_source_record_status(
        self,
        source_layer: str,
        source_table: str,
        source_record_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Update the processing status on the source record.

        This updates the status column on the actual data table.
        """
        # Map table names to actual SQL
        table_map = {
            ('bronze', 'raw_payment_messages'): 'bronze.raw_payment_messages',
            ('silver', 'stg_pain001'): 'silver.stg_pain001',
            ('gold', 'cdm_payment_instruction'): 'gold.cdm_payment_instruction',
        }

        id_column_map = {
            'raw_payment_messages': 'raw_id',
            'stg_pain001': 'stg_id',
            'cdm_payment_instruction': 'instruction_id',
        }

        full_table = table_map.get((source_layer, source_table))
        id_column = id_column_map.get(source_table)

        if not full_table or not id_column:
            return False

        sql = f"""
            UPDATE {full_table}
            SET processing_status = %s,
                processing_error = %s,
                processing_attempts = processing_attempts + 1,
                last_processed_at = CURRENT_TIMESTAMP
            WHERE {id_column} = %s
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (status, error_message, source_record_id))
            self.db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()

    def bulk_acknowledge(
        self,
        exception_ids: List[str],
        notes: Optional[str] = None,
    ) -> int:
        """Acknowledge multiple exceptions at once."""
        if not exception_ids:
            return 0

        sql = """
            UPDATE observability.obs_processing_exceptions
            SET status = %s,
                resolution_notes = COALESCE(%s, resolution_notes),
                updated_at = CURRENT_TIMESTAMP
            WHERE exception_id = ANY(%s)
              AND status = %s
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                ExceptionStatus.ACKNOWLEDGED.value,
                notes,
                exception_ids,
                ExceptionStatus.NEW.value
            ))
            self.db.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    def get_exceptions_for_record(
        self,
        source_layer: str,
        source_table: str,
        source_record_id: str,
    ) -> List[Dict]:
        """Get all exceptions for a specific record."""
        return self.get_exceptions(
            source_layer=source_layer,
            source_record_id=source_record_id,
            limit=100
        )

    def clear_resolved_exceptions(
        self,
        days_old: int = 30,
    ) -> int:
        """Archive or delete resolved exceptions older than N days."""
        sql = """
            DELETE FROM observability.obs_processing_exceptions
            WHERE status IN ('RESOLVED', 'IGNORED', 'AUTO_RESOLVED')
              AND resolved_at < NOW() - INTERVAL '%s days'
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (days_old,))
            self.db.commit()
            return cursor.rowcount
        finally:
            cursor.close()


# Convenience functions for Celery tasks
def log_bronze_exception(
    db_connection,
    batch_id: str,
    raw_id: str,
    error: Exception,
    exception_type: str = ExceptionType.PARSE_ERROR.value,
) -> str:
    """Log a Bronze layer exception."""
    manager = ExceptionManager(db_connection)
    return manager.log_exception_from_error(
        batch_id=batch_id,
        source_layer="bronze",
        source_table="raw_payment_messages",
        source_record_id=raw_id,
        error=error,
        exception_type=exception_type,
        target_layer="silver"
    )


def log_silver_exception(
    db_connection,
    batch_id: str,
    stg_id: str,
    error: Exception,
    exception_type: str = ExceptionType.TRANSFORM_ERROR.value,
) -> str:
    """Log a Silver layer exception."""
    manager = ExceptionManager(db_connection)
    return manager.log_exception_from_error(
        batch_id=batch_id,
        source_layer="silver",
        source_table="stg_pain001",
        source_record_id=stg_id,
        error=error,
        exception_type=exception_type,
        target_layer="gold"
    )


def log_gold_exception(
    db_connection,
    batch_id: str,
    instruction_id: str,
    error: Exception,
    exception_type: str = ExceptionType.DQ_FAILURE.value,
) -> str:
    """Log a Gold layer exception."""
    manager = ExceptionManager(db_connection)
    return manager.log_exception_from_error(
        batch_id=batch_id,
        source_layer="gold",
        source_table="cdm_payment_instruction",
        source_record_id=instruction_id,
        error=error,
        exception_type=exception_type,
    )

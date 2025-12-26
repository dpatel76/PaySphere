"""
GPS CDM API - Processing Errors Management Routes
==================================================

Endpoints for managing processing errors from the bronze.processing_errors table.
Supports filtering, bulk operations, retry, and analytics.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import os

router = APIRouter()


# =============================================================================
# Enums
# =============================================================================

class Zone(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


class ErrorStatus(str, Enum):
    PENDING = "PENDING"
    RETRYING = "RETRYING"
    RESOLVED = "RESOLVED"
    SKIPPED = "SKIPPED"
    ABANDONED = "ABANDONED"


class BulkAction(str, Enum):
    RETRY = "retry"
    SKIP = "skip"
    RESOLVE = "resolve"
    ABANDON = "abandon"


# =============================================================================
# Request/Response Models
# =============================================================================

class ProcessingError(BaseModel):
    """Processing error response model."""
    error_id: str
    batch_id: str
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    zone: str
    raw_id: Optional[str] = None
    stg_id: Optional[str] = None
    content_hash: Optional[str] = None
    message_type: str
    message_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: str
    error_stack_trace: Optional[str] = None
    original_content: Optional[str] = None
    status: str
    retry_count: int
    max_retries: int
    last_retry_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ErrorListResponse(BaseModel):
    """Paginated error list response."""
    items: List[ProcessingError]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorStatsResponse(BaseModel):
    """Error statistics response."""
    total_errors: int
    by_zone: Dict[str, int]
    by_status: Dict[str, int]
    by_message_type: Dict[str, int]
    by_error_code: Dict[str, int]
    pending_count: int
    retrying_count: int
    resolved_count: int
    abandoned_count: int
    avg_retry_count: float
    errors_last_hour: int
    errors_last_24h: int
    oldest_pending: Optional[datetime] = None
    newest_error: Optional[datetime] = None


class ErrorTrendResponse(BaseModel):
    """Error trend over time."""
    timestamps: List[datetime]
    counts: List[int]
    by_zone: Dict[str, List[int]]


class BulkActionRequest(BaseModel):
    """Request for bulk operations."""
    error_ids: List[str] = Field(..., min_length=1, max_length=1000)
    action: BulkAction
    notes: Optional[str] = None
    resolved_by: Optional[str] = None


class BulkActionResponse(BaseModel):
    """Response for bulk operations."""
    action: str
    requested_count: int
    success_count: int
    failed_ids: List[str]


class RetryRequest(BaseModel):
    """Request for retrying an error."""
    delay_minutes: int = Field(default=5, ge=0, le=1440)


class ResolveRequest(BaseModel):
    """Request for resolving an error."""
    resolution_notes: str = Field(..., min_length=1, max_length=1000)
    resolved_by: str = Field(..., min_length=1, max_length=100)


class ErrorCodeInfo(BaseModel):
    """Error code reference information."""
    error_code: str
    error_category: str
    description: Optional[str] = None
    is_retryable: bool
    suggested_action: Optional[str] = None


# =============================================================================
# Database Connection Helper
# =============================================================================

def get_db_connection():
    """Get database connection using environment variables."""
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5433)),
        database=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )


# =============================================================================
# Error List & Detail Endpoints
# =============================================================================

@router.get("", response_model=ErrorListResponse)
async def list_errors(
    zone: Optional[Zone] = Query(None, description="Filter by zone"),
    status: Optional[ErrorStatus] = Query(None, description="Filter by status"),
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    error_code: Optional[str] = Query(None, description="Filter by error code"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    date_from: Optional[datetime] = Query(None, description="Filter errors from date"),
    date_to: Optional[datetime] = Query(None, description="Filter errors to date"),
    search: Optional[str] = Query(None, description="Search in error message"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_desc: bool = Query(True, description="Sort descending"),
):
    """
    List processing errors with filtering and pagination.

    Supports filtering by:
    - zone (BRONZE, SILVER, GOLD)
    - status (PENDING, RETRYING, RESOLVED, SKIPPED, ABANDONED)
    - message_type (e.g., pain.001, MT103)
    - error_code (e.g., PARSE_ERROR, VALIDATION_ERROR)
    - batch_id
    - date range
    - search text in error message
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Build WHERE clause
        conditions = []
        params = []

        if zone:
            conditions.append("zone = %s")
            params.append(zone.value)
        if status:
            conditions.append("status = %s")
            params.append(status.value)
        if message_type:
            conditions.append("message_type = %s")
            params.append(message_type)
        if error_code:
            conditions.append("error_code = %s")
            params.append(error_code)
        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)
        if date_from:
            conditions.append("created_at >= %s")
            params.append(date_from)
        if date_to:
            conditions.append("created_at <= %s")
            params.append(date_to)
        if search:
            conditions.append("error_message ILIKE %s")
            params.append(f"%{search}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*) FROM bronze.processing_errors WHERE {where_clause}
        """, params)
        total = cursor.fetchone()[0]

        # Validate sort field
        valid_sort_fields = ['created_at', 'updated_at', 'status', 'zone', 'message_type', 'retry_count']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'

        sort_order = "DESC" if sort_desc else "ASC"
        offset = (page - 1) * page_size

        # Get paginated results
        cursor.execute(f"""
            SELECT error_id, batch_id, chunk_index, total_chunks, zone,
                   raw_id, stg_id, content_hash, message_type, message_id,
                   error_code, error_message, error_stack_trace, original_content,
                   status, retry_count, max_retries, last_retry_at, next_retry_at,
                   resolved_at, resolved_by, resolution_notes, created_at, updated_at
            FROM bronze.processing_errors
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """, params + [page_size, offset])

        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append(ProcessingError(
                error_id=row[0],
                batch_id=row[1],
                chunk_index=row[2],
                total_chunks=row[3],
                zone=row[4],
                raw_id=row[5],
                stg_id=row[6],
                content_hash=row[7],
                message_type=row[8],
                message_id=row[9],
                error_code=row[10],
                error_message=row[11],
                error_stack_trace=row[12],
                original_content=row[13],
                status=row[14],
                retry_count=row[15],
                max_retries=row[16],
                last_retry_at=row[17],
                next_retry_at=row[18],
                resolved_at=row[19],
                resolved_by=row[20],
                resolution_notes=row[21],
                created_at=row[22],
                updated_at=row[23],
            ))

        total_pages = (total + page_size - 1) // page_size

        return ErrorListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    finally:
        conn.close()


@router.get("/stats", response_model=ErrorStatsResponse)
async def get_error_stats(
    zone: Optional[Zone] = Query(None, description="Filter by zone"),
    hours_back: int = Query(24, ge=1, le=720, description="Hours to look back"),
):
    """
    Get error statistics and aggregations.

    Returns counts by zone, status, message type, and error code,
    plus trend information.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        zone_filter = "AND zone = %s" if zone else ""
        params = [zone.value] if zone else []

        # Total errors
        cursor.execute(f"""
            SELECT COUNT(*) FROM bronze.processing_errors WHERE 1=1 {zone_filter}
        """, params)
        total_errors = cursor.fetchone()[0]

        # By zone
        cursor.execute("""
            SELECT zone, COUNT(*) FROM bronze.processing_errors GROUP BY zone
        """)
        by_zone = {row[0]: row[1] for row in cursor.fetchall()}

        # By status
        cursor.execute(f"""
            SELECT status, COUNT(*) FROM bronze.processing_errors WHERE 1=1 {zone_filter} GROUP BY status
        """, params)
        by_status = {row[0]: row[1] for row in cursor.fetchall()}

        # By message type
        cursor.execute(f"""
            SELECT message_type, COUNT(*) FROM bronze.processing_errors WHERE 1=1 {zone_filter}
            GROUP BY message_type ORDER BY COUNT(*) DESC LIMIT 20
        """, params)
        by_message_type = {row[0]: row[1] for row in cursor.fetchall()}

        # By error code
        cursor.execute(f"""
            SELECT COALESCE(error_code, 'UNKNOWN'), COUNT(*) FROM bronze.processing_errors WHERE 1=1 {zone_filter}
            GROUP BY error_code ORDER BY COUNT(*) DESC LIMIT 20
        """, params)
        by_error_code = {row[0]: row[1] for row in cursor.fetchall()}

        # Average retry count
        cursor.execute(f"""
            SELECT COALESCE(AVG(retry_count), 0) FROM bronze.processing_errors WHERE 1=1 {zone_filter}
        """, params)
        avg_retry_count = float(cursor.fetchone()[0])

        # Errors in last hour
        cursor.execute(f"""
            SELECT COUNT(*) FROM bronze.processing_errors
            WHERE created_at >= NOW() - INTERVAL '1 hour' {zone_filter}
        """, params)
        errors_last_hour = cursor.fetchone()[0]

        # Errors in last 24 hours
        cursor.execute(f"""
            SELECT COUNT(*) FROM bronze.processing_errors
            WHERE created_at >= NOW() - INTERVAL '24 hours' {zone_filter}
        """, params)
        errors_last_24h = cursor.fetchone()[0]

        # Oldest pending error
        cursor.execute(f"""
            SELECT MIN(created_at) FROM bronze.processing_errors
            WHERE status IN ('PENDING', 'RETRYING') {zone_filter}
        """, params)
        oldest_pending = cursor.fetchone()[0]

        # Newest error
        cursor.execute(f"""
            SELECT MAX(created_at) FROM bronze.processing_errors WHERE 1=1 {zone_filter}
        """, params)
        newest_error = cursor.fetchone()[0]

        return ErrorStatsResponse(
            total_errors=total_errors,
            by_zone=by_zone,
            by_status=by_status,
            by_message_type=by_message_type,
            by_error_code=by_error_code,
            pending_count=by_status.get('PENDING', 0),
            retrying_count=by_status.get('RETRYING', 0),
            resolved_count=by_status.get('RESOLVED', 0),
            abandoned_count=by_status.get('ABANDONED', 0),
            avg_retry_count=avg_retry_count,
            errors_last_hour=errors_last_hour,
            errors_last_24h=errors_last_24h,
            oldest_pending=oldest_pending,
            newest_error=newest_error,
        )
    finally:
        conn.close()


@router.get("/trend", response_model=ErrorTrendResponse)
async def get_error_trend(
    hours_back: int = Query(24, ge=1, le=168, description="Hours to look back"),
    interval_minutes: int = Query(60, ge=15, le=360, description="Interval in minutes"),
):
    """
    Get error trend over time for charting.

    Returns timestamps and counts for the specified time range,
    broken down by zone.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        interval = f"{interval_minutes} minutes"

        cursor.execute(f"""
            WITH time_buckets AS (
                SELECT generate_series(
                    date_trunc('hour', NOW() - INTERVAL '{hours_back} hours'),
                    date_trunc('hour', NOW()),
                    INTERVAL '{interval}'
                ) AS bucket
            ),
            error_counts AS (
                SELECT
                    date_trunc('hour', created_at) AS bucket,
                    zone,
                    COUNT(*) AS cnt
                FROM bronze.processing_errors
                WHERE created_at >= NOW() - INTERVAL '{hours_back} hours'
                GROUP BY date_trunc('hour', created_at), zone
            )
            SELECT
                tb.bucket,
                COALESCE(SUM(ec.cnt), 0) AS total,
                COALESCE(SUM(CASE WHEN ec.zone = 'BRONZE' THEN ec.cnt ELSE 0 END), 0) AS bronze,
                COALESCE(SUM(CASE WHEN ec.zone = 'SILVER' THEN ec.cnt ELSE 0 END), 0) AS silver,
                COALESCE(SUM(CASE WHEN ec.zone = 'GOLD' THEN ec.cnt ELSE 0 END), 0) AS gold
            FROM time_buckets tb
            LEFT JOIN error_counts ec ON tb.bucket = ec.bucket
            GROUP BY tb.bucket
            ORDER BY tb.bucket
        """)

        rows = cursor.fetchall()
        timestamps = [row[0] for row in rows]
        counts = [int(row[1]) for row in rows]
        by_zone = {
            'BRONZE': [int(row[2]) for row in rows],
            'SILVER': [int(row[3]) for row in rows],
            'GOLD': [int(row[4]) for row in rows],
        }

        return ErrorTrendResponse(
            timestamps=timestamps,
            counts=counts,
            by_zone=by_zone,
        )
    finally:
        conn.close()


@router.get("/{error_id}", response_model=ProcessingError)
async def get_error(error_id: str):
    """Get detailed information for a specific error."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT error_id, batch_id, chunk_index, total_chunks, zone,
                   raw_id, stg_id, content_hash, message_type, message_id,
                   error_code, error_message, error_stack_trace, original_content,
                   status, retry_count, max_retries, last_retry_at, next_retry_at,
                   resolved_at, resolved_by, resolution_notes, created_at, updated_at
            FROM bronze.processing_errors
            WHERE error_id = %s
        """, (error_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Error not found")

        return ProcessingError(
            error_id=row[0],
            batch_id=row[1],
            chunk_index=row[2],
            total_chunks=row[3],
            zone=row[4],
            raw_id=row[5],
            stg_id=row[6],
            content_hash=row[7],
            message_type=row[8],
            message_id=row[9],
            error_code=row[10],
            error_message=row[11],
            error_stack_trace=row[12],
            original_content=row[13],
            status=row[14],
            retry_count=row[15],
            max_retries=row[16],
            last_retry_at=row[17],
            next_retry_at=row[18],
            resolved_at=row[19],
            resolved_by=row[20],
            resolution_notes=row[21],
            created_at=row[22],
            updated_at=row[23],
        )
    finally:
        conn.close()


@router.get("/{error_id}/history")
async def get_error_history(error_id: str):
    """Get the action history for a specific error."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT history_id, action, action_by, action_notes,
                   previous_status, new_status, created_at
            FROM bronze.processing_error_history
            WHERE error_id = %s
            ORDER BY created_at DESC
        """, (error_id,))

        rows = cursor.fetchall()
        return [
            {
                "history_id": row[0],
                "action": row[1],
                "action_by": row[2],
                "action_notes": row[3],
                "previous_status": row[4],
                "new_status": row[5],
                "created_at": row[6],
            }
            for row in rows
        ]
    finally:
        conn.close()


# =============================================================================
# Individual Error Actions
# =============================================================================

@router.post("/{error_id}/retry")
async def retry_error(error_id: str, request: RetryRequest = Body(default=RetryRequest())):
    """
    Schedule an error for retry.

    The error will be picked up by the retry processor after the delay.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Get current error state
        cursor.execute("""
            SELECT status, retry_count, max_retries FROM bronze.processing_errors
            WHERE error_id = %s
        """, (error_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Error not found")

        current_status, retry_count, max_retries = row

        if current_status in ('RESOLVED', 'SKIPPED'):
            raise HTTPException(status_code=400, detail=f"Cannot retry error with status {current_status}")

        if retry_count >= max_retries:
            raise HTTPException(status_code=400, detail="Maximum retries reached")

        next_retry = datetime.utcnow() + timedelta(minutes=request.delay_minutes)

        # Update error status
        cursor.execute("""
            UPDATE bronze.processing_errors
            SET status = 'RETRYING',
                next_retry_at = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE error_id = %s
            RETURNING status
        """, (next_retry, error_id))

        # Log history
        cursor.execute("""
            INSERT INTO bronze.processing_error_history
            (error_id, action, previous_status, new_status, action_notes)
            VALUES (%s, 'RETRY_SCHEDULED', %s, 'RETRYING', %s)
        """, (error_id, current_status, f"Scheduled for retry at {next_retry}"))

        conn.commit()

        return {
            "status": "scheduled",
            "error_id": error_id,
            "next_retry_at": next_retry.isoformat(),
        }
    finally:
        conn.close()


@router.post("/{error_id}/skip")
async def skip_error(error_id: str, reason: str = Body(..., embed=True)):
    """
    Skip an error (won't be retried).

    Use this when the error is known to be unrecoverable.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status FROM bronze.processing_errors WHERE error_id = %s
        """, (error_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Error not found")

        current_status = row[0]

        cursor.execute("""
            UPDATE bronze.processing_errors
            SET status = 'SKIPPED',
                resolution_notes = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE error_id = %s
        """, (reason, error_id))

        cursor.execute("""
            INSERT INTO bronze.processing_error_history
            (error_id, action, previous_status, new_status, action_notes)
            VALUES (%s, 'SKIPPED', %s, 'SKIPPED', %s)
        """, (error_id, current_status, reason))

        conn.commit()

        return {"status": "skipped", "error_id": error_id}
    finally:
        conn.close()


@router.post("/{error_id}/resolve")
async def resolve_error(error_id: str, request: ResolveRequest):
    """
    Mark an error as resolved.

    Use this when the issue has been manually fixed.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status FROM bronze.processing_errors WHERE error_id = %s
        """, (error_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Error not found")

        current_status = row[0]

        cursor.execute("""
            UPDATE bronze.processing_errors
            SET status = 'RESOLVED',
                resolved_at = CURRENT_TIMESTAMP,
                resolved_by = %s,
                resolution_notes = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE error_id = %s
        """, (request.resolved_by, request.resolution_notes, error_id))

        cursor.execute("""
            INSERT INTO bronze.processing_error_history
            (error_id, action, action_by, previous_status, new_status, action_notes)
            VALUES (%s, 'RESOLVED', %s, %s, 'RESOLVED', %s)
        """, (error_id, request.resolved_by, current_status, request.resolution_notes))

        conn.commit()

        return {"status": "resolved", "error_id": error_id}
    finally:
        conn.close()


@router.post("/{error_id}/abandon")
async def abandon_error(error_id: str, reason: str = Body(..., embed=True)):
    """
    Abandon an error (give up retrying).

    Use this when retries have been exhausted and manual intervention isn't possible.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status FROM bronze.processing_errors WHERE error_id = %s
        """, (error_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Error not found")

        current_status = row[0]

        cursor.execute("""
            UPDATE bronze.processing_errors
            SET status = 'ABANDONED',
                resolution_notes = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE error_id = %s
        """, (reason, error_id))

        cursor.execute("""
            INSERT INTO bronze.processing_error_history
            (error_id, action, previous_status, new_status, action_notes)
            VALUES (%s, 'ABANDONED', %s, 'ABANDONED', %s)
        """, (error_id, current_status, reason))

        conn.commit()

        return {"status": "abandoned", "error_id": error_id}
    finally:
        conn.close()


# =============================================================================
# Bulk Operations
# =============================================================================

@router.post("/bulk", response_model=BulkActionResponse)
async def bulk_action(request: BulkActionRequest):
    """
    Perform a bulk action on multiple errors.

    Supports:
    - retry: Schedule all for retry
    - skip: Skip all errors
    - resolve: Mark all as resolved
    - abandon: Mark all as abandoned
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        success_count = 0
        failed_ids = []

        for error_id in request.error_ids:
            try:
                if request.action == BulkAction.RETRY:
                    cursor.execute("""
                        UPDATE bronze.processing_errors
                        SET status = 'RETRYING',
                            next_retry_at = NOW() + INTERVAL '5 minutes',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE error_id = %s AND status NOT IN ('RESOLVED', 'SKIPPED')
                        RETURNING error_id
                    """, (error_id,))
                elif request.action == BulkAction.SKIP:
                    cursor.execute("""
                        UPDATE bronze.processing_errors
                        SET status = 'SKIPPED',
                            resolution_notes = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE error_id = %s
                        RETURNING error_id
                    """, (request.notes or 'Bulk skipped', error_id))
                elif request.action == BulkAction.RESOLVE:
                    cursor.execute("""
                        UPDATE bronze.processing_errors
                        SET status = 'RESOLVED',
                            resolved_at = CURRENT_TIMESTAMP,
                            resolved_by = %s,
                            resolution_notes = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE error_id = %s
                        RETURNING error_id
                    """, (request.resolved_by or 'SYSTEM', request.notes or 'Bulk resolved', error_id))
                elif request.action == BulkAction.ABANDON:
                    cursor.execute("""
                        UPDATE bronze.processing_errors
                        SET status = 'ABANDONED',
                            resolution_notes = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE error_id = %s
                        RETURNING error_id
                    """, (request.notes or 'Bulk abandoned', error_id))

                if cursor.fetchone():
                    success_count += 1
                else:
                    failed_ids.append(error_id)
            except Exception:
                failed_ids.append(error_id)

        conn.commit()

        return BulkActionResponse(
            action=request.action.value,
            requested_count=len(request.error_ids),
            success_count=success_count,
            failed_ids=failed_ids,
        )
    finally:
        conn.close()


@router.post("/bulk/retry-all-pending")
async def retry_all_pending(
    zone: Optional[Zone] = Query(None, description="Filter by zone"),
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    max_count: int = Query(100, ge=1, le=1000, description="Maximum errors to retry"),
):
    """
    Retry all pending errors that haven't exceeded max retries.

    Optionally filter by zone and message type.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        conditions = ["status = 'PENDING'", "retry_count < max_retries"]
        params = []

        if zone:
            conditions.append("zone = %s")
            params.append(zone.value)
        if message_type:
            conditions.append("message_type = %s")
            params.append(message_type)

        where_clause = " AND ".join(conditions)

        cursor.execute(f"""
            UPDATE bronze.processing_errors
            SET status = 'RETRYING',
                next_retry_at = NOW() + INTERVAL '5 minutes',
                updated_at = CURRENT_TIMESTAMP
            WHERE error_id IN (
                SELECT error_id FROM bronze.processing_errors
                WHERE {where_clause}
                ORDER BY created_at ASC
                LIMIT %s
            )
            RETURNING error_id
        """, params + [max_count])

        updated_ids = [row[0] for row in cursor.fetchall()]
        conn.commit()

        return {
            "status": "scheduled",
            "count": len(updated_ids),
            "error_ids": updated_ids,
        }
    finally:
        conn.close()


# =============================================================================
# Error Code Reference
# =============================================================================

@router.get("/codes/list", response_model=List[ErrorCodeInfo])
async def list_error_codes():
    """Get all error code definitions."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT error_code, error_category, description, is_retryable, suggested_action
            FROM bronze.error_codes
            ORDER BY error_category, error_code
        """)

        return [
            ErrorCodeInfo(
                error_code=row[0],
                error_category=row[1],
                description=row[2],
                is_retryable=row[3],
                suggested_action=row[4],
            )
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()


@router.get("/codes/{error_code}", response_model=ErrorCodeInfo)
async def get_error_code(error_code: str):
    """Get information about a specific error code."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT error_code, error_category, description, is_retryable, suggested_action
            FROM bronze.error_codes
            WHERE error_code = %s
        """, (error_code,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Error code not found")

        return ErrorCodeInfo(
            error_code=row[0],
            error_category=row[1],
            description=row[2],
            is_retryable=row[3],
            suggested_action=row[4],
        )
    finally:
        conn.close()

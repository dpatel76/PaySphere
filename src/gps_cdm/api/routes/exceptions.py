"""
GPS CDM API - Exception Routes
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Request/Response Models
class ExceptionResponse(BaseModel):
    exception_id: str
    batch_id: str
    source_layer: str
    source_table: str
    source_record_id: str
    exception_type: str
    exception_message: str
    severity: str
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExceptionSummaryResponse(BaseModel):
    total: int
    by_type: dict
    by_layer: dict
    by_severity: dict
    by_status: dict
    new_count: int
    resolved_count: int
    critical_count: int
    retryable_count: int


class AcknowledgeRequest(BaseModel):
    notes: Optional[str] = None
    acknowledged_by: Optional[str] = None


class ResolveRequest(BaseModel):
    resolution_notes: str
    resolved_by: str
    status: Optional[str] = "RESOLVED"


class RetryRequest(BaseModel):
    delay_seconds: int = 300


# Database connection helper
def get_db_connection():
    """Get database connection using centralized configuration."""
    import os
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5433)),
        database=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )


@router.get("", response_model=List[dict])
async def list_exceptions(
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    source_layer: Optional[str] = Query(None, description="Filter by layer (bronze, silver, gold)"),
    exception_type: Optional[str] = Query(None, description="Filter by exception type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
):
    """List processing exceptions with filters."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        exceptions = manager.get_exceptions(
            batch_id=batch_id,
            source_layer=source_layer,
            exception_type=exception_type,
            severity=severity,
            status=status,
            limit=limit,
            offset=offset,
        )
        return exceptions
    finally:
        db.close()


@router.get("/summary", response_model=ExceptionSummaryResponse)
async def exception_summary(
    batch_id: Optional[str] = Query(None),
    hours_back: int = Query(24, ge=1, le=720),
):
    """Get exception summary statistics."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        summary = manager.get_exception_summary(batch_id, hours_back)
        return ExceptionSummaryResponse(
            total=summary.total,
            by_type=summary.by_type,
            by_layer=summary.by_layer,
            by_severity=summary.by_severity,
            by_status=summary.by_status,
            new_count=summary.new_count,
            resolved_count=summary.resolved_count,
            critical_count=summary.critical_count,
            retryable_count=summary.retryable_count,
        )
    finally:
        db.close()


@router.get("/{exception_id}")
async def get_exception(exception_id: str):
    """Get detailed exception information."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        exc = manager.get_exception(exception_id)
        if not exc:
            raise HTTPException(status_code=404, detail="Exception not found")
        return exc.__dict__
    finally:
        db.close()


@router.post("/{exception_id}/acknowledge")
async def acknowledge_exception(exception_id: str, request: AcknowledgeRequest):
    """Acknowledge an exception."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        success = manager.acknowledge_exception(
            exception_id,
            notes=request.notes,
            acknowledged_by=request.acknowledged_by,
        )
        if not success:
            raise HTTPException(status_code=400, detail="Could not acknowledge exception")
        return {"status": "acknowledged", "exception_id": exception_id}
    finally:
        db.close()


@router.post("/{exception_id}/resolve")
async def resolve_exception(exception_id: str, request: ResolveRequest):
    """Resolve an exception."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        success = manager.resolve_exception(
            exception_id,
            resolution_notes=request.resolution_notes,
            resolved_by=request.resolved_by,
            status=request.status,
        )
        if not success:
            raise HTTPException(status_code=400, detail="Could not resolve exception")
        return {"status": "resolved", "exception_id": exception_id}
    finally:
        db.close()


@router.post("/{exception_id}/ignore")
async def ignore_exception(exception_id: str, reason: str, ignored_by: str):
    """Ignore an exception (won't be retried)."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        success = manager.ignore_exception(exception_id, reason, ignored_by)
        if not success:
            raise HTTPException(status_code=400, detail="Could not ignore exception")
        return {"status": "ignored", "exception_id": exception_id}
    finally:
        db.close()


@router.post("/{exception_id}/retry")
async def retry_exception(exception_id: str, request: RetryRequest):
    """Schedule an exception for retry."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        success = manager.schedule_retry(exception_id, delay_seconds=request.delay_seconds)
        if not success:
            raise HTTPException(status_code=400, detail="Could not schedule retry")
        return {"status": "scheduled", "exception_id": exception_id}
    finally:
        db.close()


@router.get("/record/{layer}/{table}/{record_id}")
async def get_exceptions_for_record(layer: str, table: str, record_id: str):
    """Get all exceptions for a specific record."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        return manager.get_exceptions_for_record(layer, table, record_id)
    finally:
        db.close()


@router.get("/retryable")
async def get_retryable_exceptions(
    source_layer: Optional[str] = None,
    limit: int = Query(100, le=1000),
):
    """Get exceptions that are due for retry."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        return manager.get_retryable_exceptions(source_layer, limit)
    finally:
        db.close()


@router.post("/bulk/acknowledge")
async def bulk_acknowledge(exception_ids: List[str], notes: Optional[str] = None):
    """Acknowledge multiple exceptions at once."""
    from gps_cdm.orchestration.exception_manager import ExceptionManager

    db = get_db_connection()
    try:
        manager = ExceptionManager(db)
        count = manager.bulk_acknowledge(exception_ids, notes)
        return {"acknowledged_count": count}
    finally:
        db.close()

"""
GPS CDM API - Reconciliation Routes
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Request/Response Models
class ReconciliationRunResponse(BaseModel):
    recon_run_id: str
    batch_id: Optional[str]
    status: str
    total_source_records: int
    total_target_records: int
    matched_count: int
    mismatched_count: int
    source_only_count: int
    match_rate: float


class InvestigateRequest(BaseModel):
    notes: str
    investigated_by: str
    status: str = "INVESTIGATED"


class ResolveRequest(BaseModel):
    action: str  # ACCEPTED, CORRECTED, REJECTED, REPROCESSED, MANUAL_FIX
    notes: str
    resolved_by: str


# Database connection helper
def get_db_connection():
    """Get database connection."""
    import psycopg2
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gps_cdm",
    )


@router.get("/summary")
async def recon_summary(
    batch_id: Optional[str] = Query(None),
    hours_back: int = Query(24, ge=1, le=720),
):
    """Get reconciliation summary."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        return service.get_reconciliation_summary(batch_id, hours_back)
    finally:
        db.close()


@router.get("/mismatches")
async def list_mismatches(
    batch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    investigation_status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """List reconciliation mismatches."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        return service.get_mismatches(
            batch_id=batch_id,
            status=status,
            investigation_status=investigation_status,
            limit=limit,
        )
    finally:
        db.close()


@router.get("/orphans")
async def get_orphans(
    direction: str = Query("bronze", description="bronze or gold"),
    batch_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Get orphan records."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        return service.get_orphans(direction, batch_id, limit)
    finally:
        db.close()


@router.post("/run/{batch_id}")
async def run_reconciliation(
    batch_id: str,
    initiated_by: Optional[str] = Query(None),
):
    """Run reconciliation for a batch."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        result = service.reconcile_batch(batch_id, initiated_by)
        return ReconciliationRunResponse(
            recon_run_id=result.recon_run_id,
            batch_id=result.batch_id,
            status=result.status,
            total_source_records=result.total_source_records,
            total_target_records=result.total_target_records,
            matched_count=result.matched_count,
            mismatched_count=result.mismatched_count,
            source_only_count=result.source_only_count,
            match_rate=result.match_rate,
        )
    finally:
        db.close()


@router.post("/{recon_id}/investigate")
async def investigate_mismatch(recon_id: str, request: InvestigateRequest):
    """Mark a mismatch as investigated."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        success = service.investigate_mismatch(
            recon_id,
            notes=request.notes,
            investigated_by=request.investigated_by,
            status=request.status,
        )
        if not success:
            raise HTTPException(status_code=400, detail="Could not update investigation")
        return {"status": "updated", "recon_id": recon_id}
    finally:
        db.close()


@router.post("/{recon_id}/resolve")
async def resolve_mismatch(recon_id: str, request: ResolveRequest):
    """Resolve a mismatch."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        success = service.resolve_mismatch(
            recon_id,
            action=request.action,
            notes=request.notes,
            resolved_by=request.resolved_by,
        )
        if not success:
            raise HTTPException(status_code=400, detail="Could not resolve mismatch")
        return {"status": "resolved", "recon_id": recon_id}
    finally:
        db.close()


@router.post("/{recon_id}/accept")
async def accept_mismatch(
    recon_id: str,
    notes: str,
    accepted_by: str,
):
    """Accept a mismatch as valid."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        success = service.accept_mismatch(recon_id, notes, accepted_by)
        if not success:
            raise HTTPException(status_code=400, detail="Could not accept mismatch")
        return {"status": "accepted", "recon_id": recon_id}
    finally:
        db.close()


@router.get("/history")
async def get_run_history(
    batch_id: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
):
    """Get reconciliation run history."""
    from gps_cdm.orchestration.reconciliation import ReconciliationService

    db = get_db_connection()
    try:
        service = ReconciliationService(db)
        return service.get_run_history(batch_id, limit)
    finally:
        db.close()

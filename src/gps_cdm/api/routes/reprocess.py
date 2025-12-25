"""
GPS CDM API - Reprocessing Routes
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# Request/Response Models
class ReprocessRecordRequest(BaseModel):
    layer: str  # bronze, silver
    record_id: str
    force: bool = False


class ReprocessBatchRequest(BaseModel):
    layer: Optional[str] = None
    limit: int = 100


class UpdateAndReprocessRequest(BaseModel):
    layer: str
    table_name: str
    record_id: str
    updates: Dict
    reprocess: bool = True


class ReprocessResponse(BaseModel):
    record_id: str
    source_layer: str
    status: str
    promoted_to_layer: Optional[str]
    new_record_id: Optional[str]
    error_message: Optional[str]


class BatchReprocessResponse(BaseModel):
    batch_id: str
    total_records: int
    success_count: int
    failed_count: int
    skipped_count: int
    duration_seconds: float


# Database connection helper
def get_db_connection():
    """Get database connection."""
    import psycopg2
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gps_cdm",
    )


@router.post("/record")
async def reprocess_record(request: ReprocessRecordRequest):
    """Re-process a single record."""
    from gps_cdm.orchestration.reprocessor import PipelineReprocessor

    db = get_db_connection()
    try:
        reprocessor = PipelineReprocessor(db)

        if request.layer == "bronze":
            result = reprocessor.reprocess_bronze_record(request.record_id, request.force)
        elif request.layer == "silver":
            result = reprocessor.reprocess_silver_record(request.record_id, request.force)
        else:
            raise HTTPException(status_code=400, detail="Invalid layer")

        return ReprocessResponse(
            record_id=result.record_id,
            source_layer=result.source_layer,
            status=result.status,
            promoted_to_layer=result.promoted_to_layer,
            new_record_id=result.new_record_id,
            error_message=result.error_message,
        )
    finally:
        db.close()


@router.post("/batch/{batch_id}")
async def reprocess_batch(batch_id: str, request: ReprocessBatchRequest):
    """Re-process failed records in batch."""
    from gps_cdm.orchestration.reprocessor import PipelineReprocessor

    db = get_db_connection()
    try:
        reprocessor = PipelineReprocessor(db)
        result = reprocessor.reprocess_failed_batch(
            batch_id,
            layer=request.layer,
            limit=request.limit,
        )
        return BatchReprocessResponse(
            batch_id=result.batch_id,
            total_records=result.total_records,
            success_count=result.success_count,
            failed_count=result.failed_count,
            skipped_count=result.skipped_count,
            duration_seconds=result.duration_seconds,
        )
    finally:
        db.close()


@router.post("/dq-failures")
async def reprocess_dq_failures(
    batch_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Re-process records that failed DQ validation."""
    from gps_cdm.orchestration.reprocessor import PipelineReprocessor
    from gps_cdm.orchestration.dq_validator import DataQualityValidator

    db = get_db_connection()
    try:
        dq_validator = DataQualityValidator(db)
        reprocessor = PipelineReprocessor(db, dq_validator=dq_validator)
        result = reprocessor.reprocess_dq_failures(batch_id, limit)
        return BatchReprocessResponse(
            batch_id=result.batch_id,
            total_records=result.total_records,
            success_count=result.success_count,
            failed_count=result.failed_count,
            skipped_count=result.skipped_count,
            duration_seconds=result.duration_seconds,
        )
    finally:
        db.close()


@router.post("/exceptions")
async def reprocess_exceptions(
    batch_id: Optional[str] = Query(None),
    exception_type: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Re-process records from exceptions."""
    from gps_cdm.orchestration.reprocessor import reprocess_exceptions

    db = get_db_connection()
    try:
        result = reprocess_exceptions(db, batch_id, exception_type, limit)
        return BatchReprocessResponse(
            batch_id=result.batch_id,
            total_records=result.total_records,
            success_count=result.success_count,
            failed_count=result.failed_count,
            skipped_count=result.skipped_count,
            duration_seconds=result.duration_seconds,
        )
    finally:
        db.close()


@router.put("/record/{layer}/{table}/{record_id}")
async def update_record(
    layer: str,
    table: str,
    record_id: str,
    updates: Dict,
    reprocess: bool = Query(True),
):
    """Update a record and optionally re-process."""
    from gps_cdm.orchestration.reprocessor import PipelineReprocessor

    db = get_db_connection()
    try:
        reprocessor = PipelineReprocessor(db)
        success, result = reprocessor.update_and_reprocess(
            layer, table, record_id, updates, reprocess
        )

        if not success:
            raise HTTPException(status_code=400, detail="Update failed")

        response = {"update_status": "success", "record_id": record_id}
        if result:
            response["reprocess_result"] = {
                "status": result.status,
                "promoted_to_layer": result.promoted_to_layer,
                "new_record_id": result.new_record_id,
            }
        return response
    finally:
        db.close()


@router.get("/stuck-records")
async def get_stuck_records(
    batch_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Get records stuck at each pipeline stage."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        results = {"bronze_to_silver": [], "silver_to_gold": [], "dq_failures": []}

        # Bronze records not promoted to Silver
        cursor.execute("""
            SELECT raw_id, message_type, processing_status, processing_error
            FROM bronze.raw_payment_messages
            WHERE processing_status = 'FAILED'
               OR (processing_status = 'PROCESSED' AND silver_stg_id IS NULL)
            LIMIT %s
        """, (limit,))
        columns = [desc[0] for desc in cursor.description]
        results["bronze_to_silver"] = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Silver records not promoted to Gold
        cursor.execute("""
            SELECT stg_id, msg_id, processing_status, processing_error
            FROM silver.stg_pain001
            WHERE processing_status = 'FAILED'
               OR (processing_status = 'PROCESSED' AND gold_instruction_id IS NULL)
            LIMIT %s
        """, (limit,))
        columns = [desc[0] for desc in cursor.description]
        results["silver_to_gold"] = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # DQ failures
        cursor.execute("""
            SELECT stg_id, msg_id, dq_status, dq_score
            FROM silver.stg_pain001
            WHERE dq_status = 'FAILED'
            LIMIT %s
        """, (limit,))
        columns = [desc[0] for desc in cursor.description]
        results["dq_failures"] = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return results
    finally:
        db.close()

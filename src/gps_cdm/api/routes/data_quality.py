"""
GPS CDM API - Data Quality Routes
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Request/Response Models
class DQMetricsResponse(BaseModel):
    layer: str
    table_name: str
    batch_id: Optional[str]
    completeness_score: Optional[float]
    validity_score: Optional[float]
    accuracy_score: Optional[float]
    overall_score: Optional[float]
    overall_status: str
    total_records: int
    passed_records: int
    failed_records: int


class DQRecordResultResponse(BaseModel):
    record_id: str
    layer: str
    table_name: str
    status: str
    overall_score: float
    passed_rules: int
    failed_rules: int


class ValidateBatchRequest(BaseModel):
    layer: str = "silver"
    table_name: str = "stg_pain001"
    update_record_status: bool = True


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
async def dq_summary(
    batch_id: Optional[str] = Query(None),
    layer: Optional[str] = Query(None),
):
    """Get DQ summary metrics."""
    from gps_cdm.orchestration.dq_validator import DataQualityValidator

    db = get_db_connection()
    try:
        validator = DataQualityValidator(db)
        metrics = validator.get_metrics(batch_id=batch_id, layer=layer)
        return [
            DQMetricsResponse(
                layer=m.layer,
                table_name=m.table_name,
                batch_id=m.batch_id,
                completeness_score=m.completeness_score,
                validity_score=m.validity_score,
                accuracy_score=m.accuracy_score,
                overall_score=m.overall_score,
                overall_status=m.overall_status,
                total_records=m.total_records,
                passed_records=m.passed_records,
                failed_records=m.failed_records,
            ) for m in metrics
        ]
    finally:
        db.close()


@router.get("/failures")
async def dq_failures(
    batch_id: Optional[str] = Query(None),
    layer: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """List records with DQ failures."""
    from gps_cdm.orchestration.dq_validator import DataQualityValidator

    db = get_db_connection()
    try:
        validator = DataQualityValidator(db)
        return validator.get_failed_records(
            batch_id=batch_id,
            layer=layer,
            table_name=table_name,
            limit=limit,
        )
    finally:
        db.close()


@router.post("/validate/{layer}/{table}/{record_id}")
async def validate_record(
    layer: str,
    table: str,
    record_id: str,
    batch_id: str = Query(..., description="Batch ID for tracking"),
):
    """Validate a single record."""
    from gps_cdm.orchestration.dq_validator import DataQualityValidator

    db = get_db_connection()
    try:
        validator = DataQualityValidator(db)
        result = validator.revalidate_record(layer, table, record_id, batch_id)
        return DQRecordResultResponse(
            record_id=result.record_id,
            layer=result.layer,
            table_name=result.table_name,
            status=result.status,
            overall_score=result.overall_score,
            passed_rules=result.passed_rules,
            failed_rules=result.failed_rules,
        )
    finally:
        db.close()


@router.post("/validate-batch/{batch_id}")
async def validate_batch(batch_id: str, request: ValidateBatchRequest):
    """Run DQ validation on entire batch."""
    from gps_cdm.orchestration.dq_validator import DataQualityValidator

    db = get_db_connection()
    try:
        validator = DataQualityValidator(db)
        result = validator.validate_batch(
            batch_id=batch_id,
            layer=request.layer,
            table_name=request.table_name,
            update_record_status=request.update_record_status,
        )
        return {
            "batch_id": result.batch_id,
            "layer": result.layer,
            "table_name": result.table_name,
            "status": result.status,
            "overall_score": result.overall_score,
            "total_records": result.total_records,
            "passed_records": result.passed_records,
            "failed_records": result.failed_records,
            "warning_records": result.warning_records,
            "dimension_scores": result.dimension_scores,
        }
    finally:
        db.close()


@router.get("/rules")
async def list_rules(
    layer: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    active_only: bool = Query(True),
):
    """List DQ rules."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        conditions = ["1=1"]
        params = []

        if layer:
            conditions.append("layer = %s")
            params.append(layer)
        if table_name:
            conditions.append("table_name = %s")
            params.append(table_name)
        if active_only:
            conditions.append("is_active = true")

        cursor.execute(f"""
            SELECT rule_id, rule_name, rule_description, layer, table_name,
                   field_name, rule_type, rule_expression, weight, is_blocking
            FROM observability.obs_dq_rules
            WHERE {' AND '.join(conditions)}
            ORDER BY layer, table_name, is_blocking DESC, weight DESC
        """, params)

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        db.close()


@router.get("/results/{batch_id}")
async def get_batch_results(
    batch_id: str,
    passed_only: Optional[bool] = Query(None),
    limit: int = Query(500, le=5000),
):
    """Get detailed DQ results for a batch."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        conditions = ["batch_id = %s"]
        params = [batch_id]

        if passed_only is not None:
            conditions.append("passed = %s")
            params.append(passed_only)

        cursor.execute(f"""
            SELECT dq_result_id, layer, table_name, record_id,
                   rule_id, rule_name, rule_type, passed,
                   actual_value, expected_value, error_message,
                   score, validated_at
            FROM observability.obs_data_quality_results
            WHERE {' AND '.join(conditions)}
            ORDER BY validated_at DESC
            LIMIT %s
        """, params + [limit])

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        db.close()

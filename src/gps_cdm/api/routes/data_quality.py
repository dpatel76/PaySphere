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
    import os
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5433")),
        dbname=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )


@router.get("/summary")
async def dq_summary(
    batch_id: Optional[str] = Query(None),
    layer: Optional[str] = Query(None),
):
    """Get DQ summary metrics from Neo4j."""
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    neo4j = get_neo4j_service()
    if not neo4j.is_available():
        # Fallback to empty response if Neo4j is not available
        return []

    # Query DQ metrics from Neo4j
    conditions = []
    if batch_id:
        conditions.append(f"d.batch_id = '{batch_id}'")
    if layer:
        conditions.append(f"d.layer = '{layer}'")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        MATCH (d:DQMetrics)
        WHERE {where_clause}
        RETURN d.batch_id as batch_id,
               d.layer as layer,
               d.entity_type as table_name,
               d.completeness_avg as completeness_score,
               d.validity_avg as validity_score,
               d.accuracy_avg as accuracy_score,
               d.overall_avg_score as overall_score,
               d.records_above_threshold as passed_records,
               d.records_below_threshold as failed_records
        ORDER BY d.evaluated_at DESC
        LIMIT 50
    """

    results = neo4j.run_query(query)

    return [
        DQMetricsResponse(
            layer=r.get("layer", "silver"),
            table_name=r.get("table_name", "unknown"),
            batch_id=r.get("batch_id"),
            completeness_score=r.get("completeness_score"),
            validity_score=r.get("validity_score"),
            accuracy_score=r.get("accuracy_score"),
            overall_score=r.get("overall_score", 0) * 100 if r.get("overall_score") else None,  # Convert to percentage
            overall_status="PASSED" if (r.get("overall_score", 0) or 0) >= 0.8 else "FAILED",
            total_records=(r.get("passed_records", 0) or 0) + (r.get("failed_records", 0) or 0),
            passed_records=r.get("passed_records", 0) or 0,
            failed_records=r.get("failed_records", 0) or 0,
        ) for r in results
    ]


@router.get("/failures")
async def dq_failures(
    batch_id: Optional[str] = Query(None),
    layer: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
):
    """List individual DQ failure records from PostgreSQL/Databricks."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        conditions = ["rules_failed > 0"]  # Records with at least one failed rule
        params = []

        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)
        if layer:
            conditions.append("layer = %s")
            params.append(layer)
        if table_name:
            conditions.append("entity_type = %s")
            params.append(table_name)

        cursor.execute(f"""
            SELECT dq_result_id, batch_id, layer, entity_type as table_name,
                   entity_id as record_id, record_key, overall_score,
                   completeness_score, accuracy_score, validity_score,
                   rules_executed, rules_passed, rules_failed, rules_warned,
                   rule_results, issues, remediation_status, evaluated_at
            FROM observability.obs_dq_results
            WHERE {' AND '.join(conditions)}
            ORDER BY evaluated_at DESC
            LIMIT %s
        """, params + [limit])

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        db.close()


@router.post("/validate/{layer}/{table}/{record_id}")
async def validate_record(
    layer: str,
    table: str,
    record_id: str,
    batch_id: str = Query(..., description="Batch ID for tracking"),
):
    """Validate a single record - triggers DQ validation via Celery task."""
    # TODO: Implement via Celery task for async validation
    # For now, return a placeholder response
    return DQRecordResultResponse(
        record_id=record_id,
        layer=layer,
        table_name=table,
        status="PENDING",
        overall_score=0.0,
        passed_rules=0,
        failed_rules=0,
    )


@router.post("/validate-batch/{batch_id}")
async def validate_batch(batch_id: str, request: ValidateBatchRequest):
    """Run DQ validation on entire batch - triggers Celery task."""
    # TODO: Implement via Celery task for async batch validation
    # For now, return a placeholder response
    return {
        "batch_id": batch_id,
        "layer": request.layer,
        "table_name": request.table_name,
        "status": "PENDING",
        "message": "Batch validation queued for processing",
    }


@router.get("/rules")
async def list_rules(
    layer: Optional[str] = Query(None),
    table_name: Optional[str] = Query(None),
    active_only: bool = Query(True),
):
    """List DQ rules from PostgreSQL validation_rules table."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        conditions = ["1=1"]
        params = []

        if layer:
            conditions.append("layer = %s")
            params.append(layer)
        if table_name:
            conditions.append("target_entity = %s")
            params.append(table_name)
        if active_only:
            conditions.append("is_active = true")

        cursor.execute(f"""
            SELECT rule_id, rule_name, rule_description, layer,
                   target_entity as table_name, target_field as field_name,
                   rule_type, dimension, severity, rule_expression, weight,
                   CASE WHEN severity = 'CRITICAL' THEN true ELSE false END as is_blocking
            FROM observability.obs_validation_rules
            WHERE {' AND '.join(conditions)}
            ORDER BY layer, target_entity, severity DESC, weight DESC
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
    """Get detailed DQ results for a batch from PostgreSQL."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        conditions = ["batch_id = %s"]
        params = [batch_id]

        if passed_only is True:
            conditions.append("rules_failed = 0")
        elif passed_only is False:
            conditions.append("rules_failed > 0")

        cursor.execute(f"""
            SELECT dq_result_id, batch_id, layer, entity_type as table_name,
                   entity_id as record_id, record_key, overall_score,
                   completeness_score, accuracy_score, validity_score,
                   rules_executed, rules_passed, rules_failed, rules_warned,
                   rule_results, issues, remediation_status, evaluated_at
            FROM observability.obs_dq_results
            WHERE {' AND '.join(conditions)}
            ORDER BY evaluated_at DESC
            LIMIT %s
        """, params + [limit])

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        db.close()

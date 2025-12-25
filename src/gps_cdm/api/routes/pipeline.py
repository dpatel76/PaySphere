"""
GPS CDM API - Pipeline Routes

Provides endpoints for pipeline monitoring:
1. Batch tracking and status
2. Pipeline statistics
3. Layer-level metrics

Data sources:
- Databricks: Primary data store for medallion layers
- PostgreSQL: Fallback for local development
- Neo4j: Knowledge graph (via graph routes)
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Data source configuration
DATA_SOURCE = os.environ.get("GPS_CDM_DATA_SOURCE", "auto")  # auto, databricks, postgresql


# Response Models
class BatchTrackingResponse(BaseModel):
    batch_id: str
    message_type: str
    source_file: Optional[str]
    status: str
    bronze_count: int
    silver_count: int
    gold_count: int
    dq_passed_count: int
    dq_failed_count: int
    error_count: int
    created_at: Optional[datetime]
    completed_at: Optional[datetime]


class LayerStats(BaseModel):
    total: int
    processed: int
    failed: int
    pending: int
    dq_passed: Optional[int] = None
    dq_failed: Optional[int] = None


class PipelineStatsResponse(BaseModel):
    bronze: LayerStats
    silver: LayerStats
    gold: LayerStats
    analytical: LayerStats


# Databricks connector singleton
_databricks_connector = None


def get_databricks_connector():
    """Get or create Databricks connector."""
    global _databricks_connector
    if _databricks_connector is None:
        try:
            from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector
            _databricks_connector = DatabricksConnector()
            if _databricks_connector.is_available():
                logger.info("Using Databricks as data source")
            else:
                _databricks_connector = None
        except Exception as e:
            logger.warning(f"Databricks not available: {e}")
            _databricks_connector = None
    return _databricks_connector


def get_db_connection():
    """Get PostgreSQL database connection."""
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5433)),
        database=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )


def should_use_databricks() -> bool:
    """Determine if Databricks should be used as data source."""
    if DATA_SOURCE == "postgresql":
        return False
    if DATA_SOURCE == "databricks":
        return True
    # Auto-detect: prefer Databricks if available
    connector = get_databricks_connector()
    return connector is not None


@router.get("/batches", response_model=List[dict])
async def list_batches(
    status: Optional[str] = Query(None, description="Filter by status"),
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    hours_back: int = Query(24, ge=1, le=720),
    limit: int = Query(50, le=500),
):
    """List recent batches with their status."""
    # Try Databricks first
    if should_use_databricks():
        try:
            connector = get_databricks_connector()
            batches = connector.get_batches(limit=limit, status=status)
            # Transform Databricks format to API format
            result = []
            for b in batches:
                stats = connector.get_layer_stats(b["batch_id"])
                result.append({
                    "batch_id": b.get("batch_id"),
                    "message_type": b.get("mapping_id", "unknown"),
                    "source_file": b.get("source_path"),
                    "status": b.get("status"),
                    "bronze_count": stats.get("bronze", 0),
                    "silver_count": stats.get("silver", 0),
                    "gold_count": stats.get("gold_payments", 0),
                    "dq_passed_count": stats.get("silver", 0),
                    "dq_failed_count": 0,
                    "error_count": b.get("failed_records", 0),
                    "created_at": b.get("created_at"),
                    "completed_at": b.get("completed_at"),
                    "data_source": "databricks",
                })
            return result
        except Exception as e:
            logger.warning(f"Databricks query failed, falling back to PostgreSQL: {e}")

    # Fallback to PostgreSQL
    db = get_db_connection()
    try:
        cursor = db.cursor()
        conditions = ["1=1"]
        params = []

        if status:
            conditions.append("status = %s")
            params.append(status)
        if message_type:
            conditions.append("message_type = %s")
            params.append(message_type)

        conditions.append("created_at >= NOW() - INTERVAL '%s hours'")
        params.append(hours_back)

        cursor.execute(f"""
            SELECT batch_id, message_type, source_file, status,
                   bronze_count, silver_count, gold_count,
                   dq_passed_count, dq_failed_count, error_count,
                   created_at, completed_at
            FROM observability.obs_batch_tracking
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT %s
        """, params + [limit])

        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        for row in rows:
            row["data_source"] = "postgresql"
        return rows
    except Exception as e:
        # Return empty list if table doesn't exist
        return []
    finally:
        db.close()


@router.get("/batches/{batch_id}")
async def get_batch(batch_id: str):
    """Get detailed batch information."""
    # Try Databricks first
    if should_use_databricks():
        try:
            connector = get_databricks_connector()
            lineage = connector.get_batch_lineage(batch_id)
            batch = lineage.get("batch")
            if batch:
                stats = connector.get_layer_stats(batch_id)
                return {
                    "batch_id": batch.get("batch_id"),
                    "message_type": batch.get("mapping_id", "unknown"),
                    "source_file": batch.get("source_path"),
                    "status": batch.get("status"),
                    "bronze_count": stats.get("bronze", 0),
                    "silver_count": stats.get("silver", 0),
                    "gold_count": stats.get("gold_payments", 0),
                    "dq_passed_count": stats.get("silver", 0),
                    "dq_failed_count": 0,
                    "error_count": batch.get("failed_records", 0),
                    "total_records": batch.get("total_records", 0),
                    "processed_records": batch.get("processed_records", 0),
                    "created_at": batch.get("created_at"),
                    "updated_at": batch.get("updated_at"),
                    "completed_at": batch.get("completed_at"),
                    "data_source": "databricks",
                }
        except Exception as e:
            logger.warning(f"Databricks query failed: {e}")

    # Fallback to PostgreSQL
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT batch_id, message_type, source_file, status,
                   bronze_count, silver_count, gold_count,
                   dq_passed_count, dq_failed_count, error_count,
                   checkpoint_offset, checkpoint_partition, checkpoint_data,
                   created_at, updated_at, completed_at
            FROM observability.obs_batch_tracking
            WHERE batch_id = %s
        """, (batch_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Batch not found")

        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        result["data_source"] = "postgresql"
        return result
    finally:
        db.close()


@router.get("/stats")
async def get_pipeline_stats(
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    hours_back: int = Query(24, ge=1, le=720),
):
    """Get pipeline statistics by layer."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Build condition
        conditions = ["created_at >= NOW() - INTERVAL '%s hours'"]
        params = [hours_back]

        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)

        where_clause = ' AND '.join(conditions)

        # Get aggregated stats
        cursor.execute(f"""
            SELECT
                COALESCE(SUM(bronze_count), 0) as bronze_total,
                COALESCE(SUM(silver_count), 0) as silver_total,
                COALESCE(SUM(gold_count), 0) as gold_total,
                COALESCE(SUM(dq_passed_count), 0) as dq_passed,
                COALESCE(SUM(dq_failed_count), 0) as dq_failed,
                COALESCE(SUM(error_count), 0) as errors,
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_batches,
                COUNT(CASE WHEN status = 'PROCESSING' THEN 1 END) as processing_batches,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_batches
            FROM observability.obs_batch_tracking
            WHERE {where_clause}
        """, params)

        row = cursor.fetchone()
        if not row:
            # Return default stats
            return {
                "bronze": {"total": 0, "processed": 0, "failed": 0, "pending": 0},
                "silver": {"total": 0, "processed": 0, "failed": 0, "pending": 0, "dq_passed": 0, "dq_failed": 0},
                "gold": {"total": 0, "processed": 0, "failed": 0, "pending": 0},
                "analytical": {"total": 0, "processed": 0, "failed": 0, "pending": 0},
            }

        bronze_total = int(row[0]) if row[0] else 0
        silver_total = int(row[1]) if row[1] else 0
        gold_total = int(row[2]) if row[2] else 0
        dq_passed = int(row[3]) if row[3] else 0
        dq_failed = int(row[4]) if row[4] else 0
        errors = int(row[5]) if row[5] else 0

        return {
            "bronze": {
                "total": bronze_total,
                "processed": bronze_total - errors,
                "failed": errors,
                "pending": 0,
            },
            "silver": {
                "total": silver_total,
                "processed": dq_passed,
                "failed": dq_failed,
                "pending": silver_total - dq_passed - dq_failed,
                "dq_passed": dq_passed,
                "dq_failed": dq_failed,
            },
            "gold": {
                "total": gold_total,
                "processed": gold_total,
                "failed": 0,
                "pending": 0,
            },
            "analytical": {
                "total": gold_total,
                "processed": gold_total,
                "failed": 0,
                "pending": 0,
            },
        }
    except Exception as e:
        # Return default stats if table doesn't exist
        return {
            "bronze": {"total": 0, "processed": 0, "failed": 0, "pending": 0},
            "silver": {"total": 0, "processed": 0, "failed": 0, "pending": 0, "dq_passed": 0, "dq_failed": 0},
            "gold": {"total": 0, "processed": 0, "failed": 0, "pending": 0},
            "analytical": {"total": 0, "processed": 0, "failed": 0, "pending": 0},
        }
    finally:
        db.close()


@router.get("/batches/{batch_id}/records/{layer}")
async def get_batch_records(
    batch_id: str,
    layer: str,
    limit: int = Query(25, le=100),
    offset: int = Query(0, ge=0),
):
    """Get records for a batch by layer."""
    # Try Databricks first
    if should_use_databricks():
        try:
            connector = get_databricks_connector()
            records = []
            if layer == "bronze":
                records = connector.get_bronze_records(batch_id=batch_id, limit=limit)
            elif layer == "silver":
                records = connector.get_silver_records(batch_id=batch_id, limit=limit)
            elif layer == "gold":
                records = connector.get_payment_instructions(batch_id=batch_id, limit=limit)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid layer: {layer}")

            # Add data source indicator
            for r in records:
                r["data_source"] = "databricks"
            return records
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Databricks query failed: {e}")

    # Fallback to PostgreSQL
    db = get_db_connection()
    try:
        cursor = db.cursor()

        if layer == "bronze":
            cursor.execute("""
                SELECT raw_id, _batch_id as batch_id, message_type, message_format,
                       source_system, processing_status, source_file_path,
                       _ingested_at as ingested_at
                FROM bronze.raw_payment_messages
                WHERE _batch_id = %s
                ORDER BY _ingested_at DESC
                LIMIT %s OFFSET %s
            """, (batch_id, limit, offset))
        elif layer == "silver":
            cursor.execute("""
                SELECT stg_id, _batch_id as batch_id, msg_id, instructed_amount,
                       instructed_currency, debtor_name, creditor_name,
                       processing_status
                FROM silver.stg_pain001
                WHERE _batch_id = %s
                ORDER BY _processed_at DESC
                LIMIT %s OFFSET %s
            """, (batch_id, limit, offset))
        elif layer == "gold":
            cursor.execute("""
                SELECT instruction_id, payment_id, source_message_type,
                       payment_type, instructed_amount, instructed_currency,
                       current_status, created_at
                FROM gold.cdm_payment_instruction
                WHERE lineage_batch_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (batch_id, limit, offset))
        else:
            raise HTTPException(status_code=400, detail=f"Invalid layer: {layer}")

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except HTTPException:
        raise
    except Exception as e:
        # Return empty list if table doesn't exist
        return []
    finally:
        db.close()


@router.get("/data-sources")
async def get_data_sources():
    """Get current data source configuration and status."""
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    # Check Databricks
    databricks_available = False
    databricks_info = {}
    try:
        connector = get_databricks_connector()
        if connector and connector.is_available():
            databricks_available = True
            databricks_info = {
                "server": connector.server_hostname,
                "catalog": connector.catalog,
                "schema": connector.schema,
            }
    except Exception:
        pass

    # Check Neo4j
    neo4j_available = False
    try:
        neo4j = get_neo4j_service()
        neo4j_available = neo4j.is_available()
    except Exception:
        pass

    # Check PostgreSQL
    postgres_available = False
    try:
        db = get_db_connection()
        db.close()
        postgres_available = True
    except Exception:
        pass

    return {
        "configured_source": DATA_SOURCE,
        "active_source": "databricks" if should_use_databricks() else "postgresql",
        "sources": {
            "databricks": {
                "available": databricks_available,
                "info": databricks_info,
                "purpose": "Medallion layer data (Bronze, Silver, Gold)",
            },
            "neo4j": {
                "available": neo4j_available,
                "purpose": "Knowledge graph (batch lineage, schema lineage)",
            },
            "postgresql": {
                "available": postgres_available,
                "purpose": "Fallback/local development",
            },
        },
    }


@router.get("/health")
async def pipeline_health():
    """Get pipeline health status."""
    # Check data sources first
    databricks_ok = should_use_databricks()
    neo4j_ok = False
    try:
        from gps_cdm.orchestration.neo4j_service import get_neo4j_service
        neo4j = get_neo4j_service()
        neo4j_ok = neo4j.is_available()
    except Exception:
        pass

    # If using Databricks, get health from there
    if databricks_ok:
        try:
            connector = get_databricks_connector()
            batches = connector.get_batches(limit=10)
            completed = len([b for b in batches if b.get("status") == "COMPLETED"])
            failed = len([b for b in batches if b.get("status") == "FAILED"])
            processing = len([b for b in batches if b.get("status") == "PROCESSING"])

            return {
                "status": "healthy" if failed == 0 else ("degraded" if failed < 3 else "unhealthy"),
                "data_source": "databricks",
                "neo4j_available": neo4j_ok,
                "recent_batches": len(batches),
                "completed_batches": completed,
                "failed_batches": failed,
                "processing_batches": processing,
            }
        except Exception as e:
            logger.warning(f"Databricks health check failed: {e}")

    # Fallback to PostgreSQL health check
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Check for recent failures
        cursor.execute("""
            SELECT
                COUNT(*) as total_recent,
                COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'PROCESSING' AND updated_at < NOW() - INTERVAL '1 hour' THEN 1 END) as stuck
            FROM observability.obs_batch_tracking
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        """)

        row = cursor.fetchone()
        total = int(row[0]) if row[0] else 0
        failed = int(row[1]) if row[1] else 0
        stuck = int(row[2]) if row[2] else 0

        health_status = "healthy"
        if stuck > 0:
            health_status = "degraded"
        if failed > total * 0.1 and total > 10:  # More than 10% failure rate
            health_status = "unhealthy"

        return {
            "status": health_status,
            "data_source": "postgresql",
            "neo4j_available": neo4j_ok,
            "recent_batches": total,
            "failed_batches": failed,
            "stuck_batches": stuck,
            "database_connected": True,
        }
    except Exception as e:
        return {
            "status": "unknown",
            "error": str(e),
            "database_connected": False,
        }
    finally:
        db.close()

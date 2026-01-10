"""
GPS CDM API - Pipeline Routes

Architecture: NiFi → Kafka (per-message-type topics) → Celery consumers

Provides endpoints for pipeline monitoring:
1. Batch tracking and status
2. Pipeline statistics
3. Layer-level metrics
4. NiFi flow status
5. Celery queue status (via Redis)
6. Message type routing and metrics

Data sources:
- Databricks: Primary data store for medallion layers
- PostgreSQL: Fallback for local development
- Neo4j: Knowledge graph (via graph routes)
- NiFi: Flow orchestration, publishes to Kafka
- Redis: Celery broker, queue inspection
- Kafka: Message streaming with per-message-type topics
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import logging
import httpx
import asyncio
import json

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


# Cache for format table mappings (refreshed periodically)
_format_table_cache = None
_format_table_cache_time = None


def get_format_table_mappings(db_cursor=None) -> Dict[str, Dict[str, str]]:
    """
    Get table mappings from mapping.message_formats table.

    Returns dict with keys:
    - 'silver_tables': set of all distinct silver table names
    - 'gold_tables': set of all distinct gold table names
    - 'format_to_silver': dict mapping format_id -> silver_table
    - 'format_to_gold': dict mapping format_id -> gold_table
    - 'silver_to_formats': dict mapping silver_table -> list of format_ids
    - 'gold_to_formats': dict mapping gold_table -> list of format_ids
    """
    global _format_table_cache, _format_table_cache_time

    # Return cached version if less than 5 minutes old
    if _format_table_cache and _format_table_cache_time:
        if datetime.now() - _format_table_cache_time < timedelta(minutes=5):
            return _format_table_cache

    close_cursor = False
    if db_cursor is None:
        conn = get_db_connection()
        db_cursor = conn.cursor()
        close_cursor = True

    try:
        db_cursor.execute("""
            SELECT format_id, silver_table, gold_table
            FROM mapping.message_formats
            WHERE is_active = true
              AND silver_table IS NOT NULL
        """)

        result = {
            'silver_tables': set(),
            'gold_tables': set(),
            'format_to_silver': {},
            'format_to_gold': {},
            'silver_to_formats': {},
            'gold_to_formats': {},
        }

        for row in db_cursor.fetchall():
            format_id, silver_table, gold_table = row

            if silver_table:
                result['silver_tables'].add(silver_table)
                result['format_to_silver'][format_id] = silver_table
                if silver_table not in result['silver_to_formats']:
                    result['silver_to_formats'][silver_table] = []
                result['silver_to_formats'][silver_table].append(format_id)

            if gold_table:
                result['gold_tables'].add(gold_table)
                result['format_to_gold'][format_id] = gold_table
                if gold_table not in result['gold_to_formats']:
                    result['gold_to_formats'][gold_table] = []
                result['gold_to_formats'][gold_table].append(format_id)

        _format_table_cache = result
        _format_table_cache_time = datetime.now()
        return result

    finally:
        if close_cursor:
            conn.close()


class PaginatedBatchResponse(BaseModel):
    """Paginated response for batch list."""
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/batches")
async def list_batches(
    status: Optional[str] = Query(None, description="Filter by status"),
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    hours_back: int = Query(24, ge=1, le=720),
    limit: int = Query(50, le=500, description="Max records (deprecated, use page_size)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(25, ge=1, le=100, description="Page size"),
):
    """List recent batches with their status and pagination support."""
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

    # Query actual bronze table for batch information
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Build conditions
        conditions = ["_ingested_at >= NOW() - INTERVAL '%s hours'"]
        params = [hours_back]

        if status:
            # Map status filter to processing_status
            status_map = {
                "COMPLETED": "PROCESSED",
                "PROCESSED": "PROCESSED",
                "FAILED": "FAILED",
                "PENDING": "PENDING",
                "PROCESSING": "PROCESSING",
            }
            conditions.append("processing_status = %s")
            params.append(status_map.get(status.upper(), status))

        if message_type:
            conditions.append("message_type = %s")
            params.append(message_type)

        where_clause = ' AND '.join(conditions)

        # First, get total count for pagination
        count_query = f"""
            SELECT COUNT(DISTINCT _batch_id)
            FROM bronze.raw_payment_messages
            WHERE {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0] or 0

        # Calculate offset for pagination
        offset = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        # Get aggregated batch data from bronze table with pagination
        cursor.execute(f"""
            SELECT
                _batch_id as batch_id,
                message_type,
                message_format,
                source_system,
                source_file_path as source_file,
                COUNT(*) as record_count,
                COUNT(CASE WHEN processing_status = 'PROCESSED' THEN 1 END) as processed_count,
                COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) as failed_count,
                COUNT(CASE WHEN processing_status IN ('PENDING', 'PROCESSING') THEN 1 END) as pending_count,
                MIN(_ingested_at) as created_at,
                MAX(processed_to_silver_at) as completed_at,
                CASE
                    WHEN COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) > 0 THEN 'FAILED'
                    WHEN COUNT(CASE WHEN processing_status IN ('PENDING', 'PROCESSING') THEN 1 END) > 0 THEN 'PROCESSING'
                    ELSE 'COMPLETED'
                END as status
            FROM bronze.raw_payment_messages
            WHERE {where_clause}
            GROUP BY _batch_id, message_type, message_format, source_system, source_file_path
            ORDER BY MIN(_ingested_at) DESC
            LIMIT %s OFFSET %s
        """, params + [page_size, offset])

        columns = [desc[0] for desc in cursor.description]
        batch_ids = []
        batch_data = []
        for row in cursor.fetchall():
            batch = dict(zip(columns, row))
            batch_ids.append(batch.get("batch_id"))
            batch_data.append(batch)

        # Get table mappings dynamically from database config
        table_mappings = get_format_table_mappings(cursor)
        silver_tables = table_mappings['silver_tables']
        gold_tables = table_mappings['gold_tables']

        # Get actual Silver counts by batch_id
        silver_counts = {}
        if batch_ids:
            placeholders = ','.join(['%s'] * len(batch_ids))
            for table in silver_tables:
                try:
                    # First try direct _batch_id match
                    cursor.execute(f"""
                        SELECT _batch_id, COUNT(*) as cnt
                        FROM silver.{table}
                        WHERE _batch_id IN ({placeholders})
                        GROUP BY _batch_id
                    """, batch_ids)
                    for row in cursor.fetchall():
                        bid, cnt = row
                        silver_counts[bid] = silver_counts.get(bid, 0) + cnt

                    # Also count via raw_id join (for records where _batch_id is null/empty)
                    cursor.execute(f"""
                        SELECT b._batch_id, COUNT(*) as cnt
                        FROM silver.{table} s
                        JOIN bronze.raw_payment_messages b ON s.raw_id = b.raw_id
                        WHERE b._batch_id IN ({placeholders})
                          AND (s._batch_id IS NULL OR s._batch_id = '')
                        GROUP BY b._batch_id
                    """, batch_ids)
                    for row in cursor.fetchall():
                        bid, cnt = row
                        silver_counts[bid] = silver_counts.get(bid, 0) + cnt
                except Exception:
                    # Rollback and get new cursor to recover from failed transaction
                    db.rollback()
                    cursor = db.cursor()
                    pass  # Table might not exist

        # Get actual Gold counts by batch_id
        gold_counts = {}
        if batch_ids:
            for table in gold_tables:
                try:
                    # Try direct _batch_id match first
                    cursor.execute(f"""
                        SELECT _batch_id, COUNT(*) as cnt
                        FROM gold.{table}
                        WHERE _batch_id IN ({placeholders})
                        GROUP BY _batch_id
                    """, batch_ids)
                    for row in cursor.fetchall():
                        bid, cnt = row
                        gold_counts[bid] = gold_counts.get(bid, 0) + cnt
                except Exception as e:
                    # Rollback and get new cursor to recover from failed transaction
                    db.rollback()
                    cursor = db.cursor()
                    pass  # Table might not have _batch_id column or might not exist

            # Also try lineage_batch_id for legacy cdm_payment_instruction table (if exists)
            try:
                cursor.execute(f"""
                    SELECT lineage_batch_id, COUNT(*) as cnt
                    FROM gold.cdm_payment_instruction
                    WHERE lineage_batch_id IN ({placeholders})
                    GROUP BY lineage_batch_id
                """, batch_ids)
                for row in cursor.fetchall():
                    bid, cnt = row
                    if bid not in gold_counts:  # Avoid double counting
                        gold_counts[bid] = gold_counts.get(bid, 0) + cnt
            except Exception:
                pass

        rows = []
        for batch in batch_data:
            batch_id = batch.get("batch_id")
            rows.append({
                "batch_id": batch_id,
                "message_type": batch.get("message_type"),
                "message_format": batch.get("message_format"),
                "source_system": batch.get("source_system"),
                "source_file": batch.get("source_file"),
                "status": batch.get("status"),
                "record_count": int(batch.get("record_count", 0)),
                "bronze_count": int(batch.get("record_count", 0)),
                "silver_count": silver_counts.get(batch_id, 0),
                "gold_count": gold_counts.get(batch_id, 0),
                "processed_count": int(batch.get("processed_count", 0)),
                "failed_count": int(batch.get("failed_count", 0)),
                "pending_count": int(batch.get("pending_count", 0)),
                "created_at": batch.get("created_at"),
                "completed_at": batch.get("completed_at"),
                "data_source": "postgresql",
            })

        # Return paginated response
        return {
            "items": rows,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    except Exception as e:
        logger.error(f"Error listing batches: {e}")
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
        }
    finally:
        db.close()


@router.get("/batches/{batch_id}")
async def get_batch(batch_id: str):
    """Get detailed batch information from actual medallion tables."""
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

    # Query from actual bronze table (same as batches list)
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT
                _batch_id as batch_id,
                message_type,
                message_format,
                source_system,
                source_file_path as source_file,
                COUNT(*) as record_count,
                COUNT(*) as bronze_count,
                COUNT(CASE WHEN processing_status = 'PROCESSED' THEN 1 END) as processed_count,
                COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) as failed_count,
                COUNT(CASE WHEN processing_status IN ('PENDING', 'PROCESSING') THEN 1 END) as pending_count,
                MIN(_ingested_at) as created_at,
                MAX(_ingested_at) as updated_at,
                CASE
                    WHEN COUNT(CASE WHEN processing_status IN ('PENDING', 'PROCESSING') THEN 1 END) = 0
                    THEN 'COMPLETED'
                    WHEN COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) > 0
                    THEN 'PARTIAL'
                    ELSE 'PROCESSING'
                END as status
            FROM bronze.raw_payment_messages
            WHERE _batch_id = %s
            GROUP BY _batch_id, message_type, message_format, source_system, source_file_path
        """, (batch_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Batch not found")

        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))

        # Get silver and gold counts
        cursor.execute("""
            SELECT COUNT(*) as silver_count
            FROM silver.stg_pain001
            WHERE _batch_id = %s
        """, (batch_id,))
        silver_row = cursor.fetchone()
        result["silver_count"] = silver_row[0] if silver_row else 0

        cursor.execute("""
            SELECT COUNT(*) as gold_count
            FROM gold.cdm_payment_instruction
            WHERE lineage_batch_id = %s
        """, (batch_id,))
        gold_row = cursor.fetchone()
        result["gold_count"] = gold_row[0] if gold_row else 0

        result["data_source"] = "postgresql"
        return result
    finally:
        db.close()


@router.get("/stats")
async def get_pipeline_stats(
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    hours_back: int = Query(24, ge=1, le=720),
):
    """Get pipeline statistics by layer - queries actual medallion layer tables."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Query actual bronze table for counts
        # Note: processing_status values are: PENDING, PROCESSING, PROCESSED, FAILED
        bronze_query = """
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN processing_status = 'PROCESSED' THEN 1 END) as processed,
                COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) as failed,
                COUNT(CASE WHEN processing_status = 'PENDING' OR processing_status = 'PROCESSING' THEN 1 END) as pending
            FROM bronze.raw_payment_messages
        """
        if batch_id:
            bronze_query += " WHERE _batch_id = %s"
            cursor.execute(bronze_query, (batch_id,))
        else:
            cursor.execute(bronze_query)

        bronze_row = cursor.fetchone()
        bronze_total = int(bronze_row[0]) if bronze_row[0] else 0
        bronze_processed = int(bronze_row[1]) if bronze_row[1] else 0
        bronze_failed = int(bronze_row[2]) if bronze_row[2] else 0
        bronze_pending = int(bronze_row[3]) if bronze_row[3] else 0

        # Query silver tables - use dynamic table mappings
        silver_total = 0
        silver_processed = 0
        table_mappings = get_format_table_mappings(cursor)
        silver_tables = list(table_mappings['silver_tables'])
        gold_tables = list(table_mappings['gold_tables'])

        for table in silver_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM silver.{table}")
                row = cursor.fetchone()
                silver_total += int(row[0]) if row and row[0] else 0
            except Exception:
                db.rollback()
                cursor = db.cursor()
                continue
        silver_processed = silver_total  # Assume all silver records are processed

        # Query gold tables dynamically
        gold_total = 0
        for gold_table in gold_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM gold.{gold_table}")
                row = cursor.fetchone()
                gold_total += int(row[0]) if row and row[0] else 0
            except Exception:
                db.rollback()
                cursor = db.cursor()
                continue

        # Analytical is based on gold (simplified)
        analytical_total = gold_total

        # Get batch counts
        batch_query = """
            SELECT COUNT(DISTINCT _batch_id) as batch_count
            FROM bronze.raw_payment_messages
        """
        cursor.execute(batch_query)
        batch_row = cursor.fetchone()
        bronze_batch_count = int(batch_row[0]) if batch_row and batch_row[0] else 0

        return {
            "bronze": {
                "total": bronze_total,
                "processed": bronze_processed,
                "failed": bronze_failed,
                "pending": bronze_pending,
                "batchCount": bronze_batch_count,
            },
            "silver": {
                "total": silver_total,
                "processed": silver_processed,
                "failed": 0,
                "pending": 0,
                "dqPassed": silver_processed,  # Simplified
                "dqFailed": 0,
                "batchCount": bronze_batch_count,  # Same as bronze for now
            },
            "gold": {
                "total": gold_total,
                "processed": gold_total,
                "failed": 0,
                "pending": 0,
                "batchCount": bronze_batch_count,
            },
            "analytical": {
                "total": analytical_total,
                "processed": analytical_total,
                "failed": 0,
                "pending": 0,
                "batchCount": bronze_batch_count,
            },
        }
    except Exception as e:
        logger.error(f"Error getting pipeline stats: {e}")
        # Return default stats if error
        return {
            "bronze": {"total": 0, "processed": 0, "failed": 0, "pending": 0},
            "silver": {"total": 0, "processed": 0, "failed": 0, "pending": 0, "dqPassed": 0, "dqFailed": 0},
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


@router.get("/records/{layer}/{record_id}")
async def get_record_details(layer: str, record_id: str):
    """Get full details for a specific record including raw content."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        if layer == "bronze":
            cursor.execute("""
                SELECT raw_id, _batch_id as batch_id, message_type, message_format,
                       source_system, source_file_path, processing_status,
                       raw_content, raw_content_hash as checksum,
                       content_size_bytes as file_size_bytes,
                       _ingested_at as ingested_at, processed_to_silver_at,
                       source_batch_id, source_sequence_number
                FROM bronze.raw_payment_messages
                WHERE raw_id = %s
            """, (record_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                record = dict(zip(columns, row))
                record['source_table'] = 'raw_payment_messages'
                return record
            raise HTTPException(status_code=404, detail="Record not found")
        elif layer == "silver":
            # Get dynamic silver table mappings and search all Silver tables
            table_mappings = get_format_table_mappings(cursor)
            silver_tables = list(table_mappings['silver_tables'])

            record = None
            for table in silver_tables:
                try:
                    cursor.execute(f"""
                        SELECT * FROM silver.{table}
                        WHERE stg_id = %s
                    """, (record_id,))
                    row = cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                        record = dict(zip(columns, row))
                        record['source_table'] = table
                        break
                except Exception as e:
                    # Rollback and get new cursor to recover from failed transaction
                    db.rollback()
                    cursor = db.cursor()
                    continue
            if record:
                return record
            raise HTTPException(status_code=404, detail="Record not found")
        elif layer == "gold":
            # Get dynamic gold table mappings and search all Gold tables
            table_mappings = get_format_table_mappings(cursor)
            gold_tables = list(table_mappings['gold_tables'])

            for gold_table in gold_tables:
                try:
                    # Try to find by primary key (varies by table)
                    pk_column = 'transfer_id' if 'pacs' in gold_table or 'pain' in gold_table or 'camt' in gold_table else 'instruction_id'
                    cursor.execute(f"""
                        SELECT * FROM gold.{gold_table}
                        WHERE {pk_column} = %s
                    """, (record_id,))
                    row = cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                        record = dict(zip(columns, row))
                        record["source_table"] = gold_table
                        return record
                except Exception as e:
                    # Rollback and get new cursor to recover from failed transaction
                    db.rollback()
                    cursor = db.cursor()
                    continue
            raise HTTPException(status_code=404, detail="Record not found")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid layer: {layer}")
    finally:
        db.close()


@router.get("/records/{layer}/{record_id}/lineage")
async def get_record_lineage(layer: str, record_id: str):
    """Get cross-zone lineage for a record showing how it flows through all zones.

    Uses actual foreign key relationships:
    - Bronze -> Silver: silver.raw_id references bronze.raw_id
    - Silver -> Gold: gold.source_stg_id references silver.stg_id
    """
    db = get_db_connection()
    try:
        cursor = db.cursor()
        result = {
            "bronze": None,
            "silver": None,
            "gold": None,
            "field_mappings": [],
        }

        # Get table mappings dynamically from database config
        table_mappings = get_format_table_mappings(cursor)
        silver_tables = list(table_mappings['silver_tables'])
        gold_tables = list(table_mappings['gold_tables'])

        if layer == "bronze":
            # Start from bronze, find linked silver and gold using foreign keys
            cursor.execute("""
                SELECT raw_id, _batch_id, message_type, message_format, source_system,
                       raw_content, processing_status, _ingested_at, extractor_output
                FROM bronze.raw_payment_messages
                WHERE raw_id = %s
            """, (record_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                result["bronze"] = dict(zip(columns, row))
                raw_id = result["bronze"]["raw_id"]

                # Dynamically compute message_format if stored as UNKNOWN
                if result["bronze"].get("message_format") == "UNKNOWN":
                    from gps_cdm.orchestration.zone_tasks import get_message_format
                    msg_type = result["bronze"].get("message_type", "")
                    result["bronze"]["message_format"] = get_message_format(msg_type)

                # Find silver record linked by raw_id (proper FK relationship)
                for table in silver_tables:
                    try:
                        cursor.execute(f"""
                            SELECT * FROM silver.{table}
                            WHERE raw_id = %s
                        """, (raw_id,))
                        srow = cursor.fetchone()
                        if srow:
                            scols = [desc[0] for desc in cursor.description]
                            result["silver"] = dict(zip(scols, srow))
                            result["silver"]["source_table"] = table
                            stg_id = result["silver"].get("stg_id")

                            # Find gold record linked by source_stg_id across all Gold tables
                            if stg_id:
                                for gold_table in gold_tables:
                                    try:
                                        cursor.execute(f"""
                                            SELECT * FROM gold.{gold_table}
                                            WHERE source_stg_id = %s
                                        """, (stg_id,))
                                        grow = cursor.fetchone()
                                        if grow:
                                            gcols = [desc[0] for desc in cursor.description]
                                            result["gold"] = dict(zip(gcols, grow))
                                            result["gold"]["source_table"] = gold_table
                                            break
                                    except Exception:
                                        db.rollback()
                                        cursor = db.cursor()
                                        continue
                            break
                    except Exception:
                        db.rollback()
                        cursor = db.cursor()
                        continue

        elif layer == "silver":
            # Start from silver, find linked bronze and gold using foreign keys
            for table in silver_tables:
                try:
                    cursor.execute(f"""
                        SELECT * FROM silver.{table}
                        WHERE stg_id = %s
                    """, (record_id,))
                    row = cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                        result["silver"] = dict(zip(columns, row))
                        result["silver"]["source_table"] = table
                        raw_id = result["silver"].get("raw_id")
                        stg_id = result["silver"].get("stg_id")

                        # Find bronze using raw_id FK
                        if raw_id:
                            cursor.execute("""
                                SELECT raw_id, _batch_id, message_type, message_format,
                                       source_system, raw_content,
                                       processing_status, _ingested_at, extractor_output
                                FROM bronze.raw_payment_messages
                                WHERE raw_id = %s
                            """, (raw_id,))
                            brow = cursor.fetchone()
                            if brow:
                                bcols = [desc[0] for desc in cursor.description]
                                result["bronze"] = dict(zip(bcols, brow))
                                # Dynamically compute message_format if stored as UNKNOWN
                                if result["bronze"].get("message_format") == "UNKNOWN":
                                    from gps_cdm.orchestration.zone_tasks import get_message_format
                                    msg_type = result["bronze"].get("message_type", "")
                                    result["bronze"]["message_format"] = get_message_format(msg_type)

                        # Find gold using source_stg_id FK across all Gold tables
                        if stg_id:
                            for gold_table in gold_tables:
                                try:
                                    cursor.execute(f"""
                                        SELECT * FROM gold.{gold_table}
                                        WHERE source_stg_id = %s
                                    """, (stg_id,))
                                    grow = cursor.fetchone()
                                    if grow:
                                        gcols = [desc[0] for desc in cursor.description]
                                        result["gold"] = dict(zip(gcols, grow))
                                        result["gold"]["source_table"] = gold_table
                                        break
                                except Exception:
                                    db.rollback()
                                    cursor = db.cursor()
                                    continue
                        break
                except Exception:
                    db.rollback()
                    cursor = db.cursor()
                    continue

        elif layer == "gold":
            # Start from gold, find linked bronze and silver using foreign keys
            # Search all Gold tables for the record
            for gold_table in gold_tables:
                try:
                    # Try to find by primary key (varies by table)
                    pk_column = 'transfer_id' if 'pacs' in gold_table or 'pain' in gold_table or 'camt' in gold_table else 'instruction_id'
                    cursor.execute(f"""
                        SELECT * FROM gold.{gold_table}
                        WHERE {pk_column} = %s
                    """, (record_id,))
                    row = cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                        result["gold"] = dict(zip(columns, row))
                        result["gold"]["source_table"] = gold_table
                        break
                except Exception:
                    db.rollback()
                    cursor = db.cursor()
                    continue

            if result["gold"]:
                stg_id = result["gold"].get("source_stg_id")
                stg_table = result["gold"].get("source_stg_table")

                # Find silver using source_stg_id FK
                if stg_id:
                    # First try the specific table if we know it
                    if stg_table and stg_table in silver_tables:
                        try:
                            cursor.execute(f"""
                                SELECT * FROM silver.{stg_table}
                                WHERE stg_id = %s
                            """, (stg_id,))
                            srow = cursor.fetchone()
                            if srow:
                                scols = [desc[0] for desc in cursor.description]
                                result["silver"] = dict(zip(scols, srow))
                                result["silver"]["source_table"] = stg_table
                        except Exception:
                            db.rollback()
                            cursor = db.cursor()

                    # Fallback: search all silver tables
                    if not result["silver"]:
                        for table in silver_tables:
                            try:
                                cursor.execute(f"""
                                    SELECT * FROM silver.{table}
                                    WHERE stg_id = %s
                                """, (stg_id,))
                                srow = cursor.fetchone()
                                if srow:
                                    scols = [desc[0] for desc in cursor.description]
                                    result["silver"] = dict(zip(scols, srow))
                                    result["silver"]["source_table"] = table
                                    break
                            except Exception:
                                db.rollback()
                                cursor = db.cursor()
                                continue

                    # Find bronze using silver's raw_id FK
                    if result["silver"]:
                        raw_id = result["silver"].get("raw_id")
                        if raw_id:
                            cursor.execute("""
                                SELECT raw_id, _batch_id, message_type, message_format,
                                       source_system, raw_content,
                                       processing_status, _ingested_at, extractor_output
                                FROM bronze.raw_payment_messages
                                WHERE raw_id = %s
                            """, (raw_id,))
                            brow = cursor.fetchone()
                            if brow:
                                bcols = [desc[0] for desc in cursor.description]
                                result["bronze"] = dict(zip(bcols, brow))
                                # Dynamically compute message_format if stored as UNKNOWN
                                if result["bronze"].get("message_format") == "UNKNOWN":
                                    from gps_cdm.orchestration.zone_tasks import get_message_format
                                    msg_type = result["bronze"].get("message_type", "")
                                    result["bronze"]["message_format"] = get_message_format(msg_type)

        # Fetch related CDM entities for Gold layer (Party, Account, Financial Institution)
        if result.get("gold"):
            gold = result["gold"]

            # Initialize gold_entities to hold denormalized party/account/agent data
            result["gold_entities"] = {}

            # Fetch Debtor Party (check multiple FK column names for different Gold tables)
            debtor_party_id = gold.get("debtor_id") or gold.get("original_debtor_party_id")
            if debtor_party_id:
                try:
                    cursor.execute("""
                        SELECT party_id, party_type, name, street_name, building_number,
                               post_code, town_name, country_sub_division, country,
                               identification_type, identification_number, tax_id, tax_id_type
                        FROM gold.cdm_party WHERE party_id = %s
                    """, (debtor_party_id,))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["debtor_party"] = dict(zip(cols, row))
                except Exception:
                    pass

            # Fetch Debtor Account (cdm_account table - check multiple FK column names)
            debtor_account_id = gold.get("debtor_account_id") or gold.get("original_debtor_account_id")
            if debtor_account_id:
                try:
                    cursor.execute("""
                        SELECT account_id, account_type, iban, account_number, currency
                        FROM gold.cdm_account WHERE account_id = %s
                    """, (debtor_account_id,))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["debtor_account"] = dict(zip(cols, row))
                except Exception:
                    pass

            # Fetch Debtor Agent (cdm_financial_institution table - check multiple FK column names)
            debtor_agent_id = gold.get("debtor_agent_id") or gold.get("original_debtor_agent_fi_id")
            if debtor_agent_id:
                try:
                    cursor.execute("""
                        SELECT fi_id, fi_type, institution_name as name, bic,
                               national_clearing_system as clearing_system_id,
                               national_clearing_code as member_id, country, lei
                        FROM gold.cdm_financial_institution WHERE fi_id = %s
                    """, (debtor_agent_id,))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["debtor_agent"] = dict(zip(cols, row))
                except Exception:
                    pass

            # Fetch Creditor Party (check multiple FK column names for different Gold tables)
            creditor_party_id = gold.get("creditor_id") or gold.get("original_creditor_party_id")
            if creditor_party_id:
                try:
                    cursor.execute("""
                        SELECT party_id, party_type, name, street_name, building_number,
                               post_code, town_name, country_sub_division, country,
                               identification_type, identification_number, tax_id, tax_id_type
                        FROM gold.cdm_party WHERE party_id = %s
                    """, (creditor_party_id,))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["creditor_party"] = dict(zip(cols, row))
                except Exception:
                    pass

            # Fetch Creditor Account (cdm_account table - check multiple FK column names)
            creditor_account_id = gold.get("creditor_account_id") or gold.get("original_creditor_account_id")
            if creditor_account_id:
                try:
                    cursor.execute("""
                        SELECT account_id, account_type, iban, account_number, currency
                        FROM gold.cdm_account WHERE account_id = %s
                    """, (creditor_account_id,))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["creditor_account"] = dict(zip(cols, row))
                except Exception:
                    pass

            # Fetch Creditor Agent (cdm_financial_institution table - check multiple FK column names)
            creditor_agent_id = gold.get("creditor_agent_id") or gold.get("original_creditor_agent_fi_id")
            if creditor_agent_id:
                try:
                    cursor.execute("""
                        SELECT fi_id, fi_type, institution_name as name, bic,
                               national_clearing_system as clearing_system_id,
                               national_clearing_code as member_id, country, lei
                        FROM gold.cdm_financial_institution WHERE fi_id = %s
                    """, (creditor_agent_id,))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["creditor_agent"] = dict(zip(cols, row))
                except Exception:
                    pass

            # Fetch Intermediary Agents if present
            for i, agent_field in enumerate(["intermediary_agent1_id", "intermediary_agent2_id"], 1):
                if gold.get(agent_field):
                    try:
                        cursor.execute("""
                            SELECT fi_id, fi_type, institution_name as name, bic,
                                   national_clearing_system as clearing_system_id, country
                            FROM gold.cdm_financial_institution WHERE fi_id = %s
                        """, (gold[agent_field],))
                        row = cursor.fetchone()
                        if row:
                            cols = [desc[0] for desc in cursor.description]
                            result["gold_entities"][f"intermediary_agent{i}"] = dict(zip(cols, row))
                    except Exception:
                        pass

            # Fetch Instructing/Instructed Agents if present (pacs.002 and similar)
            if gold.get("instructing_agent_fi_id"):
                try:
                    cursor.execute("""
                        SELECT fi_id, fi_type, institution_name as name, bic,
                               national_clearing_system as clearing_system_id, country
                        FROM gold.cdm_financial_institution WHERE fi_id = %s
                    """, (gold["instructing_agent_fi_id"],))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["instructing_agent"] = dict(zip(cols, row))
                except Exception:
                    pass

            if gold.get("instructed_agent_fi_id"):
                try:
                    cursor.execute("""
                        SELECT fi_id, fi_type, institution_name as name, bic,
                               national_clearing_system as clearing_system_id, country
                        FROM gold.cdm_financial_institution WHERE fi_id = %s
                    """, (gold["instructed_agent_fi_id"],))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["instructed_agent"] = dict(zip(cols, row))
                except Exception:
                    pass

            # Fetch Ultimate Parties if present
            if gold.get("ultimate_debtor_id"):
                try:
                    cursor.execute("""
                        SELECT party_id, party_type, name, country,
                               identification_type, identification_number
                        FROM gold.cdm_party WHERE party_id = %s
                    """, (gold["ultimate_debtor_id"],))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["ultimate_debtor"] = dict(zip(cols, row))
                except Exception:
                    pass

            if gold.get("ultimate_creditor_id"):
                try:
                    cursor.execute("""
                        SELECT party_id, party_type, name, country,
                               identification_type, identification_number
                        FROM gold.cdm_party WHERE party_id = %s
                    """, (gold["ultimate_creditor_id"],))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        result["gold_entities"]["ultimate_creditor"] = dict(zip(cols, row))
                except Exception:
                    pass

        # Get field mappings from Neo4j if available
        try:
            from gps_cdm.orchestration.neo4j_service import get_neo4j_service
            neo4j = get_neo4j_service()
            if neo4j.is_available() and result.get("bronze"):
                msg_type = result["bronze"].get("message_type", "")
                schema = neo4j.get_schema_lineage(msg_type)
                if schema and "transforms" in schema:
                    result["field_mappings"] = schema["transforms"]
        except Exception:
            pass

        # Use extractor_output from Bronze for parsed field values
        # This was computed during Bronze ingestion and stored as JSONB
        if result.get("bronze"):
            extractor_output = result["bronze"].get("extractor_output")
            if extractor_output:
                # extractor_output is already a dict (JSONB) or needs parsing
                if isinstance(extractor_output, str):
                    try:
                        result["bronze_extracted"] = json.loads(extractor_output)
                    except json.JSONDecodeError:
                        result["bronze_extracted"] = {}
                else:
                    result["bronze_extracted"] = extractor_output
            else:
                result["bronze_extracted"] = {}

        # Fetch Gold extension data if available
        if result.get("gold"):
            gold = result["gold"]
            instruction_id = gold.get("instruction_id")
            msg_type = gold.get("source_message_type", "")

            # Map message type to extension table
            extension_tables = {
                "pain.001": "cdm_payment_extension_iso20022",
                "pain.002": "cdm_payment_extension_iso20022",
                "pain.008": "cdm_payment_extension_iso20022",
                "pacs.002": "cdm_payment_extension_iso20022",
                "pacs.003": "cdm_payment_extension_iso20022",
                "pacs.004": "cdm_payment_extension_iso20022",
                "pacs.008": "cdm_payment_extension_iso20022",
                "pacs.009": "cdm_payment_extension_iso20022",
                "camt.052": "cdm_payment_extension_iso20022",
                "camt.053": "cdm_payment_extension_iso20022",
                "camt.054": "cdm_payment_extension_iso20022",
                # NOTE: All SWIFT MT messages decommissioned Nov 2025 - use ISO 20022 equivalents
                "FEDWIRE": "cdm_payment_extension_fedwire",
                "ACH": "cdm_payment_extension_ach",
                "SEPA": "cdm_payment_extension_sepa",
                "SEPA_SCT": "cdm_payment_extension_sepa",
                "SEPA_SDD": "cdm_payment_extension_sepa",
                "SEPA_INST": "cdm_payment_extension_sepa",
                "RTP": "cdm_payment_extension_rtp",
                "FEDNOW": "cdm_payment_extension_iso20022",
                "CHAPS": "cdm_payment_extension_swift",
                "BACS": "cdm_payment_extension_swift",
                "FPS": "cdm_payment_extension_iso20022",
                "CHIPS": "cdm_payment_extension_swift",
                "NPP": "cdm_payment_extension_iso20022",
            }

            ext_table = extension_tables.get(msg_type)
            if ext_table and instruction_id:
                try:
                    cursor.execute(f"""
                        SELECT * FROM gold.{ext_table}
                        WHERE instruction_id = %s
                    """, (instruction_id,))
                    ext_row = cursor.fetchone()
                    if ext_row:
                        ext_cols = [desc[0] for desc in cursor.description]
                        result["gold_extension"] = dict(zip(ext_cols, ext_row))
                        result["gold_extension"]["_table"] = ext_table
                except Exception:
                    pass

        return result
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


# =============================================================================
# NiFi Integration Endpoints
# =============================================================================

NIFI_BASE_URL = os.environ.get("NIFI_URL", "http://localhost:8080/nifi-api")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


@router.get("/nifi/status")
async def get_nifi_status():
    """Get NiFi flow status and processor metrics."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get root process group status
            flow_resp = await client.get(f"{NIFI_BASE_URL}/flow/process-groups/root/status")

            if flow_resp.status_code != 200:
                return {
                    "status": "unavailable",
                    "error": f"NiFi returned status {flow_resp.status_code}",
                }

            flow_data = flow_resp.json()
            pg_status = flow_data.get("processGroupStatus", {})
            agg_snapshot = pg_status.get("aggregateSnapshot", {})

            # Get processor summaries
            processors_resp = await client.get(f"{NIFI_BASE_URL}/flow/processors/root")
            processors_data = []
            if processors_resp.status_code == 200:
                processors_json = processors_resp.json()
                for proc in processors_json.get("processors", []):
                    status = proc.get("status", {})
                    agg = status.get("aggregateSnapshot", {})
                    processors_data.append({
                        "id": proc.get("id"),
                        "name": proc.get("component", {}).get("name"),
                        "type": proc.get("component", {}).get("type", "").split(".")[-1],
                        "state": proc.get("component", {}).get("state"),
                        "input_count": agg.get("input", "0").split(" ")[0] if agg.get("input") else 0,
                        "output_count": agg.get("output", "0").split(" ")[0] if agg.get("output") else 0,
                        "tasks_millis": agg.get("tasksDurationNanos", 0) / 1_000_000,
                    })

            return {
                "status": "running",
                "flow_status": {
                    "name": pg_status.get("name", "GPS CDM Pipeline"),
                    "queued_count": agg_snapshot.get("queuedCount", 0),
                    "queued_bytes": agg_snapshot.get("queuedSize", "0 bytes"),
                    "bytes_in": agg_snapshot.get("bytesIn", 0),
                    "bytes_out": agg_snapshot.get("bytesOut", 0),
                    "flow_files_in": agg_snapshot.get("flowFilesIn", 0),
                    "flow_files_out": agg_snapshot.get("flowFilesOut", 0),
                    "active_threads": agg_snapshot.get("activeThreadCount", 0),
                    "running_count": agg_snapshot.get("runningCount", 0),
                    "stopped_count": agg_snapshot.get("stoppedCount", 0),
                    "invalid_count": agg_snapshot.get("invalidCount", 0),
                    "disabled_count": agg_snapshot.get("disabledCount", 0),
                },
                "processors": processors_data,
            }
    except httpx.TimeoutException:
        return {"status": "timeout", "error": "NiFi connection timed out"}
    except httpx.ConnectError:
        return {"status": "unavailable", "error": "Cannot connect to NiFi"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/nifi/connections")
async def get_nifi_connections():
    """Get NiFi connection queue status."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{NIFI_BASE_URL}/flow/process-groups/root/status")
            if resp.status_code != 200:
                return {"status": "unavailable", "connections": []}

            data = resp.json()
            connections = []

            # Recursively get connection info
            async def get_pg_connections(pg_id: str):
                conn_resp = await client.get(f"{NIFI_BASE_URL}/process-groups/{pg_id}/connections")
                if conn_resp.status_code == 200:
                    for conn in conn_resp.json().get("connections", []):
                        status = conn.get("status", {}).get("aggregateSnapshot", {})
                        connections.append({
                            "id": conn.get("id"),
                            "source_name": conn.get("component", {}).get("source", {}).get("name", "Unknown"),
                            "destination_name": conn.get("component", {}).get("destination", {}).get("name", "Unknown"),
                            "queued_count": status.get("queuedCount", 0),
                            "queued_bytes": status.get("queuedSize", "0 bytes"),
                            "flow_files_in": status.get("flowFilesIn", 0),
                            "flow_files_out": status.get("flowFilesOut", 0),
                            "percent_used": status.get("percentUseCount", "0%"),
                        })

            # Get root process group connections
            await get_pg_connections("root")

            return {"status": "running", "connections": connections}
    except Exception as e:
        return {"status": "error", "error": str(e), "connections": []}


# =============================================================================
# Celery Queue Status Endpoints (Direct Redis inspection)
# =============================================================================

@router.get("/celery/queues")
async def get_celery_queues():
    """Get Celery queue depths from Redis directly."""
    try:
        import redis
        r = redis.from_url(REDIS_URL)

        # Standard Celery queues
        queue_names = ["celery", "bronze", "silver", "gold", "dq", "cdc"]
        queues = {}

        for queue in queue_names:
            length = r.llen(queue)
            queues[queue] = length

        return {
            "status": "running",
            "queues": queues,
            "total_pending": sum(queues.values()),
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "queues": {}}


# =============================================================================
# Message Type Metrics Endpoints
# =============================================================================

@router.get("/message-types/stats")
async def get_message_type_stats(
    hours_back: int = Query(24, ge=1, le=720),
):
    """Get processing statistics by message type - queries actual bronze table."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Query actual bronze table for message type stats
        # Note: processing_status values are: PENDING, PROCESSING, PROCESSED, FAILED
        cursor.execute("""
            SELECT
                message_type,
                message_format,
                COUNT(DISTINCT _batch_id) as batch_count,
                COUNT(*) as total_records,
                COUNT(CASE WHEN processing_status = 'PROCESSED' THEN 1 END) as processed,
                COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) as failed,
                COUNT(CASE WHEN processing_status IN ('PENDING', 'PROCESSING') THEN 1 END) as in_progress
            FROM bronze.raw_payment_messages
            WHERE _ingested_at >= NOW() - INTERVAL '%s hours'
            GROUP BY message_type, message_format
            ORDER BY total_records DESC
        """, (hours_back,))

        columns = [desc[0] for desc in cursor.description]
        bronze_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Build result with actual counts
        results = []
        for stats in bronze_results:
            total_records = int(stats.get("total_records", 0))
            processed = int(stats.get("processed", 0))
            failed = int(stats.get("failed", 0))
            in_progress = int(stats.get("in_progress", 0))

            results.append({
                "message_type": stats.get("message_type"),
                "message_format": stats.get("message_format"),
                "batch_count": int(stats.get("batch_count", 0)),
                "total_records": total_records,
                "total_bronze": total_records,
                "total_silver": processed,  # Assume processed bronze = silver
                "total_gold": processed,    # Assume processed = gold
                "dq_passed": processed,
                "dq_failed": 0,
                "errors": failed,
                "processed": processed,
                "failed": failed,
                "in_progress": in_progress,
                "success_rate": round((processed / total_records * 100), 1) if total_records > 0 else 0,
            })

        return {
            "message_types": results,
            "hours_back": hours_back,
        }
    except Exception as e:
        logger.error(f"Error getting message type stats: {e}")
        return {"message_types": [], "hours_back": hours_back}
    finally:
        db.close()


@router.get("/message-types/{message_type}/flow")
async def get_message_type_flow(
    message_type: str,
    hours_back: int = Query(24, ge=1, le=720),
):
    """Get detailed flow metrics for a specific message type."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Get layer progression
        cursor.execute("""
            SELECT
                batch_id,
                status,
                bronze_count,
                silver_count,
                gold_count,
                dq_passed_count,
                dq_failed_count,
                error_count,
                created_at,
                completed_at,
                EXTRACT(EPOCH FROM (completed_at - created_at)) as duration_seconds
            FROM observability.obs_batch_tracking
            WHERE message_type = %s
              AND created_at >= NOW() - INTERVAL '%s hours'
            ORDER BY created_at DESC
            LIMIT 50
        """, (message_type, hours_back))

        columns = [desc[0] for desc in cursor.description]
        batches = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Aggregate stats
        total_bronze = sum(b.get("bronze_count", 0) or 0 for b in batches)
        total_silver = sum(b.get("silver_count", 0) or 0 for b in batches)
        total_gold = sum(b.get("gold_count", 0) or 0 for b in batches)
        total_dq_passed = sum(b.get("dq_passed_count", 0) or 0 for b in batches)
        total_dq_failed = sum(b.get("dq_failed_count", 0) or 0 for b in batches)
        total_errors = sum(b.get("error_count", 0) or 0 for b in batches)

        return {
            "message_type": message_type,
            "summary": {
                "batch_count": len(batches),
                "bronze": {
                    "total": total_bronze,
                    "processed": total_bronze - total_errors,
                    "failed": total_errors,
                },
                "silver": {
                    "total": total_silver,
                    "dq_passed": total_dq_passed,
                    "dq_failed": total_dq_failed,
                },
                "gold": {
                    "total": total_gold,
                },
                "success_rate": round((total_gold / total_bronze * 100), 2) if total_bronze > 0 else 0,
                "dq_pass_rate": round((total_dq_passed / total_silver * 100), 2) if total_silver > 0 else 0,
            },
            "recent_batches": batches[:10],
        }
    except Exception as e:
        logger.error(f"Error getting message type flow: {e}")
        return {
            "message_type": message_type,
            "summary": {
                "batch_count": 0,
                "bronze": {"total": 0, "processed": 0, "failed": 0},
                "silver": {"total": 0, "dq_passed": 0, "dq_failed": 0},
                "gold": {"total": 0},
                "success_rate": 0,
                "dq_pass_rate": 0,
            },
            "recent_batches": [],
        }
    finally:
        db.close()


@router.get("/throughput")
async def get_pipeline_throughput(
    hours_back: int = Query(24, ge=1, le=168),
    interval_minutes: int = Query(60, ge=5, le=1440),
):
    """Get pipeline throughput over time - queries actual bronze table."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Query actual bronze table for throughput metrics
        cursor.execute("""
            SELECT
                date_trunc('hour', _ingested_at) as time_bucket,
                COUNT(DISTINCT _batch_id) as batch_count,
                COUNT(*) as records_ingested,
                COUNT(CASE WHEN processing_status = 'PROCESSED' THEN 1 END) as records_promoted,
                COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) as errors,
                COALESCE(AVG(EXTRACT(EPOCH FROM (processed_to_silver_at - _ingested_at))), 0) as avg_latency_seconds
            FROM bronze.raw_payment_messages
            WHERE _ingested_at >= NOW() - INTERVAL '%s hours'
            GROUP BY date_trunc('hour', _ingested_at)
            ORDER BY time_bucket ASC
        """, (hours_back,))

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Convert timestamps and decimals
        for r in results:
            if r.get("time_bucket"):
                r["time_bucket"] = r["time_bucket"].isoformat()
            for k, v in r.items():
                if hasattr(v, 'as_integer_ratio'):
                    r[k] = float(v) if v else 0
                elif isinstance(v, int):
                    r[k] = int(v)

        return {
            "throughput": results,
            "hours_back": hours_back,
            "interval_minutes": interval_minutes,
        }
    except Exception as e:
        logger.error(f"Error getting throughput: {e}")
        return {"throughput": [], "hours_back": hours_back, "interval_minutes": interval_minutes}
    finally:
        db.close()


# =============================================================================
# Full Pipeline Overview Endpoint
# =============================================================================

@router.get("/overview")
async def get_pipeline_overview():
    """Get comprehensive pipeline overview including all components."""
    # Run all status checks concurrently
    nifi_task = get_nifi_status()
    celery_task = get_celery_workers()
    celery_queues_task = get_celery_queues()

    nifi_status, celery_status, queues_status = await asyncio.gather(
        nifi_task, celery_task, celery_queues_task
    )

    # Get database stats from actual medallion tables
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Get bronze stats (actual records)
        # Note: processing_status values are: PENDING, PROCESSING, PROCESSED, FAILED
        cursor.execute("""
            SELECT
                COUNT(DISTINCT _batch_id) as total_batches,
                COUNT(*) as total_records,
                COUNT(CASE WHEN processing_status = 'PROCESSED' THEN 1 END) as processed,
                COUNT(CASE WHEN processing_status = 'FAILED' THEN 1 END) as failed,
                COUNT(CASE WHEN processing_status IN ('PENDING', 'PROCESSING') THEN 1 END) as in_progress
            FROM bronze.raw_payment_messages
            WHERE _ingested_at >= NOW() - INTERVAL '24 hours'
        """)
        row = cursor.fetchone()

        total_batches = int(row[0]) if row[0] else 0
        total_records = int(row[1]) if row[1] else 0
        processed = int(row[2]) if row[2] else 0
        failed = int(row[3]) if row[3] else 0
        in_progress = int(row[4]) if row[4] else 0

        # Get gold count
        cursor.execute("SELECT COUNT(*) FROM gold.cdm_payment_instruction")
        gold_row = cursor.fetchone()
        records_to_gold = int(gold_row[0]) if gold_row[0] else 0

        # Get silver count (sum all silver tables)
        silver_count = 0
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT 1 FROM silver.stg_pain001 UNION ALL
                    SELECT 1 FROM silver.stg_pacs008 UNION ALL
                    SELECT 1 FROM silver.stg_mt103 UNION ALL
                    SELECT 1 FROM silver.stg_mt202 UNION ALL
                    SELECT 1 FROM silver.stg_fedwire UNION ALL
                    SELECT 1 FROM silver.stg_sepa UNION ALL
                    SELECT 1 FROM silver.stg_ach UNION ALL
                    SELECT 1 FROM silver.stg_chaps UNION ALL
                    SELECT 1 FROM silver.stg_bacs UNION ALL
                    SELECT 1 FROM silver.stg_fednow UNION ALL
                    SELECT 1 FROM silver.stg_rtp UNION ALL
                    SELECT 1 FROM silver.stg_faster_payments
                ) as combined
            """)
            silver_row = cursor.fetchone()
            silver_count = int(silver_row[0]) if silver_row[0] else 0
        except Exception:
            pass

        batch_stats = {
            "total_batches_24h": total_batches,
            "total_records": total_records,
            "bronze_records": total_records,
            "silver_records": silver_count,
            "gold_records": records_to_gold,
            "processed": processed,
            "failed": failed,
            "in_progress": in_progress,
            "records_to_gold": records_to_gold,
            "success_rate": round((processed / total_records * 100), 1) if total_records > 0 else 0,
        }

        # Message type distribution from actual bronze table
        cursor.execute("""
            SELECT message_type, COUNT(*) as count
            FROM bronze.raw_payment_messages
            WHERE _ingested_at >= NOW() - INTERVAL '24 hours'
            GROUP BY message_type
            ORDER BY count DESC
            LIMIT 10
        """)
        message_types = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]

    except Exception as e:
        logger.error(f"Error getting overview stats: {e}")
        batch_stats = {
            "total_batches_24h": 0, "total_records": 0, "bronze_records": 0,
            "silver_records": 0, "gold_records": 0, "processed": 0,
            "failed": 0, "in_progress": 0, "records_to_gold": 0, "success_rate": 0
        }
        message_types = []
    finally:
        db.close()

    # Calculate overall health
    nifi_healthy = nifi_status.get("status") == "running"
    celery_healthy = celery_status.get("status") == "running" and celery_status.get("worker_count", 0) > 0
    pipeline_healthy = batch_stats.get("failed", 0) < batch_stats.get("total_records", 0) * 0.1 if batch_stats.get("total_records", 0) > 0 else True

    overall_health = "healthy"
    if not nifi_healthy or not celery_healthy:
        overall_health = "degraded"
    if not nifi_healthy and not celery_healthy:
        overall_health = "critical"
    if not pipeline_healthy:
        overall_health = "unhealthy"

    return {
        "overall_health": overall_health,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "nifi": {
                "status": nifi_status.get("status"),
                "flow_files_in": nifi_status.get("flow_status", {}).get("flow_files_in", 0),
                "queued_count": nifi_status.get("flow_status", {}).get("queued_count", 0),
                "running_processors": nifi_status.get("flow_status", {}).get("running_count", 0),
            },
            "celery": {
                "status": celery_status.get("status"),
                "worker_count": celery_status.get("worker_count", 0),
                "active_tasks": sum(w.get("active_tasks", 0) for w in celery_status.get("workers", [])),
                "queue_depth": queues_status.get("total_pending", 0),
            },
            "database": {
                "status": "connected",
                "total_records": batch_stats.get("total_records", 0),
                "bronze_records": batch_stats.get("bronze_records", 0),
                "silver_records": batch_stats.get("silver_records", 0),
                "gold_records": batch_stats.get("gold_records", 0),
                "success_rate": batch_stats.get("success_rate", 0),
            },
        },
        "batch_stats": batch_stats,
        "message_types": message_types,
        "queues": queues_status.get("queues", {}),
    }


@router.get("/mappings/{message_type}")
async def get_field_mappings(message_type: str):
    """Get Bronze→Silver→Gold field mappings for a message type from the mapping database.

    Returns mappings from:
    - mapping.silver_field_mappings: Bronze source_path → Silver target_column
    - mapping.gold_field_mappings: Silver source_expression → Gold gold_table.gold_column with entity_role

    This enables dynamic field comparison in the UI without hardcoded mappings.
    """
    result = {
        "message_type": message_type,
        "bronze_to_silver": [],
        "silver_to_gold": [],
    }

    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=503, detail="Database not available")

        cursor = conn.cursor()

        # Get Bronze → Silver mappings
        cursor.execute("""
            SELECT target_column, source_path, data_type, is_required, default_value
            FROM mapping.silver_field_mappings
            WHERE format_id = %s AND is_active = true
            ORDER BY ordinal_position
        """, (message_type.upper(),))

        for row in cursor.fetchall():
            result["bronze_to_silver"].append({
                "silver_column": row[0],
                "bronze_path": row[1],
                "data_type": row[2],
                "is_required": row[3],
                "default_value": row[4],
            })

        # Get Silver → Gold mappings
        cursor.execute("""
            SELECT gold_table, gold_column, source_expression, entity_role, data_type, is_required, default_value
            FROM mapping.gold_field_mappings
            WHERE format_id = %s AND is_active = true
            ORDER BY gold_table, ordinal_position
        """, (message_type.upper(),))

        for row in cursor.fetchall():
            result["silver_to_gold"].append({
                "gold_table": row[0],
                "gold_column": row[1],
                "silver_column": row[2],  # source_expression is the Silver column name
                "entity_role": row[3],
                "data_type": row[4],
                "is_required": row[5],
                "default_value": row[6],
            })

        cursor.close()

    except Exception as e:
        logger.error(f"Error fetching mappings for {message_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

    return result

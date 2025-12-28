"""
GPS CDM - Real-Time Batch Processing Stats API
===============================================

Provides real-time visibility into batch processing pipeline.
Uses Redis for live metrics and PostgreSQL for historical data.

Endpoints:
- GET /api/v1/stats/batches/active - Active batches in progress
- GET /api/v1/stats/batches/{batch_id} - Single batch details
- GET /api/v1/stats/throughput - Real-time throughput metrics
- GET /api/v1/stats/layers - Per-layer processing stats
- GET /api/v1/stats/errors - Error summary
- WS /api/v1/stats/stream - WebSocket for live updates
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/stats", tags=["Batch Stats"])


# =============================================================================
# MODELS
# =============================================================================

class BatchStatus(BaseModel):
    """Status of a single batch."""
    batch_id: str
    message_type: Optional[str]
    status: str
    current_layer: Optional[str]
    bronze_records: int = 0
    silver_records: int = 0
    gold_records: int = 0
    failed_records: int = 0
    started_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]


class ThroughputStats(BaseModel):
    """Real-time throughput statistics."""
    window_seconds: int
    total_records_processed: int
    records_per_second: float
    batches_completed: int
    batches_failed: int
    avg_batch_duration_ms: float
    by_message_type: Dict[str, Dict[str, Any]]
    by_layer: Dict[str, Dict[str, Any]]


class LayerStats(BaseModel):
    """Per-layer processing statistics."""
    layer: str
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int
    avg_processing_time_ms: float
    records_per_second: float


class ErrorSummary(BaseModel):
    """Error summary statistics."""
    total_errors: int
    errors_last_hour: int
    by_error_type: Dict[str, int]
    by_layer: Dict[str, int]
    by_message_type: Dict[str, int]
    recent_errors: List[Dict[str, Any]]


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection():
    """Get PostgreSQL connection."""
    import psycopg2

    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password'),
    )


def get_redis_client():
    """Get Redis client for real-time metrics."""
    import redis

    return redis.Redis.from_url(
        os.environ.get('REDIS_URL', 'redis://localhost:6379/2'),
        decode_responses=True
    )


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/batches/active", response_model=List[BatchStatus])
async def get_active_batches(
    limit: int = Query(default=100, le=1000),
    message_type: Optional[str] = None,
) -> List[BatchStatus]:
    """
    Get currently active (in-progress) batches.

    Returns batches that are PENDING, PROCESSING, or partially completed.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = """
                SELECT batch_id, message_type, status, current_layer,
                       bronze_records, silver_records, gold_records, failed_records,
                       started_at,
                       EXTRACT(EPOCH FROM (COALESCE(completed_at, CURRENT_TIMESTAMP) - started_at)) as duration_seconds,
                       error_message
                FROM observability.obs_batch_tracking
                WHERE status NOT IN ('COMPLETED', 'FAILED')
            """
            params = []

            if message_type:
                query += " AND message_type = %s"
                params.append(message_type)

            query += " ORDER BY started_at DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            rows = cur.fetchall()

        conn.close()

        return [
            BatchStatus(
                batch_id=row[0],
                message_type=row[1],
                status=row[2],
                current_layer=row[3],
                bronze_records=row[4] or 0,
                silver_records=row[5] or 0,
                gold_records=row[6] or 0,
                failed_records=row[7] or 0,
                started_at=row[8],
                duration_seconds=row[9],
                error_message=row[10],
            )
            for row in rows
        ]

    except Exception as e:
        logger.exception(f"Failed to get active batches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batches/{batch_id}", response_model=BatchStatus)
async def get_batch_status(batch_id: str) -> BatchStatus:
    """Get detailed status of a specific batch."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT batch_id, message_type, status, current_layer,
                       bronze_records, silver_records, gold_records, failed_records,
                       started_at,
                       EXTRACT(EPOCH FROM (COALESCE(completed_at, CURRENT_TIMESTAMP) - started_at)) as duration_seconds,
                       error_message
                FROM observability.obs_batch_tracking
                WHERE batch_id = %s
            """, (batch_id,))
            row = cur.fetchone()

        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")

        return BatchStatus(
            batch_id=row[0],
            message_type=row[1],
            status=row[2],
            current_layer=row[3],
            bronze_records=row[4] or 0,
            silver_records=row[5] or 0,
            gold_records=row[6] or 0,
            failed_records=row[7] or 0,
            started_at=row[8],
            duration_seconds=row[9],
            error_message=row[10],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get batch status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/throughput", response_model=ThroughputStats)
async def get_throughput_stats(
    window_seconds: int = Query(default=60, le=3600),
) -> ThroughputStats:
    """
    Get real-time throughput statistics.

    Calculates records/second, batches completed, and per-type breakdown.
    """
    try:
        conn = get_db_connection()

        # Overall stats
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) as batch_count,
                    SUM(bronze_records + silver_records + gold_records) as total_records,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                    AVG(EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000) as avg_duration_ms
                FROM observability.obs_batch_tracking
                WHERE started_at >= NOW() - INTERVAL '%s seconds'
            """, (window_seconds,))
            row = cur.fetchone()

            batch_count = row[0] or 0
            total_records = row[1] or 0
            completed = row[2] or 0
            failed = row[3] or 0
            avg_duration = row[4] or 0

        # By message type
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    message_type,
                    COUNT(*) as batches,
                    SUM(bronze_records) as bronze,
                    SUM(silver_records) as silver,
                    SUM(gold_records) as gold
                FROM observability.obs_batch_tracking
                WHERE started_at >= NOW() - INTERVAL '%s seconds'
                GROUP BY message_type
            """, (window_seconds,))
            by_type = {
                row[0]: {
                    "batches": row[1],
                    "bronze_records": row[2] or 0,
                    "silver_records": row[3] or 0,
                    "gold_records": row[4] or 0,
                }
                for row in cur.fetchall()
            }

        # By layer (from micro_batch_tracking)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    state,
                    COUNT(*) as count,
                    SUM(record_count) as records
                FROM observability.micro_batch_tracking
                WHERE created_at >= NOW() - INTERVAL '%s seconds'
                GROUP BY state
            """, (window_seconds,))
            by_layer = {
                row[0]: {
                    "batches": row[1],
                    "records": row[2] or 0,
                }
                for row in cur.fetchall()
            }

        conn.close()

        records_per_second = total_records / window_seconds if window_seconds > 0 else 0

        return ThroughputStats(
            window_seconds=window_seconds,
            total_records_processed=total_records,
            records_per_second=records_per_second,
            batches_completed=completed,
            batches_failed=failed,
            avg_batch_duration_ms=avg_duration,
            by_message_type=by_type,
            by_layer=by_layer,
        )

    except Exception as e:
        logger.exception(f"Failed to get throughput stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layers", response_model=List[LayerStats])
async def get_layer_stats() -> List[LayerStats]:
    """Get processing statistics per layer (Bronze, Silver, Gold)."""
    try:
        conn = get_db_connection()
        stats = []

        # Bronze layer
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    SUM(CASE WHEN processing_status = 'PENDING' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN processing_status = 'PROCESSING' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN processing_status = 'PROCESSED_TO_SILVER' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN processing_status = 'FAILED' THEN 1 ELSE 0 END) as failed
                FROM bronze.raw_payment_messages
                WHERE ingestion_timestamp >= NOW() - INTERVAL '1 hour'
            """)
            row = cur.fetchone()
            stats.append(LayerStats(
                layer="bronze",
                pending_count=row[0] or 0,
                processing_count=row[1] or 0,
                completed_count=row[2] or 0,
                failed_count=row[3] or 0,
                avg_processing_time_ms=0,  # Would need timing data
                records_per_second=0,
            ))

        # Silver layer stats from micro_batch_tracking
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    SUM(CASE WHEN state IN ('PENDING', 'WRITING_BRONZE', 'BRONZE_COMPLETE') THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN state = 'WRITING_SILVER' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN state IN ('SILVER_COMPLETE', 'WRITING_GOLD', 'GOLD_COMPLETE', 'COMMITTED') THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN state = 'FAILED' THEN 1 ELSE 0 END) as failed,
                    AVG(duration_ms) as avg_duration
                FROM observability.micro_batch_tracking
                WHERE created_at >= NOW() - INTERVAL '1 hour'
            """)
            row = cur.fetchone()
            stats.append(LayerStats(
                layer="silver",
                pending_count=row[0] or 0,
                processing_count=row[1] or 0,
                completed_count=row[2] or 0,
                failed_count=row[3] or 0,
                avg_processing_time_ms=row[4] or 0,
                records_per_second=0,
            ))

        # Gold layer
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    SUM(CASE WHEN state IN ('SILVER_COMPLETE') THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN state = 'WRITING_GOLD' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN state IN ('GOLD_COMPLETE', 'COMMITTED') THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN state = 'FAILED' AND error_layer = 'gold' THEN 1 ELSE 0 END) as failed
                FROM observability.micro_batch_tracking
                WHERE created_at >= NOW() - INTERVAL '1 hour'
            """)
            row = cur.fetchone()
            stats.append(LayerStats(
                layer="gold",
                pending_count=row[0] or 0,
                processing_count=row[1] or 0,
                completed_count=row[2] or 0,
                failed_count=row[3] or 0,
                avg_processing_time_ms=0,
                records_per_second=0,
            ))

        conn.close()
        return stats

    except Exception as e:
        logger.exception(f"Failed to get layer stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors", response_model=ErrorSummary)
async def get_error_summary() -> ErrorSummary:
    """Get error summary and recent errors."""
    try:
        conn = get_db_connection()

        # Total errors
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM observability.obs_processing_errors
            """)
            total = cur.fetchone()[0]

        # Errors last hour
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM observability.obs_processing_errors
                WHERE created_at >= NOW() - INTERVAL '1 hour'
            """)
            last_hour = cur.fetchone()[0]

        # By error type
        with conn.cursor() as cur:
            cur.execute("""
                SELECT error_type, COUNT(*)
                FROM observability.obs_processing_errors
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY error_type
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            by_type = {row[0]: row[1] for row in cur.fetchall()}

        # By layer
        with conn.cursor() as cur:
            cur.execute("""
                SELECT layer, COUNT(*)
                FROM observability.obs_processing_errors
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY layer
            """)
            by_layer = {row[0]: row[1] for row in cur.fetchall()}

        # By message type (from batch)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT bt.message_type, COUNT(*)
                FROM observability.obs_processing_errors e
                JOIN observability.obs_batch_tracking bt ON e.batch_id = bt.batch_id
                WHERE e.created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY bt.message_type
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            by_message_type = {row[0] or 'unknown': row[1] for row in cur.fetchall()}

        # Recent errors
        with conn.cursor() as cur:
            cur.execute("""
                SELECT error_id, batch_id, layer, table_name, error_type,
                       error_message, severity, created_at
                FROM observability.obs_processing_errors
                ORDER BY created_at DESC
                LIMIT 20
            """)
            recent = [
                {
                    "error_id": row[0],
                    "batch_id": row[1],
                    "layer": row[2],
                    "table": row[3],
                    "error_type": row[4],
                    "message": row[5][:200] if row[5] else None,
                    "severity": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                }
                for row in cur.fetchall()
            ]

        conn.close()

        return ErrorSummary(
            total_errors=total,
            errors_last_hour=last_hour,
            by_error_type=by_type,
            by_layer=by_layer,
            by_message_type=by_message_type,
            recent_errors=recent,
        )

    except Exception as e:
        logger.exception(f"Failed to get error summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kafka/consumer-lag")
async def get_kafka_consumer_lag() -> Dict[str, Any]:
    """
    Get Kafka consumer lag for all consumer groups.

    Requires Kafka admin client access.
    """
    try:
        # This would require kafka-python or confluent-kafka AdminClient
        # For now, return placeholder
        return {
            "consumer_groups": [
                {
                    "group_id": "gps-cdm-bronze",
                    "topics": {
                        "payment.bronze.pain.001": {
                            "total_lag": 0,
                            "partitions": {}
                        }
                    },
                    "status": "stable"
                }
            ],
            "note": "Implement with Kafka AdminClient for real lag metrics"
        }

    except Exception as e:
        logger.exception(f"Failed to get consumer lag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dlq")
async def get_dlq_summary() -> Dict[str, Any]:
    """Get dead letter queue summary."""
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Pending DLQ entries
            cur.execute("""
                SELECT
                    message_type,
                    COUNT(*) as count,
                    SUM(record_count) as total_records,
                    MIN(created_at) as oldest
                FROM observability.kafka_dead_letter_queue
                WHERE resolution_status = 'PENDING'
                GROUP BY message_type
            """)
            pending = [
                {
                    "message_type": row[0],
                    "batch_count": row[1],
                    "record_count": row[2],
                    "oldest": row[3].isoformat() if row[3] else None,
                }
                for row in cur.fetchall()
            ]

            # Recent DLQ entries
            cur.execute("""
                SELECT dlq_id, batch_id, message_type, record_count,
                       error_type, resolution_status, created_at
                FROM observability.kafka_dead_letter_queue
                ORDER BY created_at DESC
                LIMIT 20
            """)
            recent = [
                {
                    "dlq_id": row[0],
                    "batch_id": row[1],
                    "message_type": row[2],
                    "record_count": row[3],
                    "error_type": row[4],
                    "status": row[5],
                    "created_at": row[6].isoformat() if row[6] else None,
                }
                for row in cur.fetchall()
            ]

        conn.close()

        return {
            "pending_by_type": pending,
            "total_pending": sum(p["batch_count"] for p in pending),
            "total_pending_records": sum(p["record_count"] for p in pending),
            "recent_entries": recent,
        }

    except Exception as e:
        logger.exception(f"Failed to get DLQ summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/stream")
async def stats_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time stats streaming.

    Sends updates every second with current processing stats.
    """
    await websocket.accept()

    try:
        while True:
            # Get current stats
            stats = await _get_realtime_stats()

            # Send to client
            await websocket.send_json(stats)

            # Wait before next update
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")


async def _get_realtime_stats() -> Dict[str, Any]:
    """Get real-time stats for WebSocket streaming."""
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Active batches
            cur.execute("""
                SELECT COUNT(*),
                       SUM(bronze_records),
                       SUM(silver_records),
                       SUM(gold_records)
                FROM observability.obs_batch_tracking
                WHERE status NOT IN ('COMPLETED', 'FAILED')
            """)
            row = cur.fetchone()
            active_batches = row[0] or 0
            bronze_in_progress = row[1] or 0
            silver_in_progress = row[2] or 0
            gold_in_progress = row[3] or 0

            # Throughput (last minute)
            cur.execute("""
                SELECT COUNT(*), SUM(bronze_records + silver_records + gold_records)
                FROM observability.obs_batch_tracking
                WHERE completed_at >= NOW() - INTERVAL '1 minute'
            """)
            row = cur.fetchone()
            batches_last_minute = row[0] or 0
            records_last_minute = row[1] or 0

        conn.close()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "active_batches": active_batches,
            "records_in_progress": {
                "bronze": bronze_in_progress,
                "silver": silver_in_progress,
                "gold": gold_in_progress,
            },
            "throughput": {
                "batches_per_minute": batches_last_minute,
                "records_per_minute": records_last_minute,
                "records_per_second": records_last_minute / 60,
            }
        }

    except Exception as e:
        logger.warning(f"Failed to get realtime stats: {e}")
        return {"error": str(e)}


# Import asyncio for WebSocket
import asyncio

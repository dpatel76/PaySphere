"""
GPS CDM API - WebSocket Routes for Real-time Updates
=====================================================

Provides real-time updates for:
- Processing error counts
- Pipeline throughput
- Batch progress
"""

import asyncio
import json
import logging
from typing import List, Set
from datetime import datetime
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._update_task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

        # Start the update loop if not already running
        if self._update_task is None or self._update_task.done():
            self._update_task = asyncio.create_task(self._update_loop())

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        if not self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)

    async def _update_loop(self):
        """Periodically fetch and broadcast stats."""
        while self.active_connections:
            try:
                stats = await self._fetch_stats()
                await self.broadcast({
                    "type": "stats_update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": stats
                })
            except Exception as e:
                logger.error(f"Error in update loop: {e}")

            await asyncio.sleep(5)  # Update every 5 seconds

    async def _fetch_stats(self) -> dict:
        """Fetch current stats from database."""
        import psycopg2

        try:
            conn = psycopg2.connect(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=int(os.environ.get("POSTGRES_PORT", 5433)),
                database=os.environ.get("POSTGRES_DB", "gps_cdm"),
                user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
                password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
            )
            cursor = conn.cursor()

            # Error counts by status
            cursor.execute("""
                SELECT status, COUNT(*) FROM bronze.processing_errors GROUP BY status
            """)
            error_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # Error counts by zone
            cursor.execute("""
                SELECT zone, COUNT(*) FROM bronze.processing_errors
                WHERE status IN ('PENDING', 'RETRYING') GROUP BY zone
            """)
            pending_by_zone = {row[0]: row[1] for row in cursor.fetchall()}

            # Recent error count (last 5 minutes)
            cursor.execute("""
                SELECT COUNT(*) FROM bronze.processing_errors
                WHERE created_at >= NOW() - INTERVAL '5 minutes'
            """)
            recent_errors = cursor.fetchone()[0]

            # Pipeline throughput (records per zone in last hour)
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM bronze.raw_payment_messages
                     WHERE _ingested_at >= NOW() - INTERVAL '1 hour') as bronze_count,
                    (SELECT COUNT(*) FROM silver.stg_pain001
                     WHERE _processed_at >= NOW() - INTERVAL '1 hour') as silver_count,
                    (SELECT COUNT(*) FROM gold.cdm_payment_instruction
                     WHERE created_at >= NOW() - INTERVAL '1 hour') as gold_count
            """)
            throughput = cursor.fetchone()

            conn.close()

            return {
                "errors": {
                    "by_status": error_counts,
                    "pending_by_zone": pending_by_zone,
                    "total_pending": error_counts.get('PENDING', 0) + error_counts.get('RETRYING', 0),
                    "recent_5min": recent_errors,
                },
                "throughput": {
                    "bronze_last_hour": throughput[0] if throughput else 0,
                    "silver_last_hour": throughput[1] if throughput else 0,
                    "gold_last_hour": throughput[2] if throughput else 0,
                }
            }
        except Exception as e:
            logger.error(f"Failed to fetch stats: {e}")
            return {
                "errors": {"total_pending": 0},
                "throughput": {},
                "error": str(e)
            }


# Global connection manager
manager = ConnectionManager()


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Clients receive periodic stats updates including:
    - Error counts by status and zone
    - Pipeline throughput by layer
    - Recent error count

    Message format:
    {
        "type": "stats_update",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "errors": {...},
            "throughput": {...}
        }
    }
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Handle ping/pong or other client messages
            if data == "ping":
                await websocket.send_text("pong")
            elif data.startswith("subscribe:"):
                # Future: Handle channel subscriptions
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/status")
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "active_connections": len(manager.active_connections),
        "update_loop_running": manager._update_task is not None and not manager._update_task.done(),
    }

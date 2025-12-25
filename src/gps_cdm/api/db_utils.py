"""
GPS CDM - Database Utilities
=============================

Centralized database connection and data source management for API routes.
Supports both Databricks (primary) and PostgreSQL (fallback) data stores.

Usage:
    from gps_cdm.api.db_utils import get_data_store, DataStore

    # Get appropriate data store based on configuration
    store = get_data_store()

    # Query batches
    batches = store.get_batches(limit=50)

    # Get records by layer
    records = store.get_records("bronze", batch_id="batch_123")
"""

import os
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Data source configuration from environment
DATA_SOURCE = os.environ.get("GPS_CDM_DATA_SOURCE", "auto")  # auto, databricks, postgresql


class DataStore(ABC):
    """Abstract base class for data store implementations."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the data store is available."""
        pass

    @abstractmethod
    def get_batches(self, limit: int = 50, status: Optional[str] = None,
                    message_type: Optional[str] = None, hours_back: int = 24) -> List[Dict]:
        """Get list of batches."""
        pass

    @abstractmethod
    def get_batch(self, batch_id: str) -> Optional[Dict]:
        """Get single batch by ID."""
        pass

    @abstractmethod
    def get_records(self, layer: str, batch_id: str, limit: int = 25, offset: int = 0) -> List[Dict]:
        """Get records for a batch by layer."""
        pass

    @abstractmethod
    def get_exceptions(self, batch_id: Optional[str] = None, status: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Get processing exceptions."""
        pass

    @abstractmethod
    def get_dq_metrics(self, batch_id: Optional[str] = None, layer: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Get data quality metrics."""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source."""
        pass


class PostgreSQLStore(DataStore):
    """PostgreSQL data store implementation."""

    def __init__(self):
        self._conn_params = {
            "host": os.environ.get("POSTGRES_HOST", "localhost"),
            "port": int(os.environ.get("POSTGRES_PORT", 5433)),
            "database": os.environ.get("POSTGRES_DB", "gps_cdm"),
            "user": os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
            "password": os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
        }

    @contextmanager
    def _get_connection(self):
        """Get a database connection with context manager."""
        import psycopg2
        conn = None
        try:
            conn = psycopg2.connect(**self._conn_params)
            yield conn
        finally:
            if conn:
                conn.close()

    def is_available(self) -> bool:
        """Check if PostgreSQL is available."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"PostgreSQL not available: {e}")
            return False

    @property
    def source_name(self) -> str:
        return "postgresql"

    def get_batches(self, limit: int = 50, status: Optional[str] = None,
                    message_type: Optional[str] = None, hours_back: int = 24) -> List[Dict]:
        """Get list of batches from PostgreSQL observability tables."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # First try the batch tracking table
                try:
                    conditions = ["created_at >= NOW() - INTERVAL '%s hours'"]
                    params: List[Any] = [hours_back]

                    if status:
                        conditions.append("status = %s")
                        params.append(status)
                    if message_type:
                        conditions.append("message_type = %s")
                        params.append(message_type)

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
                except Exception:
                    # Fallback: aggregate from bronze layer
                    cursor.execute("""
                        SELECT _batch_id as batch_id, message_type,
                               COUNT(*) as bronze_count, 'PROCESSED' as status,
                               MIN(_ingested_at) as created_at
                        FROM bronze.raw_payment_messages
                        GROUP BY _batch_id, message_type
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (limit,))

                    columns = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    for row in rows:
                        row["data_source"] = "postgresql"
                        row["silver_count"] = row.get("bronze_count", 0)
                        row["gold_count"] = row.get("bronze_count", 0)
                    return rows
        except Exception as e:
            logger.error(f"Failed to get batches from PostgreSQL: {e}")
            return []

    def get_batch(self, batch_id: str) -> Optional[Dict]:
        """Get single batch by ID."""
        batches = self.get_batches(limit=1)
        # Filter by batch_id
        for b in batches:
            if b.get("batch_id") == batch_id:
                return b

        # Direct query
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT _batch_id as batch_id, message_type,
                           COUNT(*) as bronze_count, 'PROCESSED' as status
                    FROM bronze.raw_payment_messages
                    WHERE _batch_id = %s
                    GROUP BY _batch_id, message_type
                """, (batch_id,))

                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, row))
                    result["data_source"] = "postgresql"
                    return result
        except Exception as e:
            logger.error(f"Failed to get batch {batch_id}: {e}")
        return None

    def get_records(self, layer: str, batch_id: str, limit: int = 25, offset: int = 0) -> List[Dict]:
        """Get records for a batch by layer."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

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
                    return []

                columns = [desc[0] for desc in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                for row in rows:
                    row["data_source"] = "postgresql"
                return rows
        except Exception as e:
            logger.error(f"Failed to get {layer} records: {e}")
            return []

    def get_exceptions(self, batch_id: Optional[str] = None, status: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Get processing exceptions."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                conditions = ["1=1"]
                params: List[Any] = []

                if batch_id:
                    conditions.append("batch_id = %s")
                    params.append(batch_id)
                if status:
                    conditions.append("status = %s")
                    params.append(status)

                cursor.execute(f"""
                    SELECT exception_id, batch_id, source_layer, source_table,
                           source_record_id, exception_type, exception_message,
                           severity, status, created_at
                    FROM observability.obs_processing_exceptions
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
            logger.warning(f"Failed to get exceptions: {e}")
            return []

    def get_dq_metrics(self, batch_id: Optional[str] = None, layer: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Get data quality metrics."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                conditions = ["1=1"]
                params: List[Any] = []

                if batch_id:
                    conditions.append("batch_id = %s")
                    params.append(batch_id)
                if layer:
                    conditions.append("layer = %s")
                    params.append(layer)

                cursor.execute(f"""
                    SELECT metric_id, batch_id, layer, table_name,
                           completeness_score, validity_score, accuracy_score,
                           overall_score, overall_status,
                           total_records, passed_records, failed_records,
                           calculated_at
                    FROM observability.obs_data_quality_metrics
                    WHERE {' AND '.join(conditions)}
                    ORDER BY calculated_at DESC
                    LIMIT %s
                """, params + [limit])

                columns = [desc[0] for desc in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                for row in rows:
                    row["data_source"] = "postgresql"
                return rows
        except Exception as e:
            logger.warning(f"Failed to get DQ metrics: {e}")
            return []


class DatabricksStore(DataStore):
    """Databricks data store implementation."""

    def __init__(self):
        self._connector = None

    def _get_connector(self):
        """Get or create Databricks connector."""
        if self._connector is None:
            try:
                from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector
                self._connector = DatabricksConnector()
                if not self._connector.is_available():
                    self._connector = None
            except Exception as e:
                logger.warning(f"Databricks connector not available: {e}")
                self._connector = None
        return self._connector

    def is_available(self) -> bool:
        """Check if Databricks is available."""
        connector = self._get_connector()
        return connector is not None and connector.is_available()

    @property
    def source_name(self) -> str:
        return "databricks"

    def get_batches(self, limit: int = 50, status: Optional[str] = None,
                    message_type: Optional[str] = None, hours_back: int = 24) -> List[Dict]:
        """Get list of batches from Databricks."""
        connector = self._get_connector()
        if not connector:
            return []

        try:
            batches = connector.get_batches(limit=limit, status=status)
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
            logger.error(f"Failed to get batches from Databricks: {e}")
            return []

    def get_batch(self, batch_id: str) -> Optional[Dict]:
        """Get single batch by ID from Databricks."""
        connector = self._get_connector()
        if not connector:
            return None

        try:
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
                    "total_records": batch.get("total_records", 0),
                    "processed_records": batch.get("processed_records", 0),
                    "created_at": batch.get("created_at"),
                    "completed_at": batch.get("completed_at"),
                    "data_source": "databricks",
                }
        except Exception as e:
            logger.error(f"Failed to get batch {batch_id} from Databricks: {e}")
        return None

    def get_records(self, layer: str, batch_id: str, limit: int = 25, offset: int = 0) -> List[Dict]:
        """Get records for a batch by layer from Databricks."""
        connector = self._get_connector()
        if not connector:
            return []

        try:
            records = []
            if layer == "bronze":
                records = connector.get_bronze_records(batch_id=batch_id, limit=limit)
            elif layer == "silver":
                records = connector.get_silver_records(batch_id=batch_id, limit=limit)
            elif layer == "gold":
                records = connector.get_payment_instructions(batch_id=batch_id, limit=limit)

            for r in records:
                r["data_source"] = "databricks"
            return records
        except Exception as e:
            logger.error(f"Failed to get {layer} records from Databricks: {e}")
            return []

    def get_exceptions(self, batch_id: Optional[str] = None, status: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Get processing exceptions from Databricks."""
        # Databricks doesn't store exceptions - fall through to PostgreSQL
        return []

    def get_dq_metrics(self, batch_id: Optional[str] = None, layer: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Get data quality metrics from Databricks."""
        # Could be extended to query from Databricks observability tables
        return []


# Global data store instances
_postgresql_store: Optional[PostgreSQLStore] = None
_databricks_store: Optional[DatabricksStore] = None


def get_data_store() -> DataStore:
    """
    Get the appropriate data store based on configuration and availability.

    Priority:
    1. If DATA_SOURCE is explicitly set to 'databricks' or 'postgresql', use that
    2. If 'auto', prefer Databricks if available, else PostgreSQL
    """
    global _postgresql_store, _databricks_store

    # Initialize stores if needed
    if _postgresql_store is None:
        _postgresql_store = PostgreSQLStore()
    if _databricks_store is None:
        _databricks_store = DatabricksStore()

    # Explicit configuration
    if DATA_SOURCE == "postgresql":
        return _postgresql_store
    if DATA_SOURCE == "databricks":
        if _databricks_store.is_available():
            return _databricks_store
        logger.warning("Databricks requested but not available, falling back to PostgreSQL")
        return _postgresql_store

    # Auto-detect: prefer Databricks if available
    if _databricks_store.is_available():
        return _databricks_store
    return _postgresql_store


def get_all_stores() -> Dict[str, DataStore]:
    """Get all configured data stores."""
    global _postgresql_store, _databricks_store

    if _postgresql_store is None:
        _postgresql_store = PostgreSQLStore()
    if _databricks_store is None:
        _databricks_store = DatabricksStore()

    return {
        "postgresql": _postgresql_store,
        "databricks": _databricks_store,
    }


def get_data_source_info() -> Dict[str, Any]:
    """Get information about data sources."""
    stores = get_all_stores()
    active_store = get_data_store()

    return {
        "configured_source": DATA_SOURCE,
        "active_source": active_store.source_name,
        "sources": {
            name: {
                "available": store.is_available(),
                "active": store.source_name == active_store.source_name,
            }
            for name, store in stores.items()
        },
    }

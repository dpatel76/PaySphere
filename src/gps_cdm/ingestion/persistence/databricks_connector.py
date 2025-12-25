"""
GPS CDM - Databricks Remote Connector
=====================================

Connects to Databricks Free Edition from local application.
Uses Databricks SQL Connector for querying and data operations.

Setup:
1. Get your Databricks workspace URL from your account
2. Generate a Personal Access Token (PAT) in Databricks UI
3. Get the SQL Warehouse HTTP Path

Usage:
    from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector

    connector = DatabricksConnector(
        server_hostname="your-workspace.cloud.databricks.com",
        http_path="/sql/1.0/warehouses/your-warehouse-id",
        access_token="your-personal-access-token",
        catalog="workspace",
        schema="cdm_dev"
    )

    # Query data
    df = connector.query("SELECT * FROM gold_cdm_payment_instruction LIMIT 10")

    # Write data
    connector.insert_records("bronze_raw_payment", records)
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class DatabricksConnector:
    """
    Remote connector to Databricks Free Edition.

    Uses Databricks SQL Connector for serverless SQL warehouse access.
    """

    def __init__(
        self,
        server_hostname: Optional[str] = None,
        http_path: Optional[str] = None,
        access_token: Optional[str] = None,
        catalog: str = "workspace",
        schema: str = "cdm_dev",
    ):
        """
        Initialize Databricks connector.

        Args:
            server_hostname: Databricks workspace hostname (e.g., "xxx.cloud.databricks.com")
            http_path: SQL warehouse HTTP path (e.g., "/sql/1.0/warehouses/xxx")
            access_token: Personal Access Token (PAT)
            catalog: Unity Catalog name
            schema: Schema/database name
        """
        self.server_hostname = server_hostname or os.environ.get("DATABRICKS_SERVER_HOSTNAME")
        self.http_path = http_path or os.environ.get("DATABRICKS_HTTP_PATH")
        self.access_token = access_token or os.environ.get("DATABRICKS_TOKEN")
        self.catalog = catalog or os.environ.get("DATABRICKS_CATALOG", "workspace")
        self.schema = schema or os.environ.get("DATABRICKS_SCHEMA", "cdm_dev")

        self._connection = None

    def _get_connection(self):
        """Get or create database connection."""
        if self._connection is None:
            try:
                from databricks import sql

                if not all([self.server_hostname, self.http_path, self.access_token]):
                    raise ValueError(
                        "Missing Databricks configuration. Set DATABRICKS_SERVER_HOSTNAME, "
                        "DATABRICKS_HTTP_PATH, and DATABRICKS_TOKEN environment variables."
                    )

                self._connection = sql.connect(
                    server_hostname=self.server_hostname,
                    http_path=self.http_path,
                    access_token=self.access_token,
                )
                logger.info(f"Connected to Databricks: {self.server_hostname}")

            except ImportError:
                raise ImportError("databricks-sql-connector not installed. Run: pip install databricks-sql-connector")

        return self._connection

    def close(self):
        """Close the connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def get_table_name(self, table: str) -> str:
        """Get fully qualified table name."""
        return f"{self.catalog}.{self.schema}.{table}"

    def is_available(self) -> bool:
        """Check if Databricks is available."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"Databricks not available: {e}")
            return False

    def query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dicts.

        Args:
            sql: SQL query string

        Returns:
            List of dictionaries with column names as keys
        """
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def execute(self, sql: str) -> int:
        """
        Execute a SQL statement (INSERT, UPDATE, DELETE).

        Args:
            sql: SQL statement

        Returns:
            Number of affected rows
        """
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.rowcount

    def get_batches(self, limit: int = 10, status: Optional[str] = None) -> List[Dict]:
        """Get recent batches from tracking table."""
        table = self.get_table_name("obs_batch_tracking")
        sql = f"SELECT * FROM {table}"
        if status:
            sql += f" WHERE status = '{status}'"
        sql += f" ORDER BY created_at DESC LIMIT {limit}"
        return self.query(sql)

    def get_batch_lineage(self, batch_id: str) -> Dict[str, Any]:
        """Get lineage for a specific batch."""
        lineage_table = self.get_table_name("obs_data_lineage")
        batch_table = self.get_table_name("obs_batch_tracking")

        batch = self.query(f"SELECT * FROM {batch_table} WHERE batch_id = '{batch_id}'")
        lineage = self.query(f"SELECT * FROM {lineage_table} WHERE batch_id = '{batch_id}'")

        return {
            "batch": batch[0] if batch else None,
            "lineage": lineage
        }

    def get_payment_instructions(self, batch_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get payment instructions from gold layer."""
        table = self.get_table_name("gold_cdm_payment_instruction")
        sql = f"SELECT * FROM {table}"
        if batch_id:
            sql += f" WHERE _batch_id = '{batch_id}'"
        sql += f" ORDER BY created_at DESC LIMIT {limit}"
        return self.query(sql)

    def get_parties(self, batch_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get parties from gold layer."""
        table = self.get_table_name("gold_cdm_party")
        sql = f"SELECT * FROM {table}"
        if batch_id:
            sql += f" WHERE _batch_id = '{batch_id}'"
        sql += f" LIMIT {limit}"
        return self.query(sql)

    def get_accounts(self, batch_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get accounts from gold layer."""
        table = self.get_table_name("gold_cdm_account")
        sql = f"SELECT * FROM {table}"
        if batch_id:
            sql += f" WHERE _batch_id = '{batch_id}'"
        sql += f" LIMIT {limit}"
        return self.query(sql)

    def get_bronze_records(self, batch_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get raw records from bronze layer."""
        table = self.get_table_name("bronze_raw_payment")
        sql = f"SELECT raw_id, message_type, message_id, file_name, _batch_id, _ingested_at FROM {table}"
        if batch_id:
            sql += f" WHERE _batch_id = '{batch_id}'"
        sql += f" ORDER BY _ingested_at DESC LIMIT {limit}"
        return self.query(sql)

    def get_silver_records(self, batch_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get staged records from silver layer."""
        table = self.get_table_name("silver_stg_payment_instruction")
        sql = f"""
            SELECT stg_id, raw_id, message_type, message_id, amount, currency,
                   debtor_name, creditor_name, dq_score, _batch_id, _ingested_at
            FROM {table}
        """
        if batch_id:
            sql += f" WHERE _batch_id = '{batch_id}'"
        sql += f" ORDER BY _ingested_at DESC LIMIT {limit}"
        return self.query(sql)

    def get_layer_stats(self, batch_id: str) -> Dict[str, int]:
        """Get record counts per layer for a batch."""
        stats = {}

        for layer, table in [
            ("bronze", "bronze_raw_payment"),
            ("silver", "silver_stg_payment_instruction"),
            ("gold_payments", "gold_cdm_payment_instruction"),
            ("gold_parties", "gold_cdm_party"),
            ("gold_accounts", "gold_cdm_account"),
            ("gold_fis", "gold_cdm_financial_institution"),
        ]:
            full_table = self.get_table_name(table)
            try:
                result = self.query(f"SELECT COUNT(*) as cnt FROM {full_table} WHERE _batch_id = '{batch_id}'")
                stats[layer] = result[0]["cnt"] if result else 0
            except Exception:
                stats[layer] = 0

        return stats

    def sync_batch_to_neo4j(self, batch_id: str) -> bool:
        """
        Sync a Databricks batch to Neo4j for lineage visualization.

        Args:
            batch_id: The batch ID to sync

        Returns:
            True if successful
        """
        try:
            from gps_cdm.orchestration.neo4j_service import get_neo4j_service

            neo4j = get_neo4j_service()
            if not neo4j.is_available():
                logger.warning("Neo4j not available for sync")
                return False

            # Get batch info
            batch_info = self.get_batch_lineage(batch_id)
            if not batch_info.get("batch"):
                logger.warning(f"Batch {batch_id} not found in Databricks")
                return False

            batch = batch_info["batch"]

            # Convert created_at to ISO format for Neo4j
            created_at = batch.get("created_at")
            if created_at:
                if isinstance(created_at, datetime):
                    created_at_iso = created_at.isoformat()
                else:
                    # Handle string format "2025-12-24 21:50:06.123704" -> ISO format
                    created_at_str = str(created_at)
                    if " " in created_at_str and "T" not in created_at_str:
                        created_at_iso = created_at_str.replace(" ", "T")
                    else:
                        created_at_iso = created_at_str
            else:
                created_at_iso = datetime.utcnow().isoformat()

            # Upsert batch to Neo4j
            neo4j.upsert_batch({
                "batch_id": batch_id,
                "message_type": batch.get("mapping_id", "pain.001"),
                "source_system": "DATABRICKS_FREE",
                "status": batch.get("status", "UNKNOWN"),
                "created_at": created_at_iso,
                "total_records": batch.get("total_records", 0),
            })

            # Get layer stats and sync
            stats = self.get_layer_stats(batch_id)

            for layer in ["bronze", "silver", "gold_payments"]:
                layer_name = layer.replace("gold_payments", "gold")
                if stats.get(layer, 0) > 0:
                    neo4j.upsert_batch_layer(
                        batch_id=batch_id,
                        layer=layer_name,
                        stats={
                            "input_count": stats.get(layer, 0),
                            "processed_count": stats.get(layer, 0),
                            "failed_count": 0,
                        }
                    )

            logger.info(f"Synced batch {batch_id} to Neo4j")
            return True

        except Exception as e:
            logger.error(f"Failed to sync to Neo4j: {e}")
            return False


def get_databricks_connector(
    server_hostname: Optional[str] = None,
    http_path: Optional[str] = None,
    access_token: Optional[str] = None,
) -> DatabricksConnector:
    """
    Get a configured Databricks connector.

    Reads from environment variables if not provided:
    - DATABRICKS_SERVER_HOSTNAME
    - DATABRICKS_HTTP_PATH
    - DATABRICKS_TOKEN
    - DATABRICKS_CATALOG
    - DATABRICKS_SCHEMA

    Returns:
        Configured DatabricksConnector instance
    """
    return DatabricksConnector(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token,
    )

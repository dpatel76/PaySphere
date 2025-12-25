"""
GPS CDM - PostgreSQL Persistence Backend
========================================

PostgreSQL adapter for local development and testing.
Implements the same interface as Delta Lake for production.

Supports 4-layer medallion architecture:
- Bronze: Raw data as-is
- Silver: Structured per message type (stg_*)
- Gold: CDM normalized (cdm_*)
- Analytical: Data products (anl_*)
- Observability: Operational metadata (obs_*)

Usage:
    from gps_cdm.ingestion.persistence import PersistenceFactory

    persistence = PersistenceFactory.create(
        backend="postgresql",
        config={
            "host": "localhost",
            "port": 5432,
            "database": "gps_cdm",
            "user": "postgres",
            "password": "postgres",
            "ddl_directory": "/path/to/ddl/postgresql"
        }
    )
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import uuid
import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import lit, current_timestamp, to_json, struct, col
from pyspark.sql.types import StringType

from gps_cdm.ingestion.persistence.base import (
    PersistenceBackend,
    PersistenceConfig,
    WriteResult,
    WriteMode,
    Layer,
)


class PostgreSQLBackend(PersistenceBackend):
    """
    PostgreSQL persistence backend for local testing.

    Creates schemas for bronze/silver/gold/analytical and persists data using JDBC.
    Provides same interface as Delta Lake for seamless testing.

    Schema mapping:
    - bronze: raw_* tables (raw data as-is)
    - silver: stg_* tables (structured per message type)
    - gold: cdm_* tables (CDM normalized)
    - analytical: anl_* tables (data products)
    - observability: obs_* tables (operational metadata)
    """

    def __init__(self, spark: SparkSession, config: PersistenceConfig):
        """Initialize PostgreSQL backend."""
        super().__init__(spark, config)

        # Build JDBC URL
        host = config.host or "localhost"
        port = config.port or 5432
        database = config.database or config.catalog or "gps_cdm"

        self.jdbc_url = f"jdbc:postgresql://{host}:{port}/{database}"
        self.connection_props = {
            "user": config.user or "postgres",
            "password": config.password or "postgres",
            "driver": "org.postgresql.Driver",
        }

        # DDL directory for schema initialization
        self.ddl_directory = config.ddl_directory

        # Schema names (match DDL files)
        self.schemas = {
            Layer.BRONZE: config.bronze_schema,        # "bronze"
            Layer.SILVER: config.silver_schema,        # "silver"
            Layer.GOLD: config.gold_schema,            # "gold"
            Layer.ANALYTICAL: config.analytical_schema, # "analytical"
            Layer.OBSERVABILITY: config.observability_schema,  # "observability"
        }

    def initialize(self) -> bool:
        """
        Initialize PostgreSQL schemas from DDL files.

        If ddl_directory is specified, runs all DDL files in order.
        Otherwise, creates basic schema structure.

        Returns:
            True if initialization successful
        """
        try:
            if self.ddl_directory and os.path.exists(self.ddl_directory):
                return self._initialize_from_ddl()

            # Fallback: Create basic schemas
            for layer, schema in self.schemas.items():
                self._execute_sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")

            self._initialized = True
            return True

        except Exception as e:
            print(f"PostgreSQL initialization failed: {e}")
            return False

    def _initialize_from_ddl(self) -> bool:
        """
        Initialize database from DDL files.

        Runs DDL scripts in order:
        - 00_create_database.sql
        - 01_bronze_tables.sql
        - 02_silver_tables.sql
        - 03_gold_cdm_tables.sql
        - 04_analytical_tables.sql
        - 05_observability_tables.sql

        Returns:
            True if all DDL executed successfully
        """
        ddl_order = [
            "00_create_database.sql",
            "01_bronze_tables.sql",
            "02_silver_tables.sql",
            "03_gold_cdm_tables.sql",
            "04_analytical_tables.sql",
            "05_observability_tables.sql",
        ]

        for ddl_file in ddl_order:
            ddl_path = Path(self.ddl_directory) / ddl_file
            if ddl_path.exists():
                print(f"Running DDL: {ddl_file}")
                success = self._run_ddl_file(ddl_path)
                if not success:
                    print(f"Failed to run DDL: {ddl_file}")
                    return False

        self._initialized = True
        return True

    def _run_ddl_file(self, ddl_path: Path) -> bool:
        """
        Execute a DDL file via psycopg2 or subprocess.

        Uses psql command for better DDL support.
        """
        try:
            import subprocess

            host = self.config.host or "localhost"
            port = self.config.port or 5432
            database = self.config.database or self.config.catalog or "gps_cdm"
            user = self.config.user or "postgres"

            # Use psql to run DDL file
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password or "postgres"

            result = subprocess.run(
                ["psql", "-h", host, "-p", str(port), "-U", user, "-d", database, "-f", str(ddl_path)],
                env=env,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"DDL error: {result.stderr}")
                return False

            return True

        except FileNotFoundError:
            # psql not available, try alternative approach
            print("psql not found, attempting direct SQL execution...")
            return self._run_ddl_file_direct(ddl_path)
        except Exception as e:
            print(f"Failed to run DDL file: {e}")
            return False

    def _run_ddl_file_direct(self, ddl_path: Path) -> bool:
        """
        Execute DDL file using psycopg2 directly.
        """
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=self.config.host or "localhost",
                port=self.config.port or 5432,
                database=self.config.database or self.config.catalog or "gps_cdm",
                user=self.config.user or "postgres",
                password=self.config.password or "postgres",
            )
            conn.autocommit = True

            with open(ddl_path, "r") as f:
                ddl_content = f.read()

            # Split on semicolons and execute each statement
            # Skip \i and \echo commands (psql-specific)
            statements = ddl_content.split(";")
            with conn.cursor() as cur:
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt and not stmt.startswith("\\"):
                        try:
                            cur.execute(stmt)
                        except Exception as e:
                            # Skip errors for CREATE IF NOT EXISTS
                            if "already exists" not in str(e).lower():
                                print(f"Statement failed: {e}")

            conn.close()
            return True

        except ImportError:
            print("psycopg2 not installed. Cannot initialize database.")
            return False
        except Exception as e:
            print(f"Direct DDL execution failed: {e}")
            return False

    def _execute_sql(self, sql: str):
        """Execute SQL statement via JDBC."""
        # Use Spark JDBC to execute DDL
        # Note: For production, use psycopg2 or SQLAlchemy directly
        try:
            self.spark.read.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("user", self.connection_props["user"]) \
                .option("password", self.connection_props["password"]) \
                .option("driver", self.connection_props["driver"]) \
                .option("query", sql) \
                .load()
        except Exception:
            # DDL statements don't return results, so exception is expected
            pass

    def get_table_path(self, layer: Layer, table: str) -> str:
        """Get full table name with schema."""
        schema = self.schemas.get(layer, self.schemas[Layer.SILVER])
        return f"{schema}.{table}"

    def table_exists(self, layer: Layer, table: str) -> bool:
        """Check if table exists in PostgreSQL."""
        try:
            full_table = self.get_table_path(layer, table)
            self.spark.read.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"(SELECT 1 FROM {full_table} LIMIT 1) AS t") \
                .options(**self.connection_props) \
                .load()
            return True
        except Exception:
            return False

    def write(
        self,
        df: DataFrame,
        layer: Layer,
        table: str,
        batch_id: str,
        mode: WriteMode = WriteMode.APPEND,
        partition_cols: Optional[List[str]] = None,
        merge_keys: Optional[List[str]] = None,
    ) -> WriteResult:
        """
        Write DataFrame to PostgreSQL table.

        Args:
            df: DataFrame to write
            layer: Target layer
            table: Table name
            batch_id: Batch identifier
            mode: Write mode
            partition_cols: Ignored for PostgreSQL
            merge_keys: Keys for upsert (if mode=MERGE)

        Returns:
            WriteResult with operation details
        """
        full_table = self.get_table_path(layer, table)
        timestamp = datetime.utcnow()

        try:
            # Add batch tracking columns
            df_with_meta = df.withColumn("_batch_id", lit(batch_id)) \
                             .withColumn("_ingested_at", current_timestamp())

            # Determine write mode
            jdbc_mode = "append"
            if mode == WriteMode.OVERWRITE:
                jdbc_mode = "overwrite"
            elif mode == WriteMode.ERROR_IF_EXISTS:
                jdbc_mode = "error"
            elif mode == WriteMode.MERGE and merge_keys:
                # PostgreSQL upsert via temp table approach
                return self._write_with_merge(df_with_meta, full_table, batch_id, merge_keys, timestamp)

            # Write to PostgreSQL
            record_count = df.count()

            df_with_meta.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", full_table) \
                .options(**self.connection_props) \
                .mode(jdbc_mode) \
                .save()

            return WriteResult(
                success=True,
                layer=layer,
                table=table,
                records_written=record_count,
                batch_id=batch_id,
                timestamp=timestamp,
                metadata={"full_table": full_table, "mode": mode.value}
            )

        except Exception as e:
            return WriteResult(
                success=False,
                layer=layer,
                table=table,
                records_written=0,
                batch_id=batch_id,
                timestamp=timestamp,
                error_message=str(e)
            )

    def _write_with_merge(
        self,
        df: DataFrame,
        full_table: str,
        batch_id: str,
        merge_keys: List[str],
        timestamp: datetime
    ) -> WriteResult:
        """
        Implement upsert using temp table and INSERT ON CONFLICT.

        PostgreSQL doesn't have native MERGE, so we use INSERT ON CONFLICT.
        """
        temp_table = f"{full_table}_temp_{batch_id.replace('-', '_')[:8]}"

        try:
            record_count = df.count()

            # Write to temp table
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", temp_table) \
                .options(**self.connection_props) \
                .mode("overwrite") \
                .save()

            # Build upsert SQL
            columns = df.columns
            key_cols = ", ".join(merge_keys)
            insert_cols = ", ".join(columns)
            update_cols = ", ".join([f"{c} = EXCLUDED.{c}" for c in columns if c not in merge_keys])

            upsert_sql = f"""
            INSERT INTO {full_table} ({insert_cols})
            SELECT {insert_cols} FROM {temp_table}
            ON CONFLICT ({key_cols}) DO UPDATE SET {update_cols}
            """

            self._execute_sql(upsert_sql)
            self._execute_sql(f"DROP TABLE IF EXISTS {temp_table}")

            return WriteResult(
                success=True,
                layer=Layer.SILVER,
                table=full_table.split(".")[-1],
                records_written=record_count,
                batch_id=batch_id,
                timestamp=timestamp,
                metadata={"mode": "merge", "merge_keys": merge_keys}
            )

        except Exception as e:
            return WriteResult(
                success=False,
                layer=Layer.SILVER,
                table=full_table.split(".")[-1],
                records_written=0,
                batch_id=batch_id,
                timestamp=timestamp,
                error_message=str(e)
            )

    def read(
        self,
        layer: Layer,
        table: str,
        columns: Optional[List[str]] = None,
        filter_expr: Optional[str] = None,
    ) -> DataFrame:
        """
        Read data from PostgreSQL.

        Args:
            layer: Source layer
            table: Table name
            columns: Columns to select
            filter_expr: SQL WHERE clause

        Returns:
            DataFrame with requested data
        """
        full_table = self.get_table_path(layer, table)

        # Build query
        col_list = ", ".join(columns) if columns else "*"
        where = f"WHERE {filter_expr}" if filter_expr else ""
        query = f"(SELECT {col_list} FROM {full_table} {where}) AS t"

        return self.spark.read.format("jdbc") \
            .option("url", self.jdbc_url) \
            .option("dbtable", query) \
            .options(**self.connection_props) \
            .load()

    def write_lineage(
        self,
        batch_id: str,
        source_layer: Layer,
        target_layer: Layer,
        source_table: str,
        target_table: str,
        record_count: int,
        mapping_id: str,
        field_mappings: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Write table-level lineage record to observability schema."""
        try:
            lineage_id = str(uuid.uuid4())
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            record = [{
                "lineage_id": lineage_id,
                "batch_id": batch_id,
                "source_layer": source_layer.value,
                "target_layer": target_layer.value,
                "source_table": source_table,
                "target_table": target_table,
                "source_record_count": record_count,
                "target_record_count": record_count,
                "mapping_id": mapping_id,
                "field_mappings_count": len(field_mappings) if field_mappings else 0,
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"{obs_schema}.obs_data_lineage") \
                .options(**self.connection_props) \
                .mode("append") \
                .save()

            return True

        except Exception as e:
            print(f"Failed to write lineage: {e}")
            return False

    def write_error(
        self,
        batch_id: str,
        layer: Layer,
        table: str,
        error_type: str,
        error_message: str,
        record_data: Optional[str] = None,
        record_id: Optional[str] = None,
    ) -> bool:
        """Write error record to observability schema."""
        try:
            error_id = str(uuid.uuid4())
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            record = [{
                "error_id": error_id,
                "batch_id": batch_id,
                "layer": layer.value,
                "table_name": table,
                "error_type": error_type,
                "error_message": error_message[:4000] if error_message else None,
                "record_data": record_data,
                "record_id": record_id,
                "severity": "ERROR",
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"{obs_schema}.obs_processing_errors") \
                .options(**self.connection_props) \
                .mode("append") \
                .save()

            return True

        except Exception as e:
            print(f"Failed to write error: {e}")
            return False

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get batch status from tracking table."""
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]
            query = f"""
                (SELECT * FROM {obs_schema}.obs_batch_tracking
                 WHERE batch_id = '{batch_id}') AS t
            """

            df = self.spark.read.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", query) \
                .options(**self.connection_props) \
                .load()

            if df.count() == 0:
                return {"batch_id": batch_id, "status": "NOT_FOUND"}

            row = df.collect()[0]
            return row.asDict()

        except Exception as e:
            return {"batch_id": batch_id, "status": "ERROR", "error": str(e)}

    # =========================================================================
    # Field-Level Lineage
    # =========================================================================
    def write_field_lineage(
        self,
        batch_id: str,
        source_layer: Layer,
        source_table: str,
        source_field: str,
        target_layer: Layer,
        target_table: str,
        target_field: str,
        transformation_type: str,
        transformation_logic: Optional[str] = None,
        mapping_id: Optional[str] = None,
    ) -> bool:
        """Write field-level lineage record."""
        try:
            lineage_id = str(uuid.uuid4())
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            record = [{
                "lineage_id": lineage_id,
                "batch_id": batch_id,
                "source_layer": source_layer.value,
                "source_table": source_table,
                "source_field": source_field,
                "target_layer": target_layer.value,
                "target_table": target_table,
                "target_field": target_field,
                "transformation_type": transformation_type,
                "transformation_logic": transformation_logic,
                "mapping_id": mapping_id or "",
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"{obs_schema}.obs_field_lineage") \
                .options(**self.connection_props) \
                .mode("append") \
                .save()

            return True

        except Exception as e:
            print(f"Failed to write field lineage: {e}")
            return False

    def write_field_lineage_batch(
        self,
        batch_id: str,
        field_mappings: List[Dict[str, Any]],
        mapping_id: str,
    ) -> bool:
        """
        Write multiple field-level lineage records in batch.

        Args:
            batch_id: Batch identifier
            field_mappings: List of field mapping dicts with source/target info
            mapping_id: Mapping configuration ID

        Returns:
            True if all records written successfully
        """
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            records = []
            for fm in field_mappings:
                records.append({
                    "lineage_id": str(uuid.uuid4()),
                    "batch_id": batch_id,
                    "source_layer": fm.get("source_layer", "silver"),
                    "source_table": fm.get("source_table", ""),
                    "source_field": fm.get("source_field", ""),
                    "target_layer": fm.get("target_layer", "gold"),
                    "target_table": fm.get("target_table", ""),
                    "target_field": fm.get("target_field", ""),
                    "transformation_type": fm.get("transformation_type", "direct"),
                    "transformation_logic": fm.get("transformation_logic"),
                    "mapping_id": mapping_id,
                })

            if records:
                df = self.spark.createDataFrame(records)
                df.write.format("jdbc") \
                    .option("url", self.jdbc_url) \
                    .option("dbtable", f"{obs_schema}.obs_field_lineage") \
                    .options(**self.connection_props) \
                    .mode("append") \
                    .save()

            return True

        except Exception as e:
            print(f"Failed to write field lineage batch: {e}")
            return False

    # =========================================================================
    # Data Quality
    # =========================================================================
    def write_dq_result(
        self,
        batch_id: str,
        layer: Layer,
        entity_type: str,
        entity_id: str,
        overall_score: float,
        dimension_scores: Dict[str, float],
        rule_results: Dict[str, Any],
        issues: Optional[List[str]] = None,
    ) -> bool:
        """Write per-record data quality result."""
        try:
            result_id = str(uuid.uuid4())
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            record = [{
                "dq_result_id": result_id,
                "batch_id": batch_id,
                "layer": layer.value,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "overall_score": overall_score,
                "completeness_score": dimension_scores.get("completeness"),
                "accuracy_score": dimension_scores.get("accuracy"),
                "validity_score": dimension_scores.get("validity"),
                "timeliness_score": dimension_scores.get("timeliness"),
                "consistency_score": dimension_scores.get("consistency"),
                "rules_executed": len(rule_results),
                "rules_passed": sum(1 for r in rule_results.values() if r.get("passed", False)),
                "rules_failed": sum(1 for r in rule_results.values() if not r.get("passed", True)),
                "rule_results": json.dumps(rule_results),
                "issues": issues or [],
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"{obs_schema}.obs_dq_results") \
                .options(**self.connection_props) \
                .mode("append") \
                .save()

            return True

        except Exception as e:
            print(f"Failed to write DQ result: {e}")
            return False

    def write_dq_metrics(
        self,
        batch_id: str,
        layer: Layer,
        entity_type: str,
        total_records: int,
        avg_score: float,
        dimension_averages: Dict[str, float],
        records_above_threshold: int,
        records_below_threshold: int,
        top_failing_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """Write aggregated data quality metrics."""
        try:
            metric_id = str(uuid.uuid4())
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            record = [{
                "metric_id": metric_id,
                "batch_id": batch_id,
                "metric_date": datetime.now().date().isoformat(),
                "layer": layer.value,
                "entity_type": entity_type,
                "total_records": total_records,
                "avg_overall_score": avg_score,
                "avg_completeness": dimension_averages.get("completeness"),
                "avg_validity": dimension_averages.get("validity"),
                "records_above_threshold": records_above_threshold,
                "records_below_threshold": records_below_threshold,
                "top_failing_rules": json.dumps(top_failing_rules or []),
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"{obs_schema}.obs_dq_metrics") \
                .options(**self.connection_props) \
                .mode("append") \
                .save()

            return True

        except Exception as e:
            print(f"Failed to write DQ metrics: {e}")
            return False

    # =========================================================================
    # Change Data Capture (CDC)
    # =========================================================================
    def write_cdc_event(
        self,
        layer: Layer,
        table: str,
        record_id: str,
        operation: str,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        changed_fields: Optional[List[str]] = None,
        batch_id: Optional[str] = None,
    ) -> bool:
        """Write CDC event for downstream sync."""
        try:
            cdc_id = str(uuid.uuid4())
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            record = [{
                "cdc_id": cdc_id,
                "layer": layer.value,
                "table_name": table,
                "record_id": record_id,
                "operation": operation,
                "old_data": json.dumps(old_data) if old_data else None,
                "new_data": json.dumps(new_data) if new_data else None,
                "changed_fields": changed_fields or [],
                "batch_id": batch_id,
                "sync_status": "PENDING",
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"{obs_schema}.obs_cdc_tracking") \
                .options(**self.connection_props) \
                .mode("append") \
                .save()

            return True

        except Exception as e:
            print(f"Failed to write CDC event: {e}")
            return False

    def get_pending_cdc_events(
        self,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get pending CDC events for sync."""
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]
            query = f"""
                (SELECT * FROM {obs_schema}.obs_cdc_tracking
                 WHERE sync_status = 'PENDING'
                 ORDER BY change_timestamp
                 LIMIT {limit}) AS t
            """

            df = self.spark.read.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", query) \
                .options(**self.connection_props) \
                .load()

            return [row.asDict() for row in df.collect()]

        except Exception as e:
            print(f"Failed to get pending CDC events: {e}")
            return []

    def mark_cdc_synced(
        self,
        cdc_ids: List[str],
        target_system: str,
    ) -> bool:
        """Mark CDC events as synced to target system."""
        try:
            if not cdc_ids:
                return True

            obs_schema = self.schemas[Layer.OBSERVABILITY]
            ids_str = ", ".join([f"'{cdc_id}'" for cdc_id in cdc_ids])

            # Update sync status
            update_sql = f"""
                UPDATE {obs_schema}.obs_cdc_tracking
                SET sync_status = 'SYNCED',
                    synced_to = array_append(COALESCE(synced_to, ARRAY[]::text[]), '{target_system}'),
                    last_sync_attempt = CURRENT_TIMESTAMP
                WHERE cdc_id IN ({ids_str})
            """

            self._execute_sql(update_sql)
            return True

        except Exception as e:
            print(f"Failed to mark CDC synced: {e}")
            return False

    # =========================================================================
    # Checkpoint Management
    # =========================================================================
    def save_checkpoint(
        self,
        batch_id: str,
        layer: Layer,
        offset: int,
        partition: Optional[str] = None,
        key: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Save processing checkpoint for restartability."""
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            # Update batch tracking with checkpoint info
            update_sql = f"""
                UPDATE {obs_schema}.obs_batch_tracking
                SET checkpoint_layer = '{layer.value}',
                    checkpoint_offset = {offset},
                    checkpoint_partition = {f"'{partition}'" if partition else "NULL"},
                    checkpoint_key = {f"'{key}'" if key else "NULL"},
                    checkpoint_data = {f"'{json.dumps(data)}'" if data else "NULL"},
                    last_checkpoint_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE batch_id = '{batch_id}'
            """

            self._execute_sql(update_sql)
            return True

        except Exception as e:
            print(f"Failed to save checkpoint: {e}")
            return False

    def get_checkpoint(
        self,
        batch_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get latest checkpoint for a batch."""
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]
            query = f"""
                (SELECT checkpoint_layer, checkpoint_offset, checkpoint_partition,
                        checkpoint_key, checkpoint_data, last_checkpoint_at
                 FROM {obs_schema}.obs_batch_tracking
                 WHERE batch_id = '{batch_id}'
                   AND checkpoint_layer IS NOT NULL) AS t
            """

            df = self.spark.read.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", query) \
                .options(**self.connection_props) \
                .load()

            if df.count() == 0:
                return None

            row = df.collect()[0]
            return {
                "layer": row["checkpoint_layer"],
                "offset": row["checkpoint_offset"],
                "partition": row["checkpoint_partition"],
                "key": row["checkpoint_key"],
                "data": json.loads(row["checkpoint_data"]) if row["checkpoint_data"] else None,
                "timestamp": row["last_checkpoint_at"],
            }

        except Exception as e:
            print(f"Failed to get checkpoint: {e}")
            return None

    def clear_checkpoint(
        self,
        batch_id: str,
    ) -> bool:
        """Clear checkpoint after successful completion."""
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            update_sql = f"""
                UPDATE {obs_schema}.obs_batch_tracking
                SET checkpoint_layer = NULL,
                    checkpoint_offset = 0,
                    checkpoint_partition = NULL,
                    checkpoint_key = NULL,
                    checkpoint_data = NULL,
                    status = 'COMPLETED',
                    completed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE batch_id = '{batch_id}'
            """

            self._execute_sql(update_sql)
            return True

        except Exception as e:
            print(f"Failed to clear checkpoint: {e}")
            return False

    # =========================================================================
    # Batch Management
    # =========================================================================
    def create_batch(
        self,
        batch_id: str,
        source_path: str,
        message_type: str,
        mapping_id: str,
        source_system: Optional[str] = None,
    ) -> bool:
        """Create a new batch tracking record."""
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            record = [{
                "batch_id": batch_id,
                "source_path": source_path,
                "source_system": source_system,
                "mapping_id": mapping_id,
                "message_type": message_type,
                "status": "PENDING",
                "current_layer": "bronze",
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", f"{obs_schema}.obs_batch_tracking") \
                .options(**self.connection_props) \
                .mode("append") \
                .save()

            return True

        except Exception as e:
            print(f"Failed to create batch: {e}")
            return False

    def update_batch_status(
        self,
        batch_id: str,
        status: str,
        current_layer: Optional[str] = None,
        bronze_records: Optional[int] = None,
        silver_records: Optional[int] = None,
        gold_records: Optional[int] = None,
        analytical_records: Optional[int] = None,
        failed_records: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update batch tracking status."""
        try:
            obs_schema = self.schemas[Layer.OBSERVABILITY]

            updates = [f"status = '{status}'", "updated_at = CURRENT_TIMESTAMP"]

            if current_layer:
                updates.append(f"current_layer = '{current_layer}'")
            if bronze_records is not None:
                updates.append(f"bronze_records = {bronze_records}")
                updates.append("bronze_completed_at = CURRENT_TIMESTAMP")
            if silver_records is not None:
                updates.append(f"silver_records = {silver_records}")
                updates.append("silver_completed_at = CURRENT_TIMESTAMP")
            if gold_records is not None:
                updates.append(f"gold_records = {gold_records}")
                updates.append("gold_completed_at = CURRENT_TIMESTAMP")
            if analytical_records is not None:
                updates.append(f"analytical_records = {analytical_records}")
                updates.append("analytical_completed_at = CURRENT_TIMESTAMP")
            if failed_records is not None:
                updates.append(f"failed_records = {failed_records}")
            if error_message:
                updates.append(f"error_message = '{error_message[:4000]}'")
            if status == "PROCESSING":
                updates.append("started_at = COALESCE(started_at, CURRENT_TIMESTAMP)")
            if status == "COMPLETED":
                updates.append("completed_at = CURRENT_TIMESTAMP")

            update_sql = f"""
                UPDATE {obs_schema}.obs_batch_tracking
                SET {", ".join(updates)}
                WHERE batch_id = '{batch_id}'
            """

            self._execute_sql(update_sql)
            return True

        except Exception as e:
            print(f"Failed to update batch status: {e}")
            return False

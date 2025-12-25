"""
GPS CDM - Databricks Community Edition Backend
===============================================

Databricks Community Edition (CE) adapter for local/personal development.
Simpler configuration than full Databricks - no Unity Catalog.

Differences from production Delta Lake:
- Uses DBFS paths instead of Unity Catalog
- No catalog namespacing (uses default catalog)
- Simpler table management
- Works with CE free tier limitations

Usage:
    from gps_cdm.ingestion.persistence import PersistenceFactory

    persistence = PersistenceFactory.create(
        backend="databricks_ce",
        config={
            "storage_path": "/dbfs/cdm",
            "database": "cdm_dev"
        }
    )
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import uuid

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import lit, current_timestamp, col
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, TimestampType
)

from gps_cdm.ingestion.persistence.base import (
    PersistenceBackend,
    PersistenceConfig,
    WriteResult,
    WriteMode,
    Layer,
)


class DatabricksCEBackend(PersistenceBackend):
    """
    Databricks Community Edition persistence backend.

    Implements medallion architecture for Databricks CE:
    - Bronze: Raw data, append-only, stored in DBFS
    - Silver: Cleansed CDM data, merge/upsert
    - Gold: Aggregated analytics, overwrite

    No Unity Catalog - uses Hive metastore and DBFS storage.
    """

    # DDL templates for Delta Lake tables (CE-compatible, no catalog prefix)
    LINEAGE_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {database}.data_lineage (
        lineage_id STRING NOT NULL,
        batch_id STRING NOT NULL,
        source_layer STRING NOT NULL,
        target_layer STRING NOT NULL,
        source_table STRING NOT NULL,
        target_table STRING NOT NULL,
        record_count BIGINT,
        mapping_id STRING,
        field_mappings STRING,
        created_at TIMESTAMP
    )
    USING DELTA
    LOCATION '{storage_path}/observability/data_lineage'
    """

    ERROR_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {database}.processing_errors (
        error_id STRING NOT NULL,
        batch_id STRING NOT NULL,
        layer STRING NOT NULL,
        table_name STRING NOT NULL,
        error_type STRING NOT NULL,
        error_message STRING,
        record_data STRING,
        record_id STRING,
        created_at TIMESTAMP
    )
    USING DELTA
    LOCATION '{storage_path}/observability/processing_errors'
    PARTITIONED BY (layer)
    """

    BATCH_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {database}.batch_tracking (
        batch_id STRING NOT NULL,
        source_path STRING,
        mapping_id STRING,
        status STRING NOT NULL,
        total_records BIGINT,
        processed_records BIGINT,
        failed_records BIGINT,
        checkpoint_offset BIGINT,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        last_checkpoint_at TIMESTAMP,
        error_message STRING,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    USING DELTA
    LOCATION '{storage_path}/observability/batch_tracking'
    """

    def __init__(self, spark: SparkSession, config: PersistenceConfig):
        """Initialize Databricks CE backend."""
        super().__init__(spark, config)

        # CE uses a simpler storage path in DBFS
        self.storage_path = config.storage_path or "/dbfs/cdm"
        self.database = config.database or "cdm_dev"

        # Layer to subdirectory mapping
        self.layer_paths = {
            Layer.BRONZE: f"{self.storage_path}/bronze",
            Layer.SILVER: f"{self.storage_path}/silver",
            Layer.GOLD: f"{self.storage_path}/gold",
            Layer.OBSERVABILITY: f"{self.storage_path}/observability",
        }

    def initialize(self) -> bool:
        """
        Initialize Databricks CE database and tables.

        Creates database and observability tables if they don't exist.
        """
        try:
            # Create database
            self.spark.sql(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.spark.sql(f"USE {self.database}")

            # Create observability tables
            self.spark.sql(self.LINEAGE_TABLE_DDL.format(
                database=self.database, storage_path=self.storage_path
            ))
            self.spark.sql(self.ERROR_TABLE_DDL.format(
                database=self.database, storage_path=self.storage_path
            ))
            self.spark.sql(self.BATCH_TABLE_DDL.format(
                database=self.database, storage_path=self.storage_path
            ))

            self._initialized = True
            return True

        except Exception as e:
            print(f"Databricks CE initialization failed: {e}")
            return False

    def get_table_path(self, layer: Layer, table: str) -> str:
        """Get table location path for CE."""
        layer_path = self.layer_paths.get(layer, self.layer_paths[Layer.SILVER])
        return f"{layer_path}/{table}"

    def get_table_name(self, layer: Layer, table: str) -> str:
        """Get fully qualified table name (database.table)."""
        return f"{self.database}.{layer.value}_{table}"

    def table_exists(self, layer: Layer, table: str) -> bool:
        """Check if Delta table exists."""
        try:
            table_name = self.get_table_name(layer, table)
            self.spark.sql(f"DESCRIBE TABLE {table_name}")
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
        Write DataFrame to Delta Lake table in DBFS.

        Supports append, overwrite, and merge (upsert) modes.
        """
        table_path = self.get_table_path(layer, table)
        table_name = self.get_table_name(layer, table)
        timestamp = datetime.utcnow()

        try:
            # Add metadata columns
            df_with_meta = df.withColumn("_batch_id", lit(batch_id)) \
                             .withColumn("_ingested_at", current_timestamp())

            record_count = df.count()

            if mode == WriteMode.MERGE and merge_keys:
                return self._write_with_merge(
                    df_with_meta, table_name, table_path, batch_id, merge_keys, timestamp
                )

            # Build writer
            writer = df_with_meta.write.format("delta")

            # Add partitioning
            if partition_cols:
                writer = writer.partitionBy(*partition_cols)

            # Set write mode
            if mode == WriteMode.APPEND:
                writer = writer.mode("append")
            elif mode == WriteMode.OVERWRITE:
                writer = writer.mode("overwrite").option("overwriteSchema", "true")
            elif mode == WriteMode.ERROR_IF_EXISTS:
                writer = writer.mode("error")

            # Write to path and create table reference
            writer.option("path", table_path).saveAsTable(table_name)

            return WriteResult(
                success=True,
                layer=layer,
                table=table,
                records_written=record_count,
                batch_id=batch_id,
                timestamp=timestamp,
                metadata={
                    "table_name": table_name,
                    "table_path": table_path,
                    "mode": mode.value,
                    "partition_cols": partition_cols
                }
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
        table_name: str,
        table_path: str,
        batch_id: str,
        merge_keys: List[str],
        timestamp: datetime
    ) -> WriteResult:
        """
        Implement upsert using Delta Lake MERGE for CE.
        """
        try:
            record_count = df.count()

            # Check if table exists, create if not
            try:
                self.spark.sql(f"DESCRIBE TABLE {table_name}")
            except Exception:
                # First write - just save
                df.write.format("delta") \
                    .mode("overwrite") \
                    .option("path", table_path) \
                    .saveAsTable(table_name)

                return WriteResult(
                    success=True,
                    layer=Layer.SILVER,
                    table=table_name.split(".")[-1],
                    records_written=record_count,
                    batch_id=batch_id,
                    timestamp=timestamp,
                    metadata={"mode": "initial_create", "merge_keys": merge_keys}
                )

            # Create temp view for merge
            temp_view = f"_temp_merge_{batch_id.replace('-', '_')[:8]}"
            df.createOrReplaceTempView(temp_view)

            # Build merge condition
            merge_condition = " AND ".join([
                f"target.{k} = source.{k}" for k in merge_keys
            ])

            # Build update set
            update_cols = [c for c in df.columns if c not in merge_keys]
            update_set = ", ".join([f"target.{c} = source.{c}" for c in update_cols])

            # Build insert columns
            all_cols = df.columns
            insert_cols = ", ".join(all_cols)
            insert_vals = ", ".join([f"source.{c}" for c in all_cols])

            # Execute merge
            merge_sql = f"""
            MERGE INTO {table_name} AS target
            USING {temp_view} AS source
            ON {merge_condition}
            WHEN MATCHED THEN UPDATE SET {update_set}
            WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
            """

            self.spark.sql(merge_sql)

            return WriteResult(
                success=True,
                layer=Layer.SILVER,
                table=table_name.split(".")[-1],
                records_written=record_count,
                batch_id=batch_id,
                timestamp=timestamp,
                metadata={"mode": "merge", "merge_keys": merge_keys}
            )

        except Exception as e:
            return WriteResult(
                success=False,
                layer=Layer.SILVER,
                table=table_name.split(".")[-1],
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
        Read data from Delta Lake in CE.
        """
        table_name = self.get_table_name(layer, table)

        df = self.spark.read.format("delta").table(table_name)

        if columns:
            df = df.select(*columns)

        if filter_expr:
            df = df.filter(filter_expr)

        return df

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
        """Write lineage record to observability table."""
        try:
            lineage_id = str(uuid.uuid4())
            table_name = f"{self.database}.data_lineage"

            record = [{
                "lineage_id": lineage_id,
                "batch_id": batch_id,
                "source_layer": source_layer.value,
                "target_layer": target_layer.value,
                "source_table": source_table,
                "target_table": target_table,
                "record_count": record_count,
                "mapping_id": mapping_id,
                "field_mappings": json.dumps(field_mappings or {}),
                "created_at": datetime.utcnow(),
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("delta").mode("append").saveAsTable(table_name)

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
        """Write error record to observability table."""
        try:
            error_id = str(uuid.uuid4())
            table_name = f"{self.database}.processing_errors"

            record = [{
                "error_id": error_id,
                "batch_id": batch_id,
                "layer": layer.value,
                "table_name": table,
                "error_type": error_type,
                "error_message": error_message[:4000] if error_message else None,
                "record_data": record_data,
                "record_id": record_id,
                "created_at": datetime.utcnow(),
            }]

            df = self.spark.createDataFrame(record)
            df.write.format("delta").mode("append").saveAsTable(table_name)

            return True

        except Exception as e:
            print(f"Failed to write error: {e}")
            return False

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get batch status from tracking table."""
        try:
            table_name = f"{self.database}.batch_tracking"

            df = self.spark.sql(f"""
                SELECT * FROM {table_name}
                WHERE batch_id = '{batch_id}'
            """)

            if df.count() == 0:
                return {"batch_id": batch_id, "status": "NOT_FOUND"}

            row = df.collect()[0]
            return row.asDict()

        except Exception as e:
            return {"batch_id": batch_id, "status": "ERROR", "error": str(e)}

    def update_batch_status(
        self,
        batch_id: str,
        status: str,
        processed_records: Optional[int] = None,
        failed_records: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update batch tracking status."""
        try:
            table_name = f"{self.database}.batch_tracking"
            now = datetime.utcnow().isoformat()

            updates = [f"status = '{status}'", f"updated_at = '{now}'"]
            if processed_records is not None:
                updates.append(f"processed_records = {processed_records}")
            if failed_records is not None:
                updates.append(f"failed_records = {failed_records}")
            if error_message:
                updates.append(f"error_message = '{error_message[:4000]}'")
            if status in ("COMPLETED", "FAILED"):
                updates.append(f"completed_at = '{now}'")

            update_sql = f"""
            UPDATE {table_name}
            SET {', '.join(updates)}
            WHERE batch_id = '{batch_id}'
            """

            self.spark.sql(update_sql)
            return True

        except Exception as e:
            print(f"Failed to update batch status: {e}")
            return False

    # Delta-specific methods for CE
    def time_travel(
        self,
        layer: Layer,
        table: str,
        version: Optional[int] = None,
        timestamp: Optional[str] = None,
    ) -> DataFrame:
        """Read historical version using Delta time travel."""
        table_name = self.get_table_name(layer, table)

        if version is not None:
            return self.spark.read.format("delta") \
                .option("versionAsOf", version) \
                .table(table_name)
        elif timestamp:
            return self.spark.read.format("delta") \
                .option("timestampAsOf", timestamp) \
                .table(table_name)
        else:
            return self.read(layer, table)

    def get_table_history(self, layer: Layer, table: str, limit: int = 10) -> DataFrame:
        """Get version history for a Delta table."""
        table_name = self.get_table_name(layer, table)
        return self.spark.sql(f"DESCRIBE HISTORY {table_name} LIMIT {limit}")

    def optimize_table(self, layer: Layer, table: str):
        """Optimize a Delta table (compact small files)."""
        table_name = self.get_table_name(layer, table)
        self.spark.sql(f"OPTIMIZE {table_name}")

    def vacuum_table(self, layer: Layer, table: str, retention_hours: int = 168):
        """Clean up old files from Delta table."""
        table_name = self.get_table_name(layer, table)
        self.spark.sql(f"VACUUM {table_name} RETAIN {retention_hours} HOURS")


# Convenience function
def create_databricks_ce_backend(
    spark: SparkSession,
    storage_path: str = "/dbfs/cdm",
    database: str = "cdm_dev"
) -> DatabricksCEBackend:
    """
    Quick setup for Databricks CE backend.

    Args:
        spark: Active SparkSession
        storage_path: DBFS path for data storage
        database: Database name in Hive metastore

    Returns:
        Initialized DatabricksCEBackend

    Example (in Databricks notebook):
        from gps_cdm.ingestion.persistence.databricks_ce import create_databricks_ce_backend

        backend = create_databricks_ce_backend(spark)
        backend.initialize()
    """
    config = PersistenceConfig(
        backend="databricks_ce",
        storage_path=storage_path,
        database=database
    )
    backend = DatabricksCEBackend(spark, config)
    backend.initialize()
    return backend

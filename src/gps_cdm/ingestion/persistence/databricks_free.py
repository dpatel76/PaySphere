"""
GPS CDM - Databricks Free Edition Backend
==========================================

Databricks Free Edition adapter for personal learning and development.
Uses Unity Catalog and Volumes (not DBFS which is not supported in Free Edition).

Key differences from Community Edition:
- Serverless compute (no cluster management)
- Unity Catalog with Volumes for storage
- No DBFS, no classic compute, no Scala
- Daily usage limits (generous for learning)

Usage:
    from gps_cdm.ingestion.persistence import PersistenceFactory

    persistence = PersistenceFactory.create(
        backend="databricks_free",
        config={
            "catalog": "main",
            "schema": "cdm_dev",
            "volume_path": "/Volumes/main/cdm_dev/data"
        }
    )

Reference:
    https://www.databricks.com/product/faq/community-edition
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


class DatabricksFreeBackend(PersistenceBackend):
    """
    Databricks Free Edition persistence backend.

    Uses Unity Catalog for table management and Volumes for file storage.
    Designed for serverless compute environment.

    Implements medallion architecture:
    - Bronze: Raw data, append-only
    - Silver: Cleansed CDM data, merge/upsert
    - Gold: Aggregated analytics, overwrite
    """

    # DDL templates using Unity Catalog (catalog.schema.table format)
    LINEAGE_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.{schema}.obs_data_lineage (
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
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
    """

    ERROR_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.{schema}.obs_processing_errors (
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
    PARTITIONED BY (layer)
    """

    BATCH_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.{schema}.obs_batch_tracking (
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
    """

    def __init__(self, spark: SparkSession, config: PersistenceConfig):
        """Initialize Databricks Free Edition backend."""
        super().__init__(spark, config)

        # Unity Catalog naming
        self.catalog = config.catalog or "main"
        self.schema = config.schema or config.database or "cdm_dev"

        # Volume path for file storage (replaces DBFS)
        self.volume_path = config.volume_path or f"/Volumes/{self.catalog}/{self.schema}/data"

        # Layer prefixes for table naming
        self.layer_prefixes = {
            Layer.BRONZE: "bronze",
            Layer.SILVER: "silver",
            Layer.GOLD: "gold",
            Layer.OBSERVABILITY: "obs",
        }

    def initialize(self) -> bool:
        """
        Initialize Unity Catalog schema and tables.

        Creates catalog (if permitted), schema, volume, and observability tables.
        """
        try:
            # Note: Creating catalogs may require admin permissions
            # In Free Edition, typically use the default "main" catalog
            try:
                self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog}")
            except Exception:
                pass  # May not have permission, use existing catalog

            # Create schema
            self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}")

            # Create volume for file storage
            try:
                self.spark.sql(f"""
                    CREATE VOLUME IF NOT EXISTS {self.catalog}.{self.schema}.data
                    COMMENT 'GPS CDM data storage volume'
                """)
            except Exception:
                pass  # Volume may already exist

            # Create observability tables
            self.spark.sql(self.LINEAGE_TABLE_DDL.format(
                catalog=self.catalog, schema=self.schema
            ))
            self.spark.sql(self.ERROR_TABLE_DDL.format(
                catalog=self.catalog, schema=self.schema
            ))
            self.spark.sql(self.BATCH_TABLE_DDL.format(
                catalog=self.catalog, schema=self.schema
            ))

            self._initialized = True
            return True

        except Exception as e:
            print(f"Databricks Free Edition initialization failed: {e}")
            return False

    def get_table_name(self, layer: Layer, table: str) -> str:
        """Get fully qualified table name (catalog.schema.prefix_table)."""
        prefix = self.layer_prefixes.get(layer, "")
        table_name = f"{prefix}_{table}" if prefix else table
        return f"{self.catalog}.{self.schema}.{table_name}"

    def get_volume_path(self, layer: Layer, subdir: str = "") -> str:
        """Get volume path for file storage."""
        layer_name = layer.value if hasattr(layer, 'value') else str(layer)
        if subdir:
            return f"{self.volume_path}/{layer_name}/{subdir}"
        return f"{self.volume_path}/{layer_name}"

    def table_exists(self, layer: Layer, table: str) -> bool:
        """Check if Delta table exists."""
        try:
            full_table = self.get_table_name(layer, table)
            self.spark.sql(f"DESCRIBE TABLE {full_table}")
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
        Write DataFrame to Delta Lake table via Unity Catalog.

        Supports append, overwrite, and merge (upsert) modes.
        """
        full_table = self.get_table_name(layer, table)
        timestamp = datetime.utcnow()

        try:
            # Add metadata columns
            df_with_meta = df.withColumn("_batch_id", lit(batch_id)) \
                             .withColumn("_ingested_at", current_timestamp())

            record_count = df.count()

            if mode == WriteMode.MERGE and merge_keys:
                return self._write_with_merge(
                    df_with_meta, full_table, batch_id, merge_keys, timestamp
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

            # Write to managed table in Unity Catalog
            writer.saveAsTable(full_table)

            return WriteResult(
                success=True,
                layer=layer,
                table=table,
                records_written=record_count,
                batch_id=batch_id,
                timestamp=timestamp,
                metadata={
                    "full_table": full_table,
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
        full_table: str,
        batch_id: str,
        merge_keys: List[str],
        timestamp: datetime
    ) -> WriteResult:
        """Implement upsert using Delta Lake MERGE."""
        try:
            record_count = df.count()

            # Check if table exists
            try:
                self.spark.sql(f"DESCRIBE TABLE {full_table}")
            except Exception:
                # First write - just create table
                df.write.format("delta").mode("overwrite").saveAsTable(full_table)
                return WriteResult(
                    success=True,
                    layer=Layer.SILVER,
                    table=full_table.split(".")[-1],
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

            # Build insert
            all_cols = df.columns
            insert_cols = ", ".join(all_cols)
            insert_vals = ", ".join([f"source.{c}" for c in all_cols])

            # Execute merge
            merge_sql = f"""
            MERGE INTO {full_table} AS target
            USING {temp_view} AS source
            ON {merge_condition}
            WHEN MATCHED THEN UPDATE SET {update_set}
            WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
            """

            self.spark.sql(merge_sql)

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
        """Read data from Delta Lake table."""
        full_table = self.get_table_name(layer, table)

        df = self.spark.read.format("delta").table(full_table)

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
        """Write lineage record."""
        try:
            lineage_id = str(uuid.uuid4())
            full_table = f"{self.catalog}.{self.schema}.obs_data_lineage"

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
            df.write.format("delta").mode("append").saveAsTable(full_table)

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
        """Write error record."""
        try:
            error_id = str(uuid.uuid4())
            full_table = f"{self.catalog}.{self.schema}.obs_processing_errors"

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
            df.write.format("delta").mode("append").saveAsTable(full_table)

            return True

        except Exception as e:
            print(f"Failed to write error: {e}")
            return False

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get batch status from tracking table."""
        try:
            full_table = f"{self.catalog}.{self.schema}.obs_batch_tracking"

            df = self.spark.sql(f"""
                SELECT * FROM {full_table}
                WHERE batch_id = '{batch_id}'
            """)

            if df.count() == 0:
                return {"batch_id": batch_id, "status": "NOT_FOUND"}

            row = df.collect()[0]
            return row.asDict()

        except Exception as e:
            return {"batch_id": batch_id, "status": "ERROR", "error": str(e)}

    # Delta Lake features
    def time_travel(
        self,
        layer: Layer,
        table: str,
        version: Optional[int] = None,
        timestamp: Optional[str] = None,
    ) -> DataFrame:
        """Read historical version using Delta time travel."""
        full_table = self.get_table_name(layer, table)

        if version is not None:
            return self.spark.read.format("delta") \
                .option("versionAsOf", version) \
                .table(full_table)
        elif timestamp:
            return self.spark.read.format("delta") \
                .option("timestampAsOf", timestamp) \
                .table(full_table)
        else:
            return self.read(layer, table)

    def get_table_history(self, layer: Layer, table: str, limit: int = 10) -> DataFrame:
        """Get version history for a Delta table."""
        full_table = self.get_table_name(layer, table)
        return self.spark.sql(f"DESCRIBE HISTORY {full_table} LIMIT {limit}")

    def optimize_table(self, layer: Layer, table: str):
        """Optimize a Delta table."""
        full_table = self.get_table_name(layer, table)
        self.spark.sql(f"OPTIMIZE {full_table}")


# Convenience function
def create_databricks_free_backend(
    spark: SparkSession,
    catalog: str = "main",
    schema: str = "cdm_dev"
) -> DatabricksFreeBackend:
    """
    Quick setup for Databricks Free Edition backend.

    Args:
        spark: Active SparkSession (provided by Databricks)
        catalog: Unity Catalog name (default: "main")
        schema: Schema name (default: "cdm_dev")

    Returns:
        Initialized DatabricksFreeBackend

    Example (in Databricks notebook):
        from gps_cdm.ingestion.persistence.databricks_free import create_databricks_free_backend

        backend = create_databricks_free_backend(spark)
    """
    config = PersistenceConfig(
        backend="databricks_free",
        catalog=catalog,
        schema=schema
    )
    backend = DatabricksFreeBackend(spark, config)
    backend.initialize()
    return backend

"""
GPS CDM - Delta Lake Persistence Backend
========================================

Delta Lake adapter for Databricks production.
Implements the same interface as PostgreSQL for seamless deployment.

Features:
- Unity Catalog integration
- ACID transactions
- Time travel
- Schema evolution
- Partition optimization
- Z-ordering

Usage:
    from gps_cdm.ingestion.persistence import PersistenceFactory

    persistence = PersistenceFactory.create(
        backend="delta",
        config={
            "catalog": "cdm_prod",
            "storage_path": "abfss://container@account.dfs.core.windows.net/cdm",
            "unity_catalog": True
        }
    )
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import uuid

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import lit, current_timestamp, col

from gps_cdm.ingestion.persistence.base import (
    PersistenceBackend,
    PersistenceConfig,
    WriteResult,
    WriteMode,
    Layer,
)


class DeltaLakeBackend(PersistenceBackend):
    """
    Delta Lake persistence backend for Databricks production.

    Implements medallion architecture with:
    - Bronze: Raw data, append-only
    - Silver: Cleansed CDM data, merge/upsert
    - Gold: Aggregated analytics, overwrite

    Supports Unity Catalog for governance and lineage.
    """

    # DDL templates for Delta Lake tables
    LINEAGE_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.{schema}.data_lineage (
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
    PARTITIONED BY (target_layer)
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
    """

    ERROR_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.{schema}.processing_errors (
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
    PARTITIONED BY (layer, date(created_at))
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true'
    )
    """

    BATCH_TABLE_DDL = """
    CREATE TABLE IF NOT EXISTS {catalog}.{schema}.batch_tracking (
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
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true'
    )
    """

    def __init__(self, spark: SparkSession, config: PersistenceConfig):
        """Initialize Delta Lake backend."""
        super().__init__(spark, config)

        self.catalog = config.catalog
        self.storage_path = config.storage_path
        self.unity_catalog = config.unity_catalog

        # Schema/database names
        self.schemas = {
            Layer.BRONZE: config.bronze_schema,
            Layer.SILVER: config.silver_schema,
            Layer.GOLD: config.gold_schema,
            Layer.OBSERVABILITY: config.observability_schema,
        }

    def initialize(self) -> bool:
        """
        Initialize Delta Lake schemas and tables.

        Creates catalog, schemas, and observability tables if they don't exist.
        """
        try:
            # Create catalog if using Unity Catalog
            if self.unity_catalog:
                self.spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog}")
                self.spark.sql(f"USE CATALOG {self.catalog}")

            # Create schemas
            for layer, schema in self.schemas.items():
                self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{schema}")

            # Create observability tables
            obs_schema = self.schemas[Layer.OBSERVABILITY]
            self.spark.sql(self.LINEAGE_TABLE_DDL.format(
                catalog=self.catalog, schema=obs_schema
            ))
            self.spark.sql(self.ERROR_TABLE_DDL.format(
                catalog=self.catalog, schema=obs_schema
            ))
            self.spark.sql(self.BATCH_TABLE_DDL.format(
                catalog=self.catalog, schema=obs_schema
            ))

            self._initialized = True
            return True

        except Exception as e:
            print(f"Delta Lake initialization failed: {e}")
            return False

    def get_table_path(self, layer: Layer, table: str) -> str:
        """Get full table name with catalog and schema."""
        schema = self.schemas.get(layer, self.schemas[Layer.SILVER])
        return f"{self.catalog}.{schema}.{table}"

    def table_exists(self, layer: Layer, table: str) -> bool:
        """Check if Delta table exists."""
        try:
            full_table = self.get_table_path(layer, table)
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
        Write DataFrame to Delta Lake table.

        Supports append, overwrite, and merge (upsert) modes.
        Automatically adds metadata columns for lineage.
        """
        full_table = self.get_table_path(layer, table)
        timestamp = datetime.utcnow()

        try:
            # Add metadata columns
            df_with_meta = df.withColumn("_batch_id", lit(batch_id)) \
                             .withColumn("_ingested_at", current_timestamp())

            record_count = df.count()

            if mode == WriteMode.MERGE and merge_keys:
                # Use Delta Lake MERGE
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

            # Write to table
            writer.saveAsTable(full_table)

            # Optimize for Bronze/Silver (not Gold which is smaller)
            if layer in (Layer.BRONZE, Layer.SILVER) and record_count > 100000:
                self._optimize_table(full_table, partition_cols)

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
        """
        Implement upsert using Delta Lake MERGE.

        This is the most efficient way to do upserts in Delta Lake.
        """
        try:
            record_count = df.count()

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

    def _optimize_table(self, full_table: str, partition_cols: Optional[List[str]] = None):
        """
        Optimize Delta table for query performance.

        Runs OPTIMIZE and Z-ORDER on large tables.
        """
        try:
            self.spark.sql(f"OPTIMIZE {full_table}")

            # Z-order by partition columns if specified
            if partition_cols:
                zorder_cols = ", ".join(partition_cols[:3])  # Max 3 columns
                self.spark.sql(f"OPTIMIZE {full_table} ZORDER BY ({zorder_cols})")

        except Exception:
            pass  # Optimization is best-effort

    def read(
        self,
        layer: Layer,
        table: str,
        columns: Optional[List[str]] = None,
        filter_expr: Optional[str] = None,
    ) -> DataFrame:
        """
        Read data from Delta Lake.

        Supports column selection and filter pushdown.
        """
        full_table = self.get_table_path(layer, table)

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
        """Write lineage record to Delta Lake."""
        try:
            lineage_id = str(uuid.uuid4())
            full_table = self.get_table_path(Layer.OBSERVABILITY, "data_lineage")

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
        """Write error record to Delta Lake."""
        try:
            error_id = str(uuid.uuid4())
            full_table = self.get_table_path(Layer.OBSERVABILITY, "processing_errors")

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
            full_table = self.get_table_path(Layer.OBSERVABILITY, "batch_tracking")

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

    # Delta-specific methods
    def time_travel(
        self,
        layer: Layer,
        table: str,
        version: Optional[int] = None,
        timestamp: Optional[str] = None,
    ) -> DataFrame:
        """
        Read historical version of a table using Delta time travel.

        Args:
            layer: Data layer
            table: Table name
            version: Specific version number
            timestamp: Timestamp string (e.g., "2024-01-15")

        Returns:
            DataFrame at specified point in time
        """
        full_table = self.get_table_path(layer, table)

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
        full_table = self.get_table_path(layer, table)
        return self.spark.sql(f"DESCRIBE HISTORY {full_table} LIMIT {limit}")

    def vacuum_table(self, layer: Layer, table: str, retention_hours: int = 168):
        """
        Clean up old files from Delta table.

        Args:
            layer: Data layer
            table: Table name
            retention_hours: Hours to retain (default 7 days)
        """
        full_table = self.get_table_path(layer, table)
        self.spark.sql(f"VACUUM {full_table} RETAIN {retention_hours} HOURS")

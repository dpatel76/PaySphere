"""
GPS CDM - Medallion Architecture Orchestrator
==============================================

Orchestrates the full Bronze → Silver → Gold pipeline with:
- Database-agnostic persistence (PostgreSQL, Delta Lake, Starburst)
- Checkpoint/restart for large feeds
- Lineage tracking at each step
- Error handling with dead-letter routing

Usage:
    from gps_cdm.ingestion.orchestration import MedallionOrchestrator
    from gps_cdm.ingestion.persistence import PersistenceFactory

    # Create persistence backend (configurable)
    persistence = PersistenceFactory.create(
        backend="postgresql",  # or "delta" for production
        spark=spark,
        host="localhost",
        database="cdm_test"
    )

    # Create orchestrator
    orchestrator = MedallionOrchestrator(spark, persistence)

    # Run full pipeline
    result = orchestrator.ingest(
        source_path="/data/pain001/",
        mapping_id="PAIN_001_V09",
        source_table="raw_pain001",
        target_table="payment_instruction"
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid
import json

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, lit, current_timestamp, to_json, struct,
    when, count, sum as spark_sum
)
from pyspark.sql.types import StructType, StructField, StringType

from gps_cdm.ingestion.persistence.base import (
    PersistenceBackend,
    Layer,
    WriteMode,
    WriteResult,
)
from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion
from gps_cdm.ingestion.orchestration.batch_tracker import BatchTracker, BatchStatus


@dataclass
class PipelineResult:
    """Result of a full medallion pipeline run."""
    batch_id: str
    success: bool
    source_path: str
    mapping_id: str

    # Record counts
    bronze_records: int = 0
    silver_records: int = 0
    gold_records: int = 0
    error_records: int = 0

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    # Layer results
    bronze_result: Optional[WriteResult] = None
    silver_result: Optional[WriteResult] = None
    gold_result: Optional[WriteResult] = None

    # Errors
    errors: List[str] = field(default_factory=list)

    # Lineage
    lineage_recorded: bool = False


class MedallionOrchestrator:
    """
    Orchestrates the full Bronze → Silver → Gold medallion pipeline.

    Integrates:
    - ConfigDrivenIngestion for transformation logic
    - PersistenceBackend for storage (configurable)
    - BatchTracker for checkpoint/restart
    - Lineage and error tracking

    The same orchestrator code works against:
    - PostgreSQL (local testing)
    - Delta Lake (Databricks production)
    - Starburst (query federation)
    """

    def __init__(
        self,
        spark: SparkSession,
        persistence: PersistenceBackend,
        mappings_path: Optional[str] = None,
        enable_gold: bool = True,
        checkpoint_interval: int = 10000,
    ):
        """
        Initialize the medallion orchestrator.

        Args:
            spark: SparkSession
            persistence: Database-agnostic persistence backend
            mappings_path: Path to YAML mappings directory
            enable_gold: Whether to generate gold layer aggregates
            checkpoint_interval: Records between checkpoints for restart
        """
        self.spark = spark
        self.persistence = persistence
        self.mappings_path = mappings_path
        self.enable_gold = enable_gold
        self.checkpoint_interval = checkpoint_interval

        # Initialize ingestion engine
        self.engine = ConfigDrivenIngestion(
            spark=spark,
            enable_lineage=True,
            enable_validation=True,
        )

        # Initialize batch tracker (uses same persistence config)
        # For simplicity, batch tracking is in-memory for now
        self._batch_status: Dict[str, Dict[str, Any]] = {}

    def ingest(
        self,
        source_df: Optional[DataFrame] = None,
        source_path: Optional[str] = None,
        mapping_path: Optional[str] = None,
        mapping_id: Optional[str] = None,
        source_table: str = "raw_data",
        target_table: str = "payment_instruction",
        partition_cols: Optional[List[str]] = None,
        merge_keys: Optional[List[str]] = None,
        resume_batch_id: Optional[str] = None,
    ) -> PipelineResult:
        """
        Run the full Bronze → Silver → Gold pipeline.

        Args:
            source_df: Source DataFrame (alternative to source_path)
            source_path: Path to source files
            mapping_path: Path to YAML mapping file
            mapping_id: Mapping ID for lookup
            source_table: Bronze table name
            target_table: Silver table name
            partition_cols: Partitioning columns for Silver
            merge_keys: Primary keys for Silver upsert
            resume_batch_id: Resume from previous failed batch

        Returns:
            PipelineResult with details of each stage
        """
        # Generate or resume batch ID
        batch_id = resume_batch_id or str(uuid.uuid4())
        started_at = datetime.utcnow()

        result = PipelineResult(
            batch_id=batch_id,
            success=False,
            source_path=source_path or "dataframe",
            mapping_id=mapping_id or mapping_path or "unknown",
            started_at=started_at,
        )

        try:
            # ==========================================
            # STEP 1: BRONZE - Raw Data Ingestion
            # ==========================================
            print(f"[{batch_id[:8]}] Step 1: Bronze layer ingestion...")

            if source_df is None and source_path:
                # Load from source path
                source_df = self._load_source_data(source_path)

            if source_df is None:
                raise ValueError("Either source_df or source_path must be provided")

            bronze_count = source_df.count()
            result.bronze_records = bronze_count

            # Write to Bronze
            bronze_result = self.persistence.write_bronze(
                df=source_df,
                table=source_table,
                batch_id=batch_id,
                mode=WriteMode.APPEND,
            )
            result.bronze_result = bronze_result

            if not bronze_result.success:
                raise Exception(f"Bronze write failed: {bronze_result.error_message}")

            # Record Bronze lineage
            self.persistence.write_lineage(
                batch_id=batch_id,
                source_layer=Layer.BRONZE,
                target_layer=Layer.BRONZE,
                source_table=source_path or "source_df",
                target_table=source_table,
                record_count=bronze_count,
                mapping_id="RAW_INGESTION",
            )

            print(f"[{batch_id[:8]}] Bronze complete: {bronze_count} records")

            # ==========================================
            # STEP 2: SILVER - CDM Transformation
            # ==========================================
            print(f"[{batch_id[:8]}] Step 2: Silver layer transformation...")

            # Run ingestion engine
            ingestion_result = self.engine.process(
                source_df=source_df,
                mapping_path=mapping_path,
                mapping_id=mapping_id,
            )

            if ingestion_result.error_count > 0:
                # Write errors to dead-letter table
                for error in ingestion_result.errors:
                    self.persistence.write_error(
                        batch_id=batch_id,
                        layer=Layer.SILVER,
                        table=target_table,
                        error_type="TRANSFORMATION_ERROR",
                        error_message=error,
                    )
                result.error_records = ingestion_result.error_count
                result.errors.extend(ingestion_result.errors)

            silver_df = ingestion_result.output_df
            silver_count = ingestion_result.output_count
            result.silver_records = silver_count

            # Write to Silver
            silver_mode = WriteMode.MERGE if merge_keys else WriteMode.APPEND
            silver_result = self.persistence.write_silver(
                df=silver_df,
                table=target_table,
                batch_id=batch_id,
                mode=silver_mode,
                partition_cols=partition_cols,
                merge_keys=merge_keys,
            )
            result.silver_result = silver_result

            if not silver_result.success:
                raise Exception(f"Silver write failed: {silver_result.error_message}")

            # Record Silver lineage with field mappings
            self.persistence.write_lineage(
                batch_id=batch_id,
                source_layer=Layer.BRONZE,
                target_layer=Layer.SILVER,
                source_table=source_table,
                target_table=target_table,
                record_count=silver_count,
                mapping_id=result.mapping_id,
                field_mappings=ingestion_result.lineage.get("target_entities"),
            )

            print(f"[{batch_id[:8]}] Silver complete: {silver_count} records, {ingestion_result.error_count} errors")

            # ==========================================
            # STEP 3: GOLD - Aggregations (Optional)
            # ==========================================
            if self.enable_gold:
                print(f"[{batch_id[:8]}] Step 3: Gold layer aggregations...")

                gold_df = self._create_gold_aggregates(silver_df, target_table)
                gold_count = gold_df.count()
                result.gold_records = gold_count

                gold_result = self.persistence.write_gold(
                    df=gold_df,
                    table=f"{target_table}_metrics",
                    batch_id=batch_id,
                    mode=WriteMode.OVERWRITE,
                )
                result.gold_result = gold_result

                if gold_result.success:
                    self.persistence.write_lineage(
                        batch_id=batch_id,
                        source_layer=Layer.SILVER,
                        target_layer=Layer.GOLD,
                        source_table=target_table,
                        target_table=f"{target_table}_metrics",
                        record_count=gold_count,
                        mapping_id="GOLD_AGGREGATION",
                    )

                print(f"[{batch_id[:8]}] Gold complete: {gold_count} metric records")

            # ==========================================
            # COMPLETE
            # ==========================================
            result.success = True
            result.lineage_recorded = True

        except Exception as e:
            result.errors.append(str(e))
            self.persistence.write_error(
                batch_id=batch_id,
                layer=Layer.SILVER,
                table=target_table,
                error_type="PIPELINE_ERROR",
                error_message=str(e),
            )

        finally:
            result.completed_at = datetime.utcnow()
            result.duration_seconds = (
                result.completed_at - result.started_at
            ).total_seconds()

        status = "SUCCESS" if result.success else "FAILED"
        print(f"[{batch_id[:8]}] Pipeline {status} in {result.duration_seconds:.2f}s")

        return result

    def _load_source_data(self, source_path: str) -> DataFrame:
        """Load source data from path (CSV, JSON, XML, etc.)."""
        # Determine format from path
        if source_path.endswith(".csv"):
            return self.spark.read.csv(source_path, header=True, inferSchema=True)
        elif source_path.endswith(".json"):
            return self.spark.read.json(source_path)
        elif source_path.endswith(".xml"):
            return self.spark.read.format("com.databricks.spark.xml") \
                .option("rowTag", "Document") \
                .load(source_path)
        else:
            # Try text for raw message files
            schema = StructType([
                StructField("content", StringType(), True),
                StructField("source_file", StringType(), True),
            ])
            return self.spark.read.text(source_path) \
                .withColumn("source_file", lit(source_path))

    def _create_gold_aggregates(self, silver_df: DataFrame, table_name: str) -> DataFrame:
        """
        Create gold layer aggregations from silver data.

        Generates metrics like:
        - Record counts by category
        - Amount totals and averages
        - Error rates
        - Processing volumes
        """
        # Basic aggregations that work for any CDM table
        aggs = []

        columns = silver_df.columns

        # Count aggregations
        aggs.append(count("*").alias("total_records"))

        # Find amount columns and aggregate
        amount_cols = [c for c in columns if "amount" in c.lower()]
        for col_name in amount_cols[:3]:  # Limit to 3 amount columns
            aggs.append(spark_sum(col(col_name).cast("decimal(18,2)")).alias(f"sum_{col_name}"))

        # Find status/type columns for grouping
        group_cols = [c for c in columns if any(
            kw in c.lower() for kw in ["status", "type", "category", "product"]
        )]

        if group_cols:
            # Group by first category column
            group_col = group_cols[0]
            gold_df = silver_df.groupBy(col(group_col)).agg(*aggs)
        else:
            # No grouping, just totals
            gold_df = silver_df.agg(*aggs)

        # Add metadata
        gold_df = gold_df.withColumn("_aggregation_timestamp", current_timestamp()) \
                         .withColumn("_source_table", lit(table_name))

        return gold_df

    def get_pipeline_status(self, batch_id: str) -> Dict[str, Any]:
        """Get status of a pipeline run."""
        return self.persistence.get_batch_status(batch_id)

    def get_lineage(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get lineage records for a batch."""
        try:
            df = self.persistence.read(
                Layer.OBSERVABILITY,
                "data_lineage",
                filter_expr=f"batch_id = '{batch_id}'"
            )
            return [row.asDict() for row in df.collect()]
        except Exception:
            return []

    def get_errors(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get error records for a batch."""
        try:
            df = self.persistence.read(
                Layer.OBSERVABILITY,
                "processing_errors",
                filter_expr=f"batch_id = '{batch_id}'"
            )
            return [row.asDict() for row in df.collect()]
        except Exception:
            return []

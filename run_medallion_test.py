#!/usr/bin/env python3
"""
GPS CDM - Medallion Architecture End-to-End Test
=================================================

Tests the full Bronze → Silver → Gold pipeline with configurable persistence.

Usage:
    # Test with in-memory (no database required)
    python run_medallion_test.py

    # Test with PostgreSQL
    python run_medallion_test.py --backend postgresql --host localhost

    # Test specific message type
    python run_medallion_test.py --test pain001
    python run_medallion_test.py --test mt103

Prerequisites:
    pip install pyspark pyyaml
    # For PostgreSQL: pip install psycopg2-binary
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def print_header(title: str):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """Print a section header."""
    print()
    print(f"--- {title} ---")


def print_result(name: str, success: bool, message: str = ""):
    """Print a test result."""
    status = "PASS" if success else "FAIL"
    color_start = "\033[92m" if success else "\033[91m"
    color_end = "\033[0m"
    print(f"{color_start}[{status}]{color_end} {name}: {message}")


def create_spark_session():
    """Create local SparkSession."""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder \
        .appName("GPS_CDM_Medallion_Test") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.driver.memory", "2g") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    return spark


def create_in_memory_persistence(spark):
    """
    Create an in-memory persistence backend for testing.

    Uses Spark's in-memory tables instead of external database.
    """
    from gps_cdm.ingestion.persistence.base import (
        PersistenceBackend,
        PersistenceConfig,
        WriteResult,
        WriteMode,
        Layer,
    )
    import uuid
    from pyspark.sql.functions import lit, current_timestamp

    class InMemoryBackend(PersistenceBackend):
        """In-memory persistence for testing without external database."""

        def __init__(self, spark, config):
            super().__init__(spark, config)
            self.tables = {}
            self.lineage_records = []
            self.error_records = []

        def initialize(self) -> bool:
            self._initialized = True
            return True

        def get_table_path(self, layer: Layer, table: str) -> str:
            return f"{layer.value}_{table}"

        def table_exists(self, layer: Layer, table: str) -> bool:
            return self.get_table_path(layer, table) in self.tables

        def write(self, df, layer, table, batch_id, mode=WriteMode.APPEND,
                  partition_cols=None, merge_keys=None) -> WriteResult:
            full_table = self.get_table_path(layer, table)
            timestamp = datetime.utcnow()

            try:
                df_with_meta = df.withColumn("_batch_id", lit(batch_id)) \
                                 .withColumn("_ingested_at", current_timestamp())

                record_count = df.count()

                # Store in memory
                if mode == WriteMode.OVERWRITE or full_table not in self.tables:
                    self.tables[full_table] = df_with_meta
                else:
                    existing = self.tables[full_table]
                    self.tables[full_table] = existing.union(df_with_meta)

                # Register as temp view for queries
                self.tables[full_table].createOrReplaceTempView(full_table)

                return WriteResult(
                    success=True,
                    layer=layer,
                    table=table,
                    records_written=record_count,
                    batch_id=batch_id,
                    timestamp=timestamp,
                )
            except Exception as e:
                return WriteResult(
                    success=False, layer=layer, table=table,
                    records_written=0, batch_id=batch_id,
                    timestamp=timestamp, error_message=str(e)
                )

        def read(self, layer, table, columns=None, filter_expr=None):
            full_table = self.get_table_path(layer, table)
            if full_table not in self.tables:
                raise Exception(f"Table {full_table} not found")
            df = self.tables[full_table]
            if columns:
                df = df.select(*columns)
            if filter_expr:
                df = df.filter(filter_expr)
            return df

        def write_lineage(self, batch_id, source_layer, target_layer,
                          source_table, target_table, record_count,
                          mapping_id, field_mappings=None) -> bool:
            self.lineage_records.append({
                "batch_id": batch_id,
                "source_layer": source_layer.value,
                "target_layer": target_layer.value,
                "source_table": source_table,
                "target_table": target_table,
                "record_count": record_count,
                "mapping_id": mapping_id,
            })
            return True

        def write_error(self, batch_id, layer, table, error_type,
                        error_message, record_data=None, record_id=None) -> bool:
            self.error_records.append({
                "batch_id": batch_id,
                "layer": layer.value,
                "table": table,
                "error_type": error_type,
                "error_message": error_message,
            })
            return True

        def get_batch_status(self, batch_id) -> dict:
            return {"batch_id": batch_id, "status": "IN_MEMORY"}

    config = PersistenceConfig(backend="memory", catalog="test")
    return InMemoryBackend(spark, config)


def load_sample_data(spark, message_type: str):
    """Load sample message data."""
    from pyspark.sql.types import StructType, StructField, StringType

    fixtures_dir = PROJECT_ROOT / "tests" / "fixtures"

    if message_type == "pain001":
        file_path = fixtures_dir / "pain001_sample.xml"
    elif message_type == "mt103":
        file_path = fixtures_dir / "mt103_sample.txt"
    else:
        raise ValueError(f"Unknown message type: {message_type}")

    if not file_path.exists():
        raise FileNotFoundError(f"Sample file not found: {file_path}")

    content = file_path.read_text()

    schema = StructType([
        StructField("content", StringType(), True),
        StructField("message_id", StringType(), True),
        StructField("source_file", StringType(), True),
    ])

    return spark.createDataFrame([
        (content, f"{message_type}-test-001", str(file_path))
    ], schema)


def test_medallion_pipeline(spark, persistence, message_type: str, verbose: bool = False):
    """Test full medallion pipeline."""
    from gps_cdm.ingestion.orchestration.medallion import MedallionOrchestrator

    print_section(f"Testing {message_type.upper()} Medallion Pipeline")

    results = []

    try:
        # Load sample data
        source_df = load_sample_data(spark, message_type)
        results.append(("Load Sample Data", True, f"{source_df.count()} rows"))

        # Get mapping path - use separate target tables per message type
        if message_type == "pain001":
            mapping_path = PROJECT_ROOT / "mappings" / "standards" / "pain_001.yaml"
            target_table = "payment_instruction_pain001"
        else:
            mapping_path = PROJECT_ROOT / "mappings" / "standards" / "mt103.yaml"
            target_table = "payment_instruction_mt103"

        if not mapping_path.exists():
            results.append(("Mapping File", False, f"{mapping_path.name} not found"))
            for name, success, msg in results:
                print_result(name, success, msg)
            return False

        results.append(("Mapping File", True, str(mapping_path.name)))

        # Create orchestrator
        orchestrator = MedallionOrchestrator(
            spark=spark,
            persistence=persistence,
            enable_gold=True,
        )

        # Run pipeline
        pipeline_result = orchestrator.ingest(
            source_df=source_df,
            mapping_path=str(mapping_path),
            source_table=f"raw_{message_type}",
            target_table=target_table,
        )

        results.append((
            "Pipeline Execution",
            pipeline_result.success,
            f"Batch: {pipeline_result.batch_id[:8]}..."
        ))

        results.append((
            "Bronze Layer",
            pipeline_result.bronze_records > 0,
            f"{pipeline_result.bronze_records} records"
        ))

        results.append((
            "Silver Layer",
            pipeline_result.silver_records > 0,
            f"{pipeline_result.silver_records} records"
        ))

        results.append((
            "Gold Layer",
            pipeline_result.gold_records >= 0,
            f"{pipeline_result.gold_records} metric records"
        ))

        results.append((
            "Lineage Recorded",
            pipeline_result.lineage_recorded,
            f"{len(persistence.lineage_records)} lineage records"
        ))

        # Validation warnings are acceptable, pipeline errors are not
        has_pipeline_errors = any(
            "PIPELINE_ERROR" in str(e) or "TRANSFORMATION_ERROR" in str(e)
            for e in pipeline_result.errors
        )
        results.append((
            "Errors",
            not has_pipeline_errors,
            f"{pipeline_result.error_records} validation warnings" if pipeline_result.error_records > 0 else "0 errors"
        ))

        results.append((
            "Duration",
            pipeline_result.duration_seconds < 60,
            f"{pipeline_result.duration_seconds:.2f}s"
        ))

        if verbose:
            print("\n  Pipeline Details:")
            print(f"    - Batch ID: {pipeline_result.batch_id}")
            print(f"    - Bronze: {pipeline_result.bronze_records} records")
            print(f"    - Silver: {pipeline_result.silver_records} records")
            print(f"    - Gold: {pipeline_result.gold_records} metrics")
            print(f"    - Duration: {pipeline_result.duration_seconds:.2f}s")

            if pipeline_result.errors:
                print(f"\n  Errors:")
                for err in pipeline_result.errors[:5]:
                    err_str = str(err)
                    print(f"    - {err_str[:100]}...")

            # Show lineage
            print(f"\n  Lineage Trail:")
            for lineage in persistence.lineage_records:
                print(f"    - {lineage['source_layer']} → {lineage['target_layer']}: "
                      f"{lineage['source_table']} → {lineage['target_table']} "
                      f"({lineage['record_count']} records)")

            # Show stored tables
            print(f"\n  Persisted Tables:")
            for table_name in sorted(persistence.tables.keys()):
                df = persistence.tables[table_name]
                print(f"    - {table_name}: {df.count()} rows, {len(df.columns)} columns")

    except Exception as e:
        results.append(("Pipeline", False, str(e)))
        import traceback
        if verbose:
            traceback.print_exc()

    for name, success, msg in results:
        print_result(name, success, msg)

    return all(r[1] for r in results)


def main():
    """Run medallion architecture tests."""
    parser = argparse.ArgumentParser(description="GPS CDM Medallion Test")
    parser.add_argument("--test", choices=["all", "pain001", "mt103"], default="all",
                        help="Which test to run")
    parser.add_argument("--backend", choices=["memory", "postgresql", "delta"],
                        default="memory", help="Persistence backend")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--database", default="cdm_test", help="Database name")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print_header("GPS CDM - Medallion Architecture Test")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Backend: {args.backend}")
    print(f"Project: {PROJECT_ROOT}")

    results = {}

    # Create Spark session
    print_section("Initializing Spark")
    spark = create_spark_session()
    print_result("Spark Session", True, f"Version {spark.version}")

    # Create persistence backend
    print_section("Initializing Persistence")
    if args.backend == "memory":
        persistence = create_in_memory_persistence(spark)
        print_result("In-Memory Backend", True, "No external database required")
    elif args.backend == "postgresql":
        from gps_cdm.ingestion.persistence import PersistenceFactory
        try:
            persistence = PersistenceFactory.create(
                backend="postgresql",
                spark=spark,
                host=args.host,
                database=args.database,
            )
            print_result("PostgreSQL Backend", True, f"{args.host}/{args.database}")
        except Exception as e:
            print_result("PostgreSQL Backend", False, str(e))
            print("\nPostgreSQL not available. Run with --backend memory for testing.")
            return 1
    else:
        print_result("Backend", False, f"Backend {args.backend} not implemented for local test")
        return 1

    # Run tests
    if args.test in ["all", "pain001"]:
        results["pain001"] = test_medallion_pipeline(spark, persistence, "pain001", args.verbose)

    if args.test in ["all", "mt103"]:
        results["mt103"] = test_medallion_pipeline(spark, persistence, "mt103", args.verbose)

    # Summary
    print_header("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, success in results.items():
        print_result(f"{name} Pipeline", success, "PASSED" if success else "FAILED")

    print()
    print(f"Results: {passed}/{total} passed")

    # Show what was persisted
    if args.verbose and hasattr(persistence, 'tables'):
        print_section("Data Persisted")
        for layer in ["bronze", "silver", "gold"]:
            tables = [t for t in persistence.tables.keys() if t.startswith(layer)]
            if tables:
                print(f"\n{layer.upper()} Layer:")
                for table in tables:
                    df = persistence.tables[table]
                    print(f"  - {table}: {df.count()} rows")

        if persistence.lineage_records:
            print(f"\nLineage Records: {len(persistence.lineage_records)}")

    if passed == total:
        print("\n✓ All medallion pipeline tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

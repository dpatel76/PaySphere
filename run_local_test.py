#!/usr/bin/env python3
"""
GPS CDM - Local End-to-End Test Runner
========================================

Standalone script to test the configuration-driven ingestion framework
locally without Databricks.

Prerequisites:
    pip install pyspark pyyaml

Usage:
    python run_local_test.py
    python run_local_test.py --test pain001
    python run_local_test.py --test mt103
    python run_local_test.py --verbose
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
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """Print a section header."""
    print()
    print(f"--- {title} ---")


def print_result(name: str, success: bool, message: str = ""):
    """Print a test result."""
    status = "✓" if success else "✗"
    color_start = "\033[92m" if success else "\033[91m"
    color_end = "\033[0m"
    print(f"{color_start}{status}{color_end} {name}: {message}")


def test_spark_setup():
    """Test Spark setup."""
    print_section("Testing Spark Setup")

    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder \
            .appName("GPS_CDM_Test") \
            .master("local[*]") \
            .config("spark.sql.shuffle.partitions", "4") \
            .config("spark.driver.memory", "2g") \
            .config("spark.ui.enabled", "false") \
            .getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")

        print_result("Spark Session", True, f"Version {spark.version}")

        # Quick test
        df = spark.createDataFrame([("test",)], ["col"])
        count = df.count()
        print_result("DataFrame Operations", count == 1, f"Created test DataFrame")

        return spark

    except Exception as e:
        print_result("Spark Setup", False, str(e))
        return None


def test_imports():
    """Test framework imports."""
    print_section("Testing Framework Imports")

    tests = []

    try:
        from gps_cdm.ingestion.core.models import (
            MappingConfig, FieldMapping, SourceConfig, DataType, SourceFormat
        )
        tests.append(("Core Models", True, "MappingConfig, FieldMapping, etc."))
    except Exception as e:
        tests.append(("Core Models", False, str(e)))

    try:
        from gps_cdm.ingestion.core.compiler import MappingCompiler, CompiledMapping
        tests.append(("Compiler", True, "MappingCompiler, CompiledMapping"))
    except Exception as e:
        tests.append(("Compiler", False, str(e)))

    try:
        from gps_cdm.ingestion.parsers.registry import ParserRegistry
        from gps_cdm.ingestion.parsers.xml_parser import ISO20022Parser
        from gps_cdm.ingestion.parsers.mt_parser import SWIFTMTParser
        tests.append(("Parsers", True, "XML, MT, JSON, CSV parsers"))
    except Exception as e:
        tests.append(("Parsers", False, str(e)))

    try:
        from gps_cdm.ingestion.transforms.library import TransformLibrary
        count = len(TransformLibrary.list_all())
        tests.append(("Transforms", True, f"{count} transform functions"))
    except Exception as e:
        tests.append(("Transforms", False, str(e)))

    try:
        from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion
        tests.append(("Engine", True, "ConfigDrivenIngestion"))
    except Exception as e:
        tests.append(("Engine", False, str(e)))

    for name, success, msg in tests:
        print_result(name, success, msg)

    return all(t[1] for t in tests)


def test_transforms():
    """Test transform functions."""
    print_section("Testing Transform Functions")

    from gps_cdm.ingestion.transforms.library import TransformLibrary

    tests = []

    # String transforms
    result = TransformLibrary.apply("trim", "  hello  ")
    tests.append(("trim", result == "hello", f"'  hello  ' -> '{result}'"))

    result = TransformLibrary.apply("upper", "hello")
    tests.append(("upper", result == "HELLO", f"'hello' -> '{result}'"))

    # Identifier transforms
    result = TransformLibrary.apply("validate_bic", "CHABORNY")
    tests.append(("validate_bic", result == "CHABORNY", f"'CHABORNY' -> '{result}'"))

    result = TransformLibrary.apply("validate_bic", "INVALID")
    tests.append(("validate_bic (invalid)", result is None, f"'INVALID' -> '{result}'"))

    # Date transforms
    result = TransformLibrary.apply("mt_date", "240115")
    tests.append(("mt_date", result is not None, f"'240115' -> '{result}'"))

    # Payment transforms
    result = TransformLibrary.apply("parse_mt_amount", "USD10000,50")
    tests.append(("parse_mt_amount", result == 10000.50, f"'USD10000,50' -> {result}"))

    for name, success, msg in tests:
        print_result(name, success, msg)

    return all(t[1] for t in tests)


def test_lookups(spark):
    """Test lookup manager."""
    print_section("Testing Lookup Manager")

    from gps_cdm.ingestion.transforms.lookups import LookupManager

    manager = LookupManager(spark)
    tests = []

    # List tables
    tables = manager.list_tables()
    tests.append(("Load Tables", len(tables) > 0, f"{len(tables)} tables loaded"))

    # Country lookup
    result = manager.lookup("country_code", "US")
    tests.append(("Country Lookup", result == "United States", f"US -> {result}"))

    # Currency lookup
    result = manager.lookup("currency_code", "USD")
    tests.append(("Currency Lookup", result == "US Dollar", f"USD -> {result}"))

    # Charge bearer lookup
    result = manager.lookup("charge_bearer", "SHA")
    tests.append(("Charge Bearer", result == "SHAR", f"SHA -> {result}"))

    for name, success, msg in tests:
        print_result(name, success, msg)

    return all(t[1] for t in tests)


def test_compiler():
    """Test mapping compiler."""
    print_section("Testing Mapping Compiler")

    from gps_cdm.ingestion.core.compiler import MappingCompiler

    compiler = MappingCompiler()
    tests = []

    # Test pain.001 mapping
    pain001_path = PROJECT_ROOT / "mappings" / "standards" / "pain_001.yaml"
    if pain001_path.exists():
        try:
            compiled = compiler.compile(str(pain001_path))
            tests.append((
                "Compile pain.001",
                compiled is not None and compiled.total_fields > 0,
                f"{compiled.total_fields} fields, {len(compiled.target_entities)} entities"
            ))
        except Exception as e:
            tests.append(("Compile pain.001", False, str(e)))
    else:
        tests.append(("Compile pain.001", False, "Mapping file not found"))

    # Test MT103 mapping
    mt103_path = PROJECT_ROOT / "mappings" / "standards" / "mt103.yaml"
    if mt103_path.exists():
        try:
            compiled = compiler.compile(str(mt103_path))
            tests.append((
                "Compile MT103",
                compiled is not None and compiled.total_fields > 0,
                f"{compiled.total_fields} fields, {len(compiled.target_entities)} entities"
            ))
        except Exception as e:
            tests.append(("Compile MT103", False, str(e)))
    else:
        tests.append(("Compile MT103", False, "Mapping file not found"))

    for name, success, msg in tests:
        print_result(name, success, msg)

    return all(t[1] for t in tests)


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


def test_pain001_ingestion(spark, verbose: bool = False):
    """Test pain.001 end-to-end ingestion."""
    print_section("Testing pain.001 End-to-End Ingestion")

    from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion

    tests = []

    try:
        # Load sample data
        source_df = load_sample_data(spark, "pain001")
        tests.append(("Load Sample Data", True, f"{source_df.count()} rows"))

        # Get mapping path
        mapping_path = PROJECT_ROOT / "mappings" / "standards" / "pain_001.yaml"
        if not mapping_path.exists():
            tests.append(("Mapping File", False, "pain_001.yaml not found"))
            for name, success, msg in tests:
                print_result(name, success, msg)
            return False

        tests.append(("Mapping File", True, str(mapping_path.name)))

        # Run ingestion with validation enabled
        engine = ConfigDrivenIngestion(
            spark=spark,
            enable_lineage=True,
            enable_validation=True
        )

        result = engine.process(
            source_df=source_df,
            mapping_path=str(mapping_path)
        )

        tests.append((
            "Ingestion Process",
            result is not None,
            f"Mapping: {result.mapping_id}"
        ))

        tests.append((
            "Input/Output",
            result.input_count > 0,
            f"In: {result.input_count}, Out: {result.output_count}"
        ))

        tests.append((
            "Execution Time",
            result.execution_time_ms > 0,
            f"{result.execution_time_ms:.2f}ms"
        ))

        # Check output columns
        output_cols = result.output_df.columns
        has_payment_cols = any("Payment" in c for c in output_cols)
        tests.append((
            "Output Columns",
            has_payment_cols,
            f"{len(output_cols)} columns"
        ))

        if verbose:
            print("\n  Output DataFrame Schema:")
            for col in sorted(output_cols)[:15]:
                print(f"    - {col}")
            if len(output_cols) > 15:
                print(f"    ... and {len(output_cols) - 15} more")

            print("\n  Metrics:")
            for k, v in result.metrics.items():
                print(f"    - {k}: {v}")

            if result.errors:
                print("\n  Errors:")
                for err in result.errors[:5]:
                    print(f"    - {err}")

    except Exception as e:
        tests.append(("Ingestion", False, str(e)))
        import traceback
        if verbose:
            traceback.print_exc()

    for name, success, msg in tests:
        print_result(name, success, msg)

    return all(t[1] for t in tests)


def test_mt103_ingestion(spark, verbose: bool = False):
    """Test MT103 end-to-end ingestion."""
    print_section("Testing MT103 End-to-End Ingestion")

    from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion

    tests = []

    try:
        # Load sample data
        source_df = load_sample_data(spark, "mt103")
        tests.append(("Load Sample Data", True, f"{source_df.count()} rows"))

        # Get mapping path
        mapping_path = PROJECT_ROOT / "mappings" / "standards" / "mt103.yaml"
        if not mapping_path.exists():
            tests.append(("Mapping File", False, "mt103.yaml not found"))
            for name, success, msg in tests:
                print_result(name, success, msg)
            return False

        tests.append(("Mapping File", True, str(mapping_path.name)))

        # Run ingestion with validation enabled
        engine = ConfigDrivenIngestion(
            spark=spark,
            enable_lineage=True,
            enable_validation=True
        )

        result = engine.process(
            source_df=source_df,
            mapping_path=str(mapping_path)
        )

        tests.append((
            "Ingestion Process",
            result is not None,
            f"Mapping: {result.mapping_id}"
        ))

        tests.append((
            "Input/Output",
            result.input_count > 0,
            f"In: {result.input_count}, Out: {result.output_count}"
        ))

        tests.append((
            "Execution Time",
            result.execution_time_ms > 0,
            f"{result.execution_time_ms:.2f}ms"
        ))

        # Check output columns
        output_cols = result.output_df.columns
        tests.append((
            "Output Columns",
            len(output_cols) > 0,
            f"{len(output_cols)} columns"
        ))

        if verbose:
            print("\n  Output DataFrame Schema:")
            for col in sorted(output_cols)[:15]:
                print(f"    - {col}")
            if len(output_cols) > 15:
                print(f"    ... and {len(output_cols) - 15} more")

            print("\n  Metrics:")
            for k, v in result.metrics.items():
                print(f"    - {k}: {v}")

    except Exception as e:
        tests.append(("Ingestion", False, str(e)))
        import traceback
        if verbose:
            traceback.print_exc()

    for name, success, msg in tests:
        print_result(name, success, msg)

    return all(t[1] for t in tests)


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="GPS CDM Local Test Runner")
    parser.add_argument("--test", choices=["all", "pain001", "mt103"], default="all",
                        help="Which test to run")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    print_header("GPS CDM - Configuration-Driven Ingestion Framework Test")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Project: {PROJECT_ROOT}")

    results = {}

    # Test Spark setup
    spark = test_spark_setup()
    results["Spark Setup"] = spark is not None

    if not spark:
        print("\n❌ Spark setup failed. Cannot continue.")
        return 1

    # Test imports
    results["Imports"] = test_imports()

    # Test transforms
    results["Transforms"] = test_transforms()

    # Test lookups
    results["Lookups"] = test_lookups(spark)

    # Test compiler
    results["Compiler"] = test_compiler()

    # Test ingestion based on args
    if args.test in ["all", "pain001"]:
        results["pain.001 Ingestion"] = test_pain001_ingestion(spark, args.verbose)

    if args.test in ["all", "mt103"]:
        results["MT103 Ingestion"] = test_mt103_ingestion(spark, args.verbose)

    # Summary
    print_header("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, success in results.items():
        print_result(name, success, "PASSED" if success else "FAILED")

    print()
    print(f"Results: {passed}/{total} passed")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

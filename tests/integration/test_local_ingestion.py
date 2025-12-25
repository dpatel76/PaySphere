"""
GPS CDM - Local End-to-End Ingestion Tests
============================================

Tests the configuration-driven ingestion framework locally using PySpark.
No Databricks required - runs on local Spark instance.

Usage:
    # Run all tests
    pytest tests/integration/test_local_ingestion.py -v

    # Run specific test
    pytest tests/integration/test_local_ingestion.py::TestPain001Ingestion -v

    # Run with output
    pytest tests/integration/test_local_ingestion.py -v -s
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType

# Import fixtures
from tests.fixtures import load_pain001_sample, load_mt103_sample, PAIN001_SAMPLE, MT103_SAMPLE


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def spark():
    """Create local SparkSession for testing."""
    spark = SparkSession.builder \
        .appName("GPS_CDM_Local_Test") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.session.timeZone", "UTC") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()

    # Set log level to reduce noise
    spark.sparkContext.setLogLevel("WARN")

    yield spark

    spark.stop()


@pytest.fixture
def pain001_df(spark):
    """Create DataFrame with sample pain.001 message."""
    content = load_pain001_sample()
    schema = StructType([
        StructField("content", StringType(), True),
        StructField("message_id", StringType(), True),
        StructField("source_file", StringType(), True),
    ])
    return spark.createDataFrame([
        (content, "pain001-test-001", str(PAIN001_SAMPLE))
    ], schema)


@pytest.fixture
def mt103_df(spark):
    """Create DataFrame with sample MT103 message."""
    content = load_mt103_sample()
    schema = StructType([
        StructField("content", StringType(), True),
        StructField("message_id", StringType(), True),
        StructField("source_file", StringType(), True),
    ])
    return spark.createDataFrame([
        (content, "mt103-test-001", str(MT103_SAMPLE))
    ], schema)


@pytest.fixture
def mappings_path():
    """Get path to YAML mappings."""
    return str(project_root / "mappings" / "standards")


# ============================================================================
# Test Classes
# ============================================================================

class TestSparkSetup:
    """Test that Spark is properly configured."""

    def test_spark_session_created(self, spark):
        """Verify SparkSession is available."""
        assert spark is not None
        assert spark.version is not None
        print(f"\nSpark Version: {spark.version}")

    def test_spark_can_create_dataframe(self, spark):
        """Verify basic DataFrame operations work."""
        df = spark.createDataFrame([("test",)], ["col"])
        assert df.count() == 1


class TestIngestionModelsImport:
    """Test that ingestion framework modules can be imported."""

    def test_import_models(self):
        """Test importing core models."""
        from gps_cdm.ingestion.core.models import (
            MappingConfig, FieldMapping, SourceConfig,
            TransformConfig, DataType, SourceFormat
        )
        assert MappingConfig is not None
        assert SourceFormat.XML.value == "XML"
        assert DataType.STRING.value == "string"
        print("\n✓ Core models imported successfully")

    def test_import_compiler(self):
        """Test importing compiler."""
        from gps_cdm.ingestion.core.compiler import (
            MappingCompiler, CompiledMapping, CDMValidator
        )
        assert MappingCompiler is not None
        print("✓ Compiler imported successfully")

    def test_import_parsers(self):
        """Test importing parsers."""
        from gps_cdm.ingestion.parsers.base import BaseParser, ParseResult
        from gps_cdm.ingestion.parsers.xml_parser import XMLParser, ISO20022Parser
        from gps_cdm.ingestion.parsers.mt_parser import MTParser, SWIFTMTParser
        assert BaseParser is not None
        assert ISO20022Parser is not None
        print("✓ Parsers imported successfully")

    def test_import_transforms(self):
        """Test importing transforms."""
        from gps_cdm.ingestion.transforms.library import TransformLibrary
        from gps_cdm.ingestion.transforms.lookups import LookupManager

        # Check transform count
        transforms = TransformLibrary.list_all()
        print(f"✓ Transform library imported: {len(transforms)} transforms available")
        assert len(transforms) >= 50  # We created 50+ transforms

    def test_import_engine(self):
        """Test importing engine."""
        from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion, IngestionResult
        assert ConfigDrivenIngestion is not None
        print("✓ Engine imported successfully")


class TestTransformLibrary:
    """Test transform library functions."""

    def test_string_transforms(self):
        """Test string transformation functions."""
        from gps_cdm.ingestion.transforms.library import TransformLibrary

        # Test trim
        result = TransformLibrary.apply("trim", "  hello  ")
        assert result == "hello"

        # Test upper
        result = TransformLibrary.apply("upper", "hello")
        assert result == "HELLO"

        # Test truncate
        result = TransformLibrary.apply("truncate", "hello world", max_length=5)
        assert result == "hello"

        print("\n✓ String transforms working")

    def test_identifier_transforms(self):
        """Test identifier validation transforms."""
        from gps_cdm.ingestion.transforms.library import TransformLibrary

        # Valid BIC
        result = TransformLibrary.apply("validate_bic", "CHABORNY")
        assert result == "CHABORNY"

        # Invalid BIC
        result = TransformLibrary.apply("validate_bic", "INVALID")
        assert result is None

        # Normalize BIC (8 to 11 chars)
        result = TransformLibrary.apply("normalize_bic", "CHABORNY")
        assert result == "CHABORNYYXXX" or result == "CHABORNYXXX"

        print("✓ Identifier transforms working")

    def test_date_transforms(self):
        """Test date transformation functions."""
        from gps_cdm.ingestion.transforms.library import TransformLibrary

        # ISO date
        result = TransformLibrary.apply("iso_date", "2024-01-15")
        assert result is not None

        # MT date (YYMMDD)
        result = TransformLibrary.apply("mt_date", "240115")
        assert result is not None

        print("✓ Date transforms working")

    def test_payment_transforms(self):
        """Test payment-specific transforms."""
        from gps_cdm.ingestion.transforms.library import TransformLibrary

        # Parse MT amount
        result = TransformLibrary.apply("parse_mt_amount", "USD10000,50")
        assert result == 10000.50

        # Parse MT currency
        result = TransformLibrary.apply("parse_mt_currency", "USD10000,50")
        assert result == "USD"

        print("✓ Payment transforms working")


class TestLookupManager:
    """Test lookup manager functionality."""

    def test_standard_lookups_loaded(self, spark):
        """Test that standard lookups are available."""
        from gps_cdm.ingestion.transforms.lookups import LookupManager

        manager = LookupManager(spark)
        tables = manager.list_tables()

        assert "country_code" in tables
        assert "currency_code" in tables
        assert "charge_bearer" in tables

        print(f"\n✓ Lookup tables loaded: {len(tables)}")

    def test_lookup_values(self, spark):
        """Test looking up values."""
        from gps_cdm.ingestion.transforms.lookups import LookupManager

        manager = LookupManager(spark)

        # Country lookup
        result = manager.lookup("country_code", "US")
        assert result == "United States"

        # Currency lookup
        result = manager.lookup("currency_code", "USD")
        assert result == "US Dollar"

        # Charge bearer lookup
        result = manager.lookup("charge_bearer", "SHA")
        assert result == "SHAR"

        print("✓ Lookup values correct")


class TestMappingCompiler:
    """Test YAML mapping compilation."""

    def test_compile_pain001_mapping(self, mappings_path):
        """Test compiling pain.001 YAML mapping."""
        from gps_cdm.ingestion.core.compiler import MappingCompiler

        compiler = MappingCompiler()
        mapping_file = Path(mappings_path) / "pain_001.yaml"

        if not mapping_file.exists():
            pytest.skip(f"Mapping file not found: {mapping_file}")

        compiled = compiler.compile(str(mapping_file))

        assert compiled is not None
        assert compiled.config.id == "PAIN_001_V09"
        assert compiled.total_fields > 0

        print(f"\n✓ pain.001 compiled successfully")
        print(f"  - Fields: {compiled.total_fields}")
        print(f"  - Optimized: {compiled.optimized_fields}")
        print(f"  - Entities: {compiled.target_entities}")
        print(f"  - Warnings: {len(compiled.warnings)}")

    def test_compile_mt103_mapping(self, mappings_path):
        """Test compiling MT103 YAML mapping."""
        from gps_cdm.ingestion.core.compiler import MappingCompiler

        compiler = MappingCompiler()
        mapping_file = Path(mappings_path) / "mt103.yaml"

        if not mapping_file.exists():
            pytest.skip(f"Mapping file not found: {mapping_file}")

        compiled = compiler.compile(str(mapping_file))

        assert compiled is not None
        assert compiled.config.id == "MT103_SWIFT"
        assert compiled.total_fields > 0

        print(f"\n✓ MT103 compiled successfully")
        print(f"  - Fields: {compiled.total_fields}")
        print(f"  - Optimized: {compiled.optimized_fields}")
        print(f"  - Entities: {compiled.target_entities}")


class TestParserRegistry:
    """Test parser registry functionality."""

    def test_parser_registry_init(self, spark):
        """Test parser registry initialization."""
        from gps_cdm.ingestion.parsers.registry import ParserRegistry
        from gps_cdm.ingestion.core.models import SourceFormat

        registry = ParserRegistry(spark)
        parsers = registry.list_parsers()

        assert SourceFormat.XML.value in parsers
        assert SourceFormat.SWIFT_MT.value in parsers
        assert SourceFormat.JSON.value in parsers
        assert SourceFormat.CSV.value in parsers

        print(f"\n✓ Parser registry initialized")
        for fmt, parser_list in parsers.items():
            print(f"  - {fmt}: {parser_list}")

    def test_get_xml_parser(self, spark):
        """Test getting XML parser."""
        from gps_cdm.ingestion.parsers.registry import ParserRegistry
        from gps_cdm.ingestion.core.models import SourceConfig, SourceFormat

        registry = ParserRegistry(spark)

        config = SourceConfig(
            format=SourceFormat.XML,
            parser="iso20022",
            namespace="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09",
            root_element="CstmrCdtTrfInitn"
        )

        parser = registry.get_parser(config)
        assert parser is not None
        print("\n✓ XML parser retrieved successfully")

    def test_get_mt_parser(self, spark):
        """Test getting MT parser."""
        from gps_cdm.ingestion.parsers.registry import ParserRegistry
        from gps_cdm.ingestion.core.models import SourceConfig, SourceFormat

        registry = ParserRegistry(spark)

        config = SourceConfig(
            format=SourceFormat.SWIFT_MT,
            parser="swift",
            message_type="MT103"
        )

        parser = registry.get_parser(config)
        assert parser is not None
        print("\n✓ MT parser retrieved successfully")


class TestPain001Ingestion:
    """End-to-end tests for pain.001 ingestion."""

    def test_parse_pain001(self, spark, pain001_df):
        """Test parsing pain.001 XML."""
        from gps_cdm.ingestion.parsers.registry import ParserRegistry
        from gps_cdm.ingestion.core.models import SourceConfig, SourceFormat

        registry = ParserRegistry(spark)

        config = SourceConfig(
            format=SourceFormat.XML,
            parser="iso20022",
            namespace="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09",
            root_element="CstmrCdtTrfInitn"
        )

        parser = registry.get_parser(config)
        result = parser.parse(pain001_df)

        assert result.row_count == 1
        assert not result.has_errors

        print(f"\n✓ pain.001 parsed successfully")
        print(f"  - Rows: {result.row_count}")
        print(f"  - Errors: {result.error_count}")

    def test_full_pain001_ingestion(self, spark, pain001_df, mappings_path):
        """Test full pain.001 ingestion pipeline."""
        from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion

        mapping_file = Path(mappings_path) / "pain_001.yaml"
        if not mapping_file.exists():
            pytest.skip(f"Mapping file not found: {mapping_file}")

        engine = ConfigDrivenIngestion(
            spark=spark,
            enable_lineage=True,
            enable_validation=True
        )

        result = engine.process(
            source_df=pain001_df,
            mapping_path=str(mapping_file)
        )

        assert result is not None
        assert result.mapping_id == "PAIN_001_V09"
        assert result.input_count == 1

        print(f"\n✓ pain.001 ingestion complete")
        print(f"  - Mapping: {result.mapping_name}")
        print(f"  - Input: {result.input_count}")
        print(f"  - Output: {result.output_count}")
        print(f"  - Errors: {result.error_count}")
        print(f"  - Validation failures: {result.validation_failures}")
        print(f"  - Execution time: {result.execution_time_ms:.2f}ms")

        # Show output columns
        output_cols = result.output_df.columns
        print(f"  - Output columns: {len(output_cols)}")
        for col in sorted(output_cols)[:10]:
            print(f"    - {col}")
        if len(output_cols) > 10:
            print(f"    ... and {len(output_cols) - 10} more")


class TestMT103Ingestion:
    """End-to-end tests for MT103 ingestion."""

    def test_parse_mt103(self, spark, mt103_df):
        """Test parsing MT103 message."""
        from gps_cdm.ingestion.parsers.registry import ParserRegistry
        from gps_cdm.ingestion.core.models import SourceConfig, SourceFormat

        registry = ParserRegistry(spark)

        config = SourceConfig(
            format=SourceFormat.SWIFT_MT,
            parser="swift",
            message_type="MT103"
        )

        parser = registry.get_parser(config)
        result = parser.parse(mt103_df)

        assert result.row_count == 1

        # Check that blocks were extracted
        parsed_data = result.data.collect()[0]
        assert parsed_data.basic_header is not None
        assert parsed_data.text_block is not None

        print(f"\n✓ MT103 parsed successfully")
        print(f"  - Rows: {result.row_count}")
        print(f"  - Basic Header: {parsed_data.basic_header[:30]}...")
        print(f"  - Text Block length: {len(parsed_data.text_block)} chars")

    def test_full_mt103_ingestion(self, spark, mt103_df, mappings_path):
        """Test full MT103 ingestion pipeline."""
        from gps_cdm.ingestion.core.engine import ConfigDrivenIngestion

        mapping_file = Path(mappings_path) / "mt103.yaml"
        if not mapping_file.exists():
            pytest.skip(f"Mapping file not found: {mapping_file}")

        engine = ConfigDrivenIngestion(
            spark=spark,
            enable_lineage=True,
            enable_validation=True
        )

        result = engine.process(
            source_df=mt103_df,
            mapping_path=str(mapping_file)
        )

        assert result is not None
        assert result.mapping_id == "MT103_SWIFT"
        assert result.input_count == 1

        print(f"\n✓ MT103 ingestion complete")
        print(f"  - Mapping: {result.mapping_name}")
        print(f"  - Input: {result.input_count}")
        print(f"  - Output: {result.output_count}")
        print(f"  - Errors: {result.error_count}")
        print(f"  - Validation failures: {result.validation_failures}")
        print(f"  - Execution time: {result.execution_time_ms:.2f}ms")

        # Show output columns
        output_cols = result.output_df.columns
        print(f"  - Output columns: {len(output_cols)}")


# ============================================================================
# Standalone Test Runner
# ============================================================================

if __name__ == "__main__":
    """Run tests directly without pytest."""
    print("=" * 60)
    print("GPS CDM - Local Ingestion Framework Test")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Run with pytest
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
    ])

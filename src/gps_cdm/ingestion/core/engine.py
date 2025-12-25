"""
GPS Payments CDM - Configuration-Driven Ingestion Engine
=========================================================

The main execution engine for processing payments data through
configuration-driven YAML mappings into the CDM.

Key Features:
- Single optimized engine for all message formats
- Spark SQL generation for performance
- Full lineage and traceability
- Validation and quality metrics
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime
import yaml
import hashlib

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, lit, when, coalesce, concat, concat_ws,
    current_timestamp, monotonically_increasing_id,
    struct, to_json, from_json,
    xpath_string, regexp_extract, get_json_object, substring,
    expr, broadcast,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DecimalType,
    DateType, TimestampType, IntegerType, BooleanType,
)

from gps_cdm.ingestion.core.models import (
    MappingConfig, FieldMapping, SourceConfig, TransformConfig,
    TransformType, DataType, SourceFormat, ValidationRule, Severity,
)
from gps_cdm.ingestion.core.compiler import MappingCompiler, CompiledMapping, ExecutionStep
from gps_cdm.ingestion.parsers.registry import ParserRegistry
from gps_cdm.ingestion.transforms.library import TransformLibrary
from gps_cdm.ingestion.transforms.lookups import LookupManager


@dataclass
class IngestionResult:
    """Result of ingestion processing."""
    mapping_id: str
    mapping_name: str
    input_count: int
    output_count: int
    error_count: int
    validation_failures: int
    execution_time_ms: float
    output_df: DataFrame
    lineage: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Context for mapping execution."""
    mapping_config: MappingConfig
    compiled_mapping: CompiledMapping
    source_df: DataFrame
    parser: Any
    lookup_manager: LookupManager
    transform_library: TransformLibrary


class ConfigDrivenIngestion:
    """
    Main ingestion engine for configuration-driven processing.

    Processes payment messages from any source format to CDM
    using YAML-defined mappings.

    Usage:
        ingestion = ConfigDrivenIngestion(spark)

        # Process with a mapping file
        result = ingestion.process(
            source_df=raw_messages,
            mapping_path="/mappings/standards/pain_001.yaml"
        )

        # Process with pre-compiled mapping
        result = ingestion.process(
            source_df=raw_messages,
            compiled_mapping=compiled
        )

        # Access output
        cdm_df = result.output_df
    """

    def __init__(
        self,
        spark: SparkSession,
        mapping_registry_path: Optional[str] = None,
        enable_lineage: bool = True,
        enable_validation: bool = True,
    ):
        self.spark = spark
        self.mapping_registry_path = mapping_registry_path
        self.enable_lineage = enable_lineage
        self.enable_validation = enable_validation

        # Initialize components
        self.compiler = MappingCompiler()
        self.parser_registry = ParserRegistry(spark)
        self.lookup_manager = LookupManager(spark)
        self.transform_library = TransformLibrary

        # Cache compiled mappings
        self._compiled_cache: Dict[str, CompiledMapping] = {}

        # Mapping registry
        self._mapping_registry: Dict[str, str] = {}
        if mapping_registry_path:
            self._load_mapping_registry()

    def _load_mapping_registry(self) -> None:
        """Load mapping registry from path."""
        registry_path = Path(self.mapping_registry_path)
        if registry_path.exists():
            for yaml_file in registry_path.glob("**/*.yaml"):
                try:
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                    if "mapping" in data:
                        mapping_id = data["mapping"].get("id")
                        if mapping_id:
                            self._mapping_registry[mapping_id] = str(yaml_file)
                except Exception:
                    pass

    def process(
        self,
        source_df: DataFrame,
        mapping_path: Optional[str] = None,
        mapping_id: Optional[str] = None,
        compiled_mapping: Optional[CompiledMapping] = None,
        mapping_dict: Optional[Dict] = None,
        stage: str = "bronze_to_silver",
    ) -> IngestionResult:
        """
        Process source data through a mapping.

        Args:
            source_df: DataFrame with source data
            mapping_path: Path to YAML mapping file
            mapping_id: ID of registered mapping
            compiled_mapping: Pre-compiled mapping
            mapping_dict: Mapping as dictionary
            stage: For medallion format, which stage to use ("bronze_to_silver" or "silver_to_gold")

        Returns:
            IngestionResult with output DataFrame and metrics
        """
        start_time = datetime.now()

        # Get compiled mapping
        if compiled_mapping:
            compiled = compiled_mapping
        elif mapping_path:
            compiled = self._get_compiled_mapping(mapping_path, stage=stage)
        elif mapping_id:
            if mapping_id in self._mapping_registry:
                compiled = self._get_compiled_mapping(self._mapping_registry[mapping_id], stage=stage)
            else:
                raise ValueError(f"Unknown mapping ID: {mapping_id}")
        elif mapping_dict:
            compiled = self.compiler.compile_from_dict(mapping_dict)
        else:
            raise ValueError("Must provide mapping_path, mapping_id, compiled_mapping, or mapping_dict")

        config = compiled.config

        # Parse source data
        parser = self.parser_registry.get_parser(config.source)
        parse_result = parser.parse(source_df)

        # Create execution context
        context = ExecutionContext(
            mapping_config=config,
            compiled_mapping=compiled,
            source_df=parse_result.data,
            parser=parser,
            lookup_manager=self.lookup_manager,
            transform_library=self.transform_library,
        )

        # Execute mapping
        output_df = self._execute_mapping(context)

        # Add lineage if enabled
        if self.enable_lineage:
            output_df = self._add_lineage(output_df, config)

        # Run validations if enabled
        validation_failures = 0
        errors = []
        if self.enable_validation and config.validations:
            output_df, validation_failures, errors = self._run_validations(
                output_df, config.validations
            )

        # Calculate metrics
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000

        input_count = parse_result.row_count
        output_count = output_df.count()
        error_count = len(errors) + parse_result.error_count

        # Build lineage info
        lineage = {
            "mapping_id": config.id,
            "mapping_version": config.version,
            "source_format": config.source.format.value,
            "parser": config.source.parser,
            "target_entities": list(compiled.target_entities),
            "lookup_tables_used": list(compiled.lookup_tables),
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Build metrics
        metrics = {
            "input_count": input_count,
            "output_count": output_count,
            "error_count": error_count,
            "validation_failures": validation_failures,
            "execution_time_ms": execution_time,
            "optimization_ratio": compiled.get_optimization_ratio(),
            "fields_processed": compiled.total_fields,
            "optimized_fields": compiled.optimized_fields,
        }

        return IngestionResult(
            mapping_id=config.id,
            mapping_name=config.name,
            input_count=input_count,
            output_count=output_count,
            error_count=error_count,
            validation_failures=validation_failures,
            execution_time_ms=execution_time,
            output_df=output_df,
            lineage=lineage,
            errors=errors,
            metrics=metrics,
        )

    def _get_compiled_mapping(
        self,
        mapping_path: str,
        stage: str = "bronze_to_silver"
    ) -> CompiledMapping:
        """Get compiled mapping, using cache if available."""
        # Check cache (include stage in cache key)
        cache_key = hashlib.md5(f"{mapping_path}:{stage}".encode()).hexdigest()
        if cache_key in self._compiled_cache:
            return self._compiled_cache[cache_key]

        # Compile
        compiled = self.compiler.compile(mapping_path, stage=stage)

        # Cache
        self._compiled_cache[cache_key] = compiled

        return compiled

    def _execute_mapping(self, context: ExecutionContext) -> DataFrame:
        """Execute the compiled mapping against source data."""
        config = context.mapping_config
        compiled = context.compiled_mapping
        df = context.source_df

        # XML and MT formats require special extraction (XPath, regex)
        # that can't be optimized to simple column references
        source_format = config.source.format
        requires_extraction = source_format in (SourceFormat.XML, SourceFormat.SWIFT_MT)

        # Check if we can use optimized SQL path (not for XML/MT which need special extraction)
        if not requires_extraction and compiled.spark_sql and all(step.is_optimized for step in compiled.execution_plan):
            return self._execute_optimized_sql(context)

        # Otherwise, execute step by step
        return self._execute_step_by_step(context)

    def _execute_optimized_sql(self, context: ExecutionContext) -> DataFrame:
        """Execute using optimized Spark SQL."""
        compiled = context.compiled_mapping
        df = context.source_df

        # Create temp view
        df.createOrReplaceTempView("source_data")

        # Execute generated SQL
        result = self.spark.sql(compiled.spark_sql)

        return result

    def _execute_step_by_step(self, context: ExecutionContext) -> DataFrame:
        """Execute mapping step by step."""
        config = context.mapping_config
        compiled = context.compiled_mapping
        df = context.source_df
        parser = context.parser

        # Check if source format requires special extraction
        source_format = config.source.format
        requires_extraction = source_format in (SourceFormat.XML, SourceFormat.SWIFT_MT)

        # Process each step in order
        for step in compiled.execution_plan:
            field_mapping = step.field_mapping
            if not field_mapping.target:
                continue

            col_name = f"{field_mapping.target.entity}__{field_mapping.target.attribute}"

            try:
                # For XML/MT formats, always use _apply_field_mapping for proper extraction
                if not requires_extraction and step.is_optimized and step.spark_expr:
                    # Use optimized SQL expression
                    df = df.withColumn(col_name, expr(step.spark_expr))
                else:
                    # Use step-by-step transformation with proper extraction
                    df = self._apply_field_mapping(df, field_mapping, parser, col_name)
            except Exception as e:
                # Log error but continue with NULL
                df = df.withColumn(col_name, lit(None))

        return df

    def _apply_field_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply a single field mapping."""
        transform = mapping.transform

        if transform is None or transform.type == TransformType.DIRECT:
            # Direct mapping
            return self._apply_direct_mapping(df, mapping, parser, output_col)

        elif transform.type == TransformType.LOOKUP:
            return self._apply_lookup_mapping(df, mapping, parser, output_col)

        elif transform.type == TransformType.EXPRESSION:
            return self._apply_expression_mapping(df, mapping, output_col)

        elif transform.type == TransformType.CONDITIONAL:
            return self._apply_conditional_mapping(df, mapping, parser, output_col)

        elif transform.type == TransformType.REGEX:
            return self._apply_regex_mapping(df, mapping, parser, output_col)

        elif transform.type == TransformType.MERGE:
            return self._apply_merge_mapping(df, mapping, parser, output_col)

        elif transform.type == TransformType.SPLIT:
            return self._apply_split_mapping(df, mapping, parser, output_col)

        elif transform.type == TransformType.TEMPLATE:
            return self._apply_template_mapping(df, mapping, parser, output_col)

        elif transform.type == TransformType.CUSTOM:
            return self._apply_custom_mapping(df, mapping, parser, output_col)

        else:
            # Unknown transform, use source directly
            return self._apply_direct_mapping(df, mapping, parser, output_col)

    def _get_source_column(
        self,
        source: str,
        parser: Any,
    ):
        """
        Get the column expression to extract a source value based on format.
        Returns a Spark column expression.
        """
        source_format = parser.config.format

        if source_format == SourceFormat.XML:
            namespace = parser.config.namespace
            if namespace:
                # Build XPath with namespace - use local-name() for namespace-agnostic matching
                parts = source.split("/")
                xpath_parts = []
                for part in parts:
                    if part and not part.startswith("@"):
                        xpath_parts.append(f"*[local-name()='{part}']")
                    elif part.startswith("@"):
                        xpath_parts.append(part)
                xpath = "//" + "/".join(xpath_parts) if xpath_parts else source
            else:
                xpath = source if source.startswith("/") else f"//{source}"
            return xpath_string(col("content"), lit(xpath))

        elif source_format == SourceFormat.SWIFT_MT:
            pattern = rf':({source}[A-Z]?):(.*?)(?=:\d{{2}}[A-Z]?:|-\}})'
            return regexp_extract(col("text_block"), pattern, 2)

        elif source_format == SourceFormat.JSON:
            json_path = source if source.startswith("$") else f"$.{source}"
            return get_json_object(col("content"), json_path)

        elif source_format == SourceFormat.CSV:
            return col(source)

        elif source_format == SourceFormat.FIXED_WIDTH:
            if ":" in source:
                parts = source.split(":")
                start, length = int(parts[0]), int(parts[1])
                return substring(col("content"), start, length)
            return col(source)

        else:
            return col(source)

    def _apply_direct_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply direct (1:1) mapping."""
        source = mapping.source
        if not source:
            return df.withColumn(output_col, lit(None))

        # Get extraction expression based on parser type
        source_format = parser.config.format

        if source_format == SourceFormat.XML:
            # XPath extraction - need to add namespace prefix if configured
            namespace = parser.config.namespace
            if namespace:
                # Build XPath with namespace - use local-name() for namespace-agnostic matching
                # Convert path like "GrpHdr/MsgId" to "//*[local-name()='GrpHdr']/*[local-name()='MsgId']"
                parts = source.split("/")
                xpath_parts = []
                for part in parts:
                    if part and not part.startswith("@"):
                        xpath_parts.append(f"*[local-name()='{part}']")
                    elif part.startswith("@"):
                        xpath_parts.append(part)
                xpath = "//" + "/".join(xpath_parts) if xpath_parts else source
            else:
                xpath = source if source.startswith("/") else f"//{source}"

            return df.withColumn(output_col, xpath_string(col("content"), lit(xpath)))

        elif source_format == SourceFormat.SWIFT_MT:
            # MT field extraction
            pattern = rf':({source}[A-Z]?):(.*?)(?=:\d{{2}}[A-Z]?:|-\}})'
            return df.withColumn(
                output_col,
                regexp_extract(col("text_block"), pattern, 2)
            )

        elif source_format == SourceFormat.JSON:
            # JSONPath extraction
            json_path = source if source.startswith("$") else f"$.{source}"
            return df.withColumn(
                output_col,
                get_json_object(col("content"), json_path)
            )

        elif source_format == SourceFormat.CSV:
            # Column name
            return df.withColumn(output_col, col(source))

        elif source_format == SourceFormat.FIXED_WIDTH:
            # Position extraction (format: "start:length")
            if ":" in source:
                parts = source.split(":")
                start, length = int(parts[0]), int(parts[1])
                return df.withColumn(
                    output_col,
                    substring(col("content"), start, length)
                )
            return df.withColumn(output_col, col(source))

        else:
            # Default: try as column name
            return df.withColumn(output_col, col(source))

    def _apply_lookup_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply lookup transformation."""
        transform = mapping.transform
        source = mapping.source

        # Get the source column expression (handles XML XPath, MT regex, etc.)
        source_col = self._get_source_column(source, parser)

        if transform.mapping:
            # Inline mapping using CASE WHEN
            cases = []
            for key, value in transform.mapping.items():
                cases.append(
                    when(source_col == lit(key), lit(value))
                )

            # Build coalesce chain
            result_col = coalesce(*cases)
            if transform.default:
                result_col = coalesce(result_col, lit(transform.default))

            return df.withColumn(output_col, result_col)

        elif transform.table:
            # For table lookups, first extract the value to a temp column
            temp_col = f"_temp_{output_col}"
            df = df.withColumn(temp_col, source_col)

            # Use lookup manager on the extracted column
            df = self.lookup_manager.join_lookup(
                df=df,
                table_name=transform.table,
                join_col=temp_col,
                output_col=output_col,
                default_value=transform.default,
            )

            # Drop temp column
            return df.drop(temp_col)

        return df.withColumn(output_col, source_col)

    def _apply_expression_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        output_col: str
    ) -> DataFrame:
        """Apply expression transformation."""
        transform = mapping.transform
        expression = transform.expr

        if not expression:
            return df.withColumn(output_col, lit(None))

        # Replace ${field} references with column references
        import re
        expr_str = re.sub(r'\$\{(\w+)\}', r'\1', expression)

        return df.withColumn(output_col, expr(expr_str))

    def _apply_conditional_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply conditional transformation."""
        condition = mapping.condition
        source = mapping.source

        # Get source column expression
        source_col = self._get_source_column(source, parser) if source else lit(None)

        if not condition:
            return df.withColumn(output_col, source_col)

        # Parse condition and apply
        import re
        cond_str = re.sub(r'\$\{(\w+)\}', r'\1', condition)

        return df.withColumn(
            output_col,
            when(expr(cond_str), source_col).otherwise(lit(None))
        )

    def _apply_regex_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply regex extraction."""
        transform = mapping.transform
        source = mapping.source
        pattern = transform.pattern
        group = transform.group or 0

        # Get source column expression
        source_col = self._get_source_column(source, parser)

        return df.withColumn(
            output_col,
            regexp_extract(source_col, pattern, group)
        )

    def _apply_merge_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply merge (many-to-one) transformation."""
        sources = mapping.sources or []
        if not sources:
            return df.withColumn(output_col, lit(None))

        # Get column expressions for all sources
        source_cols = [self._get_source_column(s, parser) for s in sources]
        return df.withColumn(output_col, coalesce(*source_cols))

    def _apply_split_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply split (one-to-many) transformation."""
        transform = mapping.transform
        source = mapping.source
        pattern = transform.pattern or ","
        group = transform.group or 0

        # Get source column expression
        source_col = self._get_source_column(source, parser)

        # Split and get element
        from pyspark.sql.functions import split as spark_split, element_at
        return df.withColumn(
            output_col,
            element_at(spark_split(source_col, pattern), group + 1)
        )

    def _apply_template_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply template transformation."""
        transform = mapping.transform
        template = transform.template

        if not template:
            return df.withColumn(output_col, lit(None))

        # Replace ${field} with column values using concat
        import re

        parts = re.split(r'(\$\{\w+\})', template)
        concat_args = []

        for part in parts:
            if part.startswith("${") and part.endswith("}"):
                field_name = part[2:-1]
                # Use the source column helper for field references
                concat_args.append(coalesce(col(field_name), lit("")))
            elif part:
                concat_args.append(lit(part))

        if concat_args:
            return df.withColumn(output_col, concat(*concat_args))

        return df.withColumn(output_col, lit(template))

    def _apply_custom_mapping(
        self,
        df: DataFrame,
        mapping: FieldMapping,
        parser: Any,
        output_col: str
    ) -> DataFrame:
        """Apply custom function transformation."""
        transform = mapping.transform
        function_name = transform.function
        params = transform.params or {}

        if not function_name:
            return df.withColumn(output_col, lit(None))

        # Get transform from library
        transform_func = self.transform_library.get(function_name)
        if not transform_func:
            return df.withColumn(output_col, lit(None))

        # Get source column expression
        source = mapping.source
        source_col = self._get_source_column(source, parser)

        # For custom transforms, first extract the value to a temp column
        temp_col = f"_temp_{output_col}"
        df = df.withColumn(temp_col, source_col)

        # Try to get Spark expression
        spark_expr_str = self.transform_library.get_spark_expr(
            function_name, temp_col, **params
        )

        if spark_expr_str:
            df = df.withColumn(output_col, expr(spark_expr_str))
            return df.drop(temp_col)

        # No Spark expression available - return extracted value directly
        # (UDF fallback not used in local mode due to serialization issues)
        df = df.withColumn(output_col, col(temp_col))
        return df.drop(temp_col)

    def _add_lineage(self, df: DataFrame, config: MappingConfig) -> DataFrame:
        """Add lineage tracking columns."""
        return df.withColumn(
            "_ingestion_metadata",
            struct(
                lit(config.id).alias("mapping_id"),
                lit(config.version).alias("mapping_version"),
                current_timestamp().alias("ingestion_timestamp"),
                monotonically_increasing_id().alias("ingestion_row_id"),
            )
        )

    def _run_validations(
        self,
        df: DataFrame,
        validations: List[ValidationRule]
    ) -> Tuple[DataFrame, int, List[Dict]]:
        """Run validation rules and return results."""
        errors = []
        total_failures = 0

        for validation in validations:
            try:
                # Evaluate validation rule
                rule_expr = validation.rule
                import re
                rule_expr = re.sub(r'\$\{(\w+)\}', r'\1', rule_expr)

                # Count failures
                failure_count = df.filter(f"NOT ({rule_expr})").count()

                if failure_count > 0:
                    total_failures += failure_count
                    errors.append({
                        "validation_id": validation.id,
                        "rule": validation.rule,
                        "severity": validation.severity.value,
                        "message": validation.message,
                        "failure_count": failure_count,
                    })

                    # Add validation result column
                    if validation.severity == Severity.ERROR:
                        # Flag records that fail
                        df = df.withColumn(
                            f"_validation_{validation.id}",
                            when(expr(rule_expr), lit("PASS")).otherwise(lit("FAIL"))
                        )

            except Exception as e:
                errors.append({
                    "validation_id": validation.id,
                    "rule": validation.rule,
                    "severity": "ERROR",
                    "message": f"Validation error: {str(e)}",
                    "failure_count": -1,
                })

        return df, total_failures, errors

    def process_by_type(
        self,
        source_df: DataFrame,
        message_type: str
    ) -> IngestionResult:
        """
        Process by message type, auto-selecting appropriate mapping.

        Args:
            source_df: Source DataFrame
            message_type: Message type (e.g., "pain.001", "MT103")

        Returns:
            IngestionResult
        """
        # Find mapping for message type
        mapping_id = self._find_mapping_for_type(message_type)
        if not mapping_id:
            raise ValueError(f"No mapping found for message type: {message_type}")

        return self.process(source_df, mapping_id=mapping_id)

    def _find_mapping_for_type(self, message_type: str) -> Optional[str]:
        """Find mapping ID for a message type."""
        # Normalize message type
        msg_type = message_type.upper().replace(".", "_")

        # Search registry
        for mapping_id, path in self._mapping_registry.items():
            if msg_type in mapping_id.upper():
                return mapping_id

        return None

    def list_available_mappings(self) -> List[Dict[str, str]]:
        """List all available mappings."""
        return [
            {"id": mid, "path": path}
            for mid, path in self._mapping_registry.items()
        ]

    def validate_mapping(self, mapping_path: str) -> List[str]:
        """
        Validate a mapping file without executing.

        Returns list of validation errors.
        """
        errors = []

        try:
            compiled = self.compiler.compile(mapping_path)

            # Add warnings as errors
            for warning in compiled.warnings:
                errors.append(str(warning))

            # Validate parser exists
            try:
                self.parser_registry.get_parser(compiled.config.source)
            except ValueError as e:
                errors.append(f"Parser error: {e}")

            # Validate lookup tables exist
            for table in compiled.lookup_tables:
                if not self.lookup_manager.get(table):
                    errors.append(f"Unknown lookup table: {table}")

        except Exception as e:
            errors.append(f"Compilation error: {e}")

        return errors

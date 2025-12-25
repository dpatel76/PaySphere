"""
GPS Payments CDM - Mapping Compiler
====================================

Compiles YAML mapping configurations into executable transformation plans.
Validates mappings against CDM entity definitions and optimizes execution.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import re

from gps_cdm.ingestion.core.models import (
    MappingConfig,
    FieldMapping,
    TransformConfig,
    TransformType,
    DataType,
    Severity,
    ValidationRule,
)


@dataclass
class CompilationError:
    """Error encountered during mapping compilation."""
    field_id: Optional[str]
    message: str
    severity: Severity
    line_number: Optional[int] = None

    def __str__(self) -> str:
        loc = f"[{self.field_id}]" if self.field_id else ""
        line = f" (line {self.line_number})" if self.line_number else ""
        return f"{self.severity.value}{loc}{line}: {self.message}"


@dataclass
class ExecutionStep:
    """Single step in the execution plan."""
    field_mapping: FieldMapping
    order: int
    dependencies: List[str]
    spark_expr: Optional[str] = None
    is_optimized: bool = False


@dataclass
class CompiledMapping:
    """Compiled and validated mapping ready for execution."""
    config: MappingConfig
    execution_plan: List[ExecutionStep]
    spark_sql: Optional[str] = None
    warnings: List[CompilationError] = field(default_factory=list)

    # Statistics
    total_fields: int = 0
    optimized_fields: int = 0
    lookup_tables: Set[str] = field(default_factory=set)
    target_entities: Set[str] = field(default_factory=set)

    def get_optimization_ratio(self) -> float:
        """Get ratio of fields that can use native Spark SQL."""
        if self.total_fields == 0:
            return 0.0
        return self.optimized_fields / self.total_fields


class CDMValidator:
    """Validates mappings against CDM entity definitions."""

    # CDM Entity definitions with their attributes
    # Reference: /documents/cdm/ entity specifications
    # Extended to support all payment standards (ISO20022, SWIFT MT, Regional)
    CDM_ENTITIES = {
        "Payment": {
            "payment_id", "payment_type", "status", "creation_datetime",
            "settlement_date", "requested_execution_date", "requested_execution_datetime",
            "purpose_code", "regulatory_reporting_code", "batch_id", "message_id",
            "number_of_transactions", "control_sum", "priority", "category_purpose",
            "local_instrument", "service_level", "clearing_channel",
        },
        "PaymentInstruction": {
            "instruction_id", "payment_id", "sequence_number", "end_to_end_id",
            "uetr", "instruction_identification", "instructed_amount",
            "instructed_currency", "settlement_amount", "settlement_currency",
            "settlement_date", "exchange_rate", "charge_bearer", "remittance_information",
            "original_amount", "original_currency", "purpose_code", "purpose_proprietary",
            "sender_to_receiver_info", "bank_operation_code", "instruction_code",
            "transaction_type_code", "regulatory_reporting",
        },
        "Party": {
            "party_id", "party_type", "party_role", "name", "family_name",
            "given_name", "legal_name", "trading_name", "date_of_birth",
            "country_of_birth", "nationality", "tax_id", "tax_id_type",
            "lei", "registration_number", "industry_code", "bic",
            "account_number", "party_identifier", "contact_phone", "contact_email",
        },
        "PartyIdentification": {
            "identification_id", "party_id", "identification_type",
            "identification_value", "issuer", "issue_date", "expiry_date",
            "country_of_issue",
        },
        "Account": {
            "account_id", "account_type", "account_number", "account_name",
            "iban", "bban", "currency", "status", "opening_date",
            "closing_date", "institution_id", "owner_party_id", "proxy_type", "proxy_id",
        },
        "FinancialInstitution": {
            "institution_id", "bic", "clearing_system_id", "member_id",
            "institution_name", "branch_id", "country", "lei",
            "clearing_member_id", "postal_address",
        },
        "Address": {
            "address_id", "party_id", "address_type", "street_name",
            "building_number", "building_name", "floor", "post_box",
            "postal_code", "town_name", "country_subdivision", "country",
            "address_lines", "department", "sub_department", "room",
        },
        "PaymentCharges": {
            "charge_id", "instruction_id", "charge_type", "charge_amount",
            "charge_currency", "bearer", "agent_id",
            "sender_charges", "receiver_charges", "total_charges",
        },
        "TransactionReference": {
            "reference_id", "payment_id", "reference_type", "reference_value",
            "issuer", "issue_date", "related_reference", "clearing_reference",
        },
        "RegulatoryReporting": {
            "reporting_id", "payment_id", "authority", "report_type",
            "details", "country", "amount", "currency", "date_time",
            "debit_credit_indicator", "information",
        },
        "Document": {
            "document_id", "document_type", "document_number", "line_details",
            "issue_date", "expiry_date", "issuer", "payment_id",
            "referred_document_amount",
        },
        "Agent": {
            "agent_id", "payment_id", "agent_role", "institution_id",
            "account_id", "sequence", "correspondent_bic", "correspondent_location",
            "receiver_correspondent_bic", "intermediary_bic",
        },
        "ExchangeRate": {
            "rate_id", "instruction_id", "source_currency", "target_currency",
            "rate", "rate_type", "contract_id", "quotation_date",
        },
        "PaymentStatus": {
            "status_id", "payment_id", "status_code", "status_reason",
            "effective_datetime", "reporter_id", "original_message_id",
        },
        "SettlementInstruction": {
            "settlement_id", "payment_id", "method", "priority",
            "clearing_system", "settlement_account_id",
        },
        "BatchHeader": {
            "batch_id", "creation_datetime", "message_id", "initiating_party_id",
            "number_of_transactions", "control_sum", "payment_information_id",
            "payment_method", "batch_booking", "service_level",
        },
    }

    # CDM Data type mappings
    CDM_ATTRIBUTE_TYPES = {
        "payment_id": DataType.UUID,
        "amount": DataType.DECIMAL,
        "instructed_amount": DataType.DECIMAL,
        "settlement_amount": DataType.DECIMAL,
        "charge_amount": DataType.DECIMAL,
        "control_sum": DataType.DECIMAL,
        "exchange_rate": DataType.DECIMAL,
        "rate": DataType.DECIMAL,
        "date_of_birth": DataType.DATE,
        "settlement_date": DataType.DATE,
        "issue_date": DataType.DATE,
        "expiry_date": DataType.DATE,
        "opening_date": DataType.DATE,
        "closing_date": DataType.DATE,
        "creation_datetime": DataType.DATETIME,
        "effective_datetime": DataType.DATETIME,
        "date_time": DataType.DATETIME,
        "number_of_transactions": DataType.INTEGER,
        "sequence_number": DataType.INTEGER,
        "sequence": DataType.INTEGER,
    }

    @classmethod
    def validate_entity(cls, entity: str) -> Optional[str]:
        """Validate entity exists in CDM. Returns error message if invalid."""
        if entity not in cls.CDM_ENTITIES:
            return f"Unknown CDM entity: '{entity}'. Valid entities: {sorted(cls.CDM_ENTITIES.keys())}"
        return None

    @classmethod
    def validate_attribute(cls, entity: str, attribute: str) -> Optional[str]:
        """Validate attribute exists for entity. Returns error message if invalid."""
        if entity not in cls.CDM_ENTITIES:
            return f"Cannot validate attribute '{attribute}' for unknown entity '{entity}'"

        if attribute not in cls.CDM_ENTITIES[entity]:
            return (
                f"Unknown attribute '{attribute}' for entity '{entity}'. "
                f"Valid attributes: {sorted(cls.CDM_ENTITIES[entity])}"
            )
        return None

    @classmethod
    def get_expected_type(cls, attribute: str) -> DataType:
        """Get expected data type for an attribute."""
        return cls.CDM_ATTRIBUTE_TYPES.get(attribute, DataType.STRING)


class SparkSQLGenerator:
    """Generates optimized Spark SQL expressions from field mappings."""

    # Transform types that can be fully expressed in Spark SQL
    OPTIMIZABLE_TRANSFORMS = {
        TransformType.DIRECT,
        TransformType.LOOKUP,
        TransformType.EXPRESSION,
        TransformType.CONDITIONAL,
        TransformType.REGEX,
        TransformType.TEMPLATE,
    }

    @classmethod
    def can_optimize(cls, mapping: FieldMapping) -> bool:
        """Check if field mapping can be compiled to Spark SQL."""
        if mapping.transform is None:
            return True  # Direct copy
        return mapping.transform.type in cls.OPTIMIZABLE_TRANSFORMS

    @classmethod
    def generate_expression(cls, mapping: FieldMapping, source_alias: str = "src") -> str:
        """Generate Spark SQL expression for field mapping."""
        if mapping.transform is None:
            # Direct mapping
            return cls._direct_expr(mapping, source_alias)

        transform_type = mapping.transform.type

        if transform_type == TransformType.DIRECT:
            return cls._direct_expr(mapping, source_alias)
        elif transform_type == TransformType.LOOKUP:
            return cls._lookup_expr(mapping, source_alias)
        elif transform_type == TransformType.EXPRESSION:
            return cls._expression_expr(mapping, source_alias)
        elif transform_type == TransformType.CONDITIONAL:
            return cls._conditional_expr(mapping, source_alias)
        elif transform_type == TransformType.REGEX:
            return cls._regex_expr(mapping, source_alias)
        elif transform_type == TransformType.TEMPLATE:
            return cls._template_expr(mapping, source_alias)
        elif transform_type == TransformType.MERGE:
            return cls._merge_expr(mapping, source_alias)
        else:
            raise ValueError(f"Cannot generate SQL for transform type: {transform_type}")

    @classmethod
    def _direct_expr(cls, mapping: FieldMapping, source_alias: str) -> str:
        """Direct field copy with type conversion."""
        source = mapping.source
        cast_expr = cls._type_cast(f"{source_alias}.{source}", mapping.data_type)
        return cast_expr

    @classmethod
    def _lookup_expr(cls, mapping: FieldMapping, source_alias: str) -> str:
        """Lookup transformation via map or join."""
        transform = mapping.transform
        source = mapping.source

        if transform.mapping:
            # Inline map using CASE WHEN
            cases = []
            for key, value in transform.mapping.items():
                cases.append(f"WHEN {source_alias}.{source} = '{key}' THEN '{value}'")

            default = f"'{transform.default}'" if transform.default else "NULL"
            return f"CASE {' '.join(cases)} ELSE {default} END"
        elif transform.table:
            # Will need join - return placeholder
            return f"lookup_{transform.table}.value"
        else:
            return f"{source_alias}.{source}"

    @classmethod
    def _expression_expr(cls, mapping: FieldMapping, source_alias: str) -> str:
        """Custom expression."""
        expr = mapping.transform.expr
        # Replace field references with qualified names
        expr = re.sub(r'\$\{(\w+)\}', rf'{source_alias}.\1', expr)
        return expr

    @classmethod
    def _conditional_expr(cls, mapping: FieldMapping, source_alias: str) -> str:
        """Conditional expression."""
        condition = mapping.condition or mapping.transform.expr
        source = mapping.source

        # Simple condition format: value if condition
        condition = re.sub(r'\$\{(\w+)\}', rf'{source_alias}.\1', condition)
        return f"CASE WHEN {condition} THEN {source_alias}.{source} ELSE NULL END"

    @classmethod
    def _regex_expr(cls, mapping: FieldMapping, source_alias: str) -> str:
        """Regex extraction."""
        transform = mapping.transform
        source = mapping.source
        pattern = transform.pattern
        group = transform.group or 0

        return f"regexp_extract({source_alias}.{source}, '{pattern}', {group})"

    @classmethod
    def _template_expr(cls, mapping: FieldMapping, source_alias: str) -> str:
        """String template."""
        transform = mapping.transform
        template = transform.template

        # Replace ${field} with concat patterns
        def replace_field(match):
            field_name = match.group(1)
            return f"', {source_alias}.{field_name}, '"

        result = re.sub(r'\$\{(\w+)\}', replace_field, template)
        return f"concat('{result}')"

    @classmethod
    def _merge_expr(cls, mapping: FieldMapping, source_alias: str) -> str:
        """Merge multiple sources."""
        sources = mapping.sources or []
        qualified = [f"{source_alias}.{s}" for s in sources]
        return f"coalesce({', '.join(qualified)})"

    @classmethod
    def _type_cast(cls, expr: str, data_type: DataType) -> str:
        """Add type casting to expression."""
        type_map = {
            DataType.STRING: "STRING",
            DataType.INTEGER: "INT",
            DataType.DECIMAL: "DECIMAL(18,4)",
            DataType.BOOLEAN: "BOOLEAN",
            DataType.DATE: "DATE",
            DataType.DATETIME: "TIMESTAMP",
            DataType.TIME: "STRING",
            DataType.UUID: "STRING",
        }

        spark_type = type_map.get(data_type, "STRING")
        return f"CAST({expr} AS {spark_type})"


class MappingCompiler:
    """
    Compiles YAML mapping configurations into executable plans.

    Responsibilities:
    1. Parse and validate YAML syntax
    2. Validate against CDM entity definitions
    3. Build dependency graph for execution ordering
    4. Generate optimized Spark SQL where possible
    5. Produce execution plan with warnings
    """

    def __init__(self, cdm_validator: CDMValidator = None):
        self.cdm_validator = cdm_validator or CDMValidator()
        self.errors: List[CompilationError] = []
        self.warnings: List[CompilationError] = []

    def compile(
        self,
        mapping_path: str,
        stage: str = "bronze_to_silver"
    ) -> CompiledMapping:
        """
        Compile a YAML mapping file into an executable plan.

        Args:
            mapping_path: Path to YAML mapping file
            stage: For medallion format, which stage to use ("bronze_to_silver" or "silver_to_gold")

        Returns:
            CompiledMapping with execution plan

        Raises:
            CompilationError if critical errors found
        """
        self.errors = []
        self.warnings = []

        path = Path(mapping_path)

        # Load YAML
        config = self._load_yaml(path, stage=stage)
        if config is None:
            raise ValueError(f"Failed to load mapping: {path}")

        # Validate against CDM
        self._validate_cdm_targets(config)

        # Build dependency graph
        dependencies = self._build_dependency_graph(config.fields)

        # Order fields by dependencies
        ordered_fields = self._topological_sort(config.fields, dependencies)

        # Generate execution plan
        execution_plan = self._generate_execution_plan(ordered_fields, dependencies)

        # Generate optimized SQL if possible
        spark_sql = self._generate_spark_sql(config, execution_plan)

        # Collect statistics
        total_fields = len(config.fields)
        optimized_fields = sum(1 for step in execution_plan if step.is_optimized)
        lookup_tables = self._collect_lookup_tables(config.fields)
        target_entities = set(config.get_entities())

        # Raise if critical errors
        critical_errors = [e for e in self.errors if e.severity == Severity.ERROR]
        if critical_errors:
            error_msgs = "\n".join(str(e) for e in critical_errors)
            raise ValueError(f"Compilation failed with errors:\n{error_msgs}")

        return CompiledMapping(
            config=config,
            execution_plan=execution_plan,
            spark_sql=spark_sql,
            warnings=self.warnings,
            total_fields=total_fields,
            optimized_fields=optimized_fields,
            lookup_tables=lookup_tables,
            target_entities=target_entities,
        )

    def compile_from_dict(self, data: Dict, source_path: Optional[Path] = None) -> CompiledMapping:
        """Compile from dictionary (already parsed YAML)."""
        self.errors = []
        self.warnings = []

        config = MappingConfig.from_dict(data, source_path)

        # Validate against CDM
        self._validate_cdm_targets(config)

        # Build dependency graph
        dependencies = self._build_dependency_graph(config.fields)

        # Order fields by dependencies
        ordered_fields = self._topological_sort(config.fields, dependencies)

        # Generate execution plan
        execution_plan = self._generate_execution_plan(ordered_fields, dependencies)

        # Generate optimized SQL if possible
        spark_sql = self._generate_spark_sql(config, execution_plan)

        # Collect statistics
        total_fields = len(config.fields)
        optimized_fields = sum(1 for step in execution_plan if step.is_optimized)
        lookup_tables = self._collect_lookup_tables(config.fields)
        target_entities = set(config.get_entities())

        # Raise if critical errors
        critical_errors = [e for e in self.errors if e.severity == Severity.ERROR]
        if critical_errors:
            error_msgs = "\n".join(str(e) for e in critical_errors)
            raise ValueError(f"Compilation failed with errors:\n{error_msgs}")

        return CompiledMapping(
            config=config,
            execution_plan=execution_plan,
            spark_sql=spark_sql,
            warnings=self.warnings,
            total_fields=total_fields,
            optimized_fields=optimized_fields,
            lookup_tables=lookup_tables,
            target_entities=target_entities,
        )

    def _load_yaml(
        self,
        path: Path,
        stage: str = "bronze_to_silver"
    ) -> Optional[MappingConfig]:
        """Load and parse YAML mapping file."""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            return MappingConfig.from_dict(data, path, stage=stage)
        except yaml.YAMLError as e:
            self.errors.append(CompilationError(
                field_id=None,
                message=f"YAML parse error: {e}",
                severity=Severity.ERROR,
            ))
            return None
        except Exception as e:
            self.errors.append(CompilationError(
                field_id=None,
                message=f"Failed to load mapping: {e}",
                severity=Severity.ERROR,
            ))
            return None

    def _validate_cdm_targets(self, config: MappingConfig) -> None:
        """Validate all target entities and attributes against CDM.

        For medallion format (stage-based mappings), the "Staging" entity is
        used as a placeholder and is not validated against CDM entities.
        """
        # Skip validation for medallion format (targets are staging columns, not CDM entities)
        is_medallion = config.stage is not None

        for i, field in enumerate(config.fields):
            if not field.target:
                continue

            field_id = f"field[{i}]"

            # Skip CDM validation for Staging entity (medallion format)
            if is_medallion or field.target.entity == "Staging":
                continue

            # Validate entity
            entity_error = CDMValidator.validate_entity(field.target.entity)
            if entity_error:
                self.errors.append(CompilationError(
                    field_id=field_id,
                    message=entity_error,
                    severity=Severity.ERROR,
                ))
                continue

            # Validate attribute
            attr_error = CDMValidator.validate_attribute(
                field.target.entity,
                field.target.attribute
            )
            if attr_error:
                self.errors.append(CompilationError(
                    field_id=field_id,
                    message=attr_error,
                    severity=Severity.ERROR,
                ))
                continue

            # Check type compatibility
            expected_type = CDMValidator.get_expected_type(field.target.attribute)
            if field.data_type != expected_type and expected_type != DataType.STRING:
                self.warnings.append(CompilationError(
                    field_id=field_id,
                    message=(
                        f"Type mismatch: field declares '{field.data_type.value}' "
                        f"but CDM expects '{expected_type.value}' for {field.target.attribute}"
                    ),
                    severity=Severity.WARNING,
                ))

    def _build_dependency_graph(
        self,
        fields: List[FieldMapping]
    ) -> Dict[int, List[int]]:
        """Build dependency graph between fields."""
        dependencies: Dict[int, List[int]] = defaultdict(list)

        # Build index of target columns to field index
        target_to_idx = {}
        for i, field in enumerate(fields):
            if field.target:
                col_name = f"{field.target.entity}__{field.target.attribute}"
                target_to_idx[col_name] = i

        # Find dependencies via depends_on and expression references
        for i, field in enumerate(fields):
            if field.transform and field.transform.depends_on:
                for dep in field.transform.depends_on:
                    if dep in target_to_idx:
                        dependencies[i].append(target_to_idx[dep])

            # Check expression for ${field} references
            if field.transform and field.transform.expr:
                refs = re.findall(r'\$\{(\w+__\w+)\}', field.transform.expr)
                for ref in refs:
                    if ref in target_to_idx:
                        dependencies[i].append(target_to_idx[ref])

        return dependencies

    def _topological_sort(
        self,
        fields: List[FieldMapping],
        dependencies: Dict[int, List[int]]
    ) -> List[Tuple[int, FieldMapping]]:
        """Sort fields by dependencies using topological sort."""
        n = len(fields)
        in_degree = [0] * n

        for i in range(n):
            for dep in dependencies[i]:
                in_degree[i] += 1

        # Start with fields that have no dependencies
        queue = [i for i in range(n) if in_degree[i] == 0]
        result = []

        while queue:
            idx = queue.pop(0)
            result.append((idx, fields[idx]))

            # Find fields that depend on this one
            for i in range(n):
                if idx in dependencies[i]:
                    in_degree[i] -= 1
                    if in_degree[i] == 0:
                        queue.append(i)

        # Check for cycles
        if len(result) != n:
            self.warnings.append(CompilationError(
                field_id=None,
                message="Circular dependency detected in field mappings",
                severity=Severity.WARNING,
            ))
            # Add remaining fields at end
            remaining = [i for i in range(n) if i not in [r[0] for r in result]]
            for i in remaining:
                result.append((i, fields[i]))

        return result

    def _generate_execution_plan(
        self,
        ordered_fields: List[Tuple[int, FieldMapping]],
        dependencies: Dict[int, List[int]]
    ) -> List[ExecutionStep]:
        """Generate execution plan from ordered fields."""
        plan = []

        for order, (idx, field) in enumerate(ordered_fields):
            can_optimize = SparkSQLGenerator.can_optimize(field)
            spark_expr = None

            if can_optimize:
                try:
                    spark_expr = SparkSQLGenerator.generate_expression(field)
                except Exception as e:
                    self.warnings.append(CompilationError(
                        field_id=f"field[{idx}]",
                        message=f"Could not generate Spark SQL: {e}",
                        severity=Severity.WARNING,
                    ))
                    can_optimize = False

            step = ExecutionStep(
                field_mapping=field,
                order=order,
                dependencies=[d for d in dependencies[idx]],
                spark_expr=spark_expr,
                is_optimized=can_optimize,
            )
            plan.append(step)

        return plan

    def _generate_spark_sql(
        self,
        config: MappingConfig,
        execution_plan: List[ExecutionStep]
    ) -> Optional[str]:
        """Generate complete Spark SQL if all fields are optimizable."""
        # Check if we can generate full SQL
        if not all(step.is_optimized for step in execution_plan):
            return None

        # Build SELECT clause
        select_parts = []
        for step in execution_plan:
            field = step.field_mapping
            if field.target:
                col_name = f"{field.target.entity}__{field.target.attribute}"
                select_parts.append(f"  {step.spark_expr} AS {col_name}")

        # Build SQL
        sql = f"""
-- Auto-generated Spark SQL for {config.name}
-- Mapping ID: {config.id}
-- Generated fields: {len(select_parts)}

SELECT
{',\n'.join(select_parts)}
FROM source_data src
"""
        return sql.strip()

    def _collect_lookup_tables(self, fields: List[FieldMapping]) -> Set[str]:
        """Collect all lookup tables referenced in mappings."""
        tables = set()
        for field in fields:
            if field.transform and field.transform.table:
                tables.add(field.transform.table)
        return tables

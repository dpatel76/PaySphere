"""
GPS CDM - Data Quality Validator
=================================

Validates data quality at each layer of the medallion pipeline.
Executes rules defined in obs_dq_rules table, stores per-record results,
and calculates aggregated metrics.

Usage:
    validator = DataQualityValidator(db_connection)

    # Validate a single record
    result = validator.validate_record(record, "silver", "stg_pain001", "batch123")

    # Validate entire batch
    batch_result = validator.validate_batch("batch123", "silver", "stg_pain001")

    # Get DQ metrics
    metrics = validator.get_metrics(batch_id="batch123", layer="gold")
"""

import uuid
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class DQDimension(str, Enum):
    """Data quality dimensions."""
    COMPLETENESS = "COMPLETENESS"
    VALIDITY = "VALIDITY"
    ACCURACY = "ACCURACY"
    CONSISTENCY = "CONSISTENCY"
    UNIQUENESS = "UNIQUENESS"
    TIMELINESS = "TIMELINESS"
    CUSTOM = "CUSTOM"


class DQStatus(str, Enum):
    """Data quality status."""
    NOT_VALIDATED = "NOT_VALIDATED"
    VALIDATING = "VALIDATING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


@dataclass
class DQRule:
    """Represents a data quality rule."""
    rule_id: str
    rule_name: str
    layer: str
    table_name: str
    field_name: Optional[str]
    rule_type: str
    rule_expression: str
    expression_type: str = "SQL"
    weight: float = 1.0
    error_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    is_blocking: bool = False
    is_active: bool = True


@dataclass
class DQRuleResult:
    """Result of evaluating a single rule on a record."""
    rule_id: str
    rule_name: str
    rule_type: str
    passed: bool
    actual_value: Optional[str] = None
    expected_value: Optional[str] = None
    error_message: Optional[str] = None
    weight: float = 1.0
    score: float = 0.0  # 0 or 100


@dataclass
class DQRecordResult:
    """Result of validating a single record."""
    record_id: str
    layer: str
    table_name: str
    status: str
    overall_score: float
    rule_results: List[DQRuleResult] = field(default_factory=list)
    passed_rules: int = 0
    failed_rules: int = 0
    blocking_failures: int = 0

    @property
    def passed(self) -> bool:
        return self.blocking_failures == 0 and self.overall_score >= 70


@dataclass
class DQBatchResult:
    """Result of validating a batch."""
    batch_id: str
    layer: str
    table_name: str
    status: str
    overall_score: float
    total_records: int = 0
    passed_records: int = 0
    failed_records: int = 0
    warning_records: int = 0
    rules_executed: int = 0
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    validated_at: Optional[datetime] = None


@dataclass
class DQMetrics:
    """Aggregated data quality metrics."""
    layer: str
    table_name: str
    batch_id: Optional[str]
    completeness_score: Optional[float] = None
    validity_score: Optional[float] = None
    accuracy_score: Optional[float] = None
    consistency_score: Optional[float] = None
    uniqueness_score: Optional[float] = None
    timeliness_score: Optional[float] = None
    overall_score: Optional[float] = None
    overall_status: str = "NOT_VALIDATED"
    total_records: int = 0
    passed_records: int = 0
    failed_records: int = 0


class DataQualityValidator:
    """
    Validates data quality using configurable rules.

    Supports SQL-based and Python-based rule expressions.
    Stores results in obs_data_quality_results and calculates
    metrics in obs_data_quality_metrics.
    """

    def __init__(self, db_connection):
        """
        Initialize the validator.

        Args:
            db_connection: Database connection (psycopg2 or compatible)
        """
        self.db = db_connection
        self._rules_cache: Dict[str, List[DQRule]] = {}

    def get_rules(
        self,
        layer: str,
        table_name: str,
        active_only: bool = True,
    ) -> List[DQRule]:
        """Get DQ rules for a specific layer/table."""
        cache_key = f"{layer}:{table_name}"
        if cache_key in self._rules_cache:
            return self._rules_cache[cache_key]

        conditions = ["layer = %s", "table_name = %s"]
        params = [layer, table_name]

        if active_only:
            conditions.append("is_active = true")

        sql = f"""
            SELECT rule_id, rule_name, layer, table_name, field_name,
                   rule_type, rule_expression, expression_type,
                   weight, error_threshold, warning_threshold,
                   is_blocking, is_active
            FROM observability.obs_dq_rules
            WHERE {' AND '.join(conditions)}
            ORDER BY is_blocking DESC, weight DESC, rule_id
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            rules = []
            for row in cursor.fetchall():
                rules.append(DQRule(
                    rule_id=row[0],
                    rule_name=row[1],
                    layer=row[2],
                    table_name=row[3],
                    field_name=row[4],
                    rule_type=row[5],
                    rule_expression=row[6],
                    expression_type=row[7] or "SQL",
                    weight=float(row[8]) if row[8] else 1.0,
                    error_threshold=float(row[9]) if row[9] else None,
                    warning_threshold=float(row[10]) if row[10] else None,
                    is_blocking=row[11],
                    is_active=row[12],
                ))
            self._rules_cache[cache_key] = rules
            return rules
        finally:
            cursor.close()

    def _evaluate_sql_rule(
        self,
        rule: DQRule,
        record: Dict,
    ) -> DQRuleResult:
        """Evaluate a SQL-based rule against a record."""
        # For SQL rules, we substitute field values into the expression
        expression = rule.rule_expression

        # Replace field references with actual values
        for field, value in record.items():
            placeholder = field
            if value is None:
                expression = expression.replace(f"{placeholder} IS NOT NULL", "FALSE")
                expression = expression.replace(f"{placeholder} IS NULL", "TRUE")
                expression = expression.replace(placeholder, "NULL")
            elif isinstance(value, str):
                expression = expression.replace(placeholder, f"'{value}'")
            elif isinstance(value, (int, float, Decimal)):
                expression = expression.replace(placeholder, str(value))
            elif isinstance(value, bool):
                expression = expression.replace(placeholder, "TRUE" if value else "FALSE")

        # Try to evaluate simple expressions locally
        try:
            # Handle simple cases
            result = self._evaluate_simple_expression(expression, record)
            if result is not None:
                passed = result
            else:
                # Fall back to database evaluation
                cursor = self.db.cursor()
                try:
                    cursor.execute(f"SELECT {expression}")
                    passed = cursor.fetchone()[0]
                finally:
                    cursor.close()

            return DQRuleResult(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                rule_type=rule.rule_type,
                passed=bool(passed),
                actual_value=str(record.get(rule.field_name)) if rule.field_name else None,
                weight=rule.weight,
                score=100.0 if passed else 0.0,
            )
        except Exception as e:
            return DQRuleResult(
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                rule_type=rule.rule_type,
                passed=False,
                error_message=f"Rule evaluation error: {str(e)}",
                weight=rule.weight,
                score=0.0,
            )

    def _evaluate_simple_expression(
        self,
        expression: str,
        record: Dict,
    ) -> Optional[bool]:
        """
        Try to evaluate simple expressions without database.

        Returns None if expression is too complex.
        """
        expr = expression.strip()

        # Handle IS NOT NULL
        if " IS NOT NULL" in expr:
            field = expr.replace(" IS NOT NULL", "").strip().strip("'")
            if field in record:
                return record[field] is not None and record[field] != ''
            return False

        # Handle IS NULL
        if " IS NULL" in expr:
            field = expr.replace(" IS NULL", "").strip().strip("'")
            if field in record:
                return record[field] is None or record[field] == ''
            return True

        # Handle > 0 checks
        if " > 0" in expr:
            field = expr.replace(" > 0", "").strip().strip("'")
            if field in record:
                try:
                    return float(record[field]) > 0
                except (TypeError, ValueError):
                    return False
            return False

        # Handle LENGTH() = N
        match = re.match(r"LENGTH\('?(\w+)'?\)\s*=\s*(\d+)", expr)
        if match:
            field = match.group(1)
            expected_len = int(match.group(2))
            value = record.get(field)
            if value:
                return len(str(value)) == expected_len
            return False

        # Handle LENGTH() IN (N, M)
        match = re.match(r"LENGTH\('?(\w+)'?\)\s*IN\s*\((\d+),\s*(\d+)\)", expr)
        if match:
            field = match.group(1)
            len1 = int(match.group(2))
            len2 = int(match.group(3))
            value = record.get(field)
            if value:
                return len(str(value)) in (len1, len2)
            return False

        # Handle LENGTH() BETWEEN
        match = re.match(r"LENGTH\('?(\w+)'?\)\s*BETWEEN\s*(\d+)\s*AND\s*(\d+)", expr)
        if match:
            field = match.group(1)
            min_len = int(match.group(2))
            max_len = int(match.group(3))
            value = record.get(field)
            if value:
                return min_len <= len(str(value)) <= max_len
            return False

        # Handle simple OR with IS NULL
        if " OR " in expr and " IS NULL" in expr:
            parts = expr.split(" OR ")
            for part in parts:
                part = part.strip()
                result = self._evaluate_simple_expression(part, record)
                if result:
                    return True
            return False

        return None  # Can't evaluate locally

    def validate_record(
        self,
        record: Dict,
        layer: str,
        table_name: str,
        batch_id: str,
        record_id: Optional[str] = None,
        store_results: bool = True,
    ) -> DQRecordResult:
        """
        Validate a single record against all applicable rules.

        Args:
            record: Record data as dictionary
            layer: Layer (bronze, silver, gold)
            table_name: Table name
            batch_id: Batch identifier
            record_id: Record ID (auto-detected if not provided)
            store_results: Whether to store results in database

        Returns:
            DQRecordResult with validation outcome
        """
        # Detect record ID
        if not record_id:
            for id_field in ['stg_id', 'raw_id', 'instruction_id', 'id']:
                if id_field in record:
                    record_id = str(record[id_field])
                    break
            if not record_id:
                record_id = str(uuid.uuid4())

        rules = self.get_rules(layer, table_name)
        if not rules:
            return DQRecordResult(
                record_id=record_id,
                layer=layer,
                table_name=table_name,
                status=DQStatus.PASSED.value,
                overall_score=100.0,
            )

        result = DQRecordResult(
            record_id=record_id,
            layer=layer,
            table_name=table_name,
            status=DQStatus.VALIDATING.value,
            overall_score=0.0,
        )

        total_weight = 0.0
        weighted_score = 0.0

        for rule in rules:
            rule_result = self._evaluate_sql_rule(rule, record)
            result.rule_results.append(rule_result)

            if rule_result.passed:
                result.passed_rules += 1
            else:
                result.failed_rules += 1
                if rule.is_blocking:
                    result.blocking_failures += 1

            total_weight += rule_result.weight
            weighted_score += rule_result.score * rule_result.weight

            # Store individual rule result
            if store_results:
                self._store_rule_result(
                    batch_id=batch_id,
                    layer=layer,
                    table_name=table_name,
                    record_id=record_id,
                    rule_result=rule_result,
                    rule=rule,
                )

        # Calculate overall score
        if total_weight > 0:
            result.overall_score = weighted_score / total_weight
        else:
            result.overall_score = 100.0

        # Determine status
        if result.blocking_failures > 0:
            result.status = DQStatus.FAILED.value
        elif result.overall_score >= 90:
            result.status = DQStatus.PASSED.value
        elif result.overall_score >= 70:
            result.status = DQStatus.WARNING.value
        else:
            result.status = DQStatus.FAILED.value

        return result

    def _store_rule_result(
        self,
        batch_id: str,
        layer: str,
        table_name: str,
        record_id: str,
        rule_result: DQRuleResult,
        rule: DQRule,
    ):
        """Store a rule result in the database."""
        sql = """
            INSERT INTO observability.obs_data_quality_results (
                dq_result_id, batch_id, layer, table_name, record_id,
                rule_id, rule_name, rule_type, rule_expression,
                passed, actual_value, expected_value, error_message,
                weight, score, validated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, CURRENT_TIMESTAMP
            )
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                str(uuid.uuid4()),
                batch_id,
                layer,
                table_name,
                record_id,
                rule_result.rule_id,
                rule_result.rule_name,
                rule_result.rule_type,
                rule.rule_expression,
                rule_result.passed,
                rule_result.actual_value,
                rule_result.expected_value,
                rule_result.error_message,
                rule_result.weight,
                rule_result.score,
            ))
            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            cursor.close()

    def validate_batch(
        self,
        batch_id: str,
        layer: str,
        table_name: str,
        update_record_status: bool = True,
    ) -> DQBatchResult:
        """
        Validate all records in a batch.

        Args:
            batch_id: Batch identifier
            layer: Layer (bronze, silver, gold)
            table_name: Table name
            update_record_status: Update dq_status on source table

        Returns:
            DQBatchResult with batch-level metrics
        """
        # Get records for batch
        records = self._get_batch_records(batch_id, layer, table_name)

        result = DQBatchResult(
            batch_id=batch_id,
            layer=layer,
            table_name=table_name,
            status=DQStatus.VALIDATING.value,
            overall_score=0.0,
            total_records=len(records),
        )

        if not records:
            result.status = DQStatus.PASSED.value
            result.overall_score = 100.0
            return result

        total_score = 0.0
        dimension_scores: Dict[str, List[float]] = {
            dim.value: [] for dim in DQDimension
        }

        rules = self.get_rules(layer, table_name)
        result.rules_executed = len(rules)

        for record in records:
            record_result = self.validate_record(
                record=record,
                layer=layer,
                table_name=table_name,
                batch_id=batch_id,
                store_results=True,
            )

            total_score += record_result.overall_score

            if record_result.status == DQStatus.PASSED.value:
                result.passed_records += 1
            elif record_result.status == DQStatus.WARNING.value:
                result.warning_records += 1
            else:
                result.failed_records += 1

            # Aggregate dimension scores
            for rule_result in record_result.rule_results:
                dim = rule_result.rule_type
                if dim in dimension_scores:
                    dimension_scores[dim].append(rule_result.score)

            # Update record status
            if update_record_status:
                self._update_record_dq_status(
                    layer, table_name, record_result.record_id,
                    record_result.status, record_result.overall_score
                )

        # Calculate averages
        result.overall_score = total_score / len(records) if records else 100.0

        for dim, scores in dimension_scores.items():
            if scores:
                result.dimension_scores[dim] = sum(scores) / len(scores)

        # Determine overall status
        if result.failed_records == 0:
            result.status = DQStatus.PASSED.value
        elif result.failed_records / result.total_records > 0.1:
            result.status = DQStatus.FAILED.value
        else:
            result.status = DQStatus.WARNING.value

        result.validated_at = datetime.now()

        # Store metrics
        self._store_batch_metrics(result)

        return result

    def _get_batch_records(
        self,
        batch_id: str,
        layer: str,
        table_name: str,
    ) -> List[Dict]:
        """Get all records for a batch."""
        table_map = {
            ('bronze', 'raw_payment_messages'): ('bronze.raw_payment_messages', '_batch_id'),
            ('silver', 'stg_pain001'): ('silver.stg_pain001', '_batch_id'),
            ('gold', 'cdm_payment_instruction'): ('gold.cdm_payment_instruction', 'lineage_batch_id'),
        }

        full_table, batch_col = table_map.get((layer, table_name), (None, None))
        if not full_table:
            return []

        sql = f"SELECT * FROM {full_table} WHERE {batch_col} = %s"

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (batch_id,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def _update_record_dq_status(
        self,
        layer: str,
        table_name: str,
        record_id: str,
        status: str,
        score: float,
    ):
        """Update DQ status on the source record."""
        table_map = {
            ('silver', 'stg_pain001'): ('silver.stg_pain001', 'stg_id'),
            ('gold', 'cdm_payment_instruction'): ('gold.cdm_payment_instruction', 'instruction_id'),
        }

        full_table, id_col = table_map.get((layer, table_name), (None, None))
        if not full_table:
            return

        sql = f"""
            UPDATE {full_table}
            SET dq_status = %s,
                dq_score = %s,
                dq_validated_at = CURRENT_TIMESTAMP
            WHERE {id_col} = %s
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (status, score, record_id))
            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            cursor.close()

    def _store_batch_metrics(self, result: DQBatchResult):
        """Store batch-level DQ metrics."""
        sql = """
            INSERT INTO observability.obs_data_quality_metrics (
                metric_id, batch_id, layer, table_name,
                completeness_score, validity_score, accuracy_score,
                consistency_score, uniqueness_score, timeliness_score,
                overall_score, overall_status,
                total_records, passed_records, failed_records, warning_records,
                rules_executed, calculated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s,
                %s, CURRENT_TIMESTAMP
            )
        """

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, (
                str(uuid.uuid4()),
                result.batch_id,
                result.layer,
                result.table_name,
                result.dimension_scores.get('COMPLETENESS'),
                result.dimension_scores.get('VALIDITY'),
                result.dimension_scores.get('ACCURACY'),
                result.dimension_scores.get('CONSISTENCY'),
                result.dimension_scores.get('UNIQUENESS'),
                result.dimension_scores.get('TIMELINESS'),
                result.overall_score,
                result.status,
                result.total_records,
                result.passed_records,
                result.failed_records,
                result.warning_records,
                result.rules_executed,
            ))
            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            cursor.close()

    def get_metrics(
        self,
        batch_id: Optional[str] = None,
        layer: Optional[str] = None,
        table_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[DQMetrics]:
        """Get DQ metrics with filters."""
        conditions = ["1=1"]
        params = []

        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)
        if layer:
            conditions.append("layer = %s")
            params.append(layer)
        if table_name:
            conditions.append("table_name = %s")
            params.append(table_name)

        sql = f"""
            SELECT layer, table_name, batch_id,
                   completeness_score, validity_score, accuracy_score,
                   consistency_score, uniqueness_score, timeliness_score,
                   overall_score, overall_status,
                   total_records, passed_records, failed_records
            FROM observability.obs_data_quality_metrics
            WHERE {' AND '.join(conditions)}
            ORDER BY calculated_at DESC
            LIMIT %s
        """
        params.append(limit)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            return [
                DQMetrics(
                    layer=row[0],
                    table_name=row[1],
                    batch_id=row[2],
                    completeness_score=float(row[3]) if row[3] else None,
                    validity_score=float(row[4]) if row[4] else None,
                    accuracy_score=float(row[5]) if row[5] else None,
                    consistency_score=float(row[6]) if row[6] else None,
                    uniqueness_score=float(row[7]) if row[7] else None,
                    timeliness_score=float(row[8]) if row[8] else None,
                    overall_score=float(row[9]) if row[9] else None,
                    overall_status=row[10],
                    total_records=row[11] or 0,
                    passed_records=row[12] or 0,
                    failed_records=row[13] or 0,
                )
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()

    def get_failed_records(
        self,
        batch_id: Optional[str] = None,
        layer: Optional[str] = None,
        table_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get records with DQ failures."""
        conditions = ["passed = false"]
        params = []

        if batch_id:
            conditions.append("batch_id = %s")
            params.append(batch_id)
        if layer:
            conditions.append("layer = %s")
            params.append(layer)
        if table_name:
            conditions.append("table_name = %s")
            params.append(table_name)

        sql = f"""
            SELECT DISTINCT record_id, layer, table_name, batch_id,
                   array_agg(rule_id) as failed_rules,
                   array_agg(error_message) FILTER (WHERE error_message IS NOT NULL) as errors
            FROM observability.obs_data_quality_results
            WHERE {' AND '.join(conditions)}
            GROUP BY record_id, layer, table_name, batch_id
            ORDER BY batch_id DESC
            LIMIT %s
        """
        params.append(limit)

        cursor = self.db.cursor()
        try:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def revalidate_record(
        self,
        layer: str,
        table_name: str,
        record_id: str,
        batch_id: str,
    ) -> DQRecordResult:
        """
        Re-validate a single record (after data correction).

        This clears previous results and runs validation fresh.
        """
        # Clear previous results for this record
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                DELETE FROM observability.obs_data_quality_results
                WHERE layer = %s AND table_name = %s AND record_id = %s
            """, (layer, table_name, record_id))
            self.db.commit()
        finally:
            cursor.close()

        # Get current record data
        records = self._get_record_by_id(layer, table_name, record_id)
        if not records:
            return DQRecordResult(
                record_id=record_id,
                layer=layer,
                table_name=table_name,
                status=DQStatus.FAILED.value,
                overall_score=0.0,
            )

        # Re-validate
        return self.validate_record(
            record=records[0],
            layer=layer,
            table_name=table_name,
            batch_id=batch_id,
            record_id=record_id,
            store_results=True,
        )

    def _get_record_by_id(
        self,
        layer: str,
        table_name: str,
        record_id: str,
    ) -> List[Dict]:
        """Get a single record by ID."""
        table_map = {
            ('bronze', 'raw_payment_messages'): ('bronze.raw_payment_messages', 'raw_id'),
            ('silver', 'stg_pain001'): ('silver.stg_pain001', 'stg_id'),
            ('gold', 'cdm_payment_instruction'): ('gold.cdm_payment_instruction', 'instruction_id'),
        }

        full_table, id_col = table_map.get((layer, table_name), (None, None))
        if not full_table:
            return []

        cursor = self.db.cursor()
        try:
            cursor.execute(f"SELECT * FROM {full_table} WHERE {id_col} = %s", (record_id,))
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            return [dict(zip(columns, row))] if row else []
        finally:
            cursor.close()

    def clear_cache(self):
        """Clear the rules cache."""
        self._rules_cache.clear()

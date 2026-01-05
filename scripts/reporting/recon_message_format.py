#!/usr/bin/env python3
"""
Message Format Reconciliation Script

This script performs comprehensive field coverage validation for a message format:
1. Standard → Silver: Validates all standard fields are mapped to Silver columns
2. Silver → Gold: Validates all Silver columns are mapped to Gold tables
3. Data Validation: Compares actual values across zones for a specific record

Usage:
    python scripts/reporting/recon_message_format.py --format pain.001
    python scripts/reporting/recon_message_format.py --format pain.001 --stg-id <uuid>
    python scripts/reporting/recon_message_format.py --format pain.001 --latest
    python scripts/reporting/recon_message_format.py --format pain.001 --output report.txt

Environment Variables:
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from decimal import Decimal
import json

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


@dataclass
class CoverageStats:
    """Statistics for coverage analysis."""
    total: int = 0
    mapped: int = 0
    unmapped: int = 0
    mandatory_total: int = 0
    mandatory_mapped: int = 0
    mandatory_unmapped: int = 0

    @property
    def coverage_pct(self) -> float:
        return (self.mapped / self.total * 100) if self.total > 0 else 0.0

    @property
    def mandatory_coverage_pct(self) -> float:
        return (self.mandatory_mapped / self.mandatory_total * 100) if self.mandatory_total > 0 else 0.0


@dataclass
class FieldMapping:
    """Represents a field mapping."""
    source_field: str
    target_field: str
    source_path: Optional[str] = None
    parser_path: Optional[str] = None
    data_type: Optional[str] = None
    is_mandatory: bool = False
    is_mapped: bool = False
    source_value: Any = None
    target_value: Any = None
    values_match: Optional[bool] = None


@dataclass
class ReconReport:
    """Complete reconciliation report."""
    format_id: str
    timestamp: datetime
    stg_id: Optional[str] = None

    # Coverage stats
    standard_to_silver: CoverageStats = field(default_factory=CoverageStats)
    silver_to_gold: CoverageStats = field(default_factory=CoverageStats)

    # Field details
    standard_fields: List[FieldMapping] = field(default_factory=list)
    silver_to_gold_fields: List[FieldMapping] = field(default_factory=list)

    # Data validation (if stg_id provided)
    bronze_data: Dict[str, Any] = field(default_factory=dict)
    silver_data: Dict[str, Any] = field(default_factory=dict)
    gold_data: Dict[str, Any] = field(default_factory=dict)

    # Value comparisons
    value_comparisons: List[Dict[str, Any]] = field(default_factory=list)

    # Issues found
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def get_db_connection():
    """Create database connection from environment variables."""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
    )


def get_format_info(cursor, format_id: str) -> Dict[str, str]:
    """Get format metadata including Silver table name."""
    cursor.execute("""
        SELECT format_id, format_name, silver_table, description
        FROM mapping.message_formats
        WHERE format_id = %s AND is_active = TRUE
    """, (format_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Format '{format_id}' not found in mapping.message_formats")
    return {
        'format_id': row[0],
        'format_name': row[1],
        'silver_table': row[2],
        'description': row[3]
    }


def analyze_standard_to_silver(cursor, format_id: str) -> Tuple[CoverageStats, List[FieldMapping]]:
    """
    Analyze coverage from standard fields to Silver mappings.

    Only considers LEAF NODES (fields with actual data types), not container elements.
    Container elements have NULL or empty data_type, or 'complex' type.

    Returns coverage stats and list of field mappings.
    """
    # Get all LEAF NODE standard fields for the format
    # Exclude container/complex elements that don't carry data
    cursor.execute("""
        SELECT
            sf.field_name,
            sf.field_path,
            sf.is_mandatory,
            sf.data_type,
            sf.field_category,
            sm.target_column,
            sm.parser_path,
            sm.source_path as silver_source_path
        FROM mapping.standard_fields sf
        LEFT JOIN mapping.silver_field_mappings sm
            ON sf.format_id = sm.format_id
            AND (
                -- Match by field_path to source_path
                sf.field_path = sm.source_path
                OR sf.normalized_path = sm.source_path
                -- Or match by field name patterns
                OR LOWER(sf.field_name) = LOWER(sm.target_column)
            )
            AND sm.is_active = TRUE
        WHERE sf.format_id = %s
          AND sf.is_active = TRUE
          -- Only leaf nodes (have data type defined, not complex/container)
          AND sf.data_type IS NOT NULL
          AND sf.data_type != ''
          AND sf.data_type != 'complex'
        ORDER BY sf.standard_field_id
    """, (format_id,))

    rows = cursor.fetchall()

    stats = CoverageStats()
    mappings = []

    for row in rows:
        field_name, field_path, is_mandatory, data_type, category, target_col, parser_path, silver_source = row

        is_mapped = target_col is not None

        mapping = FieldMapping(
            source_field=field_name,
            target_field=target_col or '',
            source_path=field_path,
            parser_path=parser_path,
            data_type=data_type,
            is_mandatory=is_mandatory or False,
            is_mapped=is_mapped
        )
        mappings.append(mapping)

        stats.total += 1
        if is_mapped:
            stats.mapped += 1
        else:
            stats.unmapped += 1

        if is_mandatory:
            stats.mandatory_total += 1
            if is_mapped:
                stats.mandatory_mapped += 1
            else:
                stats.mandatory_unmapped += 1

    return stats, mappings


def analyze_silver_to_gold(cursor, format_id: str, silver_table: str) -> Tuple[CoverageStats, List[FieldMapping]]:
    """
    Analyze coverage from Silver columns to Gold mappings.

    Returns coverage stats and list of field mappings.
    """
    # Get all Silver columns that have mappings
    cursor.execute("""
        SELECT
            sm.target_column as silver_column,
            sm.source_path,
            sm.parser_path,
            sm.data_type,
            sm.is_required,
            gm.gold_table,
            gm.gold_column,
            gm.entity_role
        FROM mapping.silver_field_mappings sm
        LEFT JOIN mapping.gold_field_mappings gm
            ON sm.format_id = gm.format_id
            AND (
                -- Match by column name
                LOWER(sm.target_column) = LOWER(gm.source_expression)
                OR sm.target_column = gm.source_expression
                -- Or partial match for nested references
                OR gm.source_expression LIKE '%%' || sm.target_column || '%%'
            )
            AND gm.is_active = TRUE
        WHERE sm.format_id = %s AND sm.is_active = TRUE
        ORDER BY sm.ordinal_position
    """, (format_id,))

    rows = cursor.fetchall()

    stats = CoverageStats()
    mappings = []
    seen_columns = set()

    for row in rows:
        silver_col, source_path, parser_path, data_type, is_required, gold_table, gold_col, entity_role = row

        # Avoid duplicates
        if silver_col in seen_columns:
            continue
        seen_columns.add(silver_col)

        is_mapped = gold_col is not None

        target_desc = f"{gold_table}.{gold_col}" if gold_table and gold_col else ''
        if entity_role:
            target_desc += f" ({entity_role})"

        mapping = FieldMapping(
            source_field=silver_col,
            target_field=target_desc,
            source_path=source_path,
            parser_path=parser_path,
            data_type=data_type,
            is_mandatory=is_required or False,
            is_mapped=is_mapped
        )
        mappings.append(mapping)

        stats.total += 1
        if is_mapped:
            stats.mapped += 1
        else:
            stats.unmapped += 1

        if is_required:
            stats.mandatory_total += 1
            if is_mapped:
                stats.mandatory_mapped += 1
            else:
                stats.mandatory_unmapped += 1

    return stats, mappings


def get_latest_stg_id(cursor, format_id: str, silver_table: str) -> Optional[str]:
    """Get the most recent stg_id for the format."""
    cursor.execute(f"""
        SELECT stg_id
        FROM silver.{silver_table}
        WHERE processing_status = 'PROMOTED_TO_GOLD'
        ORDER BY _processed_at DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    return row[0] if row else None


def get_bronze_data(cursor, raw_id: str) -> Dict[str, Any]:
    """Get Bronze record data."""
    cursor.execute("""
        SELECT raw_id, message_type, raw_content, processing_status, _ingested_at
        FROM bronze.raw_payment_messages
        WHERE raw_id = %s
    """, (raw_id,))
    row = cursor.fetchone()
    if not row:
        return {}
    return {
        'raw_id': row[0],
        'message_type': row[1],
        'raw_content': row[2][:500] + '...' if row[2] and len(row[2]) > 500 else row[2],
        'processing_status': row[3],
        '_ingested_at': str(row[4]) if row[4] else None
    }


def get_silver_data(cursor, stg_id: str, silver_table: str) -> Dict[str, Any]:
    """Get Silver record data."""
    cursor.execute(f"""
        SELECT * FROM silver.{silver_table}
        WHERE stg_id = %s
    """, (stg_id,))

    row = cursor.fetchone()
    if not row:
        return {}

    columns = [desc[0] for desc in cursor.description]
    data = {}
    for col, val in zip(columns, row):
        # Convert special types to strings for display
        if isinstance(val, Decimal):
            data[col] = float(val)
        elif isinstance(val, datetime):
            data[col] = str(val)
        elif val is not None:
            data[col] = val
    return data


def get_gold_data(cursor, stg_id: str) -> Dict[str, Any]:
    """Get Gold record data (instruction + entities)."""
    data = {'instruction': {}, 'parties': [], 'accounts': [], 'financial_institutions': []}

    # Get payment instruction
    cursor.execute("""
        SELECT instruction_id, payment_id, source_message_type, payment_type, scheme_code,
               instructed_amount, instructed_currency, end_to_end_id, uetr,
               debtor_id, creditor_id, debtor_account_id, creditor_account_id,
               debtor_agent_id, creditor_agent_id, current_status, message_id
        FROM gold.cdm_payment_instruction
        WHERE source_stg_id = %s
    """, (stg_id,))

    row = cursor.fetchone()
    if row:
        columns = [desc[0] for desc in cursor.description]
        for col, val in zip(columns, row):
            if isinstance(val, Decimal):
                data['instruction'][col] = float(val)
            elif val is not None:
                data['instruction'][col] = val

    # Get parties linked to this instruction
    if data['instruction'].get('debtor_id'):
        cursor.execute("""
            SELECT party_id, name, party_type, country, created_at
            FROM gold.cdm_party WHERE party_id = %s
        """, (data['instruction']['debtor_id'],))
        row = cursor.fetchone()
        if row:
            data['parties'].append({
                'role': 'DEBTOR', 'party_id': row[0], 'name': row[1],
                'party_type': row[2], 'country': row[3]
            })

    if data['instruction'].get('creditor_id'):
        cursor.execute("""
            SELECT party_id, name, party_type, country, created_at
            FROM gold.cdm_party WHERE party_id = %s
        """, (data['instruction']['creditor_id'],))
        row = cursor.fetchone()
        if row:
            data['parties'].append({
                'role': 'CREDITOR', 'party_id': row[0], 'name': row[1],
                'party_type': row[2], 'country': row[3]
            })

    # Get accounts
    for role, col in [('DEBTOR', 'debtor_account_id'), ('CREDITOR', 'creditor_account_id')]:
        if data['instruction'].get(col):
            cursor.execute("""
                SELECT account_id, account_number, account_type, currency
                FROM gold.cdm_account WHERE account_id = %s
            """, (data['instruction'][col],))
            row = cursor.fetchone()
            if row:
                data['accounts'].append({
                    'role': role, 'account_id': row[0], 'account_number': row[1],
                    'account_type': row[2], 'currency': row[3]
                })

    # Get financial institutions
    for role, col in [('DEBTOR_AGENT', 'debtor_agent_id'), ('CREDITOR_AGENT', 'creditor_agent_id')]:
        if data['instruction'].get(col):
            cursor.execute("""
                SELECT fi_id, bic, lei, country
                FROM gold.cdm_financial_institution WHERE fi_id = %s
            """, (data['instruction'][col],))
            row = cursor.fetchone()
            if row:
                data['financial_institutions'].append({
                    'role': role, 'fi_id': row[0], 'bic': row[1],
                    'lei': row[2], 'country': row[3]
                })

    return data


def compare_values(silver_data: Dict, gold_data: Dict) -> List[Dict[str, Any]]:
    """Compare values between Silver and Gold for key fields."""
    comparisons = []

    instruction = gold_data.get('instruction', {})

    # Define field mappings: (silver_col, gold_location, description)
    # Note: msg_id (Group Header MsgId) maps to message_id in Gold, not end_to_end_id
    field_pairs = [
        ('msg_id', ('instruction', 'message_id'), 'Message ID'),
        ('instructed_amount', ('instruction', 'instructed_amount'), 'Instructed Amount'),
        ('instructed_currency', ('instruction', 'instructed_currency'), 'Currency'),
        ('end_to_end_id', ('instruction', 'end_to_end_id'), 'End-to-End ID'),
        ('uetr', ('instruction', 'uetr'), 'UETR'),
        ('debtor_name', ('parties', 'DEBTOR', 'name'), 'Debtor Name'),
        ('creditor_name', ('parties', 'CREDITOR', 'name'), 'Creditor Name'),
        ('debtor_account_iban', ('accounts', 'DEBTOR', 'account_number'), 'Debtor Account'),
        ('creditor_account_iban', ('accounts', 'CREDITOR', 'account_number'), 'Creditor Account'),
        ('debtor_agent_bic', ('financial_institutions', 'DEBTOR_AGENT', 'bic'), 'Debtor Agent BIC'),
        ('creditor_agent_bic', ('financial_institutions', 'CREDITOR_AGENT', 'bic'), 'Creditor Agent BIC'),
    ]

    for silver_col, gold_loc, desc in field_pairs:
        silver_val = silver_data.get(silver_col)

        # Navigate to gold value
        gold_val = None
        if gold_loc[0] == 'instruction':
            gold_val = instruction.get(gold_loc[1])
        elif gold_loc[0] in ('parties', 'accounts', 'financial_institutions'):
            entities = gold_data.get(gold_loc[0], [])
            for entity in entities:
                if entity.get('role') == gold_loc[1]:
                    gold_val = entity.get(gold_loc[2])
                    break

        # Compare values
        if silver_val is not None or gold_val is not None:
            # Normalize for comparison
            sv = str(silver_val).strip() if silver_val else None
            gv = str(gold_val).strip() if gold_val else None

            # Handle numeric comparison
            if silver_col in ('instructed_amount',):
                try:
                    sv = float(silver_val) if silver_val else None
                    gv = float(gold_val) if gold_val else None
                    match = sv == gv if sv is not None and gv is not None else sv == gv
                except (ValueError, TypeError):
                    match = sv == gv
            else:
                match = sv == gv

            comparisons.append({
                'field': desc,
                'silver_column': silver_col,
                'silver_value': silver_val,
                'gold_value': gold_val,
                'match': match
            })

    return comparisons


def generate_report(report: ReconReport, output_file: Optional[str] = None) -> str:
    """Generate formatted report text."""
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append(f"MESSAGE FORMAT RECONCILIATION REPORT")
    lines.append("=" * 80)
    lines.append(f"Format:     {report.format_id}")
    lines.append(f"Timestamp:  {report.timestamp.isoformat()}")
    if report.stg_id:
        lines.append(f"Record:     {report.stg_id}")
    lines.append("")

    # Standard → Silver Coverage
    lines.append("-" * 80)
    lines.append("1. STANDARD → SILVER COVERAGE")
    lines.append("-" * 80)
    stats = report.standard_to_silver
    lines.append(f"Total Standard Fields:     {stats.total}")
    lines.append(f"Mapped to Silver:          {stats.mapped} ({stats.coverage_pct:.1f}%)")
    lines.append(f"Unmapped:                  {stats.unmapped}")
    lines.append(f"Mandatory Fields:          {stats.mandatory_total}")
    lines.append(f"Mandatory Mapped:          {stats.mandatory_mapped} ({stats.mandatory_coverage_pct:.1f}%)")
    lines.append(f"Mandatory Unmapped:        {stats.mandatory_unmapped}")
    lines.append("")

    # Show unmapped mandatory fields
    unmapped_mandatory = [m for m in report.standard_fields if m.is_mandatory and not m.is_mapped]
    if unmapped_mandatory:
        lines.append("UNMAPPED MANDATORY FIELDS:")
        for m in unmapped_mandatory[:20]:  # Limit to 20
            lines.append(f"  - {m.source_field}: {m.source_path}")
        if len(unmapped_mandatory) > 20:
            lines.append(f"  ... and {len(unmapped_mandatory) - 20} more")
        lines.append("")

    # Show some unmapped optional fields
    unmapped_optional = [m for m in report.standard_fields if not m.is_mandatory and not m.is_mapped]
    if unmapped_optional:
        lines.append(f"UNMAPPED OPTIONAL FIELDS ({len(unmapped_optional)} total):")
        for m in unmapped_optional[:10]:  # Show first 10
            lines.append(f"  - {m.source_field}: {m.source_path}")
        if len(unmapped_optional) > 10:
            lines.append(f"  ... and {len(unmapped_optional) - 10} more")
        lines.append("")

    # Silver → Gold Coverage
    lines.append("-" * 80)
    lines.append("2. SILVER → GOLD COVERAGE")
    lines.append("-" * 80)
    stats = report.silver_to_gold
    lines.append(f"Total Silver Columns:      {stats.total}")
    lines.append(f"Mapped to Gold:            {stats.mapped} ({stats.coverage_pct:.1f}%)")
    lines.append(f"Unmapped:                  {stats.unmapped}")
    lines.append(f"Required Columns:          {stats.mandatory_total}")
    lines.append(f"Required Mapped:           {stats.mandatory_mapped} ({stats.mandatory_coverage_pct:.1f}%)")
    lines.append("")

    # Show unmapped Silver columns
    unmapped_silver = [m for m in report.silver_to_gold_fields if not m.is_mapped]
    if unmapped_silver:
        lines.append(f"UNMAPPED SILVER COLUMNS ({len(unmapped_silver)} total):")
        for m in unmapped_silver[:15]:
            req = " [REQUIRED]" if m.is_mandatory else ""
            lines.append(f"  - {m.source_field}{req}")
        if len(unmapped_silver) > 15:
            lines.append(f"  ... and {len(unmapped_silver) - 15} more")
        lines.append("")

    # Data Validation (if stg_id provided)
    if report.stg_id and report.silver_data:
        lines.append("-" * 80)
        lines.append("3. DATA VALUE COMPARISON")
        lines.append("-" * 80)

        lines.append(f"\nSilver Record (stg_id: {report.stg_id}):")
        key_silver_fields = ['msg_id', 'debtor_name', 'creditor_name', 'instructed_amount',
                            'instructed_currency', 'debtor_account_iban', 'creditor_account_iban',
                            'debtor_agent_bic', 'creditor_agent_bic', 'processing_status']
        for field in key_silver_fields:
            val = report.silver_data.get(field)
            if val is not None:
                lines.append(f"  {field}: {val}")

        lines.append(f"\nGold Record:")
        if report.gold_data.get('instruction'):
            instr = report.gold_data['instruction']
            lines.append(f"  instruction_id: {instr.get('instruction_id')}")
            lines.append(f"  instructed_amount: {instr.get('instructed_amount')}")
            lines.append(f"  instructed_currency: {instr.get('instructed_currency')}")
            lines.append(f"  end_to_end_id: {instr.get('end_to_end_id')}")
            lines.append(f"  current_status: {instr.get('current_status')}")

        for party in report.gold_data.get('parties', []):
            lines.append(f"  Party ({party['role']}): {party.get('name')}")

        for acct in report.gold_data.get('accounts', []):
            lines.append(f"  Account ({acct['role']}): {acct.get('account_number')} ({acct.get('currency')})")

        for fi in report.gold_data.get('financial_institutions', []):
            lines.append(f"  FI ({fi['role']}): {fi.get('bic')}")

        # Value comparison results
        lines.append(f"\nValue Comparison:")
        all_match = True
        for comp in report.value_comparisons:
            status = "✓" if comp['match'] else "✗"
            if not comp['match']:
                all_match = False
            lines.append(f"  {status} {comp['field']}: Silver='{comp['silver_value']}' Gold='{comp['gold_value']}'")

        lines.append("")
        if all_match:
            lines.append("ALL VALUES MATCH ✓")
        else:
            lines.append("VALUE MISMATCHES DETECTED ✗")

    # Issues and Warnings
    if report.issues:
        lines.append("")
        lines.append("-" * 80)
        lines.append("ISSUES")
        lines.append("-" * 80)
        for issue in report.issues:
            lines.append(f"  ✗ {issue}")

    if report.warnings:
        lines.append("")
        lines.append("-" * 80)
        lines.append("WARNINGS")
        lines.append("-" * 80)
        for warning in report.warnings:
            lines.append(f"  ⚠ {warning}")

    # Summary
    lines.append("")
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)

    std_silver = report.standard_to_silver
    silver_gold = report.silver_to_gold

    overall_status = "PASS" if (
        std_silver.mandatory_coverage_pct == 100 and
        silver_gold.coverage_pct >= 50 and
        not report.issues
    ) else "NEEDS ATTENTION"

    lines.append(f"Standard → Silver:  {std_silver.coverage_pct:.1f}% ({std_silver.mapped}/{std_silver.total})")
    lines.append(f"  Mandatory:        {std_silver.mandatory_coverage_pct:.1f}% ({std_silver.mandatory_mapped}/{std_silver.mandatory_total})")
    lines.append(f"Silver → Gold:      {silver_gold.coverage_pct:.1f}% ({silver_gold.mapped}/{silver_gold.total})")
    lines.append(f"Overall Status:     {overall_status}")
    lines.append("=" * 80)

    report_text = "\n".join(lines)

    # Output to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_text)
        print(f"Report written to: {output_file}")

    return report_text


def run_reconciliation(format_id: str, stg_id: Optional[str] = None,
                       use_latest: bool = False, output_file: Optional[str] = None) -> ReconReport:
    """
    Run full reconciliation for a message format.

    Args:
        format_id: Message format ID (e.g., 'pain.001')
        stg_id: Optional specific Silver record to validate
        use_latest: If True and stg_id not provided, use latest record
        output_file: Optional file path to write report

    Returns:
        ReconReport with all findings
    """
    report = ReconReport(
        format_id=format_id,
        timestamp=datetime.now()
    )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get format info
        try:
            format_info = get_format_info(cursor, format_id)
            silver_table = format_info['silver_table']
        except ValueError as e:
            report.issues.append(str(e))
            return report

        print(f"Analyzing format: {format_id} (Silver table: {silver_table})")

        # 1. Analyze Standard → Silver coverage
        print("  Checking Standard → Silver coverage...")
        report.standard_to_silver, report.standard_fields = analyze_standard_to_silver(cursor, format_id)

        # 2. Analyze Silver → Gold coverage
        print("  Checking Silver → Gold coverage...")
        report.silver_to_gold, report.silver_to_gold_fields = analyze_silver_to_gold(cursor, format_id, silver_table)

        # 3. Data validation if stg_id provided or use_latest
        if stg_id or use_latest:
            if use_latest and not stg_id:
                stg_id = get_latest_stg_id(cursor, format_id, silver_table)
                if not stg_id:
                    report.warnings.append("No processed records found for data validation")

            if stg_id:
                print(f"  Validating data for stg_id: {stg_id}")
                report.stg_id = stg_id

                # Get Silver data
                report.silver_data = get_silver_data(cursor, stg_id, silver_table)
                if not report.silver_data:
                    report.issues.append(f"Silver record not found: {stg_id}")
                else:
                    # Get Bronze data
                    raw_id = report.silver_data.get('raw_id')
                    if raw_id:
                        report.bronze_data = get_bronze_data(cursor, raw_id)

                    # Get Gold data
                    report.gold_data = get_gold_data(cursor, stg_id)
                    if not report.gold_data.get('instruction'):
                        report.warnings.append("Gold instruction record not found")

                    # Compare values
                    report.value_comparisons = compare_values(report.silver_data, report.gold_data)

                    # Check for mismatches
                    mismatches = [c for c in report.value_comparisons if not c['match']]
                    if mismatches:
                        for m in mismatches:
                            report.issues.append(
                                f"Value mismatch for {m['field']}: Silver='{m['silver_value']}' vs Gold='{m['gold_value']}'"
                            )

        # Add warnings for low coverage
        if report.standard_to_silver.mandatory_unmapped > 0:
            report.warnings.append(
                f"{report.standard_to_silver.mandatory_unmapped} mandatory standard fields not mapped to Silver"
            )

        if report.silver_to_gold.coverage_pct < 50:
            report.warnings.append(
                f"Silver → Gold coverage is only {report.silver_to_gold.coverage_pct:.1f}%"
            )

    finally:
        cursor.close()
        conn.close()

    # Generate and print report
    report_text = generate_report(report, output_file)
    print(report_text)

    return report


def main():
    parser = argparse.ArgumentParser(
        description='Message Format Reconciliation Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/reporting/recon_message_format.py --format pain.001
  python scripts/reporting/recon_message_format.py --format pain.001 --latest
  python scripts/reporting/recon_message_format.py --format pain.001 --stg-id <uuid>
  python scripts/reporting/recon_message_format.py --format pain.001 --output report.txt
        """
    )

    parser.add_argument('--format', '-f', required=True,
                       help='Message format ID (e.g., pain.001, mt103)')
    parser.add_argument('--stg-id', '-s',
                       help='Specific Silver stg_id to validate')
    parser.add_argument('--latest', '-l', action='store_true',
                       help='Use the latest processed record for validation')
    parser.add_argument('--output', '-o',
                       help='Output file path for the report')

    args = parser.parse_args()

    run_reconciliation(
        format_id=args.format,
        stg_id=args.stg_id,
        use_latest=args.latest,
        output_file=args.output
    )


if __name__ == '__main__':
    main()

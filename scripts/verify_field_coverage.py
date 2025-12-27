#!/usr/bin/env python3
"""
GPS CDM - Field Coverage Verification Script

Verifies 100% field coverage for all message types:
1. Syncs YAML mappings to database
2. Compares Silver staging table columns with Bronze→Silver mappings
3. Compares Gold CDM table columns with Silver→Gold mappings
4. Reports gaps and coverage percentage

Coverage Requirements:
- Silver: 100% of data columns must have Bronze source mappings
- Gold: 100% of data columns (excl. FKs) must have Silver source mappings
"""

import os
import sys
import yaml
import psycopg2
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class CoverageReport:
    """Coverage report for a message type."""
    message_type: str
    silver_table: str
    # Silver coverage (Bronze→Silver)
    silver_total_columns: int = 0
    silver_data_columns: int = 0  # Excluding system columns
    silver_mapped: int = 0
    silver_unmapped: List[str] = field(default_factory=list)
    # Gold coverage (Silver→Gold) - how many Silver columns flow to Gold
    gold_silver_columns_mapped: int = 0  # Silver columns that have Gold mappings
    gold_unmapped_silver_columns: List[str] = field(default_factory=list)
    # Gold target tables info
    gold_tables: Dict[str, dict] = field(default_factory=dict)
    # Errors
    errors: List[str] = field(default_factory=list)

    @property
    def silver_coverage(self) -> float:
        """Bronze→Silver: % of Silver columns that have Bronze source mappings."""
        if self.silver_data_columns == 0:
            return 100.0
        return (self.silver_mapped / self.silver_data_columns) * 100

    @property
    def gold_coverage(self) -> float:
        """Silver→Gold: % of Silver columns that have Gold target mappings."""
        if self.silver_data_columns == 0:
            return 100.0
        return (self.gold_silver_columns_mapped / self.silver_data_columns) * 100

    def print_report(self):
        print(f"\n{'='*70}")
        print(f"Message Type: {self.message_type}")
        print(f"{'='*70}")

        # Silver coverage (Bronze→Silver)
        print(f"\n[SILVER] Bronze→Silver: {self.silver_table}")
        print(f"  Total columns: {self.silver_total_columns} (data: {self.silver_data_columns})")
        print(f"  Mapped from Bronze: {self.silver_mapped}")
        print(f"  Coverage: {self.silver_coverage:.1f}%")
        if self.silver_unmapped:
            print(f"  UNMAPPED ({len(self.silver_unmapped)}): {', '.join(self.silver_unmapped[:8])}")
            if len(self.silver_unmapped) > 8:
                print(f"    ... and {len(self.silver_unmapped) - 8} more")

        # Gold coverage (Silver→Gold)
        print(f"\n[GOLD] Silver→Gold: CDM Tables")
        print(f"  Silver columns mapped to Gold: {self.gold_silver_columns_mapped}/{self.silver_data_columns}")
        print(f"  Coverage: {self.gold_coverage:.1f}%")
        if self.gold_unmapped_silver_columns:
            print(f"  Silver columns NOT mapped to Gold ({len(self.gold_unmapped_silver_columns)}):")
            for col in self.gold_unmapped_silver_columns[:10]:
                print(f"    - {col}")
            if len(self.gold_unmapped_silver_columns) > 10:
                print(f"    ... and {len(self.gold_unmapped_silver_columns) - 10} more")

        # Gold table breakdown
        print(f"\n  Gold table targets:")
        for table_name, info in self.gold_tables.items():
            print(f"    {table_name}: {info['mapped_count']} mappings")

        if self.errors:
            print(f"\n[ERRORS]")
            for err in self.errors:
                print(f"  - {err}")


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5433)),
        database=os.environ.get("POSTGRES_DB", "gps_cdm"),
        user=os.environ.get("POSTGRES_USER", "gps_cdm_svc"),
        password=os.environ.get("POSTGRES_PASSWORD", "gps_cdm_password"),
    )


def get_table_columns(conn, schema: str, table: str) -> List[str]:
    """Get list of columns for a table."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """, (schema, table))
    columns = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return columns


def get_mapped_silver_columns(conn, message_type: str) -> Set[str]:
    """Get silver columns that have Bronze→Silver mappings."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT target_column
        FROM mapping.silver_field_mappings
        WHERE format_id = %s AND is_active = true
    """, (message_type,))
    columns = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return columns


def get_silver_to_gold_mappings(conn, message_type: str) -> Tuple[Set[str], Dict[str, int]]:
    """Get Silver columns that have Gold mappings, and count per Gold table.

    Returns:
        - Set of Silver column names that are mapped to Gold
        - Dict of Gold table name -> count of mappings
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source_expression, gold_table, gold_column
        FROM mapping.gold_field_mappings
        WHERE format_id = %s AND is_active = true
    """, (message_type,))

    silver_columns_mapped: Set[str] = set()
    gold_table_counts: Dict[str, int] = {}

    for row in cursor.fetchall():
        source_expr, gold_table, gold_col = row
        # source_expression is the Silver column name (or expression)
        # Simple column references are just the column name
        if source_expr and not source_expr.startswith("'"):  # Skip constant values
            # Handle simple column names (most common case)
            silver_columns_mapped.add(source_expr)
        if gold_table not in gold_table_counts:
            gold_table_counts[gold_table] = 0
        gold_table_counts[gold_table] += 1

    cursor.close()
    return silver_columns_mapped, gold_table_counts


def get_silver_table_name(message_type: str) -> str:
    """Map message type to silver table name."""
    mapping = {
        "pain.001": "stg_pain001",
        "pacs.008": "stg_pacs008",
        "MT103": "stg_mt103",
        "MT202": "stg_mt202",
        "FEDWIRE": "stg_fedwire",
        "ACH": "stg_ach",
        "SEPA": "stg_sepa",
        "RTP": "stg_rtp",
    }
    return mapping.get(message_type, f"stg_{message_type.lower().replace('.', '')}")


# Silver system columns - these don't need source mappings
SILVER_SYSTEM_COLUMNS = {
    "stg_id",  # Auto-generated UUID
    "raw_id",  # FK to bronze
    "processing_status",  # Set by pipeline
    "processed_to_gold_at",  # Set after gold promotion
    "processing_error",  # Set on error
    "source_raw_id",  # Alternative FK
    "_batch_id",  # Lineage
    "_processed_at",  # Lineage
    "_partition_id",  # Partition
}

# Gold system columns - these don't need source mappings
GOLD_SYSTEM_COLUMNS = {
    # IDs
    "instruction_id", "payment_id", "party_id", "account_id", "fi_id",
    # FK references (set programmatically when creating entity relationships)
    "debtor_id", "debtor_account_id", "debtor_agent_id",
    "creditor_id", "creditor_account_id", "creditor_agent_id",
    "intermediary_agent1_id", "intermediary_agent2_id",
    "ultimate_debtor_id", "ultimate_creditor_id",
    "owner_id", "financial_institution_id", "parent_fi_id",
    # Source tracking (set by pipeline)
    "source_message_type", "source_stg_table", "source_stg_id", "source_system",
    # Audit columns
    "created_at", "updated_at", "created_by", "updated_by",
    "record_version", "is_deleted", "is_current",
    "valid_from", "valid_to",
    # Lineage
    "lineage_batch_id", "lineage_pipeline_run_id",
    # Partition
    "partition_year", "partition_month", "region",
    # Data quality
    "data_quality_score", "data_quality_issues",
}


def verify_message_type(conn, message_type: str) -> CoverageReport:
    """Verify coverage for a single message type."""
    report = CoverageReport(message_type=message_type, silver_table=get_silver_table_name(message_type))

    # === SILVER COVERAGE (Bronze→Silver) ===
    silver_columns = get_table_columns(conn, "silver", report.silver_table)
    if not silver_columns:
        report.errors.append(f"Silver table silver.{report.silver_table} not found")
        return report

    report.silver_total_columns = len(silver_columns)

    # Filter out system columns
    silver_data_columns = [c for c in silver_columns if c not in SILVER_SYSTEM_COLUMNS]
    report.silver_data_columns = len(silver_data_columns)

    # Get Bronze→Silver mapped columns from database
    mapped_silver = get_mapped_silver_columns(conn, message_type)

    # Calculate Silver coverage
    mapped_count = 0
    for col in silver_data_columns:
        if col in mapped_silver:
            mapped_count += 1
        else:
            report.silver_unmapped.append(col)

    report.silver_mapped = mapped_count

    # === GOLD COVERAGE (Silver→Gold) ===
    # Get Silver columns that have Gold mappings
    silver_cols_with_gold_mapping, gold_table_counts = get_silver_to_gold_mappings(conn, message_type)

    # Calculate how many Silver data columns are mapped to Gold
    gold_mapped_count = 0
    for col in silver_data_columns:
        if col in silver_cols_with_gold_mapping:
            gold_mapped_count += 1
        else:
            report.gold_unmapped_silver_columns.append(col)

    report.gold_silver_columns_mapped = gold_mapped_count

    # Store Gold table breakdown
    for table_name, count in gold_table_counts.items():
        report.gold_tables[table_name] = {'mapped_count': count}

    return report


def sync_message_type(message_type: str) -> dict:
    """Sync YAML to database for a message type."""
    from gps_cdm.orchestration.mapping_sync import MappingSync
    sync = MappingSync()
    result = sync.sync_message_type(message_type)
    return result.to_dict()


def main():
    """Main entry point."""
    print("=" * 70)
    print("GPS CDM - Field Coverage Verification")
    print("=" * 70)
    print("\nTarget: 100% coverage for all Silver and Gold data columns")

    # Message types to verify
    message_types = [
        "pain.001",
        "MT103",
        "FEDWIRE",
        "ACH",
        "SEPA",
        "RTP",
    ]

    conn = get_db_connection()

    # First, sync all mappings from YAML to database
    print("\n[1] Syncing YAML mappings to database...")
    for msg_type in message_types:
        try:
            result = sync_message_type(msg_type)
            silver_total = result["silver"]["added"] + result["silver"]["updated"]
            gold_total = result["gold"]["added"] + result["gold"]["updated"]
            print(f"  {msg_type}: silver={silver_total}, gold={gold_total}")
            if result.get("errors"):
                for err in result["errors"]:
                    print(f"    ERROR: {err[:60]}...")
        except Exception as e:
            print(f"  {msg_type}: ERROR - {e}")

    # Verify coverage for each message type
    print("\n[2] Verifying field coverage...")
    reports = []

    for msg_type in message_types:
        report = verify_message_type(conn, msg_type)
        reports.append(report)
        report.print_report()

    conn.close()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - Target: 100% Coverage")
    print("=" * 70)
    print(f"{'Message Type':<15} {'Bronze→Silver':<20} {'Silver→Gold':<20} {'Status'}")
    print("-" * 70)

    all_complete = True
    for report in reports:
        silver_status = f"{report.silver_mapped}/{report.silver_data_columns} ({report.silver_coverage:.0f}%)"
        gold_status = f"{report.gold_silver_columns_mapped}/{report.silver_data_columns} ({report.gold_coverage:.0f}%)"

        complete = report.silver_coverage >= 100 and report.gold_coverage >= 100
        status = "✓ 100%" if complete else "⚠ NEEDS WORK"
        if not complete:
            all_complete = False

        print(f"{report.message_type:<15} {silver_status:<20} {gold_status:<20} {status}")

    print("-" * 70)
    if all_complete:
        print("All message types have 100% coverage!")
    else:
        print("Some message types need additional Silver→Gold mappings.")
        print("\nNext steps:")
        print("1. Review Silver columns NOT mapped to Gold in each report above")
        print("2. Add missing silver_to_gold field mappings in YAML files")
        print("3. Re-run sync and verification")


if __name__ == "__main__":
    main()

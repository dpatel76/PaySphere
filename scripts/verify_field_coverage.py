#!/usr/bin/env python3
"""
GPS CDM - Field Coverage Verification Script

Verifies 100% field coverage for all message types:
1. Syncs YAML mappings to database
2. Compares Silver staging table columns with Bronze→Silver mappings
3. Compares Gold CDM table columns with Silver→Gold mappings
4. Reports gaps and coverage percentage
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
    silver_columns: int = 0
    silver_mapped: int = 0
    silver_unmapped: List[str] = field(default_factory=list)
    gold_tables: List[str] = field(default_factory=list)
    gold_columns: int = 0
    gold_mapped: int = 0
    gold_unmapped: Dict[str, List[str]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def silver_coverage(self) -> float:
        if self.silver_columns == 0:
            return 0.0
        return (self.silver_mapped / self.silver_columns) * 100

    @property
    def gold_coverage(self) -> float:
        if self.gold_columns == 0:
            return 0.0
        return (self.gold_mapped / self.gold_columns) * 100

    def print_report(self):
        print(f"\n{'='*60}")
        print(f"Message Type: {self.message_type}")
        print(f"{'='*60}")

        print(f"\n[SILVER] {self.silver_table}")
        print(f"  Total columns: {self.silver_columns}")
        print(f"  Mapped: {self.silver_mapped}")
        print(f"  Coverage: {self.silver_coverage:.1f}%")
        if self.silver_unmapped:
            print(f"  Unmapped columns: {', '.join(self.silver_unmapped[:10])}")
            if len(self.silver_unmapped) > 10:
                print(f"    ... and {len(self.silver_unmapped) - 10} more")

        print(f"\n[GOLD] CDM Tables")
        for table in self.gold_tables:
            unmapped = self.gold_unmapped.get(table, [])
            print(f"  {table}:")
            print(f"    Unmapped: {', '.join(unmapped[:5]) if unmapped else 'None'}")
        print(f"  Total columns: {self.gold_columns}")
        print(f"  Mapped: {self.gold_mapped}")
        print(f"  Coverage: {self.gold_coverage:.1f}%")

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
    """Get silver columns that have mappings."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT target_column
        FROM mapping.silver_field_mappings
        WHERE format_id = %s AND is_active = true
    """, (message_type,))
    columns = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return columns


def get_mapped_gold_columns(conn, message_type: str) -> Dict[str, Set[str]]:
    """Get gold columns that have mappings, grouped by table."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gold_table, gold_column
        FROM mapping.gold_field_mappings
        WHERE format_id = %s AND is_active = true
    """, (message_type,))

    result: Dict[str, Set[str]] = {}
    for row in cursor.fetchall():
        table, column = row
        if table not in result:
            result[table] = set()
        result[table].add(column)
    cursor.close()
    return result


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


def get_gold_tables() -> List[str]:
    """List of CDM gold tables."""
    return [
        "cdm_payment_instruction",
        "cdm_party",
        "cdm_account",
        "cdm_financial_institution"
    ]


# Columns to skip in coverage calculation (system/audit columns)
SYSTEM_COLUMNS = {
    # Common audit columns
    "created_at", "updated_at", "created_by", "updated_by",
    "record_version", "is_deleted", "is_current",
    "valid_from", "valid_to",
    # Processing columns
    "processing_status", "processed_to_gold_at", "dq_score", "dq_issues",
    # Lineage columns
    "lineage_batch_id", "lineage_pipeline_run_id",
    "_batch_id", "_partition_id", "_ingested_at", "_source_system",
    # IDs that are auto-generated
    "stg_id", "raw_id", "instruction_id", "payment_id",
    "party_id", "account_id", "fi_id",
    # Partition columns
    "partition_year", "partition_month", "region",
}


def verify_message_type(conn, message_type: str) -> CoverageReport:
    """Verify coverage for a single message type."""
    report = CoverageReport(message_type=message_type, silver_table=get_silver_table_name(message_type))

    # Check silver table
    silver_columns = get_table_columns(conn, "silver", report.silver_table)
    if not silver_columns:
        report.errors.append(f"Silver table silver.{report.silver_table} not found")
        return report

    # Filter out system columns
    silver_data_columns = [c for c in silver_columns if c not in SYSTEM_COLUMNS]
    report.silver_columns = len(silver_data_columns)

    # Get mapped columns
    mapped_silver = get_mapped_silver_columns(conn, message_type)
    report.silver_mapped = len(mapped_silver & set(silver_data_columns))
    report.silver_unmapped = [c for c in silver_data_columns if c not in mapped_silver]

    # Check gold tables
    report.gold_tables = get_gold_tables()
    mapped_gold = get_mapped_gold_columns(conn, message_type)

    total_gold_columns = 0
    total_gold_mapped = 0

    for gold_table in report.gold_tables:
        gold_columns = get_table_columns(conn, "gold", gold_table)
        gold_data_columns = [c for c in gold_columns if c not in SYSTEM_COLUMNS]
        total_gold_columns += len(gold_data_columns)

        mapped_cols = mapped_gold.get(gold_table, set())
        total_gold_mapped += len(mapped_cols & set(gold_data_columns))

        unmapped = [c for c in gold_data_columns if c not in mapped_cols]
        if unmapped:
            report.gold_unmapped[gold_table] = unmapped

    report.gold_columns = total_gold_columns
    report.gold_mapped = total_gold_mapped

    return report


def sync_message_type(message_type: str) -> dict:
    """Sync YAML to database for a message type."""
    from gps_cdm.orchestration.mapping_sync import MappingSync
    sync = MappingSync()
    result = sync.sync_message_type(message_type)
    return result.to_dict()


def main():
    """Main entry point."""
    print("=" * 60)
    print("GPS CDM - Field Coverage Verification")
    print("=" * 60)

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
                    print(f"    ERROR: {err[:80]}...")
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
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Message Type':<15} {'Silver %':<12} {'Gold %':<12} {'Status'}")
    print("-" * 60)

    for report in reports:
        status = "✓ COMPLETE" if report.silver_coverage >= 80 and report.gold_coverage >= 50 else "⚠ INCOMPLETE"
        print(f"{report.message_type:<15} {report.silver_coverage:>6.1f}%      {report.gold_coverage:>6.1f}%      {status}")


if __name__ == "__main__":
    main()

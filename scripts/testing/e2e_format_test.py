#!/usr/bin/env python3
"""
GPS CDM - End-to-End Format Testing Script (Dynamic)
=====================================================

Tests the complete NiFi → Kafka → Bronze → Silver → Gold pipeline for
message formats with FULLY DYNAMIC element-level validation.

This script:
1. Sends test file to NiFi
2. Uses the appropriate extractor to parse the test file and get EXPECTED values
3. Reads ACTUAL values from Bronze/Silver/Gold tables
4. Uses mapping tables to know which columns to compare
5. Reports element-level comparison results

Usage:
    python scripts/testing/e2e_format_test.py --format pain.008 --verbose
    python scripts/testing/e2e_format_test.py --formats pain.008,pacs.002,pacs.004
    python scripts/testing/e2e_format_test.py --all
"""

import os
import sys
import json
import time
import uuid
import argparse
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gps_cdm.message_formats.base import ExtractorRegistry
from gps_cdm.message_formats.iso20022 import (
    Pacs002Parser, Pacs002Extractor,
    Pacs004Parser, Pacs004Extractor,
    Pacs008Parser, Pacs008Extractor,
    Pacs009Parser, Pacs009Extractor,
    Pain001Parser, Pain001Extractor,
    Pain008Parser, Pain008Extractor,
)

# Map format types to their parser classes (ISO 20022 composite formats)
ISO20022_PARSERS = {
    # Base ISO 20022 formats
    'pacs.002': Pacs002Parser,
    'pacs.004': Pacs004Parser,
    'pacs.008': Pacs008Parser,
    'pacs.009': Pacs009Parser,
    'pain.001': Pain001Parser,
    'pain.008': Pain008Parser,
    # Composite formats - pacs.008 variants (12 regional schemes)
    'TARGET2_pacs008': Pacs008Parser,
    'CHAPS_pacs008': Pacs008Parser,
    'FEDWIRE_pacs008': Pacs008Parser,
    'FEDNOW_pacs008': Pacs008Parser,
    'RTP_pacs008': Pacs008Parser,
    'NPP_pacs008': Pacs008Parser,
    'UAEFTS_pacs008': Pacs008Parser,
    'MEPS_PLUS_pacs008': Pacs008Parser,
    'RTGS_HK_pacs008': Pacs008Parser,
    'INSTAPAY_pacs008': Pacs008Parser,
    'FPS_pacs008': Pacs008Parser,
    'CHIPS_pacs008': Pacs008Parser,
    'SEPA_pacs008': Pacs008Parser,
    'SEPA_INST_pacs008': Pacs008Parser,
    # Composite formats - pacs.009 variants
    'TARGET2_pacs009': Pacs009Parser,
    'CHAPS_pacs009': Pacs009Parser,
    'UAEFTS_pacs009': Pacs009Parser,
    'MEPS_PLUS_pacs009': Pacs009Parser,
    'RTGS_HK_pacs009': Pacs009Parser,
    'INSTAPAY_pacs009': Pacs009Parser,
    'CHIPS_pacs009': Pacs009Parser,
    'FEDNOW_pacs009': Pacs009Parser,
    'FEDWIRE_pacs009': Pacs009Parser,
    # Composite formats - pacs.002 variants
    'TARGET2_pacs002': Pacs002Parser,
    'UAEFTS_pacs002': Pacs002Parser,
    'CHAPS_pacs002': Pacs002Parser,
    'FEDNOW_pacs002': Pacs002Parser,
    'FEDWIRE_pacs002': Pacs002Parser,
    'FPS_pacs002': Pacs002Parser,
    'CHIPS_pacs002': Pacs002Parser,
    'INSTAPAY_pacs002': Pacs002Parser,
    'RTP_pacs002': Pacs002Parser,
    'NPP_pacs002': Pacs002Parser,
    'MEPS_PLUS_pacs002': Pacs002Parser,
    'RTGS_HK_pacs002': Pacs002Parser,
    'SEPA_pacs002': Pacs002Parser,
    'SEPA_INST_pacs002': Pacs002Parser,
    # Composite formats - pacs.004 variants
    'TARGET2_pacs004': Pacs004Parser,
    'CHAPS_pacs004': Pacs004Parser,
    'FEDNOW_pacs004': Pacs004Parser,
    'FEDWIRE_pacs004': Pacs004Parser,
    'NPP_pacs004': Pacs004Parser,
    # Composite formats - pain.001 variants
    'SEPA_pain001': Pain001Parser,
    # Composite formats - pain.008 variants
    'SEPA_pain008': Pain008Parser,
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Test data directory
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_data" / "e2e"
NIFI_INPUT_DIR = "/opt/nifi/nifi-current/input"

# All format types to test - 61 format combinations
# NOTE: Legacy base formats that have migrated to ISO 20022 (CHAPS, CHIPS, FEDNOW, FEDWIRE,
#       FPS, INSTAPAY, MEPS_PLUS, NPP, RTGS_HK, RTP, SEPA, TARGET2, UAEFTS) have been removed.
#       Only their ISO 20022 composite variants (e.g., CHAPS_pacs008) are tested.
# NOTE: SWIFT MT messages (MT103, MT202, MT940) were decommissioned by SWIFT in Nov 2025.
#       Use ISO 20022 equivalents: MT103→pacs.008, MT202→pacs.009, MT940/MT950→camt.053
ALL_FORMAT_TYPES = [
    # Base ISO 20022 formats (6)
    "pacs.002", "pacs.004", "pacs.008", "pacs.009", "pain.001", "pain.008",
    # True legacy formats - proprietary standards (11) - MT messages removed
    "ACH", "BACS", "BOJNET", "camt.053", "CNAPS", "KFTC",
    "PAYNOW", "PIX", "PROMPTPAY", "SARIE", "UPI",
    # CHAPS composite formats - UK RTGS (4)
    "CHAPS_pacs002", "CHAPS_pacs004", "CHAPS_pacs008", "CHAPS_pacs009",
    # CHIPS composite formats - US Large Value (3)
    "CHIPS_pacs002", "CHIPS_pacs008", "CHIPS_pacs009",
    # FEDNOW composite formats - US Instant (4)
    "FEDNOW_pacs002", "FEDNOW_pacs004", "FEDNOW_pacs008", "FEDNOW_pacs009",
    # FEDWIRE composite formats - US Fed (4)
    "FEDWIRE_pacs002", "FEDWIRE_pacs004", "FEDWIRE_pacs008", "FEDWIRE_pacs009",
    # FPS composite formats - UK Faster Payments (2)
    "FPS_pacs002", "FPS_pacs008",
    # INSTAPAY composite formats - Philippines (3)
    "INSTAPAY_pacs002", "INSTAPAY_pacs008", "INSTAPAY_pacs009",
    # MEPS_PLUS composite formats - Singapore (3)
    "MEPS_PLUS_pacs002", "MEPS_PLUS_pacs008", "MEPS_PLUS_pacs009",
    # NPP composite formats - Australia (3)
    "NPP_pacs002", "NPP_pacs004", "NPP_pacs008",
    # RTGS_HK composite formats - Hong Kong (3)
    "RTGS_HK_pacs002", "RTGS_HK_pacs008", "RTGS_HK_pacs009",
    # RTP composite formats - US Real-Time (2)
    "RTP_pacs002", "RTP_pacs008",
    # SEPA composite formats - EU (6)
    "SEPA_pacs002", "SEPA_pacs008", "SEPA_pain001", "SEPA_pain008",
    "SEPA_INST_pacs002", "SEPA_INST_pacs008",
    # TARGET2 composite formats - EU RTGS (4)
    "TARGET2_pacs002", "TARGET2_pacs004", "TARGET2_pacs008", "TARGET2_pacs009",
    # UAEFTS composite formats - UAE (3)
    "UAEFTS_pacs002", "UAEFTS_pacs008", "UAEFTS_pacs009",
]

# Map format types to their Gold table names (new semantic tables)
# For legacy/regional formats, use cdm_payment_instruction as fallback
GOLD_TABLE_MAP = {
    # pacs.008 variants -> cdm_pacs_fi_customer_credit_transfer (14)
    'pacs.008': 'cdm_pacs_fi_customer_credit_transfer',
    'TARGET2_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'CHAPS_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'UAEFTS_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'FEDWIRE_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'FEDNOW_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'FPS_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'CHIPS_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'RTP_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'NPP_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'MEPS_PLUS_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'RTGS_HK_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'INSTAPAY_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'SEPA_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    'SEPA_INST_pacs008': 'cdm_pacs_fi_customer_credit_transfer',
    # pacs.009 variants -> cdm_pacs_fi_credit_transfer (9)
    'pacs.009': 'cdm_pacs_fi_credit_transfer',
    'TARGET2_pacs009': 'cdm_pacs_fi_credit_transfer',
    'CHAPS_pacs009': 'cdm_pacs_fi_credit_transfer',
    'UAEFTS_pacs009': 'cdm_pacs_fi_credit_transfer',
    'MEPS_PLUS_pacs009': 'cdm_pacs_fi_credit_transfer',
    'RTGS_HK_pacs009': 'cdm_pacs_fi_credit_transfer',
    'INSTAPAY_pacs009': 'cdm_pacs_fi_credit_transfer',
    'CHIPS_pacs009': 'cdm_pacs_fi_credit_transfer',
    'FEDNOW_pacs009': 'cdm_pacs_fi_credit_transfer',
    'FEDWIRE_pacs009': 'cdm_pacs_fi_credit_transfer',
    # pacs.002 variants -> cdm_pacs_fi_payment_status_report (14)
    'pacs.002': 'cdm_pacs_fi_payment_status_report',
    'TARGET2_pacs002': 'cdm_pacs_fi_payment_status_report',
    'UAEFTS_pacs002': 'cdm_pacs_fi_payment_status_report',
    'CHAPS_pacs002': 'cdm_pacs_fi_payment_status_report',
    'FEDNOW_pacs002': 'cdm_pacs_fi_payment_status_report',
    'FEDWIRE_pacs002': 'cdm_pacs_fi_payment_status_report',
    'FPS_pacs002': 'cdm_pacs_fi_payment_status_report',
    'CHIPS_pacs002': 'cdm_pacs_fi_payment_status_report',
    'INSTAPAY_pacs002': 'cdm_pacs_fi_payment_status_report',
    'RTP_pacs002': 'cdm_pacs_fi_payment_status_report',
    'NPP_pacs002': 'cdm_pacs_fi_payment_status_report',
    'MEPS_PLUS_pacs002': 'cdm_pacs_fi_payment_status_report',
    'RTGS_HK_pacs002': 'cdm_pacs_fi_payment_status_report',
    'SEPA_pacs002': 'cdm_pacs_fi_payment_status_report',
    'SEPA_INST_pacs002': 'cdm_pacs_fi_payment_status_report',
    # pacs.004 variants -> cdm_pacs_payment_return (5)
    'pacs.004': 'cdm_pacs_payment_return',
    'TARGET2_pacs004': 'cdm_pacs_payment_return',
    'CHAPS_pacs004': 'cdm_pacs_payment_return',
    'FEDNOW_pacs004': 'cdm_pacs_payment_return',
    'FEDWIRE_pacs004': 'cdm_pacs_payment_return',
    'NPP_pacs004': 'cdm_pacs_payment_return',
    # pain.001 variants -> cdm_pain_customer_credit_transfer_initiation (2)
    'pain.001': 'cdm_pain_customer_credit_transfer_initiation',
    'SEPA_pain001': 'cdm_pain_customer_credit_transfer_initiation',
    # pain.008 variants -> cdm_pain_customer_direct_debit_initiation (2)
    'pain.008': 'cdm_pain_customer_direct_debit_initiation',
    'SEPA_pain008': 'cdm_pain_customer_direct_debit_initiation',
    # True legacy payment formats (proprietary standards) -> cdm_pacs_fi_customer_credit_transfer
    'ACH': 'cdm_pacs_fi_customer_credit_transfer',
    'BACS': 'cdm_pacs_fi_customer_credit_transfer',
    # BOJNET uses pacs.009 format (FI-to-FI transfer, Japan BOJ-NET)
    'BOJNET': 'cdm_pacs_fi_credit_transfer',
    'CNAPS': 'cdm_pacs_fi_customer_credit_transfer',
    'KFTC': 'cdm_pacs_fi_customer_credit_transfer',
    'PAYNOW': 'cdm_pacs_fi_customer_credit_transfer',
    'PIX': 'cdm_pacs_fi_customer_credit_transfer',
    'PROMPTPAY': 'cdm_pacs_fi_customer_credit_transfer',
    'SARIE': 'cdm_pacs_fi_customer_credit_transfer',
    'UPI': 'cdm_pacs_fi_customer_credit_transfer',
    # NOTE: SWIFT MT formats (MT103, MT202, MT940) were decommissioned by SWIFT in Nov 2025
    # Use ISO 20022 equivalents: MT103→pacs.008, MT202→pacs.009, MT940/MT950→camt.053
    # Statement formats -> cdm_camt_bank_to_customer_statement
    'camt.053': 'cdm_camt_bank_to_customer_statement',
}

# Map Gold tables to their primary ID column
GOLD_TABLE_ID_COLUMNS = {
    'cdm_pacs_fi_customer_credit_transfer': 'transfer_id',
    'cdm_pacs_fi_credit_transfer': 'transfer_id',
    'cdm_pacs_fi_payment_status_report': 'status_report_id',
    'cdm_pacs_payment_return': 'return_id',
    'cdm_pacs_fi_direct_debit': 'direct_debit_id',
    'cdm_pain_customer_credit_transfer_initiation': 'initiation_id',
    'cdm_pain_customer_direct_debit_initiation': 'initiation_id',
    'cdm_pain_customer_payment_status_report': 'status_report_id',
    'cdm_camt_bank_to_customer_statement': 'statement_id',
    'cdm_camt_bank_to_customer_account_report': 'report_id',
    'cdm_camt_bank_to_customer_debit_credit_notification': 'notification_id',
    'cdm_camt_fi_payment_cancellation_request': 'cancellation_request_id',
}


@dataclass
class FieldValidation:
    """Result of validating a single field."""
    field_name: str
    expected: Any
    actual: Any
    passed: bool
    source: str = ""  # 'extractor', 'mapping', 'generated'
    message: str = ""


@dataclass
class ZoneValidation:
    """Validation results for a single zone."""
    zone: str
    record_id: Optional[str] = None
    status: str = "NOT_FOUND"
    field_validations: List[FieldValidation] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for v in self.field_validations if v.passed)

    @property
    def total_count(self) -> int:
        return len(self.field_validations)


@dataclass
class E2ETestResult:
    """Complete E2E test result for a single format."""
    test_id: str
    format_type: str
    file_name: str
    start_time: datetime
    end_time: Optional[datetime] = None

    bronze: ZoneValidation = field(default_factory=lambda: ZoneValidation(zone="bronze"))
    silver: ZoneValidation = field(default_factory=lambda: ZoneValidation(zone="silver"))
    gold: ZoneValidation = field(default_factory=lambda: ZoneValidation(zone="gold"))

    gold_entities: Dict[str, int] = field(default_factory=dict)  # parties, accounts, fis

    errors: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Overall pass if all zones have records and critical validations pass."""
        if self.bronze.status == "NOT_FOUND":
            return False
        if self.silver.status == "NOT_FOUND":
            return False
        if self.gold.status == "NOT_FOUND":
            return False
        # Check critical field validations passed
        critical_silver = [v for v in self.silver.field_validations if v.field_name in
                         ('stg_id', 'raw_id', 'message_id', 'amount', 'currency')]
        critical_gold = [v for v in self.gold.field_validations if v.field_name in
                        ('instruction_id', 'source_stg_id', 'instructed_amount')]
        return all(v.passed for v in critical_silver + critical_gold)

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0


class DynamicE2ETester:
    """
    Dynamic E2E tester that uses extractors and mapping tables for validation.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.conn = self._get_connection()

    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=int(os.environ.get('POSTGRES_PORT', 5433)),
            database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
            user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
            password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password')
        )

    def _log(self, level: str, msg: str, **kwargs):
        """Log with optional verbose details."""
        extra = ' | '.join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ''
        full_msg = f"{msg} | {extra}" if extra else msg
        if level == "DEBUG" and not self.verbose:
            return
        getattr(logger, level.lower())(full_msg)

    def get_test_file_path(self, format_type: str) -> Path:
        """Get path to test file for a format."""
        # Try different extensions
        for ext in ['.xml', '.json', '.txt', '.ach']:
            file_name = f"{format_type}-e2e-test{ext}"
            path = TEST_DATA_DIR / file_name
            if path.exists():
                return path
        raise FileNotFoundError(f"No test file found for format: {format_type}")

    def parse_test_file_with_extractor(self, format_type: str, file_path: Path) -> Dict[str, Any]:
        """
        Parse the test file using the appropriate parser.
        Returns the parsed content that would be used for Silver extraction.
        """
        # Read file content
        with open(file_path, 'r') as f:
            raw_content = f.read()

        # Check if we have an ISO 20022 parser for this format
        parser_class = ISO20022_PARSERS.get(format_type)
        if parser_class:
            try:
                parser = parser_class()
                parsed = parser.parse(raw_content)
                self._log("DEBUG", f"Parsed with {parser_class.__name__}",
                         keys=list(parsed.keys())[:10])
                return parsed
            except Exception as e:
                self._log("WARNING", f"ISO 20022 parser failed", error=str(e)[:200])
                import traceback
                if self.verbose:
                    traceback.print_exc()

        # Try ExtractorRegistry (for non-ISO formats like MT103, ACH, FEDWIRE)
        extractor = ExtractorRegistry.get(format_type)
        if extractor:
            if hasattr(extractor, 'parser') and hasattr(extractor.parser, 'parse'):
                try:
                    parsed = extractor.parser.parse(raw_content)
                    self._log("DEBUG", f"Parsed with {type(extractor.parser).__name__}",
                             keys=list(parsed.keys())[:10])
                    return parsed
                except Exception as e:
                    self._log("WARNING", f"Extractor parser failed", error=str(e)[:100])

        # Try JSON parse
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            pass

        # Return raw content wrapper
        return {'_raw_text': raw_content}

    def get_silver_mappings(self, format_type: str) -> List[Dict[str, Any]]:
        """Get Silver field mappings from database for comparison."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get effective mappings (with inheritance)
            cur.execute("""
                SELECT em.target_column, em.source_path,
                       COALESCE(sfm.parser_path, em.source_path) as parser_path,
                       sfm.data_type
                FROM mapping.v_effective_silver_mappings em
                LEFT JOIN mapping.silver_field_mappings sfm
                    ON UPPER(sfm.format_id) = UPPER(em.effective_from_format)
                    AND sfm.target_column = em.target_column
                    AND sfm.is_active = TRUE
                WHERE UPPER(em.format_id) = UPPER(%s)
                ORDER BY sfm.ordinal_position NULLS LAST
            """, (format_type,))
            return [dict(row) for row in cur.fetchall()]

    def get_gold_mappings(self, format_type: str) -> List[Dict[str, Any]]:
        """Get Gold field mappings from database for comparison."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT em.gold_table, em.gold_column, em.source_expression,
                       em.entity_role, em.transform_expression, em.default_value
                FROM mapping.v_effective_gold_mappings em
                WHERE em.format_id = %s
                ORDER BY em.gold_table, em.entity_role NULLS FIRST
            """, (format_type,))
            return [dict(row) for row in cur.fetchall()]

    def get_silver_table(self, format_type: str) -> str:
        """Get Silver table name for a format."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT silver_table FROM mapping.message_formats
                WHERE UPPER(format_id) = UPPER(%s) AND is_active = TRUE
            """, (format_type,))
            row = cur.fetchone()
            if row:
                return row[0]
            raise ValueError(f"No Silver table found for format: {format_type}")

    def extract_expected_silver_values(self, format_type: str, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract expected Silver values from parsed content using mappings.
        This simulates what DynamicMapper would produce.
        """
        mappings = self.get_silver_mappings(format_type)
        expected = {}

        for mapping in mappings:
            col = mapping['target_column']
            parser_path = mapping.get('parser_path') or mapping.get('source_path')

            if not parser_path:
                continue

            # Skip generated/context values
            if parser_path.startswith('_'):
                continue

            # Resolve value from parsed content
            value = self._resolve_path(parsed_content, parser_path)
            if value is not None:
                expected[col] = value

        return expected

    def _resolve_path(self, data: Dict[str, Any], path: str) -> Any:
        """Resolve a dotted path to a value in nested dict."""
        if not path or not data:
            return None

        # Try direct key first
        if path in data:
            return data[path]

        # Try nested path
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
            if value is None:
                return None
        return value

    def send_test_file(self, format_type: str) -> Tuple[str, str, Path]:
        """Send test file to NiFi. Returns (test_id, file_name, file_path)."""
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        file_path = self.get_test_file_path(format_type)
        file_name = file_path.name

        # Copy to temp directory
        temp_dir = Path("/tmp/e2e_test_files")
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / file_name

        # Copy file
        with open(file_path, 'r') as src, open(temp_file, 'w') as dst:
            dst.write(src.read())

        # Send to NiFi using tar
        cmd = f"cd {temp_dir} && COPYFILE_DISABLE=1 tar cf - {file_name} | docker exec -i gps-cdm-nifi tar xf - -C {NIFI_INPUT_DIR}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0 and "Ignoring unknown extended header" not in result.stderr:
            raise RuntimeError(f"Failed to copy file to NiFi: {result.stderr}")

        self._log("INFO", f"Sent test file to NiFi", format=format_type, file=file_name, test_id=test_id)
        return test_id, file_name, file_path

    def find_bronze_record(self, format_type: str, wait_seconds: int = 20) -> Optional[Dict[str, Any]]:
        """Find the most recent Bronze record for a format type."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=wait_seconds + 10)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT raw_id, message_type, message_format, raw_content,
                       processing_status, _batch_id, _ingested_at
                FROM bronze.raw_payment_messages
                WHERE message_type = %s
                  AND _ingested_at > %s
                ORDER BY _ingested_at DESC
                LIMIT 1
            """, (format_type, cutoff_time))
            row = cur.fetchone()
            return dict(row) if row else None

    def find_silver_record(self, format_type: str, raw_id: str) -> Optional[Dict[str, Any]]:
        """Find Silver record by raw_id."""
        silver_table = self.get_silver_table(format_type)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                SELECT * FROM silver.{silver_table}
                WHERE raw_id = %s
                ORDER BY stg_id DESC
                LIMIT 1
            """, (raw_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_gold_table_for_format(self, format_type: str) -> Tuple[str, str]:
        """Get Gold table name and ID column for a format type."""
        # Try explicit mapping first
        gold_table = GOLD_TABLE_MAP.get(format_type)
        if gold_table:
            id_col = GOLD_TABLE_ID_COLUMNS.get(gold_table, 'instruction_id')
            return gold_table, id_col

        # Try database lookup
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT gold_table FROM mapping.message_formats
                WHERE UPPER(format_id) = UPPER(%s) AND is_active = TRUE
            """, (format_type,))
            row = cur.fetchone()
            if row and row[0]:
                gold_table = row[0]
                id_col = GOLD_TABLE_ID_COLUMNS.get(gold_table, 'instruction_id')
                return gold_table, id_col

        # No fallback - all formats must have semantic Gold tables
        raise ValueError(f"No Gold table mapping found for format: {format_type}")

    def find_gold_records(self, stg_id: str, format_type: str = None) -> Dict[str, Any]:
        """Find all Gold records by stg_id, using format-specific semantic tables.

        Entities (party, account, fi) are looked up via FK joins from the main Gold table,
        NOT via source_stg_id (which no longer exists on entity tables).
        """
        result = {
            'instruction': None,
            'gold_table': None,
            'id_column': None,
            'parties': [],
            'accounts': [],
            'financial_institutions': []
        }

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Determine which Gold table to query
            gold_table, id_col = self.get_gold_table_for_format(format_type)

            result['gold_table'] = gold_table
            result['id_column'] = id_col

            # Query the semantic Gold table
            try:
                cur.execute(f"""
                    SELECT * FROM gold.{gold_table}
                    WHERE source_stg_id = %s
                    LIMIT 1
                """, (stg_id,))
                row = cur.fetchone()
                if row:
                    result['instruction'] = dict(row)
                    self._log("DEBUG", f"Found Gold record in {gold_table}",
                             id=row.get(id_col), stg_id=stg_id)
            except Exception as e:
                self._log("WARNING", f"Error querying {gold_table}", error=str(e)[:100])

            # If no instruction found, return early
            if not result['instruction']:
                return result

            instruction = result['instruction']

            # Parties - lookup via FK from main Gold table
            # Semantic tables use *_party_id columns, legacy tables use *_id
            party_ids = []
            for fk_col in ['debtor_party_id', 'creditor_party_id', 'ultimate_debtor_party_id',
                          'ultimate_creditor_party_id', 'initiating_party_id',
                          # Legacy column names
                          'debtor_id', 'creditor_id', 'ultimate_debtor_id', 'ultimate_creditor_id']:
                party_id = instruction.get(fk_col)
                if party_id and party_id not in party_ids:
                    party_ids.append(party_id)

            if party_ids:
                try:
                    cur.execute("""
                        SELECT * FROM gold.cdm_party
                        WHERE party_id = ANY(%s)
                    """, (party_ids,))
                    result['parties'] = [dict(r) for r in cur.fetchall()]
                except Exception as e:
                    self._log("DEBUG", f"Error querying parties", error=str(e)[:100])

            # Accounts - lookup via FK from main Gold table
            account_ids = []
            for fk_col in ['debtor_account_id', 'creditor_account_id']:
                account_id = instruction.get(fk_col)
                if account_id and account_id not in account_ids:
                    account_ids.append(account_id)

            if account_ids:
                try:
                    cur.execute("""
                        SELECT * FROM gold.cdm_account
                        WHERE account_id = ANY(%s)
                    """, (account_ids,))
                    result['accounts'] = [dict(r) for r in cur.fetchall()]
                except Exception as e:
                    self._log("DEBUG", f"Error querying accounts", error=str(e)[:100])

            # Financial institutions - lookup via FK from main Gold table
            # Semantic tables use *_fi_id columns
            fi_ids = []
            for fk_col in ['debtor_agent_fi_id', 'creditor_agent_fi_id',
                          'instructing_agent_fi_id', 'instructed_agent_fi_id',
                          'intermediary_agent1_fi_id', 'intermediary_agent2_fi_id', 'intermediary_agent3_fi_id',
                          # pacs.009 FI credit transfer columns (FI-to-FI, not customer)
                          'debtor_fi_id', 'creditor_fi_id',
                          # Legacy column names
                          'debtor_agent_id', 'creditor_agent_id', 'intermediary_agent1_id', 'intermediary_agent2_id']:
                fi_id = instruction.get(fk_col)
                if fi_id and fi_id not in fi_ids:
                    fi_ids.append(fi_id)

            if fi_ids:
                try:
                    cur.execute("""
                        SELECT * FROM gold.cdm_financial_institution
                        WHERE fi_id = ANY(%s)
                    """, (fi_ids,))
                    result['financial_institutions'] = [dict(r) for r in cur.fetchall()]
                except Exception as e:
                    self._log("DEBUG", f"Error querying financial_institutions", error=str(e)[:100])

        return result

    def compare_values(self, expected: Any, actual: Any) -> bool:
        """Compare two values with type normalization."""
        if expected is None and actual is None:
            return True
        if expected is None or actual is None:
            return False

        # Handle array vs single value comparison
        # If actual is a list with single element, compare against that element
        if isinstance(actual, list) and len(actual) == 1 and not isinstance(expected, list):
            actual = actual[0]
        # If expected is a list with single element, compare against that element
        if isinstance(expected, list) and len(expected) == 1 and not isinstance(actual, list):
            expected = expected[0]

        # Normalize types for comparison
        exp_str = str(expected).strip().lower()
        act_str = str(actual).strip().lower()

        # Handle numeric comparisons
        try:
            exp_num = float(expected)
            act_num = float(actual)
            return abs(exp_num - act_num) < 0.01
        except (ValueError, TypeError):
            pass

        # String comparison
        return exp_str == act_str

    def validate_silver(self, expected_values: Dict[str, Any],
                       actual_record: Dict[str, Any]) -> List[FieldValidation]:
        """Validate Silver record against expected values from extractor."""
        validations = []

        # Always validate these critical fields exist
        critical_fields = ['stg_id', 'raw_id']
        for field_name in critical_fields:
            actual = actual_record.get(field_name)
            validations.append(FieldValidation(
                field_name=field_name,
                expected="<present>",
                actual=actual,
                passed=actual is not None,
                source="critical",
                message="" if actual else f"{field_name} is missing"
            ))

        # Compare expected values from extractor
        for col, expected in expected_values.items():
            actual = actual_record.get(col)
            passed = self.compare_values(expected, actual)

            validations.append(FieldValidation(
                field_name=col,
                expected=expected,
                actual=actual,
                passed=passed,
                source="extractor",
                message="" if passed else f"Mismatch: expected={expected}, actual={actual}"
            ))

        return validations

    def validate_gold(self, gold_records: Dict[str, Any],
                     silver_record: Dict[str, Any],
                     gold_mappings: List[Dict[str, Any]],
                     format_type: str = None) -> List[FieldValidation]:
        """Validate Gold records against expected values derived from Silver."""
        validations = []

        instruction = gold_records.get('instruction')
        gold_table = gold_records.get('gold_table', 'cdm_payment_instruction')
        id_col = gold_records.get('id_column', 'instruction_id')

        # Critical: instruction must exist
        validations.append(FieldValidation(
            field_name="gold_record_exists",
            expected=True,
            actual=instruction is not None,
            passed=instruction is not None,
            source="critical",
            message="" if instruction else f"Gold record not created in {gold_table}"
        ))

        if not instruction:
            return validations

        # Validate primary ID exists (using format-specific ID column)
        validations.append(FieldValidation(
            field_name=id_col,
            expected="<present>",
            actual=instruction.get(id_col),
            passed=instruction.get(id_col) is not None,
            source="critical"
        ))

        # Validate source_stg_id matches
        expected_stg_id = silver_record.get('stg_id')
        actual_stg_id = instruction.get('source_stg_id')
        validations.append(FieldValidation(
            field_name="source_stg_id",
            expected=expected_stg_id,
            actual=actual_stg_id,
            passed=expected_stg_id == actual_stg_id,
            source="lineage"
        ))

        # Validate amount if present in Silver
        # Silver column names vary by format, and Gold column names vary by table type
        # pacs.008/pain.001 use instructed_amount, pacs.009 uses interbank_settlement_amount
        for silver_col in ['amount', 'instructed_amount', 'intr_bk_sttlm_amt', 'instd_amt']:
            if silver_record.get(silver_col):
                expected_amount = silver_record.get(silver_col)
                # Try multiple Gold column names - different tables use different names
                actual_amount = (
                    instruction.get('instructed_amount') or
                    instruction.get('interbank_settlement_amount') or
                    instruction.get('amount')
                )
                validations.append(FieldValidation(
                    field_name="instructed_amount",
                    expected=expected_amount,
                    actual=actual_amount,
                    passed=self.compare_values(expected_amount, actual_amount),
                    source="mapping"
                ))
                break

        # Validate entity counts
        parties = gold_records.get('parties', [])
        accounts = gold_records.get('accounts', [])
        fis = gold_records.get('financial_institutions', [])

        # pacs.009 is FI-to-FI credit transfer - no customer parties/accounts, only FIs
        # pacs.002 is status report - may not have parties/accounts
        # pacs.004 is payment return - entities are optional (refers to original payment)
        is_fi_only_format = 'pacs.009' in format_type or 'pacs009' in format_type
        is_status_format = 'pacs.002' in format_type or 'pacs002' in format_type
        is_return_format = 'pacs.004' in format_type or 'pacs004' in format_type

        # For FI-only, status, and return formats, parties/accounts are optional
        if is_fi_only_format or is_status_format or is_return_format:
            validations.append(FieldValidation(
                field_name="parties_created",
                expected=">=0 (FI-to-FI format)",
                actual=len(parties),
                passed=True,  # Always pass for FI-only formats
                source="entities"
            ))
            validations.append(FieldValidation(
                field_name="accounts_created",
                expected=">=0 (FI-to-FI format)",
                actual=len(accounts),
                passed=True,  # Always pass for FI-only formats
                source="entities"
            ))
        else:
            validations.append(FieldValidation(
                field_name="parties_created",
                expected=">0",
                actual=len(parties),
                passed=len(parties) > 0,
                source="entities"
            ))
            validations.append(FieldValidation(
                field_name="accounts_created",
                expected=">0",
                actual=len(accounts),
                passed=len(accounts) > 0,
                source="entities"
            ))

        validations.append(FieldValidation(
            field_name="fis_created",
            expected=">0",
            actual=len(fis),
            passed=len(fis) > 0,
            source="entities"
        ))

        return validations

    def run_test(self, format_type: str, wait_seconds: int = 20) -> E2ETestResult:
        """Run E2E test for a single format."""
        now = datetime.utcnow()
        result = E2ETestResult(
            test_id=f"test_{uuid.uuid4().hex[:8]}",
            format_type=format_type,
            file_name="",
            start_time=now
        )

        try:
            # Step 1: Get test file and parse with extractor
            file_path = self.get_test_file_path(format_type)
            result.file_name = file_path.name

            parsed_content = self.parse_test_file_with_extractor(format_type, file_path)
            expected_silver = self.extract_expected_silver_values(format_type, parsed_content)

            self._log("DEBUG", f"Extracted {len(expected_silver)} expected Silver values",
                     sample_keys=list(expected_silver.keys())[:5])

            # Step 2: Send file to NiFi
            test_id, file_name, _ = self.send_test_file(format_type)
            result.test_id = test_id

            # Step 3: Wait for processing
            self._log("INFO", f"Waiting {wait_seconds}s for processing...")
            time.sleep(wait_seconds)

            # Step 4: Find and validate Bronze
            self._log("INFO", "Checking Bronze layer...")
            bronze_record = self.find_bronze_record(format_type, wait_seconds)

            if bronze_record:
                result.bronze.record_id = bronze_record['raw_id']
                result.bronze.status = "SUCCESS"
                result.bronze.field_validations.append(FieldValidation(
                    field_name="raw_id",
                    expected="<present>",
                    actual=bronze_record['raw_id'],
                    passed=True,
                    source="critical"
                ))
                result.bronze.field_validations.append(FieldValidation(
                    field_name="processing_status",
                    expected="PROMOTED_TO_SILVER",
                    actual=bronze_record['processing_status'],
                    passed=bronze_record['processing_status'] in ('PROMOTED_TO_SILVER', 'PENDING'),
                    source="status"
                ))
                self._log("INFO", f"Bronze: SUCCESS", raw_id=bronze_record['raw_id'])
            else:
                result.bronze.status = "NOT_FOUND"
                result.bronze.errors.append("Bronze record not found")
                self._log("ERROR", "Bronze record NOT FOUND")
                result.end_time = datetime.utcnow()
                return result

            # Step 5: Find and validate Silver
            self._log("INFO", "Checking Silver layer...")
            silver_record = self.find_silver_record(format_type, bronze_record['raw_id'])

            if silver_record:
                result.silver.record_id = silver_record['stg_id']
                result.silver.status = "SUCCESS"
                result.silver.field_validations = self.validate_silver(expected_silver, silver_record)

                passed = sum(1 for v in result.silver.field_validations if v.passed)
                total = len(result.silver.field_validations)
                self._log("INFO", f"Silver: SUCCESS", stg_id=silver_record['stg_id'],
                         validations=f"{passed}/{total}")

                # Log failed validations
                for v in result.silver.field_validations:
                    if not v.passed and v.field_name not in ('stg_id', 'raw_id'):
                        self._log("WARNING", f"Silver validation failed: {v.field_name}",
                                 expected=v.expected, actual=v.actual)
            else:
                result.silver.status = "NOT_FOUND"
                result.silver.errors.append("Silver record not found")
                self._log("ERROR", "Silver record NOT FOUND")
                result.end_time = datetime.utcnow()
                return result

            # Step 6: Find and validate Gold (with retries for async processing)
            self._log("INFO", "Checking Gold layer...")
            gold_records = None
            max_retries = 3
            retry_delay = 2  # seconds

            for attempt in range(max_retries):
                gold_records = self.find_gold_records(silver_record['stg_id'], format_type)
                if gold_records.get('instruction'):
                    break
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)

            gold_mappings = self.get_gold_mappings(format_type)

            if gold_records.get('instruction'):
                id_col = gold_records.get('id_column', 'instruction_id')
                result.gold.record_id = gold_records['instruction'].get(id_col)
                result.gold.status = "SUCCESS"
                result.gold.field_validations = self.validate_gold(
                    gold_records, silver_record, gold_mappings, format_type
                )

                result.gold_entities = {
                    'parties': len(gold_records.get('parties', [])),
                    'accounts': len(gold_records.get('accounts', [])),
                    'financial_institutions': len(gold_records.get('financial_institutions', []))
                }

                passed = sum(1 for v in result.gold.field_validations if v.passed)
                total = len(result.gold.field_validations)
                self._log("INFO", f"Gold: SUCCESS",
                         instruction_id=result.gold.record_id,
                         validations=f"{passed}/{total}",
                         entities=result.gold_entities)

                # Log failed validations
                for v in result.gold.field_validations:
                    if not v.passed:
                        self._log("WARNING", f"Gold validation failed: {v.field_name}",
                                 expected=v.expected, actual=v.actual)
            else:
                result.gold.status = "NOT_FOUND"
                result.gold.errors.append("Gold instruction not found")
                self._log("ERROR", "Gold instruction NOT FOUND")

        except Exception as e:
            import traceback
            result.errors.append(str(e))
            self._log("ERROR", f"Test failed with exception", error=str(e))
            if self.verbose:
                traceback.print_exc()

        result.end_time = datetime.utcnow()
        return result

    def run_bulk_test(self, formats: List[str], timeout_seconds: int = 90) -> List[E2ETestResult]:
        """
        Run bulk parallel E2E test for multiple formats.

        This method:
        1. Publishes all test messages simultaneously to NiFi
        2. Polls periodically for zone completion
        3. Validates all records once processing is complete
        4. Returns categorized results
        """
        from datetime import timezone
        from concurrent.futures import ThreadPoolExecutor, as_completed

        now = datetime.now(timezone.utc)
        results: Dict[str, E2ETestResult] = {}
        format_files: Dict[str, Tuple[str, Path, Dict[str, Any]]] = {}

        print("\n" + "#" * 80)
        print("# GPS CDM E2E BULK TEST")
        print(f"# Testing {len(formats)} formats")
        print(f"# Started: {now.isoformat()}")
        print("#" * 80 + "\n")

        # Step 1: Prepare test files and parse expected values
        print("=" * 60)
        print("Preparing test files...")
        print("=" * 60)

        skipped_formats = []
        for fmt in formats:
            try:
                file_path = self.get_test_file_path(fmt)
                parsed_content = self.parse_test_file_with_extractor(fmt, file_path)
                expected_silver = self.extract_expected_silver_values(fmt, parsed_content)

                format_files[fmt] = (file_path.name, file_path, {'parsed': parsed_content, 'expected': expected_silver})

                results[fmt] = E2ETestResult(
                    test_id=f"bulk_{uuid.uuid4().hex[:8]}",
                    format_type=fmt,
                    file_name=file_path.name,
                    start_time=now
                )
            except FileNotFoundError as e:
                self._log("WARNING", f"Skipping {fmt}: {e}")
                skipped_formats.append(fmt)

        print(f"Prepared {len(format_files)} test files ({len(skipped_formats)} skipped)\n")

        # Step 2: Publish all test files to NiFi in parallel
        print("=" * 60)
        print(f"Publishing {len(format_files)} test messages...")
        print("=" * 60)

        temp_dir = Path("/tmp/e2e_bulk_test")
        temp_dir.mkdir(exist_ok=True)

        # Copy all files to temp directory
        for fmt, (file_name, file_path, _) in format_files.items():
            temp_file = temp_dir / file_name
            with open(file_path, 'r') as src, open(temp_file, 'w') as dst:
                dst.write(src.read())

        # Bulk copy to NiFi using tar
        cmd = f"cd {temp_dir} && COPYFILE_DISABLE=1 tar cf - . | docker exec -i gps-cdm-nifi tar xf - -C {NIFI_INPUT_DIR}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0 and "Ignoring unknown extended header" not in result.stderr:
            raise RuntimeError(f"Failed to copy files to NiFi: {result.stderr}")

        # Clean up macOS metadata files
        subprocess.run(
            "docker exec gps-cdm-nifi bash -c 'rm -f /opt/nifi/nifi-current/input/._*'",
            shell=True, capture_output=True
        )

        print(f"Published {len(format_files)} files to NiFi\n")

        # Step 3: Poll for zone completion
        print("=" * 60)
        print(f"Polling for zone completion (timeout: {timeout_seconds}s)...")
        print("=" * 60)

        start_poll = time.time()
        cutoff_time = now - timedelta(seconds=10)

        while (time.time() - start_poll) < timeout_seconds:
            elapsed = int(time.time() - start_poll)

            # Count records in each zone
            bronze_count = self._count_recent_bronze(format_files.keys(), cutoff_time)
            silver_count = self._count_recent_silver(format_files.keys(), cutoff_time)
            gold_count = self._count_recent_gold(format_files.keys(), cutoff_time)

            print(f"  [{elapsed}s] Bronze: {bronze_count}/{len(format_files)}, "
                  f"Silver: {silver_count}/{len(format_files)}, "
                  f"Gold: {gold_count}/{len(format_files)}")

            # Check if all zones complete
            if gold_count >= len(format_files):
                print(f"\n  All {len(format_files)} messages processed through Gold!\n")
                break

            time.sleep(5)

        # Step 4: Validate all records
        print("=" * 60)
        print("Validating records...")
        print("=" * 60)

        for fmt, (file_name, file_path, data) in format_files.items():
            result = results[fmt]
            expected_silver = data['expected']

            try:
                # Find Bronze record
                bronze_record = self.find_bronze_record(fmt, timeout_seconds + 30)
                if bronze_record:
                    result.bronze.record_id = bronze_record['raw_id']
                    result.bronze.status = "SUCCESS"
                    result.bronze.field_validations.append(FieldValidation(
                        field_name="raw_id", expected="<present>",
                        actual=bronze_record['raw_id'], passed=True, source="critical"
                    ))
                else:
                    result.bronze.status = "NOT_FOUND"
                    result.bronze.errors.append("Bronze record not found")
                    continue

                # Find Silver record
                silver_record = self.find_silver_record(fmt, bronze_record['raw_id'])
                if silver_record:
                    result.silver.record_id = silver_record['stg_id']
                    result.silver.status = "SUCCESS"
                    result.silver.field_validations = self.validate_silver(expected_silver, silver_record)
                else:
                    result.silver.status = "NOT_FOUND"
                    result.silver.errors.append("Silver record not found")
                    continue

                # Find Gold records
                gold_records = self.find_gold_records(silver_record['stg_id'], fmt)
                gold_mappings = self.get_gold_mappings(fmt)

                if gold_records.get('instruction'):
                    id_col = gold_records.get('id_column', 'instruction_id')
                    result.gold.record_id = gold_records['instruction'].get(id_col)
                    result.gold.status = "SUCCESS"
                    result.gold.field_validations = self.validate_gold(
                        gold_records, silver_record, gold_mappings, fmt
                    )
                    result.gold_entities = {
                        'parties': len(gold_records.get('parties', [])),
                        'accounts': len(gold_records.get('accounts', [])),
                        'financial_institutions': len(gold_records.get('financial_institutions', []))
                    }
                else:
                    result.gold.status = "NOT_FOUND"
                    result.gold.errors.append("Gold instruction not found")

            except Exception as e:
                result.errors.append(str(e)[:200])
                self._log("ERROR", f"Validation error for {fmt}", error=str(e)[:100])

            result.end_time = datetime.now(timezone.utc)

        return list(results.values())

    def _count_recent_bronze(self, formats: List[str], cutoff_time: datetime) -> int:
        """Count recent Bronze records for given formats."""
        try:
            self.conn.rollback()  # Clear any failed transaction
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(DISTINCT message_type)
                    FROM bronze.raw_payment_messages
                    WHERE message_type = ANY(%s)
                      AND _ingested_at > %s
                """, (list(formats), cutoff_time))
                return cur.fetchone()[0]
        except Exception as e:
            self._log("WARNING", f"Bronze count error: {e}")
            return 0

    def _count_recent_silver(self, formats: List[str], cutoff_time: datetime) -> int:
        """Count recent Silver records for given formats."""
        count = 0
        try:
            self.conn.rollback()  # Clear any failed transaction
            with self.conn.cursor() as cur:
                for fmt in formats:
                    try:
                        silver_table = self.get_silver_table(fmt)
                        cur.execute(f"""
                            SELECT COUNT(*) FROM silver.{silver_table}
                        """)
                        if cur.fetchone()[0] > 0:
                            count += 1
                    except:
                        self.conn.rollback()
        except Exception as e:
            self._log("WARNING", f"Silver count error: {e}")
        return count

    def _count_recent_gold(self, formats: List[str], cutoff_time: datetime) -> int:
        """Count recent Gold records for given formats."""
        count = 0
        try:
            self.conn.rollback()  # Clear any failed transaction
            with self.conn.cursor() as cur:
                for fmt in formats:
                    try:
                        gold_table, _ = self.get_gold_table_for_format(fmt)
                        cur.execute(f"""
                            SELECT COUNT(*) FROM gold.{gold_table}
                            WHERE source_message_type = %s
                        """, (fmt,))
                        if cur.fetchone()[0] > 0:
                            count += 1
                    except:
                        self.conn.rollback()
        except Exception as e:
            self._log("WARNING", f"Gold count error: {e}")
        return count

    def print_summary(self, results: List[E2ETestResult]):
        """Print summary of all test results with categorization."""
        print("\n" + "=" * 80)
        print("E2E TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed

        print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

        # Categorize results
        categories = {
            'ISO 20022 Base': [],
            'ISO 20022 pacs.008 Variants': [],
            'ISO 20022 pacs.009 Variants': [],
            'ISO 20022 pacs.002 Variants': [],
            'ISO 20022 pacs.004 Variants': [],
            'ISO 20022 pain Variants': [],
            'Legacy/Regional': [],
        }

        for r in results:
            fmt = r.format_type
            if fmt in ('pacs.002', 'pacs.004', 'pacs.008', 'pacs.009', 'pain.001', 'pain.008', 'camt.053'):
                categories['ISO 20022 Base'].append(r)
            elif '_pacs008' in fmt:
                categories['ISO 20022 pacs.008 Variants'].append(r)
            elif '_pacs009' in fmt:
                categories['ISO 20022 pacs.009 Variants'].append(r)
            elif '_pacs002' in fmt:
                categories['ISO 20022 pacs.002 Variants'].append(r)
            elif '_pacs004' in fmt:
                categories['ISO 20022 pacs.004 Variants'].append(r)
            elif '_pain' in fmt:
                categories['ISO 20022 pain Variants'].append(r)
            else:
                categories['Legacy/Regional'].append(r)

        # Print category summary
        print("\n" + "-" * 80)
        print("RESULTS BY CATEGORY")
        print("-" * 80)

        for cat_name, cat_results in categories.items():
            if not cat_results:
                continue
            cat_passed = sum(1 for r in cat_results if r.passed)
            cat_total = len(cat_results)
            status = "✅" if cat_passed == cat_total else "⚠️" if cat_passed > 0 else "❌"
            print(f"\n{status} {cat_name}: {cat_passed}/{cat_total}")

            for r in cat_results:
                icon = "✅" if r.passed else "❌"
                bronze = "B✓" if r.bronze.status == "SUCCESS" else "B✗"
                silver = "S✓" if r.silver.status == "SUCCESS" else "S✗"
                gold = "G✓" if r.gold.status == "SUCCESS" else "G✗"
                print(f"   {icon} {r.format_type:30} [{bronze} {silver} {gold}]")

        # Only show detailed info for failures
        failures = [r for r in results if not r.passed]
        if failures:
            print("\n" + "-" * 80)
            print(f"DETAILED FAILURES ({len(failures)})")
            print("-" * 80)

        for result in failures:
            print(f"\n❌ FAIL [{result.format_type}]")
            print(f"   File: {result.file_name}")
            print(f"   Bronze: {result.bronze.status} (raw_id: {result.bronze.record_id or 'N/A'})")
            print(f"   Silver: {result.silver.status} (stg_id: {result.silver.record_id or 'N/A'})")
            print(f"   Gold: {result.gold.status} (id: {result.gold.record_id or 'N/A'})")

            if result.gold_entities:
                print(f"   Entities: Parties={result.gold_entities.get('parties', 0)}, "
                      f"Accounts={result.gold_entities.get('accounts', 0)}, "
                      f"FIs={result.gold_entities.get('financial_institutions', 0)}")

            # Show failed validations
            all_failed = []
            for zone in [result.bronze, result.silver, result.gold]:
                for v in zone.field_validations:
                    if not v.passed:
                        all_failed.append(f"{zone.zone}.{v.field_name}: expected={v.expected}, actual={v.actual}")

            if all_failed:
                print(f"   Failed Validations:")
                for f in all_failed[:10]:  # Limit to first 10
                    print(f"      - {f}")
                if len(all_failed) > 10:
                    print(f"      ... and {len(all_failed) - 10} more")

            if result.errors:
                print(f"   Errors: {', '.join(result.errors)}")

            print(f"   Duration: {result.duration_seconds:.2f}s")

        print("\n" + "=" * 80)
        return passed == len(results)


def main():
    parser = argparse.ArgumentParser(description='E2E Format Testing (Dynamic)')
    parser.add_argument('--formats', type=str, help='Comma-separated list of formats to test')
    parser.add_argument('--all', action='store_true', help='Test all new formats')
    parser.add_argument('--format', type=str, help='Single format to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--wait', type=int, default=20, help='Wait time for processing (seconds)')
    parser.add_argument('--bulk', action='store_true', help='Bulk parallel testing mode')
    parser.add_argument('--timeout', type=int, default=90, help='Bulk mode timeout (seconds)')

    args = parser.parse_args()

    # Determine formats to test
    if args.all:
        formats = ALL_FORMAT_TYPES
    elif args.formats:
        formats = [f.strip() for f in args.formats.split(',')]
    elif args.format:
        formats = [args.format]
    else:
        formats = ALL_FORMAT_TYPES

    logger.info("=" * 70)
    logger.info(f"E2E FORMAT TESTING (DYNAMIC) - {len(formats)} formats")
    logger.info("=" * 70)

    tester = DynamicE2ETester(verbose=args.verbose)

    # Use bulk parallel mode if requested
    if args.bulk:
        results = tester.run_bulk_test(formats, timeout_seconds=args.timeout)
    else:
        results = []
        for format_type in formats:
            logger.info("=" * 60)
            logger.info(f"TESTING FORMAT: {format_type}")
            logger.info("=" * 60)

            try:
                result = tester.run_test(format_type, wait_seconds=args.wait)
                results.append(result)
            except FileNotFoundError as e:
                logger.error(f"Skipping {format_type}: {e}")
            except Exception as e:
                logger.error(f"Failed to test {format_type}: {e}")
                import traceback
                if args.verbose:
                    traceback.print_exc()

    # Print summary
    all_passed = tester.print_summary(results)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

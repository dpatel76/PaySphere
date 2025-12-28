#!/usr/bin/env python3
"""
E2E Test for All 29 Message Format Extractors
==============================================

Tests Bronze → Silver → Gold pipeline for all message formats.
Uses direct Celery task invocation (bypasses NiFi).

Usage:
    cd /Users/dineshpatel/code/projects/gps_cdm
    source .venv/bin/activate

    # Run all tests
    GPS_CDM_DATA_SOURCE=postgresql \
    POSTGRES_HOST=localhost POSTGRES_PORT=5433 \
    POSTGRES_DB=gps_cdm POSTGRES_USER=gps_cdm_svc \
    POSTGRES_PASSWORD=gps_cdm_password \
    PYTHONPATH=src:$PYTHONPATH python3 tests/e2e/test_all_message_formats.py

    # Run specific format
    ... python3 tests/e2e/test_all_message_formats.py MT103
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import psycopg2

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from gps_cdm.orchestration.celery_tasks import process_bronze_partition


# ============================================================================
# TEST DATA DIRECTORY
# ============================================================================

TEST_DATA_DIR = Path(__file__).parent.parent / 'data' / 'samples' / 'nifi_e2e'


# ============================================================================
# MESSAGE FORMAT TEST DATA
# ============================================================================

def load_test_file(filename: str) -> str:
    """Load test file content."""
    filepath = TEST_DATA_DIR / filename
    if not filepath.exists():
        return None
    return filepath.read_text()


def get_test_data() -> Dict[str, Dict[str, Any]]:
    """Get test data for all message formats."""
    return {
        # ISO 20022 Family
        'pain.001': {
            'file': 'pain.001_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'pacs.008': {
            'file': 'pacs.008_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'camt.053': {
            'file': 'camt.053_nifi_e2e.xml',
            'content_type': 'xml',
        },

        # SWIFT MT Family
        'MT103': {
            'file': 'MT103_nifi_e2e.txt',
            'content_type': 'swift',
        },
        'MT202': {
            'file': 'MT202_nifi_e2e.txt',
            'content_type': 'swift',
        },
        'MT940': {
            'file': 'MT940_nifi_e2e.txt',
            'content_type': 'swift',
        },

        # US Domestic
        'FEDWIRE': {
            'file': 'FEDWIRE_nifi_e2e.txt',
            'content_type': 'text',
        },
        'ACH': {
            'file': 'ACH_nifi_e2e.txt',
            'content_type': 'text',
        },
        'RTP': {
            'file': 'RTP_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'FEDNOW': {
            'file': 'FEDNOW_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'CHIPS': {
            'file': 'CHIPS_nifi_e2e.txt',
            'content_type': 'text',
        },

        # UK
        'CHAPS': {
            'file': 'CHAPS_nifi_e2e.txt',
            'content_type': 'text',
        },
        'BACS': {
            'file': 'BACS_nifi_e2e.txt',
            'content_type': 'text',
        },
        'FPS': {
            'file': 'FPS_nifi_e2e.xml',
            'content_type': 'xml',
        },

        # EU
        'SEPA': {
            'file': 'SEPA_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'TARGET2': {
            'file': 'TARGET2_nifi_e2e.xml',
            'content_type': 'xml',
        },

        # APAC
        'NPP': {
            'file': 'NPP_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'UPI': {
            'file': 'UPI_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'PIX': {
            'file': 'PIX_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'CNAPS': {
            'file': 'CNAPS_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'BOJNET': {
            'file': 'BOJNET_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'KFTC': {
            'file': 'KFTC_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'MEPS_PLUS': {
            'file': 'MEPS_PLUS_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'RTGS_HK': {
            'file': 'RTGS_HK_nifi_e2e.xml',
            'content_type': 'xml',
        },

        # Middle East
        'SARIE': {
            'file': 'SARIE_nifi_e2e.xml',
            'content_type': 'xml',
        },
        'UAEFTS': {
            'file': 'UAEFTS_nifi_e2e.xml',
            'content_type': 'xml',
        },

        # SE Asia Instant
        'INSTAPAY': {
            'file': 'INSTAPAY_nifi_e2e.json',
            'content_type': 'json',
        },
        'PAYNOW': {
            'file': 'PAYNOW_nifi_e2e.json',
            'content_type': 'json',
        },
        'PROMPTPAY': {
            'file': 'PROMPTPAY_nifi_e2e.json',
            'content_type': 'json',
        },
    }


# ============================================================================
# DATABASE VERIFICATION
# ============================================================================

def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=int(os.environ.get('POSTGRES_PORT', 5433)),
        database=os.environ.get('POSTGRES_DB', 'gps_cdm'),
        user=os.environ.get('POSTGRES_USER', 'gps_cdm_svc'),
        password=os.environ.get('POSTGRES_PASSWORD', 'gps_cdm_password'),
    )


def verify_bronze_record(conn, raw_id: str) -> Optional[Dict]:
    """Check if Bronze record exists."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT raw_id, message_type, _batch_id, _ingested_at
            FROM bronze.raw_payment_messages
            WHERE raw_id = %s
        """, (raw_id,))
        row = cur.fetchone()
        if row:
            return {
                'raw_id': row[0],
                'message_type': row[1],
                'batch_id': row[2],
                'ingested_at': row[3],
            }
    return None


def verify_silver_record(conn, message_type: str, raw_id: str) -> Optional[Dict]:
    """Check if Silver record exists."""
    # Map message types to table names
    table_map = {
        'pain.001': 'stg_pain001',
        'pacs.008': 'stg_pacs008',
        'camt.053': 'stg_camt053',
        'MT103': 'stg_mt103',
        'MT202': 'stg_mt202',
        'MT940': 'stg_mt940',
        'FEDWIRE': 'stg_fedwire',
        'ACH': 'stg_ach',
        'RTP': 'stg_rtp',
        'FEDNOW': 'stg_fednow',
        'CHIPS': 'stg_chips',
        'CHAPS': 'stg_chaps',
        'BACS': 'stg_bacs',
        'FPS': 'stg_faster_payments',
        'SEPA': 'stg_sepa',
        'TARGET2': 'stg_target2',
        'NPP': 'stg_npp',
        'UPI': 'stg_upi',
        'PIX': 'stg_pix',
        'CNAPS': 'stg_cnaps',
        'BOJNET': 'stg_bojnet',
        'KFTC': 'stg_kftc',
        'MEPS_PLUS': 'stg_meps_plus',
        'RTGS_HK': 'stg_rtgs_hk',
        'SARIE': 'stg_sarie',
        'UAEFTS': 'stg_uaefts',
        'INSTAPAY': 'stg_instapay',
        'PAYNOW': 'stg_paynow',
        'PROMPTPAY': 'stg_promptpay',
    }

    table_name = table_map.get(message_type, f'stg_{message_type.lower()}')

    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT stg_id, raw_id, _batch_id
                FROM silver.{table_name}
                WHERE raw_id = %s
            """, (raw_id,))
            row = cur.fetchone()
            if row:
                return {
                    'stg_id': row[0],
                    'raw_id': row[1],
                    'batch_id': row[2],
                }
    except Exception as e:
        print(f"  Warning: Could not query {table_name}: {e}")
    return None


def verify_gold_entities(conn, stg_id: str) -> Dict[str, int]:
    """Count Gold entities linked to a Silver record."""
    counts = {}

    # Check payment instructions
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM gold.cdm_payment_instruction
            WHERE source_stg_id = %s
        """, (stg_id,))
        counts['payment_instructions'] = cur.fetchone()[0]

    # Check parties (via payment instruction)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(DISTINCT p.party_id)
            FROM gold.cdm_party p
            JOIN gold.cdm_payment_instruction pi ON (
                p.party_id = pi.debtor_id OR
                p.party_id = pi.creditor_id
            )
            WHERE pi.source_stg_id = %s
        """, (stg_id,))
        counts['parties'] = cur.fetchone()[0]

    # Check accounts
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(DISTINCT a.account_id)
            FROM gold.cdm_account a
            JOIN gold.cdm_payment_instruction pi ON (
                a.account_id = pi.debtor_account_id OR
                a.account_id = pi.creditor_account_id
            )
            WHERE pi.source_stg_id = %s
        """, (stg_id,))
        counts['accounts'] = cur.fetchone()[0]

    return counts


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_e2e_test(message_type: str, test_info: Dict) -> Tuple[bool, str]:
    """
    Run E2E test for a single message format.

    Returns: (success, message)
    """
    print(f"\n{'='*60}")
    print(f"Testing: {message_type}")
    print(f"{'='*60}")

    # Load test file
    content = load_test_file(test_info['file'])
    if not content:
        return False, f"Test file not found: {test_info['file']}"

    print(f"  File: {test_info['file']}")
    print(f"  Content type: {test_info['content_type']}")
    print(f"  Content length: {len(content)} bytes")

    # Generate unique batch ID for this test
    batch_id = f"e2e-test-{message_type.lower()}-{uuid.uuid4().hex[:8]}"
    partition_id = f"test-{message_type.lower()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Prepare message content based on content type
    if test_info['content_type'] == 'json':
        try:
            message_content = json.loads(content)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
    else:
        # For XML, SWIFT, text - pass as raw string
        message_content = content

    # Submit Celery task
    print(f"\n  Submitting Celery task...")
    print(f"    Batch ID: {batch_id}")
    print(f"    Partition ID: {partition_id}")

    try:
        result = process_bronze_partition.delay(
            partition_id=partition_id,
            file_paths=[],
            message_type=message_type,
            batch_id=batch_id,
            config={'message_content': message_content}
        )

        # Wait for result with timeout
        output = result.get(timeout=60)

        print(f"\n  Task Result:")
        print(f"    Status: {output.get('status')}")
        print(f"    Persisted to: {output.get('persisted_to')}")
        print(f"    Raw ID: {output.get('raw_id')}")
        print(f"    Stg ID: {output.get('stg_id')}")

        status = output.get('status', '').upper()
        if status not in ('SUCCESS', 'PARTIAL'):
            return False, f"Task failed: {output.get('error', 'Unknown error')}"

        records_processed = output.get('records_processed', 0)
        if records_processed == 0:
            return False, "No records processed"

    except Exception as e:
        return False, f"Celery task error: {e}"

    # Verify database records by batch_id
    print(f"\n  Verifying database records...")

    conn = get_db_connection()
    try:
        # Check Bronze by batch_id
        with conn.cursor() as cur:
            cur.execute("""
                SELECT raw_id, message_type, _batch_id
                FROM bronze.raw_payment_messages
                WHERE _batch_id = %s
                ORDER BY _ingested_at DESC
                LIMIT 1
            """, (batch_id,))
            bronze_row = cur.fetchone()

        if bronze_row:
            raw_id = bronze_row[0]
            print(f"    ✓ Bronze record exists (raw_id: {raw_id})")
        else:
            return False, f"Bronze record not found for batch_id: {batch_id}"

        # Check Silver
        silver = verify_silver_record(conn, message_type, raw_id)
        if silver:
            print(f"    ✓ Silver record exists (stg_id: {silver['stg_id']})")
            stg_id = silver['stg_id']
        else:
            return False, f"Silver record not found for raw_id: {raw_id}"

        # Check Gold
        gold_counts = verify_gold_entities(conn, stg_id)
        print(f"    Gold entities:")
        print(f"      Payment Instructions: {gold_counts['payment_instructions']}")
        print(f"      Parties: {gold_counts['parties']}")
        print(f"      Accounts: {gold_counts['accounts']}")

        if gold_counts['payment_instructions'] == 0:
            return False, "No Gold payment instruction created"

    finally:
        conn.close()

    return True, "E2E test passed"


def run_all_tests(filter_type: Optional[str] = None):
    """Run E2E tests for all message formats."""
    test_data = get_test_data()

    if filter_type:
        if filter_type not in test_data:
            print(f"Unknown message type: {filter_type}")
            print(f"Available types: {', '.join(sorted(test_data.keys()))}")
            sys.exit(1)
        test_data = {filter_type: test_data[filter_type]}

    print("\n" + "="*70)
    print("GPS CDM E2E Test - All Message Formats")
    print("="*70)
    print(f"\nTest data directory: {TEST_DATA_DIR}")
    print(f"Message types to test: {len(test_data)}")

    results = {}
    passed = 0
    failed = 0

    for msg_type, test_info in sorted(test_data.items()):
        success, message = run_e2e_test(msg_type, test_info)
        results[msg_type] = {'success': success, 'message': message}

        if success:
            passed += 1
            print(f"\n  ✓ PASSED: {message}")
        else:
            failed += 1
            print(f"\n  ✗ FAILED: {message}")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nTotal: {len(test_data)}  |  Passed: {passed}  |  Failed: {failed}")

    if failed > 0:
        print("\nFailed tests:")
        for msg_type, result in sorted(results.items()):
            if not result['success']:
                print(f"  - {msg_type}: {result['message']}")

    print("\n" + "="*70)

    return failed == 0


if __name__ == '__main__':
    # Check if specific format requested
    filter_type = sys.argv[1] if len(sys.argv) > 1 else None

    success = run_all_tests(filter_type)
    sys.exit(0 if success else 1)

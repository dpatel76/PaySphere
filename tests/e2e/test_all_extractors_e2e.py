#!/usr/bin/env python3
"""
E2E Test for ALL Message Format Extractors.

Tests each extractor through the full Bronze → Silver → Gold pipeline
to identify which extractors work and which need fixes.

Usage:
    PYTHONPATH=src:$PYTHONPATH python tests/e2e/test_all_extractors_e2e.py [message_type]
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gps_cdm.orchestration.zone_tasks import process_medallion_pipeline

# Test file configurations - maps message type to test file
TEST_FILES = {
    # ISO 20022 Payment Messages
    'pain.001': 'pain.001_nifi_e2e.xml',
    'pacs.008': 'pacs.008_nifi_e2e.xml',

    # ISO 20022 Statement Messages
    'camt.053': 'camt.053_nifi_e2e.xml',

    # SWIFT MT Messages
    'MT103': 'MT103_nifi_e2e.txt',
    'MT202': 'MT202_nifi_e2e.txt',
    'MT940': 'MT940_nifi_e2e.txt',

    # US Payment Schemes
    'FEDWIRE': 'FEDWIRE_nifi_e2e.txt',
    'FEDNOW': 'FEDNOW_nifi_e2e.xml',
    'ACH': 'ACH_nifi_e2e.txt',
    'CHIPS': 'CHIPS_nifi_e2e.txt',
    'RTP': 'RTP_nifi_e2e.xml',

    # EU/UK Payment Schemes
    'SEPA': 'SEPA_nifi_e2e.xml',
    'CHAPS': 'CHAPS_nifi_e2e.txt',
    'BACS': 'BACS_nifi_e2e.txt',
    'FPS': 'FPS_nifi_e2e.xml',
    'TARGET2': 'TARGET2_nifi_e2e.xml',

    # APAC Payment Schemes
    'NPP': 'NPP_nifi_e2e.xml',
    'UPI': 'UPI_nifi_e2e.xml',
    'RTGS_HK': 'RTGS_HK_nifi_e2e.xml',
    'MEPS_PLUS': 'MEPS_PLUS_nifi_e2e.xml',
    'BOJNET': 'BOJNET_nifi_e2e.xml',
    'KFTC': 'KFTC_nifi_e2e.xml',
    'CNAPS': 'CNAPS_nifi_e2e.xml',

    # Middle East Payment Schemes
    'SARIE': 'SARIE_nifi_e2e.xml',
    'UAEFTS': 'UAEFTS_nifi_e2e.xml',

    # LatAm Payment Schemes
    'PIX': 'PIX_nifi_e2e.xml',

    # Southeast Asia Payment Schemes
    'PROMPTPAY': 'PROMPTPAY_nifi_e2e.json',
    'PAYNOW': 'PAYNOW_nifi_e2e.json',
    'INSTAPAY': 'INSTAPAY_nifi_e2e.json',
}

TEST_DATA_DIR = Path(__file__).parent.parent / 'data' / 'samples' / 'nifi_e2e'


def read_file(path: Path) -> str:
    """Read file content."""
    with open(path, 'r') as f:
        return f.read()


def run_test(message_type: str, filename: str) -> dict:
    """Run E2E test for a message type."""
    file_path = TEST_DATA_DIR / filename

    if not file_path.exists():
        return {
            'status': 'SKIPPED',
            'message': f'File not found: {file_path}',
        }

    # Read file content
    content = read_file(file_path)

    # Create unique batch ID
    batch_id = f"e2e_test_{message_type}_{uuid.uuid4().hex[:8]}"

    print(f"\n{'='*60}")
    print(f"Testing {message_type}")
    print(f"  File: {filename}")
    print(f"  Batch ID: {batch_id}")

    # Submit to pipeline
    start_time = time.time()
    try:
        records = [{
            'content': content,
            'message_type': message_type,
        }]

        result = process_medallion_pipeline.delay(
            batch_id=batch_id,
            records=records,
            config={}
        )

        # Wait for result (max 60 seconds)
        output = result.get(timeout=60)
        elapsed = time.time() - start_time

        status = output.get('status', 'UNKNOWN')
        print(f"  Status: {status}")
        print(f"  Time: {elapsed:.2f}s")

        # Check counts from output
        bronze_info = output.get('bronze', {})
        silver_info = output.get('silver', {})
        gold_info = output.get('gold', {})

        bronze_count = len(bronze_info.get('raw_ids', []))
        silver_count = len(silver_info.get('stg_ids', []))
        gold_count = len(gold_info.get('instruction_ids', []))

        print(f"  Bronze: {bronze_count}, Silver: {silver_count}, Gold: {gold_count}")

        # Report failures
        if bronze_info.get('failed'):
            print(f"  Bronze failures: {bronze_info['failed'][:2]}")  # First 2 errors
        if silver_info.get('failed'):
            print(f"  Silver failures: {silver_info['failed'][:2]}")
        if gold_info.get('failed'):
            print(f"  Gold failures: {gold_info['failed'][:2]}")

        # Determine overall success
        if status == 'SUCCESS' and bronze_count > 0 and silver_count > 0 and gold_count > 0:
            overall_status = 'SUCCESS'
        elif status == 'SUCCESS' and bronze_count > 0 and silver_count > 0:
            overall_status = 'PARTIAL'  # Bronze+Silver but no Gold
        elif status == 'SUCCESS' and bronze_count > 0:
            overall_status = 'BRONZE_ONLY'
        else:
            overall_status = 'FAILED'

        return {
            'status': overall_status,
            'batch_id': batch_id,
            'bronze_count': bronze_count,
            'silver_count': silver_count,
            'gold_count': gold_count,
            'elapsed': elapsed,
            'errors': {
                'bronze': bronze_info.get('failed', []),
                'silver': silver_info.get('failed', []),
                'gold': gold_info.get('failed', []),
            }
        }

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)[:200]
        print(f"  ERROR: {error_msg}")
        return {
            'status': 'ERROR',
            'message': error_msg,
            'batch_id': batch_id,
            'elapsed': elapsed,
        }


def main():
    """Run all extractor E2E tests."""
    print("=" * 60)
    print("GPS CDM - All Extractors E2E Test")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Check if specific message type requested
    if len(sys.argv) > 1:
        requested = sys.argv[1]
        if requested in TEST_FILES:
            results = {requested: run_test(requested, TEST_FILES[requested])}
        else:
            print(f"Unknown message type: {requested}")
            print(f"Available types: {', '.join(sorted(TEST_FILES.keys()))}")
            return 1
    else:
        results = {}
        for msg_type, filename in sorted(TEST_FILES.items()):
            results[msg_type] = run_test(msg_type, filename)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Type':<12} {'Status':<12} {'Bronze':<8} {'Silver':<8} {'Gold':<8} {'Time':<8}")
    print("-" * 80)

    success = 0
    partial = 0
    failed = 0
    skipped = 0
    errors = []

    for msg_type, result in sorted(results.items()):
        status = result.get('status', 'UNKNOWN')
        bronze = result.get('bronze_count', 0)
        silver = result.get('silver_count', 0)
        gold = result.get('gold_count', 0)
        elapsed = result.get('elapsed', 0)

        status_display = status
        if status == 'SUCCESS':
            success += 1
            status_display = '✓ SUCCESS'
        elif status == 'PARTIAL':
            partial += 1
            status_display = '⚠ PARTIAL'
        elif status == 'BRONZE_ONLY':
            partial += 1
            status_display = '⚠ BRONZE'
        elif status == 'SKIPPED':
            skipped += 1
            status_display = '- SKIPPED'
        else:
            failed += 1
            status_display = '✗ FAILED'
            if result.get('errors'):
                errors.append((msg_type, result['errors']))
            elif result.get('message'):
                errors.append((msg_type, {'error': result['message']}))

        print(f"{msg_type:<12} {status_display:<12} {bronze:<8} {silver:<8} {gold:<8} {elapsed:.2f}s")

    print("-" * 80)
    total = len(results)
    print(f"Success: {success}/{total}, Partial: {partial}/{total}, Failed: {failed}/{total}, Skipped: {skipped}/{total}")

    # Print errors for failed tests
    if errors:
        print("\n" + "=" * 80)
        print("ERRORS")
        print("=" * 80)
        for msg_type, err_info in errors:
            print(f"\n{msg_type}:")
            if isinstance(err_info, dict):
                for zone, errs in err_info.items():
                    if errs:
                        print(f"  {zone}: {errs[:2]}")  # First 2 errors per zone

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

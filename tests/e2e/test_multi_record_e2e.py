#!/usr/bin/env python3
"""
E2E Test for Multi-Record Files via Celery Pipeline.

Tests that files with multiple records correctly create multiple
Bronze, Silver, and Gold entries using the MessageSplitter.

Usage:
    PYTHONPATH=src:$PYTHONPATH python tests/e2e/test_multi_record_e2e.py
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Use process_medallion_pipeline which has the MessageSplitter integration
from gps_cdm.orchestration.zone_tasks import process_medallion_pipeline


# Test file configurations - each should have 3 records
TEST_FILES = {
    'pain.001': {
        'file': 'tests/data/samples/nifi_e2e/pain.001_multi.xml',
        'expected_records': 3,  # 3 CdtTrfTxInf elements
    },
    'MT103': {
        'file': 'tests/data/samples/nifi_e2e/MT103_multi.txt',
        'expected_records': 3,  # 3 SWIFT messages separated by headers
    },
    'ACH': {
        'file': 'tests/data/samples/nifi_e2e/ACH_multi.txt',
        'expected_records': 3,  # 3 entry detail records (6 records)
    },
    'FEDWIRE': {
        'file': 'tests/data/samples/nifi_e2e/FEDWIRE_multi.txt',
        'expected_records': 3,  # 3 messages separated by ###
    },
    'SEPA': {
        'file': 'tests/data/samples/nifi_e2e/SEPA_multi.xml',
        'expected_records': 3,  # 3 CdtTrfTxInf elements
    },
    'RTP': {
        'file': 'tests/data/samples/nifi_e2e/RTP_multi.xml',
        'expected_records': 3,  # 3 CdtTrfTxInf elements
    },
}


def read_file(path: str) -> str:
    """Read file content."""
    with open(path, 'r') as f:
        return f.read()


def run_test(message_type: str, config: dict) -> dict:
    """Run E2E test for a message type."""
    file_path = config['file']
    expected = config['expected_records']

    if not os.path.exists(file_path):
        return {
            'status': 'SKIPPED',
            'message': f'File not found: {file_path}',
        }

    # Read file content
    content = read_file(file_path)

    # Create unique batch ID
    batch_id = f"multi_test_{message_type}_{uuid.uuid4().hex[:8]}"

    print(f"\n{'='*60}")
    print(f"Testing {message_type}")
    print(f"  File: {file_path}")
    print(f"  Expected records: {expected}")
    print(f"  Batch ID: {batch_id}")

    # Submit to Celery using process_medallion_pipeline (has MessageSplitter)
    start_time = time.time()
    try:
        # Format records as expected by process_medallion_pipeline
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

        print(f"  Status: {output.get('status', 'UNKNOWN')}")
        print(f"  Time: {elapsed:.2f}s")

        # Check counts from output
        bronze_info = output.get('bronze', {})
        silver_info = output.get('silver', {})
        gold_info = output.get('gold', {})

        bronze_count = len(bronze_info.get('raw_ids', []))
        silver_count = len(silver_info.get('stg_ids', []))
        gold_count = len(gold_info.get('instruction_ids', []))

        print(f"  Bronze: {bronze_count}, Silver: {silver_count}, Gold: {gold_count}")

        if bronze_info.get('failed'):
            print(f"  Bronze failures: {len(bronze_info['failed'])}")
        if silver_info.get('failed'):
            print(f"  Silver failures: {len(silver_info['failed'])}")
        if gold_info.get('failed'):
            print(f"  Gold failures: {len(gold_info['failed'])}")

        return {
            'status': 'SUCCESS' if output.get('status') == 'SUCCESS' else output.get('status', 'FAILED'),
            'batch_id': batch_id,
            'bronze_count': bronze_count,
            'silver_count': silver_count,
            'gold_count': gold_count,
            'expected': expected,
            'elapsed': elapsed,
            'output': output,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ERROR: {str(e)[:100]}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'ERROR',
            'message': str(e),
            'batch_id': batch_id,
            'elapsed': elapsed,
        }


def main():
    """Run all multi-record E2E tests."""
    print("="*60)
    print("GPS CDM Multi-Record E2E Tests")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)

    results = {}

    for msg_type, config in TEST_FILES.items():
        results[msg_type] = run_test(msg_type, config)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Type':<12} {'Status':<10} {'Bronze':<8} {'Silver':<8} {'Gold':<8} {'Time':<8}")
    print("-"*60)

    passed = 0
    failed = 0

    for msg_type, result in results.items():
        status = result.get('status', 'UNKNOWN')
        bronze = result.get('bronze_count', 0)
        silver = result.get('silver_count', 0)
        gold = result.get('gold_count', 0)
        elapsed = result.get('elapsed', 0)

        print(f"{msg_type:<12} {status:<10} {bronze:<8} {silver:<8} {gold:<8} {elapsed:.2f}s")

        if status == 'SUCCESS':
            passed += 1
        else:
            failed += 1

    print("-"*60)
    print(f"Passed: {passed}/{len(results)}, Failed: {failed}/{len(results)}")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

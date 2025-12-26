#!/usr/bin/env python3
"""
Process test files through the GPS CDM pipeline.
This script sends each record to Celery for processing.
"""
import json
import sys
import os
import uuid
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def process_file(file_path: str, message_type: str):
    """Process a test file through the pipeline."""
    from gps_cdm.orchestration.celery_tasks import process_bronze_partition

    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"Message Type: {message_type}")
    print(f"{'='*60}")

    with open(file_path, 'r') as f:
        data = json.load(f)

    records = data.get('records', [])
    print(f"Found {len(records)} records")

    results = []
    for i, record in enumerate(records):
        batch_id = f"test-{message_type}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{i+1:03d}"
        partition_id = f"part-{i+1:03d}"

        print(f"\n  Record {i+1}/{len(records)}: {record.get('messageId', 'N/A')}")
        print(f"    Batch ID: {batch_id}")

        try:
            # Call Celery task synchronously for testing
            result = process_bronze_partition(
                partition_id=partition_id,
                file_paths=[],
                message_type=message_type,
                batch_id=batch_id,
                config={'message_content': record}
            )

            print(f"    Status: {result.get('status')}")
            print(f"    Persisted to: {result.get('persisted_to')}")

            if result.get('errors'):
                print(f"    Errors: {result.get('errors')}")

            results.append(result)

        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({'status': 'FAILED', 'error': str(e)})

    # Summary
    success_count = sum(1 for r in results if r.get('status') == 'SUCCESS')
    failed_count = sum(1 for r in results if r.get('status') == 'FAILED')

    print(f"\n{'='*60}")
    print(f"Summary for {message_type}:")
    print(f"  Total: {len(records)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {failed_count}")
    print(f"{'='*60}")

    return results


def main():
    # Set environment variables
    os.environ['GPS_CDM_DATA_SOURCE'] = 'postgresql'
    os.environ['POSTGRES_HOST'] = 'localhost'
    os.environ['POSTGRES_PORT'] = '5433'
    os.environ['POSTGRES_DB'] = 'gps_cdm'
    os.environ['POSTGRES_USER'] = 'gps_cdm_svc'
    os.environ['POSTGRES_PASSWORD'] = 'gps_cdm_password'
    os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
    os.environ['NEO4J_USER'] = 'neo4j'
    os.environ['NEO4J_PASSWORD'] = 'neo4jpassword123'

    test_files = [
        ('pain.001_test_batch.json', 'pain.001'),
        ('mt103_test_batch.json', 'MT103'),
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))

    all_results = {}
    for filename, message_type in test_files:
        file_path = os.path.join(script_dir, filename)
        if os.path.exists(file_path):
            all_results[message_type] = process_file(file_path, message_type)
        else:
            print(f"File not found: {file_path}")

    print("\n" + "="*60)
    print("OVERALL SUMMARY")
    print("="*60)

    for msg_type, results in all_results.items():
        success = sum(1 for r in results if r.get('status') == 'SUCCESS')
        total = len(results)
        print(f"  {msg_type}: {success}/{total} records processed successfully")


if __name__ == '__main__':
    main()

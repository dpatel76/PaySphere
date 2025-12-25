#!/usr/bin/env python3
"""
Process all 63 test message files through the Celery pipeline directly.

This script bypasses NiFi and submits tasks directly to Celery for processing.
Useful for testing when NiFi has permission issues.

Usage:
    python scripts/process_test_messages.py [--input-dir data/nifi_input]
"""

import os
import sys
import json
import uuid
from datetime import datetime
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gps_cdm.orchestration.celery_tasks import process_bronze_partition


def extract_message_type_from_filename(filename):
    """Extract message type from filename."""
    # Remove extension
    base = filename.rsplit('.', 1)[0]
    # Get first part before underscore
    msg_type = base.split('_')[0]

    # Handle special cases
    # ISO 20022: pain_001 -> pain.001
    if msg_type.lower() in ['pain', 'pacs', 'camt', 'acmt']:
        parts = base.split('_')[:2]
        return f"{parts[0].lower()}.{parts[1]}"

    # SWIFT MT and regional: MT103, SEPA_SCT, etc.
    return msg_type


def process_all_messages(input_dir: str = "data/nifi_input"):
    """Process all test message files through Celery."""
    print(f"Processing test messages from {input_dir}")
    print("=" * 60)

    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} not found")
        return

    # Get all files
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    print(f"Found {len(files)} files to process\n")

    results = {'success': 0, 'failed': 0, 'errors': []}

    for i, filename in enumerate(sorted(files), 1):
        filepath = os.path.join(input_dir, filename)
        msg_type = extract_message_type_from_filename(filename)

        print(f"[{i:2d}/{len(files)}] {filename} -> {msg_type}", end=" ")

        try:
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Generate batch ID
            batch_id = f"batch_{uuid.uuid4().hex[:12]}"

            # Create message content dict
            # For XML, wrap in a dict; for JSON, parse it
            if filename.endswith('.json'):
                try:
                    message_content = json.loads(content)
                except:
                    message_content = {"raw": content, "format": "json"}
            elif filename.endswith('.xml'):
                message_content = {
                    "raw_xml": content,
                    "format": "xml",
                    "messageType": msg_type
                }
            else:
                message_content = {
                    "raw": content,
                    "format": filename.rsplit('.', 1)[-1],
                    "messageType": msg_type
                }

            # Call the Celery task synchronously (without .delay)
            result = process_bronze_partition(
                partition_id=batch_id,
                file_paths=[filepath],
                message_type=msg_type,
                batch_id=batch_id,
                config={
                    "message_content": message_content,
                    "source": "test_script",
                    "filename": filename
                }
            )

            if result.get('status') == 'SUCCESS':
                print(f"✓ {result.get('records_processed', 0)} records")
                results['success'] += 1
            else:
                print(f"✗ {result.get('errors', ['Unknown error'])}")
                results['failed'] += 1
                results['errors'].append((filename, result.get('errors')))

        except Exception as e:
            print(f"✗ Error: {e}")
            results['failed'] += 1
            results['errors'].append((filename, str(e)))

    print("\n" + "=" * 60)
    print(f"Processing Complete")
    print(f"  Success: {results['success']}")
    print(f"  Failed: {results['failed']}")

    if results['errors']:
        print("\nErrors:")
        for filename, error in results['errors'][:10]:
            print(f"  - {filename}: {error}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Process test messages through Celery")
    parser.add_argument(
        "--input-dir",
        default="data/nifi_input",
        help="Input directory with test files (default: data/nifi_input)"
    )
    args = parser.parse_args()

    process_all_messages(args.input_dir)


if __name__ == "__main__":
    main()

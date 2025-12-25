"""
GPS CDM - Celery Pipeline Integration Test
============================================

Tests the actual Celery task execution with PostgreSQL.

Prerequisites:
    1. Redis running: redis-server
    2. PostgreSQL running with gps_cdm database
    3. Celery worker: celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold -l info

Usage:
    python tests/integration/test_celery_pipeline.py
"""

import os
import sys
import uuid
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# PostgreSQL connection
PSQL_BIN = "/opt/homebrew/opt/postgresql@16/bin/psql"
DB_NAME = "gps_cdm"


def run_sql(sql: str, fetch: bool = True) -> list:
    """Execute SQL and return results."""
    cmd = [PSQL_BIN, "-d", DB_NAME, "-t", "-A", "-F", "|", "-c", sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SQL Error: {result.stderr}")
        return []
    if fetch and result.stdout.strip():
        rows = []
        for line in result.stdout.strip().split("\n"):
            if line:
                rows.append(line.split("|"))
        return rows
    return []


def test_celery_bronze_task():
    """Test Bronze layer Celery task."""
    print("\n" + "=" * 60)
    print("TEST: CELERY BRONZE TASK")
    print("=" * 60)

    from gps_cdm.orchestration.celery_tasks import process_bronze_partition

    batch_id = str(uuid.uuid4())
    partition_id = f"{batch_id}:bronze:0"

    # Create a temp file with test content
    import tempfile
    test_content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr><MsgId>CELERY-TEST-001</MsgId></GrpHdr>
    </CstmrCdtTrfInitn>
</Document>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(test_content)
        test_file = f.name

    config = {
        "backend": "postgresql",
        "catalog": "gps_cdm",
        "host": "localhost",
        "port": 5432,
    }

    print(f"  Submitting Bronze task...")
    print(f"  Batch ID: {batch_id}")
    print(f"  File: {test_file}")

    # Execute task synchronously for testing
    result = process_bronze_partition(
        partition_id=partition_id,
        file_paths=[test_file],
        message_type="pain001",
        batch_id=batch_id,
        config=config,
    )

    print(f"\n  Task Result:")
    print(f"    Status: {result.get('status')}")
    print(f"    Records Processed: {result.get('records_processed')}")
    print(f"    Duration: {result.get('duration_seconds', 0):.2f}s")

    # Cleanup
    os.unlink(test_file)

    return result.get('status') == 'SUCCESS', batch_id


def test_celery_silver_task():
    """Test Silver layer Celery task."""
    print("\n" + "=" * 60)
    print("TEST: CELERY SILVER TASK")
    print("=" * 60)

    from gps_cdm.orchestration.celery_tasks import process_silver_transform

    batch_id = str(uuid.uuid4())
    partition_id = f"{batch_id}:silver:0"

    config = {
        "backend": "postgresql",
        "catalog": "gps_cdm",
    }

    mapping_path = str(PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml")

    print(f"  Submitting Silver task...")
    print(f"  Batch ID: {batch_id}")
    print(f"  Mapping: {mapping_path}")

    result = process_silver_transform(
        partition_id=partition_id,
        record_ids=[],
        message_type="pain001",
        mapping_path=mapping_path,
        batch_id=batch_id,
        config=config,
    )

    print(f"\n  Task Result:")
    print(f"    Status: {result.get('status')}")
    print(f"    Target Table: {result.get('target_table')}")
    print(f"    Duration: {result.get('duration_seconds', 0):.2f}s")

    return result.get('status') in ['SUCCESS', 'PARTIAL'], batch_id


def test_celery_gold_task():
    """Test Gold layer Celery task."""
    print("\n" + "=" * 60)
    print("TEST: CELERY GOLD TASK")
    print("=" * 60)

    from gps_cdm.orchestration.celery_tasks import process_gold_aggregate

    batch_id = str(uuid.uuid4())
    partition_id = f"{batch_id}:gold:0"

    config = {
        "backend": "postgresql",
        "catalog": "gps_cdm",
    }

    mapping_paths = {
        "pain001": str(PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml"),
    }

    print(f"  Submitting Gold task...")
    print(f"  Batch ID: {batch_id}")

    result = process_gold_aggregate(
        partition_id=partition_id,
        source_tables=["stg_pain001"],
        mapping_paths=mapping_paths,
        batch_id=batch_id,
        config=config,
    )

    print(f"\n  Task Result:")
    print(f"    Status: {result.get('status')}")
    print(f"    Target Table: {result.get('target_table')}")
    print(f"    Duration: {result.get('duration_seconds', 0):.2f}s")

    return result.get('status') == 'SUCCESS', batch_id


def test_celery_async_workflow():
    """Test async Celery workflow with actual task submission."""
    print("\n" + "=" * 60)
    print("TEST: CELERY ASYNC WORKFLOW")
    print("=" * 60)

    from gps_cdm.orchestration.celery_tasks import (
        process_bronze_partition,
        app as celery_app,
    )

    # Check if Celery workers are running
    print("  Checking Celery connection...")
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        if active:
            print(f"  [OK] Celery workers found: {list(active.keys())}")
        else:
            print("  [WARN] No active Celery workers found")
            print("         Start workers with: celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold -l info")
            return False, None
    except Exception as e:
        print(f"  [WARN] Cannot connect to Celery: {e}")
        print("         Make sure Redis is running and Celery workers are started")
        return False, None

    batch_id = str(uuid.uuid4())
    partition_id = f"{batch_id}:async:0"

    # Create test file
    import tempfile
    test_content = '{"messageType": "pain.001", "content": "async test"}'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(test_content)
        test_file = f.name

    config = {"backend": "postgresql", "catalog": "gps_cdm"}

    print(f"\n  Submitting async Bronze task...")
    print(f"  Batch ID: {batch_id}")

    # Submit task asynchronously
    async_result = process_bronze_partition.delay(
        partition_id=partition_id,
        file_paths=[test_file],
        message_type="pain001",
        batch_id=batch_id,
        config=config,
    )

    print(f"  Task ID: {async_result.id}")
    print(f"  Waiting for result (timeout 30s)...")

    try:
        result = async_result.get(timeout=30)
        print(f"\n  [OK] Async Task Completed:")
        print(f"    Status: {result.get('status')}")
        print(f"    Records: {result.get('records_processed')}")
        os.unlink(test_file)
        return result.get('status') == 'SUCCESS', batch_id
    except Exception as e:
        print(f"\n  [FAIL] Async task failed: {e}")
        os.unlink(test_file)
        return False, None


def test_celery_workflow_chain():
    """Test chained workflow: Bronze -> Silver -> Gold."""
    print("\n" + "=" * 60)
    print("TEST: CELERY WORKFLOW CHAIN (Bronze -> Silver -> Gold)")
    print("=" * 60)

    from celery import chain
    from gps_cdm.orchestration.celery_tasks import (
        process_bronze_partition,
        process_silver_transform,
        process_gold_aggregate,
        app as celery_app,
    )

    # Check workers
    try:
        inspect = celery_app.control.inspect()
        if not inspect.active():
            print("  [SKIP] No Celery workers running")
            return False, None
    except:
        print("  [SKIP] Cannot connect to Celery")
        return False, None

    batch_id = str(uuid.uuid4())

    # Create test file
    import tempfile
    test_content = """<?xml version="1.0"?><Document><MsgId>CHAIN-TEST</MsgId></Document>"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(test_content)
        test_file = f.name

    config = {"backend": "postgresql", "catalog": "gps_cdm"}
    mapping_path = str(PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml")

    print(f"  Creating workflow chain...")
    print(f"  Batch ID: {batch_id}")

    # Create chain
    workflow = chain(
        process_bronze_partition.s(
            partition_id=f"{batch_id}:bronze:0",
            file_paths=[test_file],
            message_type="pain001",
            batch_id=batch_id,
            config=config,
        ),
        process_silver_transform.s(
            partition_id=f"{batch_id}:silver:0",
            record_ids=[],
            message_type="pain001",
            mapping_path=mapping_path,
            batch_id=batch_id,
            config=config,
        ),
        process_gold_aggregate.s(
            partition_id=f"{batch_id}:gold:0",
            source_tables=["stg_pain001"],
            mapping_paths={"pain001": mapping_path},
            batch_id=batch_id,
            config=config,
        ),
    )

    print("  Executing workflow chain...")
    async_result = workflow.apply_async()

    try:
        result = async_result.get(timeout=60)
        print(f"\n  [OK] Workflow Chain Completed:")
        print(f"    Final Status: {result.get('status')}")
        os.unlink(test_file)
        return True, batch_id
    except Exception as e:
        print(f"\n  [FAIL] Workflow failed: {e}")
        os.unlink(test_file)
        return False, None


def show_celery_status():
    """Show Celery cluster status."""
    print("\n" + "=" * 60)
    print("CELERY CLUSTER STATUS")
    print("=" * 60)

    from gps_cdm.orchestration.celery_tasks import app as celery_app

    try:
        inspect = celery_app.control.inspect()

        # Active workers
        active = inspect.active()
        print(f"\n  Active Workers:")
        if active:
            for worker, tasks in active.items():
                print(f"    {worker}: {len(tasks)} active tasks")
        else:
            print("    None - Start workers with:")
            print("    celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold,dq,cdc -l info")

        # Registered tasks
        registered = inspect.registered()
        print(f"\n  Registered Tasks:")
        if registered:
            for worker, tasks in registered.items():
                gps_tasks = [t for t in tasks if 'gps_cdm' in t]
                print(f"    {worker}: {len(gps_tasks)} GPS CDM tasks")
                for task in gps_tasks[:5]:
                    print(f"      - {task}")

        # Queues
        print(f"\n  Configured Queues:")
        print(f"    bronze, silver, gold, analytical, dq, cdc")

    except Exception as e:
        print(f"  [ERROR] Cannot connect to Celery: {e}")
        print(f"  Make sure Redis is running: redis-cli ping")


def main():
    """Run Celery integration tests."""
    print("\n" + "=" * 60)
    print("GPS CDM - CELERY INTEGRATION TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")

    # Show Celery status
    show_celery_status()

    results = []

    # Test 1: Synchronous Bronze task
    success, batch_id = test_celery_bronze_task()
    results.append(("Bronze Task (sync)", success))

    # Test 2: Synchronous Silver task
    success, batch_id = test_celery_silver_task()
    results.append(("Silver Task (sync)", success))

    # Test 3: Synchronous Gold task
    success, batch_id = test_celery_gold_task()
    results.append(("Gold Task (sync)", success))

    # Test 4: Async task (requires workers)
    success, batch_id = test_celery_async_workflow()
    results.append(("Async Task", success))

    # Test 5: Workflow chain (requires workers)
    success, batch_id = test_celery_workflow_chain()
    results.append(("Workflow Chain", success))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    passed = sum(1 for _, p in results if p)
    print(f"\n  {passed}/{len(results)} tests passed")

    if passed < len(results):
        print("\n  To run all tests, start Celery workers:")
        print("  celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold,dq,cdc -l info")


if __name__ == "__main__":
    main()

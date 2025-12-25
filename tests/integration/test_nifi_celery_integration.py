"""
GPS CDM - NiFi + Celery Integration Test
==========================================

This test simulates exactly how NiFi orchestrates Celery tasks:
1. NiFi uses InvokeHTTP to call Flower's HTTP API
2. Flower routes task to appropriate Celery queue
3. Celery worker executes task and returns result
4. NiFi waits for completion via Wait/Notify pattern

Prerequisites:
    1. Redis running: redis-server (or docker-compose)
    2. PostgreSQL running with gps_cdm database
    3. Flower running: celery -A gps_cdm.orchestration.celery_tasks flower --port=5555
    4. Celery workers: celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold,dq,cdc -l info

Quick Start with Docker:
    docker-compose -f docker-compose.nifi.yaml up -d redis postgres flower
    PYTHONPATH=src celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold,dq,cdc -l info &
    PYTHONPATH=src python tests/integration/test_nifi_celery_integration.py

Usage:
    python tests/integration/test_nifi_celery_integration.py
"""

import os
import sys
import uuid
import json
import time
import tempfile
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configuration (matches NiFi template variables)
FLOWER_URL = os.environ.get("FLOWER_URL", "http://localhost:5555")
FLOWER_AUTH = ("admin", "flowerpassword")  # If auth enabled
DB_CONFIG = {
    "backend": "postgresql",
    "catalog": "gps_cdm",
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", ""),
    "password": os.environ.get("DB_PASSWORD", ""),
}
MAPPING_PATH = str(PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml")


def flower_api_available() -> bool:
    """Check if Flower API is available (simulating NiFi's connectivity check)."""
    try:
        response = requests.get(f"{FLOWER_URL}/api/workers", timeout=5)
        return response.status_code == 200
    except:
        return False


def submit_celery_task(task_name: str, args: list, kwargs: dict = None) -> Optional[str]:
    """
    Submit a Celery task via Flower HTTP API.

    This is EXACTLY how NiFi submits tasks using InvokeHTTP processor:
    - POST to /api/task/send-task/<task_name>
    - JSON body with args and kwargs
    - Returns task_id for tracking
    """
    url = f"{FLOWER_URL}/api/task/send-task/{task_name}"
    payload = {
        "args": args,
        "kwargs": kwargs or {},
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("task-id")
        else:
            print(f"  [ERROR] Task submission failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  [ERROR] Failed to submit task: {e}")
        return None


def wait_for_task(task_id: str, timeout: int = 60) -> Optional[Dict[str, Any]]:
    """
    Wait for Celery task to complete via Flower API.

    This simulates NiFi's Wait processor pattern:
    - Poll /api/task/result/<task_id>
    - Wait until state is SUCCESS, FAILURE, or timeout
    """
    url = f"{FLOWER_URL}/api/task/result/{task_id}"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                result = response.json()
                state = result.get("state")

                if state == "SUCCESS":
                    return result.get("result")
                elif state == "FAILURE":
                    print(f"  [ERROR] Task failed: {result.get('result')}")
                    return None
                elif state in ["PENDING", "STARTED", "RETRY"]:
                    time.sleep(1)
                    continue
            else:
                time.sleep(1)
        except Exception as e:
            time.sleep(1)

    print(f"  [TIMEOUT] Task {task_id} did not complete in {timeout}s")
    return None


def test_nifi_bronze_flow():
    """
    Simulate NiFi Zone 1: Bronze Layer flow.

    NiFi Flow:
    1. ListSFTP/ConsumeKafka -> Get payment file
    2. UpdateAttribute -> Add batch.id, ingestion.timestamp
    3. InvokeHTTP -> Submit to Celery Bronze task via Flower API
    4. Wait -> Wait for Bronze completion
    """
    print("\n" + "=" * 60)
    print("NIFI SIMULATION: ZONE 1 - BRONZE LAYER")
    print("=" * 60)

    # Step 1: Simulate NiFi ListSFTP/FetchSFTP (create test file)
    print("  [NiFi] ListSFTP -> Fetching payment file...")

    test_content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>NIFI-INTEGRATION-TEST-001</MsgId>
            <CreDtTm>2024-12-24T10:00:00</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>10000.00</CtrlSum>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PMTINF-NIFI-001</PmtInfId>
            <CdtTrfTxInf>
                <PmtId><EndToEndId>E2E-NIFI-001</EndToEndId></PmtId>
                <Amt><InstdAmt Ccy="USD">10000.00</InstdAmt></Amt>
                <Cdtr><Nm>Test Corporation</Nm></Cdtr>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(test_content)
        test_file = f.name

    print(f"  [NiFi] File fetched: {test_file}")

    # Step 2: Simulate NiFi UpdateAttribute (add metadata)
    batch_id = str(uuid.uuid4())
    ingestion_timestamp = datetime.utcnow().isoformat()
    message_type = "pain001"

    print(f"  [NiFi] UpdateAttribute -> batch.id = {batch_id[:8]}...")
    print(f"  [NiFi] UpdateAttribute -> ingestion.timestamp = {ingestion_timestamp}")
    print(f"  [NiFi] UpdateAttribute -> message.type = {message_type}")

    # Step 3: Simulate NiFi InvokeHTTP -> Submit to Celery via Flower
    print(f"  [NiFi] InvokeHTTP -> POST {FLOWER_URL}/api/task/send-task/...")

    task_name = "gps_cdm.orchestration.celery_tasks.process_bronze_partition"
    partition_id = f"{batch_id}:bronze:0"

    task_id = submit_celery_task(
        task_name=task_name,
        args=[partition_id, [test_file], message_type, batch_id, DB_CONFIG],
    )

    if not task_id:
        print("  [FAIL] Failed to submit Bronze task")
        os.unlink(test_file)
        return None, None

    print(f"  [NiFi] Task submitted: {task_id}")

    # Step 4: Simulate NiFi Wait processor
    print(f"  [NiFi] Wait -> Waiting for Bronze completion...")

    result = wait_for_task(task_id, timeout=60)

    # Cleanup
    os.unlink(test_file)

    if result:
        print(f"  [NiFi] Wait -> Task completed!")
        print(f"         Status: {result.get('status')}")
        print(f"         Records Processed: {result.get('records_processed')}")
        print(f"         Duration: {result.get('duration_seconds', 0):.2f}s")
        return batch_id, result
    else:
        print("  [FAIL] Bronze task did not complete")
        return None, None


def test_nifi_silver_flow(batch_id: str):
    """
    Simulate NiFi Zone 2: Silver Layer flow.
    """
    print("\n" + "=" * 60)
    print("NIFI SIMULATION: ZONE 2 - SILVER LAYER")
    print("=" * 60)

    print(f"  [NiFi] Received from Bronze Zone: batch.id = {batch_id[:8]}...")

    # Simulate NiFi InvokeHTTP for Silver transform
    print(f"  [NiFi] InvokeHTTP -> Submit Silver transform task...")

    task_name = "gps_cdm.orchestration.celery_tasks.process_silver_transform"
    partition_id = f"{batch_id}:silver:0"

    task_id = submit_celery_task(
        task_name=task_name,
        args=[partition_id, [], "pain001", MAPPING_PATH, batch_id, DB_CONFIG],
    )

    if not task_id:
        print("  [FAIL] Failed to submit Silver task")
        return None

    print(f"  [NiFi] Task submitted: {task_id}")
    print(f"  [NiFi] Wait -> Waiting for Silver completion...")

    result = wait_for_task(task_id, timeout=60)

    if result:
        print(f"  [NiFi] Wait -> Task completed!")
        print(f"         Status: {result.get('status')}")
        print(f"         Target Table: {result.get('target_table')}")
        return result
    else:
        print("  [FAIL] Silver task did not complete")
        return None


def test_nifi_gold_flow(batch_id: str):
    """
    Simulate NiFi Zone 3: Gold Layer flow.
    """
    print("\n" + "=" * 60)
    print("NIFI SIMULATION: ZONE 3 - GOLD LAYER (CDM)")
    print("=" * 60)

    print(f"  [NiFi] Received from Silver Zone: batch.id = {batch_id[:8]}...")

    # Simulate NiFi InvokeHTTP for Gold aggregate
    print(f"  [NiFi] InvokeHTTP -> Submit Gold aggregate task...")

    task_name = "gps_cdm.orchestration.celery_tasks.process_gold_aggregate"
    partition_id = f"{batch_id}:gold:0"

    task_id = submit_celery_task(
        task_name=task_name,
        args=[
            partition_id,
            ["stg_pain001"],
            {"pain001": MAPPING_PATH},
            batch_id,
            DB_CONFIG,
        ],
    )

    if not task_id:
        print("  [FAIL] Failed to submit Gold task")
        return None

    print(f"  [NiFi] Task submitted: {task_id}")
    print(f"  [NiFi] Wait -> Waiting for Gold completion...")

    result = wait_for_task(task_id, timeout=120)

    if result:
        print(f"  [NiFi] Wait -> Task completed!")
        print(f"         Status: {result.get('status')}")
        print(f"         Records Processed: {result.get('records_processed', 0)}")
        return result
    else:
        print("  [FAIL] Gold task did not complete")
        return None


def test_nifi_dq_flow(batch_id: str):
    """
    Simulate NiFi Zone 5: DQ Layer flow.
    """
    print("\n" + "=" * 60)
    print("NIFI SIMULATION: ZONE 5 - DATA QUALITY")
    print("=" * 60)

    print(f"  [NiFi] Received from Gold Zone: batch.id = {batch_id[:8]}...")

    # Simulate NiFi InvokeHTTP for DQ evaluation
    print(f"  [NiFi] InvokeHTTP -> Submit DQ evaluation task...")

    task_name = "gps_cdm.orchestration.celery_tasks.run_dq_evaluation"

    task_id = submit_celery_task(
        task_name=task_name,
        args=[batch_id, "gold", "cdm_payment_instruction", DB_CONFIG],
    )

    if not task_id:
        print("  [FAIL] Failed to submit DQ task")
        return None

    print(f"  [NiFi] Task submitted: {task_id}")
    print(f"  [NiFi] Wait -> Waiting for DQ completion...")

    result = wait_for_task(task_id, timeout=60)

    if result:
        print(f"  [NiFi] Wait -> Task completed!")
        print(f"         Status: {result.get('status')}")
        return result
    else:
        print("  [FAIL] DQ task did not complete")
        return None


def run_full_nifi_celery_test():
    """
    Run complete NiFi + Celery integration test.

    This simulates the entire NiFi flow from gps_cdm_zone_orchestration.json:
    Zone 0 (Ingestion) -> Zone 1 (Bronze) -> Zone 2 (Silver) -> Zone 3 (Gold) -> Zone 5 (DQ)
    """
    print("\n" + "=" * 60)
    print("GPS CDM - NIFI + CELERY INTEGRATION TEST")
    print("=" * 60)
    print(f"Flower API: {FLOWER_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Mapping: {MAPPING_PATH}")

    # Check Flower API (simulates NiFi connectivity check)
    print("\n[PREFLIGHT] Checking Flower API availability...")
    if not flower_api_available():
        print("[FAIL] Flower API not available at {FLOWER_URL}")
        print("\nTo start the required services:")
        print("  1. Start Redis: redis-server")
        print("  2. Start Flower: PYTHONPATH=src celery -A gps_cdm.orchestration.celery_tasks flower --port=5555")
        print("  3. Start Workers: PYTHONPATH=src celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold,dq,cdc -l info")
        return

    print("[OK] Flower API available")

    # Check for active workers
    try:
        response = requests.get(f"{FLOWER_URL}/api/workers", timeout=5)
        workers = response.json()
        if workers:
            print(f"[OK] Celery workers found: {list(workers.keys())}")
        else:
            print("[WARN] No Celery workers active")
            print("       Start workers: PYTHONPATH=src celery -A gps_cdm.orchestration.celery_tasks worker -Q bronze,silver,gold,dq,cdc -l info")
            return
    except Exception as e:
        print(f"[WARN] Could not check workers: {e}")

    # Run the flow
    results = []

    # Zone 1: Bronze
    batch_id, bronze_result = test_nifi_bronze_flow()
    results.append(("Zone 1: Bronze", bronze_result is not None))

    if not batch_id:
        print("\n[ABORT] Bronze failed, cannot continue")
        return

    # Zone 2: Silver
    silver_result = test_nifi_silver_flow(batch_id)
    results.append(("Zone 2: Silver", silver_result is not None))

    # Zone 3: Gold
    gold_result = test_nifi_gold_flow(batch_id)
    results.append(("Zone 3: Gold", gold_result is not None))

    # Zone 5: DQ
    dq_result = test_nifi_dq_flow(batch_id)
    results.append(("Zone 5: DQ", dq_result is not None))

    # Summary
    print("\n" + "=" * 60)
    print("NIFI + CELERY INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"\n  Batch ID: {batch_id}")
    print()

    for zone_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {zone_name}")

    passed_count = sum(1 for _, p in results if p)
    print(f"\n  {passed_count}/{len(results)} zones passed")

    if passed_count == len(results):
        print("\n  [SUCCESS] Full NiFi + Celery integration test PASSED!")
        print("  The pipeline correctly processes: Ingestion -> Bronze -> Silver -> Gold -> DQ")
    else:
        print("\n  [PARTIAL] Some zones failed. Check logs above for details.")


if __name__ == "__main__":
    run_full_nifi_celery_test()

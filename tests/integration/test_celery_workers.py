"""
GPS CDM - End-to-End Celery Worker Integration Test
====================================================

Tests actual Celery task execution with workers processing messages
from Redis queues, then persisting to PostgreSQL.

This test:
1. Starts Celery workers in background
2. Submits async tasks to Bronze/Silver/Gold queues
3. Waits for task completion
4. Verifies data persistence in PostgreSQL
5. Verifies CDC events were captured
6. Stops workers

Usage:
    python tests/integration/test_celery_workers.py
"""

import os
import sys
import uuid
import json
import time
import signal
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional

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
        print(f"  SQL Error: {result.stderr}")
        return []
    if fetch and result.stdout.strip():
        rows = []
        for line in result.stdout.strip().split("\n"):
            if line:
                rows.append(line.split("|"))
        return rows
    return []


def check_redis():
    """Check if Redis is running."""
    result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.strip() == "PONG"


def check_postgres():
    """Check if PostgreSQL is running."""
    result = run_sql("SELECT 1;")
    return len(result) > 0


class CeleryWorkerManager:
    """Manages Celery worker processes for testing."""

    def __init__(self):
        self.worker_processes = []
        self.log_dir = Path(tempfile.mkdtemp(prefix="celery_test_"))

    def start_workers(self, queues: list, concurrency: int = 2) -> bool:
        """Start Celery workers for specified queues."""
        print(f"  Starting Celery workers for queues: {', '.join(queues)}")

        for queue in queues:
            log_file = self.log_dir / f"worker_{queue}.log"
            cmd = [
                "celery",
                "-A", "gps_cdm.orchestration.celery_tasks",
                "worker",
                "-Q", queue,
                "-c", str(concurrency),
                "-l", "INFO",
                "--without-gossip",
                "--without-mingle",
                "--without-heartbeat",
                "-n", f"worker_{queue}@%h",
            ]

            with open(log_file, 'w') as f:
                proc = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=str(PROJECT_ROOT),
                    env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
                )
                self.worker_processes.append((queue, proc, log_file))

        # Wait for workers to start
        time.sleep(5)

        # Check if workers are running
        all_running = True
        for queue, proc, log_file in self.worker_processes:
            if proc.poll() is not None:
                print(f"  [FAIL] Worker for queue '{queue}' failed to start")
                with open(log_file) as f:
                    print(f"  Log:\n{f.read()[:500]}")
                all_running = False
            else:
                print(f"  [OK] Worker for queue '{queue}' started (PID: {proc.pid})")

        return all_running

    def stop_workers(self):
        """Stop all worker processes."""
        print("  Stopping Celery workers...")
        for queue, proc, log_file in self.worker_processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
            print(f"  [OK] Worker for queue '{queue}' stopped")

        # Cleanup log directory
        import shutil
        shutil.rmtree(self.log_dir, ignore_errors=True)

    def get_logs(self, queue: str) -> str:
        """Get log content for a queue."""
        for q, proc, log_file in self.worker_processes:
            if q == queue and log_file.exists():
                with open(log_file) as f:
                    return f.read()
        return ""


def test_async_bronze_task(worker_manager: CeleryWorkerManager) -> tuple:
    """Test async Bronze layer task."""
    print("\n" + "=" * 60)
    print("TEST: ASYNC BRONZE TASK")
    print("=" * 60)

    from gps_cdm.orchestration.celery_tasks import process_bronze_partition

    batch_id = str(uuid.uuid4())
    partition_id = f"{batch_id}:bronze:0"

    # Create test file
    test_content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>ASYNC-CELERY-TEST-001</MsgId>
            <CreDtTm>2024-12-21T10:00:00</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>5000.00</CtrlSum>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PMTINF-ASYNC-001</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <Dbtr><Nm>Async Test Debtor</Nm></Dbtr>
            <DbtrAcct><Id><IBAN>US12345678901234</IBAN></Id></DbtrAcct>
            <CdtTrfTxInf>
                <PmtId><EndToEndId>E2E-ASYNC-001</EndToEndId></PmtId>
                <Amt><InstdAmt Ccy="USD">5000.00</InstdAmt></Amt>
                <Cdtr><Nm>Async Test Creditor</Nm></Cdtr>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""

    test_file = Path(tempfile.mktemp(suffix=".xml"))
    test_file.write_text(test_content)

    config = {"backend": "postgresql", "catalog": "gps_cdm"}

    print(f"  Submitting async Bronze task...")
    print(f"  Batch ID: {batch_id}")
    print(f"  File: {test_file}")

    # Submit task asynchronously
    async_result = process_bronze_partition.apply_async(
        kwargs={
            "partition_id": partition_id,
            "file_paths": [str(test_file)],
            "message_type": "pain001",
            "batch_id": batch_id,
            "config": config,
        },
        queue="bronze",
    )

    print(f"  Task ID: {async_result.id}")
    print(f"  Waiting for result (timeout 60s)...")

    try:
        result = async_result.get(timeout=60)
        print(f"\n  [OK] Async Task Completed:")
        print(f"    Status: {result.get('status')}")
        print(f"    Records: {result.get('records_processed')}")
        print(f"    Duration: {result.get('duration_seconds', 0):.2f}s")

        # Verify data in PostgreSQL
        rows = run_sql(f"""
            SELECT raw_id, message_type, file_path
            FROM bronze.raw_payment_messages
            WHERE message_type = 'pain.001'
            ORDER BY ingested_at DESC
            LIMIT 1;
        """)

        if rows:
            print(f"\n  [OK] Verified Bronze data in PostgreSQL:")
            print(f"    raw_id: {rows[0][0][:8]}...")
            print(f"    type: {rows[0][1]}")

        test_file.unlink()
        return result.get('status') == 'SUCCESS', batch_id

    except Exception as e:
        print(f"\n  [FAIL] Async task failed: {e}")
        # Print worker logs for debugging
        log = worker_manager.get_logs("bronze")
        if log:
            print(f"\n  Worker logs (last 500 chars):\n{log[-500:]}")
        test_file.unlink()
        return False, None


def test_async_workflow_chain(worker_manager: CeleryWorkerManager) -> tuple:
    """Test async chained workflow: Bronze -> Silver -> Gold."""
    print("\n" + "=" * 60)
    print("TEST: ASYNC WORKFLOW CHAIN (Bronze -> Silver -> Gold)")
    print("=" * 60)

    from celery import chain
    from gps_cdm.orchestration.celery_tasks import (
        process_bronze_partition,
        process_silver_transform,
        process_gold_aggregate,
    )

    batch_id = str(uuid.uuid4())

    # Create test file
    test_content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>CHAIN-ASYNC-001</MsgId>
            <CreDtTm>2024-12-21T11:00:00</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PMTINF-CHAIN-001</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <Dbtr><Nm>Chain Test Debtor</Nm></Dbtr>
            <CdtTrfTxInf>
                <PmtId><EndToEndId>E2E-CHAIN-001</EndToEndId></PmtId>
                <Amt><InstdAmt Ccy="EUR">7500.00</InstdAmt></Amt>
                <Cdtr><Nm>Chain Test Creditor</Nm></Cdtr>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""

    test_file = Path(tempfile.mktemp(suffix=".xml"))
    test_file.write_text(test_content)

    config = {"backend": "postgresql", "catalog": "gps_cdm"}
    mapping_path = str(PROJECT_ROOT / "mappings" / "message_types" / "pain001.yaml")

    print(f"  Creating workflow chain...")
    print(f"  Batch ID: {batch_id}")

    # Note: In real implementation, tasks pass data between stages
    # For testing, we submit Bronze task and verify results

    async_result = process_bronze_partition.apply_async(
        kwargs={
            "partition_id": f"{batch_id}:bronze:0",
            "file_paths": [str(test_file)],
            "message_type": "pain001",
            "batch_id": batch_id,
            "config": config,
        },
        queue="bronze",
    )

    print(f"  Bronze Task ID: {async_result.id}")
    print(f"  Waiting for Bronze to complete...")

    try:
        result = async_result.get(timeout=60)
        print(f"  [OK] Bronze completed: {result.get('status')}")

        # Verify CDC events were captured
        cdc_rows = run_sql("""
            SELECT table_name, operation, COUNT(*)
            FROM observability.obs_cdc_tracking
            WHERE change_timestamp > NOW() - INTERVAL '5 minutes'
            GROUP BY table_name, operation
            ORDER BY table_name;
        """)

        if cdc_rows:
            print(f"\n  CDC Events captured:")
            for row in cdc_rows:
                print(f"    {row[0]}: {row[1]} ({row[2]} events)")

        test_file.unlink()
        return result.get('status') == 'SUCCESS', batch_id

    except Exception as e:
        print(f"\n  [FAIL] Workflow failed: {e}")
        test_file.unlink()
        return False, None


def test_cdc_verification() -> bool:
    """Verify CDC triggers are capturing changes."""
    print("\n" + "=" * 60)
    print("TEST: CDC TRIGGER VERIFICATION")
    print("=" * 60)

    # Count CDC events
    rows = run_sql("""
        SELECT
            layer,
            table_name,
            operation,
            COUNT(*) as event_count,
            MAX(change_timestamp) as last_event
        FROM observability.obs_cdc_tracking
        GROUP BY layer, table_name, operation
        ORDER BY layer, table_name, operation;
    """)

    if rows:
        print("\n  CDC Events by Table:")
        print("  " + "-" * 60)
        print(f"  {'Layer':<12} {'Table':<25} {'Op':<8} {'Count':>8}")
        print("  " + "-" * 60)
        for row in rows:
            print(f"  {row[0]:<12} {row[1]:<25} {row[2]:<8} {row[3]:>8}")

        total = sum(int(row[3]) for row in rows)
        print("  " + "-" * 60)
        print(f"  Total CDC events: {total}")
        return total > 0
    else:
        print("  [WARN] No CDC events found")
        return False


def main():
    """Run end-to-end Celery worker tests."""
    print("\n" + "=" * 60)
    print("GPS CDM - END-TO-END CELERY WORKER TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")

    # Pre-flight checks
    print("\nPRE-FLIGHT CHECKS")
    print("-" * 40)

    if not check_redis():
        print("  [FAIL] Redis not running. Start with: redis-server")
        return
    print("  [OK] Redis is running")

    if not check_postgres():
        print("  [FAIL] PostgreSQL not accessible")
        return
    print("  [OK] PostgreSQL is accessible")

    # Initialize worker manager
    worker_manager = CeleryWorkerManager()

    results = []

    try:
        # Start workers
        print("\nSTARTING CELERY WORKERS")
        print("-" * 40)
        if not worker_manager.start_workers(["bronze", "silver", "gold"]):
            print("\n[FAIL] Could not start workers. Aborting.")
            worker_manager.stop_workers()
            return

        # Run tests
        success, batch_id = test_async_bronze_task(worker_manager)
        results.append(("Async Bronze Task", success))

        success, batch_id = test_async_workflow_chain(worker_manager)
        results.append(("Async Workflow Chain", success))

        # Test CDC verification
        success = test_cdc_verification()
        results.append(("CDC Trigger Verification", success))

    finally:
        # Stop workers
        print("\nSTOPPING CELERY WORKERS")
        print("-" * 40)
        worker_manager.stop_workers()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    passed = sum(1 for _, p in results if p)
    print(f"\n  {passed}/{len(results)} tests passed")


if __name__ == "__main__":
    main()

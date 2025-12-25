"""
GPS CDM - Orchestrated Pipeline Integration Test
=================================================

Tests the full orchestrated pipeline:
1. Celery tasks process data
2. Data is written to Databricks (Bronze → Silver → Gold)
3. Lineage is synced to Neo4j knowledge graph
4. API reads from correct sources

Prerequisites:
- Databricks Free Edition configured
- Neo4j running
- Redis running (for Celery)
- Environment variables set

Run:
    pytest tests/integration/test_orchestrated_pipeline.py -v -s
"""

import pytest
import os
import uuid
from datetime import datetime
import time


# Sample XML for testing
SAMPLE_PAIN001_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>TEST_MSG_{msg_id}</MsgId>
      <CreDtTm>{timestamp}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT_{msg_id}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <Dbtr>
        <Nm>Test Debtor {msg_id}</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id><IBAN>DE89370400440532013000</IBAN></Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId><BIC>COBADEFFXXX</BIC></FinInstnId>
      </DbtrAgt>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>E2E_{msg_id}</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="EUR">{amount}</InstdAmt>
        </Amt>
        <Cdtr>
          <Nm>Test Creditor {msg_id}</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id><IBAN>FR1420041010050500013M02606</IBAN></Id>
        </CdtrAcct>
        <CdtrAgt>
          <FinInstnId><BIC>BNPAFRPPXXX</BIC></FinInstnId>
        </CdtrAgt>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''


@pytest.fixture
def databricks_connector():
    """Get Databricks connector."""
    from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector

    required_vars = ["DATABRICKS_SERVER_HOSTNAME", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        pytest.skip(f"Missing environment variables: {missing}")

    connector = DatabricksConnector()
    if not connector.is_available():
        pytest.skip("Databricks is not available")

    yield connector
    connector.close()


@pytest.fixture
def neo4j_service():
    """Get Neo4j service."""
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    service = get_neo4j_service()
    if not service.is_available():
        pytest.skip("Neo4j is not available")
    return service


@pytest.fixture
def celery_app():
    """Get Celery app configured for testing."""
    from gps_cdm.orchestration.databricks_pipeline_tasks import app
    return app


def generate_test_xml(amount: float = 1000.00) -> tuple:
    """Generate test XML with unique identifiers."""
    msg_id = uuid.uuid4().hex[:8]
    timestamp = datetime.utcnow().isoformat()
    xml = SAMPLE_PAIN001_XML.format(
        msg_id=msg_id,
        timestamp=timestamp,
        amount=amount,
    )
    return msg_id, xml


class TestCeleryTaskDirect:
    """
    Test Celery tasks directly (synchronously) without a worker.
    This tests the task logic without needing the full Celery infrastructure.
    """

    def test_process_batch_to_databricks_sync(self, databricks_connector, neo4j_service):
        """Test the batch processing task synchronously."""
        from gps_cdm.orchestration.databricks_pipeline_tasks import process_batch_to_databricks

        # Generate test data
        msg_id, xml_content = generate_test_xml(amount=2500.00)
        batch_id = f"test_celery_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{msg_id}"

        print(f"\n{'='*60}")
        print(f"Testing Celery Task: process_batch_to_databricks")
        print(f"{'='*60}")
        print(f"Batch ID: {batch_id}")

        # Run task synchronously (without Celery worker)
        result = process_batch_to_databricks.apply(
            args=[batch_id, xml_content, "pain.001", "test_orchestrated.xml"]
        ).get()

        print(f"\nTask Result:")
        print(f"  Status: {result['status']}")
        print(f"  Bronze Count: {result['bronze_count']}")
        print(f"  Silver Count: {result['silver_count']}")
        print(f"  Gold Count: {result['gold_count']}")
        print(f"  Duration: {result.get('duration_ms', 'N/A')} ms")

        # Verify result
        assert result["status"] == "COMPLETED", f"Expected COMPLETED, got {result['status']}"
        assert result["bronze_count"] == 1
        assert result["silver_count"] == 1
        assert result["gold_count"] == 1

        # Verify data in Databricks
        print("\nVerifying data in Databricks...")
        batch = databricks_connector.get_batch_lineage(batch_id)
        assert batch["batch"] is not None, "Batch not found in Databricks"
        print(f"  ✓ Batch found: {batch['batch']['status']}")

        bronze = databricks_connector.get_bronze_records(batch_id=batch_id, limit=1)
        assert len(bronze) == 1, "Bronze record not found"
        print(f"  ✓ Bronze record: {bronze[0]['raw_id']}")

        silver = databricks_connector.get_silver_records(batch_id=batch_id, limit=1)
        assert len(silver) == 1, "Silver record not found"
        print(f"  ✓ Silver record: {silver[0]['stg_id']}")
        print(f"    Amount: {silver[0]['amount']} {silver[0]['currency']}")
        print(f"    DQ Score: {silver[0]['dq_score']}")

        gold = databricks_connector.get_payment_instructions(batch_id=batch_id, limit=1)
        assert len(gold) == 1, "Gold record not found"
        print(f"  ✓ Gold record: {gold[0]['instruction_id']}")

        print(f"\n✓ Celery task completed successfully!")

    def test_sync_batch_to_neo4j_sync(self, databricks_connector, neo4j_service):
        """Test the Neo4j sync task synchronously."""
        from gps_cdm.orchestration.databricks_pipeline_tasks import (
            process_batch_to_databricks,
            sync_batch_to_neo4j,
        )

        # First create a batch
        msg_id, xml_content = generate_test_xml(amount=3500.00)
        batch_id = f"test_neo4j_sync_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{msg_id}"

        print(f"\n{'='*60}")
        print(f"Testing Celery Task: sync_batch_to_neo4j")
        print(f"{'='*60}")
        print(f"Batch ID: {batch_id}")

        # Process batch first
        process_result = process_batch_to_databricks.apply(
            args=[batch_id, xml_content, "pain.001", "test_neo4j_sync.xml"]
        ).get()
        assert process_result["status"] == "COMPLETED"
        print(f"  ✓ Batch processed to Databricks")

        # Now sync to Neo4j
        sync_result = sync_batch_to_neo4j.apply(args=[batch_id]).get()

        print(f"\nSync Result:")
        print(f"  Status: {sync_result['status']}")

        assert sync_result["status"] in ["SYNCED", "PARTIAL"]

        # Verify in Neo4j
        print("\nVerifying data in Neo4j...")
        lineage = neo4j_service.get_batch_lineage(batch_id)
        assert lineage is not None, "Lineage not found in Neo4j"
        assert lineage.get("batch") is not None, "Batch not in Neo4j"

        print(f"  ✓ Batch found in Neo4j")
        print(f"    Batch ID: {lineage['batch']['batch_id']}")
        print(f"    Status: {lineage['batch'].get('status')}")
        print(f"    Source: {lineage['batch'].get('source_system')}")

        print(f"\n✓ Neo4j sync completed successfully!")


class TestFullOrchestration:
    """
    Test the complete orchestrated flow from ingestion to Neo4j.
    """

    def test_full_pipeline_orchestration(self, databricks_connector, neo4j_service):
        """
        Test the complete orchestrated pipeline:
        1. Submit XML message
        2. Process through medallion layers (Bronze → Silver → Gold)
        3. Sync lineage to Neo4j
        4. Verify all data is correctly stored and linked
        """
        from gps_cdm.orchestration.databricks_pipeline_tasks import (
            process_batch_to_databricks,
            sync_batch_to_neo4j,
        )

        msg_id, xml_content = generate_test_xml(amount=5000.00)
        batch_id = f"test_full_orch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{msg_id}"

        print(f"\n{'='*60}")
        print(f"FULL ORCHESTRATED PIPELINE TEST")
        print(f"{'='*60}")
        print(f"Batch ID: {batch_id}")
        print(f"Message ID: TEST_MSG_{msg_id}")

        # Step 1: Process to Databricks
        print(f"\n[Step 1] Processing to Databricks...")
        start_time = time.time()
        process_result = process_batch_to_databricks.apply(
            args=[batch_id, xml_content, "pain.001", "orchestrated_test.xml"]
        ).get()
        process_duration = time.time() - start_time

        assert process_result["status"] == "COMPLETED"
        print(f"  ✓ Databricks processing complete ({process_duration:.2f}s)")
        print(f"    Bronze: {process_result['bronze_count']}")
        print(f"    Silver: {process_result['silver_count']}")
        print(f"    Gold: {process_result['gold_count']}")

        # Step 2: Sync to Neo4j
        print(f"\n[Step 2] Syncing to Neo4j...")
        start_time = time.time()
        sync_result = sync_batch_to_neo4j.apply(args=[batch_id]).get()
        sync_duration = time.time() - start_time

        assert sync_result["status"] in ["SYNCED", "PARTIAL"]
        print(f"  ✓ Neo4j sync complete ({sync_duration:.2f}s)")

        # Step 3: Verify end-to-end traceability
        print(f"\n[Step 3] Verifying end-to-end traceability...")

        # Verify in Databricks
        bronze = databricks_connector.get_bronze_records(batch_id=batch_id, limit=1)
        silver = databricks_connector.get_silver_records(batch_id=batch_id, limit=1)
        gold = databricks_connector.get_payment_instructions(batch_id=batch_id, limit=1)

        assert len(bronze) == 1, "Missing bronze record"
        assert len(silver) == 1, "Missing silver record"
        assert len(gold) == 1, "Missing gold record"

        # Verify linkage
        raw_id = bronze[0]["raw_id"]
        stg_raw_id = silver[0]["raw_id"]
        gold_stg_id = gold[0]["stg_id"]
        silver_stg_id = silver[0]["stg_id"]

        assert stg_raw_id == raw_id, f"Silver->Bronze link broken: {stg_raw_id} != {raw_id}"
        assert gold_stg_id == silver_stg_id, f"Gold->Silver link broken: {gold_stg_id} != {silver_stg_id}"

        print(f"  ✓ Traceability verified:")
        print(f"    Bronze (raw_id): {raw_id}")
        print(f"    Silver (stg_id): {silver_stg_id} → links to raw_id: {stg_raw_id}")
        print(f"    Gold (instruction_id): {gold[0]['instruction_id']} → links to stg_id: {gold_stg_id}")

        # Verify in Neo4j
        lineage = neo4j_service.get_batch_lineage(batch_id)
        assert lineage.get("batch") is not None

        print(f"  ✓ Neo4j lineage verified")
        print(f"    Batch in knowledge graph: {lineage['batch']['batch_id']}")

        # Step 4: Summary
        print(f"\n{'='*60}")
        print(f"ORCHESTRATION TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✓ Batch ID: {batch_id}")
        print(f"✓ Databricks: 3 records (Bronze, Silver, Gold)")
        print(f"✓ Neo4j: Batch lineage synced")
        print(f"✓ Total Duration: {process_duration + sync_duration:.2f}s")
        print(f"✓ End-to-end traceability: VERIFIED")
        print(f"{'='*60}")

    def test_api_reads_orchestrated_data(self, databricks_connector, neo4j_service):
        """
        Test that API endpoints correctly read data that was
        written by the orchestrated pipeline.
        """
        from fastapi.testclient import TestClient
        from gps_cdm.api import app
        from gps_cdm.orchestration.databricks_pipeline_tasks import (
            process_batch_to_databricks,
            sync_batch_to_neo4j,
        )

        msg_id, xml_content = generate_test_xml(amount=7500.00)
        batch_id = f"test_api_orch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{msg_id}"

        print(f"\n{'='*60}")
        print(f"Testing API with Orchestrated Data")
        print(f"{'='*60}")
        print(f"Batch ID: {batch_id}")

        # Process and sync
        process_result = process_batch_to_databricks.apply(
            args=[batch_id, xml_content, "pain.001", "api_test.xml"]
        ).get()
        sync_result = sync_batch_to_neo4j.apply(args=[batch_id]).get()

        assert process_result["status"] == "COMPLETED"
        print(f"  ✓ Data processed and synced")

        # Test API endpoints
        client = TestClient(app)

        # Test /pipeline/batches
        print(f"\n[API Test 1] GET /pipeline/batches")
        response = client.get("/api/v1/pipeline/batches?limit=5")
        assert response.status_code == 200
        batches = response.json()

        found = any(b["batch_id"] == batch_id for b in batches)
        assert found, f"Batch {batch_id} not found in API response"
        print(f"  ✓ Batch found in /pipeline/batches")

        # Verify data source is Databricks
        batch_data = next(b for b in batches if b["batch_id"] == batch_id)
        assert batch_data.get("data_source") == "databricks"
        print(f"  ✓ Data source confirmed: {batch_data.get('data_source')}")

        # Test /pipeline/batches/{id}
        print(f"\n[API Test 2] GET /pipeline/batches/{batch_id}")
        response = client.get(f"/api/v1/pipeline/batches/{batch_id}")
        assert response.status_code == 200
        batch_detail = response.json()
        assert batch_detail["batch_id"] == batch_id
        assert batch_detail.get("data_source") == "databricks"
        print(f"  ✓ Batch detail retrieved from Databricks")

        # Test /pipeline/batches/{id}/records/bronze
        print(f"\n[API Test 3] GET /pipeline/batches/{batch_id}/records/bronze")
        response = client.get(f"/api/v1/pipeline/batches/{batch_id}/records/bronze")
        assert response.status_code == 200
        bronze_records = response.json()
        assert len(bronze_records) > 0
        assert bronze_records[0].get("data_source") == "databricks"
        print(f"  ✓ Bronze records retrieved: {len(bronze_records)}")

        # Test /graph/batches/{id}/lineage (from Neo4j)
        print(f"\n[API Test 4] GET /graph/batches/{batch_id}/lineage")
        response = client.get(f"/api/v1/graph/batches/{batch_id}/lineage")
        assert response.status_code == 200
        lineage_data = response.json()
        assert lineage_data["batch_id"] == batch_id
        print(f"  ✓ Lineage retrieved from Neo4j")

        print(f"\n{'='*60}")
        print(f"API INTEGRATION TEST COMPLETE")
        print(f"{'='*60}")
        print(f"✓ Pipeline endpoints read from: Databricks")
        print(f"✓ Graph endpoints read from: Neo4j")
        print(f"{'='*60}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

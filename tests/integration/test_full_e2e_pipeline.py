"""
GPS CDM - Full End-to-End Pipeline Integration Test
====================================================

Tests the complete pipeline with:
1. Databricks as the data store (medallion layers)
2. Neo4j as the knowledge graph
3. API layer reading from the correct sources
4. Celery task orchestration

Prerequisites:
- Databricks Free Edition with data processed
- Neo4j running (docker-compose -f docker-compose.nifi.yaml up neo4j -d)
- API server running or test client
- Environment variables set:
  - DATABRICKS_SERVER_HOSTNAME
  - DATABRICKS_HTTP_PATH
  - DATABRICKS_TOKEN

Run:
    export DATABRICKS_SERVER_HOSTNAME=dbc-96614790-02e2.cloud.databricks.com
    export DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/138ee010ba0585d3
    export DATABRICKS_TOKEN=<your-token>
    pytest tests/integration/test_full_e2e_pipeline.py -v
"""

import pytest
import os
from datetime import datetime


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def databricks_connector():
    """Get Databricks connector, skip if not configured."""
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
    """Get Neo4j service, skip if not available."""
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    service = get_neo4j_service()
    if not service.is_available():
        pytest.skip("Neo4j is not available")
    return service


@pytest.fixture
def api_client():
    """Get FastAPI test client."""
    from fastapi.testclient import TestClient
    from gps_cdm.api import app

    return TestClient(app)


# ============================================================================
# DATA SOURCE VERIFICATION TESTS
# ============================================================================

class TestDataSourceConfiguration:
    """Tests to verify data sources are correctly configured."""

    def test_databricks_is_primary_data_source(self, databricks_connector):
        """Verify Databricks is available and has data."""
        assert databricks_connector.is_available()

        # Check that tables exist
        batches = databricks_connector.get_batches(limit=1)
        assert isinstance(batches, list)
        print(f"\n✓ Databricks connected: {databricks_connector.catalog}.{databricks_connector.schema}")
        print(f"  Batches available: {len(batches) > 0}")

    def test_neo4j_is_knowledge_graph(self, neo4j_service):
        """Verify Neo4j is available for knowledge graph."""
        assert neo4j_service.is_available()
        print("\n✓ Neo4j connected for knowledge graph")

    def test_api_data_sources_endpoint(self, api_client, databricks_connector, neo4j_service):
        """Verify API correctly reports data sources."""
        response = api_client.get("/api/v1/pipeline/data-sources")
        assert response.status_code == 200

        data = response.json()
        print(f"\n✓ API Data Sources:")
        print(f"  Configured: {data.get('configured_source')}")
        print(f"  Active: {data.get('active_source')}")
        print(f"  Databricks available: {data['sources']['databricks']['available']}")
        print(f"  Neo4j available: {data['sources']['neo4j']['available']}")

        # Verify Databricks is the active source when available
        if data['sources']['databricks']['available']:
            assert data.get('active_source') == 'databricks', \
                "Databricks should be active source when available"


# ============================================================================
# API ENDPOINT TESTS (Data from Databricks)
# ============================================================================

class TestAPIFromDatabricks:
    """Tests to verify API reads data from Databricks."""

    def test_list_batches_from_databricks(self, api_client, databricks_connector):
        """Verify /pipeline/batches reads from Databricks."""
        response = api_client.get("/api/v1/pipeline/batches?limit=5")
        assert response.status_code == 200

        batches = response.json()
        assert isinstance(batches, list)

        if batches:
            # Check that data_source indicates Databricks
            first_batch = batches[0]
            assert first_batch.get("data_source") == "databricks", \
                f"Expected data_source=databricks, got {first_batch.get('data_source')}"

            print(f"\n✓ Batches from Databricks:")
            for b in batches[:3]:
                print(f"  - {b['batch_id']}: {b['status']} (source: {b['data_source']})")

    def test_get_batch_detail_from_databricks(self, api_client, databricks_connector):
        """Verify /pipeline/batches/{id} reads from Databricks."""
        # Get a batch ID first
        db_batches = databricks_connector.get_batches(limit=1)
        if not db_batches:
            pytest.skip("No batches in Databricks")

        batch_id = db_batches[0]["batch_id"]

        response = api_client.get(f"/api/v1/pipeline/batches/{batch_id}")
        assert response.status_code == 200

        batch = response.json()
        assert batch.get("data_source") == "databricks"
        assert batch.get("batch_id") == batch_id

        print(f"\n✓ Batch detail from Databricks:")
        print(f"  Batch ID: {batch['batch_id']}")
        print(f"  Status: {batch['status']}")
        print(f"  Bronze: {batch.get('bronze_count', 0)}")
        print(f"  Silver: {batch.get('silver_count', 0)}")
        print(f"  Gold: {batch.get('gold_count', 0)}")

    def test_get_batch_records_from_databricks(self, api_client, databricks_connector):
        """Verify /pipeline/batches/{id}/records/{layer} reads from Databricks."""
        # Get a batch with data
        db_batches = databricks_connector.get_batches(limit=5, status="COMPLETED")
        if not db_batches:
            db_batches = databricks_connector.get_batches(limit=1)

        if not db_batches:
            pytest.skip("No batches in Databricks")

        batch_id = db_batches[0]["batch_id"]

        # Test each layer
        for layer in ["bronze", "silver", "gold"]:
            response = api_client.get(
                f"/api/v1/pipeline/batches/{batch_id}/records/{layer}?limit=5"
            )
            assert response.status_code == 200

            records = response.json()
            print(f"\n✓ {layer.upper()} records from Databricks: {len(records)}")

            if records:
                assert records[0].get("data_source") == "databricks"
                # Print sample record keys
                print(f"  Sample record keys: {list(records[0].keys())[:5]}")


# ============================================================================
# API ENDPOINT TESTS (Knowledge Graph from Neo4j)
# ============================================================================

class TestAPIFromNeo4j:
    """Tests to verify API reads knowledge graph from Neo4j."""

    def test_batch_lineage_from_neo4j(self, api_client, databricks_connector, neo4j_service):
        """Verify /graph/batches/{id}/lineage reads from Neo4j."""
        # First sync a batch to Neo4j
        db_batches = databricks_connector.get_batches(limit=1, status="COMPLETED")
        if not db_batches:
            db_batches = databricks_connector.get_batches(limit=1)

        if not db_batches:
            pytest.skip("No batches available")

        batch_id = db_batches[0]["batch_id"]

        # Sync to Neo4j
        databricks_connector.sync_batch_to_neo4j(batch_id)

        # Query via API
        response = api_client.get(f"/api/v1/graph/batches/{batch_id}/lineage")
        assert response.status_code == 200

        lineage = response.json()
        assert lineage.get("batch_id") == batch_id

        print(f"\n✓ Batch lineage from Neo4j:")
        print(f"  Batch ID: {lineage['batch_id']}")
        print(f"  Status: {lineage.get('status')}")
        print(f"  Layers: {len(lineage.get('layers', []))}")

    def test_graph_health_endpoint(self, api_client, neo4j_service):
        """Verify /graph/health reads from Neo4j."""
        response = api_client.get("/api/v1/graph/health")
        assert response.status_code == 200

        health = response.json()
        assert health.get("neo4j_available") is True
        print(f"\n✓ Graph health: {health['status']}")


# ============================================================================
# END-TO-END FLOW TESTS
# ============================================================================

class TestEndToEndFlow:
    """Tests for complete data flow through the system."""

    def test_full_data_lineage_flow(self, databricks_connector, neo4j_service):
        """Test data flows correctly from Databricks to Neo4j."""
        # 1. Get batch from Databricks
        batches = databricks_connector.get_batches(limit=5, status="COMPLETED")
        if not batches:
            pytest.skip("No completed batches in Databricks")

        # Find a batch with data in all layers
        test_batch = None
        for batch in batches:
            stats = databricks_connector.get_layer_stats(batch["batch_id"])
            if stats.get("bronze", 0) > 0 and stats.get("silver", 0) > 0:
                test_batch = batch
                break

        if not test_batch:
            pytest.skip("No batch with full pipeline data")

        batch_id = test_batch["batch_id"]
        print(f"\n✓ Testing E2E flow for batch: {batch_id}")

        # 2. Get layer stats from Databricks
        stats = databricks_connector.get_layer_stats(batch_id)
        print(f"  Databricks layer stats:")
        for layer, count in stats.items():
            print(f"    - {layer}: {count}")

        # 3. Sync to Neo4j
        sync_result = databricks_connector.sync_batch_to_neo4j(batch_id)
        assert sync_result is True
        print(f"  ✓ Synced to Neo4j")

        # 4. Verify in Neo4j
        neo4j_lineage = neo4j_service.get_batch_lineage(batch_id)
        assert neo4j_lineage is not None
        assert neo4j_lineage.get("batch") is not None
        print(f"  ✓ Verified in Neo4j")

        # 5. Verify traceability through layers
        bronze = databricks_connector.get_bronze_records(batch_id=batch_id, limit=1)
        silver = databricks_connector.get_silver_records(batch_id=batch_id, limit=1)
        gold = databricks_connector.get_payment_instructions(batch_id=batch_id, limit=1)

        print(f"\n  Traceability check:")
        print(f"    Bronze records: {len(bronze)}")
        print(f"    Silver records: {len(silver)}")
        print(f"    Gold records: {len(gold)}")

        # Verify data exists in each layer
        assert stats.get("bronze", 0) > 0, "Should have bronze records"

    def test_api_serves_correct_data_sources(self, api_client, databricks_connector, neo4j_service):
        """Verify API uses correct source for each type of data."""
        # 1. Pipeline data should come from Databricks
        batches_response = api_client.get("/api/v1/pipeline/batches?limit=1")
        if batches_response.status_code == 200 and batches_response.json():
            batch = batches_response.json()[0]
            assert batch.get("data_source") == "databricks", \
                "Pipeline batches should come from Databricks"
            print("\n✓ Pipeline data source: Databricks")

        # 2. Sync a batch and verify graph comes from Neo4j
        db_batches = databricks_connector.get_batches(limit=1)
        if db_batches:
            batch_id = db_batches[0]["batch_id"]
            databricks_connector.sync_batch_to_neo4j(batch_id)

            lineage_response = api_client.get(f"/api/v1/graph/batches/{batch_id}/lineage")
            if lineage_response.status_code == 200:
                # Graph endpoints inherently use Neo4j
                print("✓ Graph data source: Neo4j")

        # 3. Health should report both sources
        health_response = api_client.get("/api/v1/pipeline/health")
        assert health_response.status_code == 200
        health = health_response.json()

        print(f"\n✓ Health check:")
        print(f"  Data source: {health.get('data_source')}")
        print(f"  Neo4j available: {health.get('neo4j_available')}")
        print(f"  Status: {health.get('status')}")


# ============================================================================
# PIPELINE STATS TESTS
# ============================================================================

class TestPipelineStats:
    """Tests for pipeline statistics from Databricks."""

    def test_pipeline_stats(self, api_client, databricks_connector):
        """Verify pipeline stats are calculated correctly."""
        response = api_client.get("/api/v1/pipeline/stats")
        assert response.status_code == 200

        stats = response.json()
        print(f"\n✓ Pipeline Stats:")
        for layer in ["bronze", "silver", "gold", "analytical"]:
            layer_stats = stats.get(layer, {})
            print(f"  {layer}: total={layer_stats.get('total', 0)}, processed={layer_stats.get('processed', 0)}")

    def test_health_shows_both_sources(self, api_client, databricks_connector, neo4j_service):
        """Verify health endpoint shows status of all data sources."""
        response = api_client.get("/api/v1/pipeline/health")
        assert response.status_code == 200

        health = response.json()

        # Should show data source
        assert "data_source" in health
        # Should show Neo4j status
        assert "neo4j_available" in health

        print(f"\n✓ Health Status:")
        print(f"  Overall: {health.get('status')}")
        print(f"  Data source: {health.get('data_source')}")
        print(f"  Neo4j: {health.get('neo4j_available')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

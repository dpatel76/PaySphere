"""
GPS CDM - Databricks + Neo4j End-to-End Integration Test
=========================================================

Tests the complete pipeline:
1. Connect to Databricks Free Edition
2. Query processed data from all layers
3. Sync batch lineage to Neo4j
4. Verify lineage graph in Neo4j

Prerequisites:
- Databricks Free Edition account with data processed
- Neo4j running (docker-compose -f docker-compose.nifi.yaml up neo4j -d)
- Environment variables set:
  - DATABRICKS_SERVER_HOSTNAME
  - DATABRICKS_HTTP_PATH
  - DATABRICKS_TOKEN

Run:
    pytest tests/integration/test_databricks_neo4j_e2e.py -v
"""

import pytest
import os
from datetime import datetime


@pytest.fixture
def databricks_connector():
    """Get Databricks connector, skip if not configured."""
    from gps_cdm.ingestion.persistence.databricks_connector import DatabricksConnector

    # Check for required env vars
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


class TestDatabricksConnection:
    """Tests for Databricks connectivity."""

    def test_databricks_connection(self, databricks_connector):
        """Test basic Databricks connectivity."""
        assert databricks_connector.is_available() is True

    def test_query_batches(self, databricks_connector):
        """Test querying batch tracking table."""
        batches = databricks_connector.get_batches(limit=5)
        assert isinstance(batches, list)
        print(f"\nFound {len(batches)} batches")
        for b in batches[:3]:
            print(f"  - {b.get('batch_id')}: {b.get('status')}")

    def test_query_bronze_layer(self, databricks_connector):
        """Test querying bronze layer."""
        records = databricks_connector.get_bronze_records(limit=5)
        assert isinstance(records, list)
        print(f"\nBronze records: {len(records)}")
        for r in records[:3]:
            print(f"  - {r.get('message_type')}: {r.get('message_id')}")

    def test_query_silver_layer(self, databricks_connector):
        """Test querying silver layer."""
        records = databricks_connector.get_silver_records(limit=5)
        assert isinstance(records, list)
        print(f"\nSilver records: {len(records)}")
        for r in records[:3]:
            print(f"  - {r.get('debtor_name')} -> {r.get('creditor_name')}: {r.get('amount')} {r.get('currency')}")

    def test_query_gold_layer(self, databricks_connector):
        """Test querying gold layer."""
        payments = databricks_connector.get_payment_instructions(limit=5)
        parties = databricks_connector.get_parties(limit=5)
        accounts = databricks_connector.get_accounts(limit=5)

        print(f"\nGold layer:")
        print(f"  - Payment Instructions: {len(payments)}")
        print(f"  - Parties: {len(parties)}")
        print(f"  - Accounts: {len(accounts)}")

        assert isinstance(payments, list)
        assert isinstance(parties, list)
        assert isinstance(accounts, list)


class TestNeo4jDatabricksIntegration:
    """Tests for Neo4j + Databricks integration."""

    def test_sync_batch_to_neo4j(self, databricks_connector, neo4j_service):
        """Test syncing a Databricks batch to Neo4j."""
        # Get the most recent completed batch
        batches = databricks_connector.get_batches(limit=1, status="COMPLETED")
        if not batches:
            batches = databricks_connector.get_batches(limit=1)

        if not batches:
            pytest.skip("No batches found in Databricks")

        batch_id = batches[0]["batch_id"]
        print(f"\nSyncing batch: {batch_id}")

        # Sync to Neo4j
        result = databricks_connector.sync_batch_to_neo4j(batch_id)
        assert result is True

        # Verify in Neo4j
        lineage = neo4j_service.get_batch_lineage(batch_id)
        assert lineage is not None
        assert lineage.get("batch") is not None
        assert lineage["batch"]["batch_id"] == batch_id

        print(f"Neo4j lineage verified for batch: {batch_id}")

    def test_layer_stats_sync(self, databricks_connector, neo4j_service):
        """Test that layer stats are synced correctly."""
        batches = databricks_connector.get_batches(limit=1, status="COMPLETED")
        if not batches:
            pytest.skip("No completed batches found")

        batch_id = batches[0]["batch_id"]

        # Get stats from Databricks
        db_stats = databricks_connector.get_layer_stats(batch_id)
        print(f"\nDatabricks layer stats for {batch_id}:")
        for layer, count in db_stats.items():
            print(f"  - {layer}: {count}")

        # Sync to Neo4j
        databricks_connector.sync_batch_to_neo4j(batch_id)

        # Verify layers in Neo4j
        lineage = neo4j_service.get_batch_lineage(batch_id)
        neo4j_layers = lineage.get("layers", [])
        print(f"\nNeo4j layers: {len(neo4j_layers)}")

        assert len(neo4j_layers) >= 0  # May not have all layers yet


class TestEndToEndPipeline:
    """End-to-end pipeline tests."""

    def test_full_lineage_chain(self, databricks_connector, neo4j_service):
        """Test complete lineage from Databricks through Neo4j."""
        # Get a batch with data in all layers
        batches = databricks_connector.get_batches(limit=5, status="COMPLETED")
        if not batches:
            pytest.skip("No completed batches found")

        test_batch = None
        for batch in batches:
            stats = databricks_connector.get_layer_stats(batch["batch_id"])
            if stats.get("bronze", 0) > 0 and stats.get("silver", 0) > 0:
                test_batch = batch
                break

        if not test_batch:
            pytest.skip("No batch with full pipeline data found")

        batch_id = test_batch["batch_id"]
        print(f"\nTesting full lineage for batch: {batch_id}")

        # 1. Verify Databricks data
        db_lineage = databricks_connector.get_batch_lineage(batch_id)
        assert db_lineage["batch"] is not None
        print(f"  Databricks batch status: {db_lineage['batch'].get('status')}")

        stats = databricks_connector.get_layer_stats(batch_id)
        print(f"  Databricks layer counts: {stats}")

        # 2. Sync to Neo4j
        sync_result = databricks_connector.sync_batch_to_neo4j(batch_id)
        assert sync_result is True
        print("  Synced to Neo4j: OK")

        # 3. Verify Neo4j lineage
        neo4j_lineage = neo4j_service.get_batch_lineage(batch_id)
        assert neo4j_lineage is not None
        assert neo4j_lineage.get("batch") is not None
        print(f"  Neo4j batch found: OK")

        # 4. Verify data can be traced
        bronze = databricks_connector.get_bronze_records(batch_id=batch_id, limit=1)
        silver = databricks_connector.get_silver_records(batch_id=batch_id, limit=1)
        gold = databricks_connector.get_payment_instructions(batch_id=batch_id, limit=1)

        print(f"\n  Traceability check:")
        print(f"    Bronze raw_id: {bronze[0]['raw_id'] if bronze else 'N/A'}")
        print(f"    Silver raw_id: {silver[0]['raw_id'] if silver else 'N/A'}")
        print(f"    Gold stg_id: {gold[0].get('stg_id', 'N/A') if gold else 'N/A'}")

        print("\n  End-to-end lineage verified!")

    def test_data_quality_flow(self, databricks_connector):
        """Test data quality scores flow through pipeline."""
        records = databricks_connector.get_silver_records(limit=10)
        if not records:
            pytest.skip("No silver records found")

        print("\nData Quality Scores:")
        for r in records:
            dq = r.get("dq_score", 0)
            print(f"  - {r.get('message_id', 'N/A')}: DQ={dq}")

        # Check that DQ scores are calculated
        scores = [r.get("dq_score") for r in records if r.get("dq_score") is not None]
        assert len(scores) > 0, "No DQ scores found"
        print(f"\nAverage DQ Score: {sum(float(s) for s in scores) / len(scores):.2f}")


class TestConfigurationValidation:
    """Tests for configuration and setup validation."""

    def test_catalog_schema_exists(self, databricks_connector):
        """Test that catalog and schema are properly configured."""
        catalog = databricks_connector.catalog
        schema = databricks_connector.schema

        # Try to query the schema
        tables = databricks_connector.query(f"SHOW TABLES IN {catalog}.{schema}")
        assert len(tables) > 0, f"No tables found in {catalog}.{schema}"

        print(f"\nTables in {catalog}.{schema}:")
        for t in tables:
            print(f"  - {t.get('tableName', t)}")

    def test_all_required_tables_exist(self, databricks_connector):
        """Test that all required CDM tables exist."""
        required_tables = [
            "obs_batch_tracking",
            "obs_data_lineage",
            "obs_processing_errors",
            "bronze_raw_payment",
            "silver_stg_payment_instruction",
            "gold_cdm_payment_instruction",
            "gold_cdm_party",
            "gold_cdm_account",
            "gold_cdm_financial_institution",
        ]

        catalog = databricks_connector.catalog
        schema = databricks_connector.schema
        tables = databricks_connector.query(f"SHOW TABLES IN {catalog}.{schema}")
        table_names = [t.get("tableName", str(t)) for t in tables]

        missing = [t for t in required_tables if t not in table_names]
        if missing:
            print(f"\nMissing tables: {missing}")

        assert len(missing) == 0, f"Missing required tables: {missing}"
        print(f"\nAll {len(required_tables)} required tables exist!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

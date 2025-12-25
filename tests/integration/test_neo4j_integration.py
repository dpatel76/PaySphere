"""
GPS CDM - Neo4j Integration Tests
=================================

Tests for Neo4j integration with the data processing pipeline.
Requires Neo4j to be running (docker-compose -f docker-compose.nifi.yaml up neo4j -d)
"""

import pytest
import uuid
from datetime import datetime


@pytest.fixture
def neo4j_service():
    """Get Neo4j service, skip if not available."""
    from gps_cdm.orchestration.neo4j_service import get_neo4j_service

    service = get_neo4j_service()
    if not service.is_available():
        pytest.skip("Neo4j is not available")
    return service


class TestNeo4jService:
    """Tests for Neo4j service operations."""

    def test_neo4j_connectivity(self, neo4j_service):
        """Test Neo4j is connected and available."""
        assert neo4j_service.is_available() is True

    def test_upsert_batch(self, neo4j_service):
        """Test creating/updating a batch in Neo4j."""
        batch_id = f"test_batch_{uuid.uuid4().hex[:8]}"

        result = neo4j_service.upsert_batch({
            "batch_id": batch_id,
            "message_type": "pain.001",
            "source_system": "TEST",
            "status": "PROCESSING",
            "created_at": datetime.utcnow().isoformat(),
            "total_records": 100,
        })

        assert result is True

        # Verify batch exists
        lineage = neo4j_service.get_batch_lineage(batch_id)
        assert lineage is not None
        assert lineage["batch"]["batch_id"] == batch_id
        assert lineage["batch"]["message_type"] == "pain.001"

    def test_upsert_batch_layer(self, neo4j_service):
        """Test creating batch layer stats."""
        batch_id = f"test_batch_{uuid.uuid4().hex[:8]}"

        # First create the batch
        neo4j_service.upsert_batch({
            "batch_id": batch_id,
            "message_type": "pain.001",
            "source_system": "TEST",
            "status": "PROCESSING",
            "created_at": datetime.utcnow().isoformat(),
        })

        # Add bronze layer
        result = neo4j_service.upsert_batch_layer(
            batch_id=batch_id,
            layer="bronze",
            stats={
                "input_count": 100,
                "processed_count": 95,
                "failed_count": 5,
                "pending_count": 0,
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "duration_ms": 1500,
            }
        )

        assert result is True

        # Verify layer exists
        lineage = neo4j_service.get_batch_lineage(batch_id)
        assert len(lineage["layers"]) == 1
        assert lineage["layers"][0]["layer"] == "bronze"
        assert lineage["layers"][0]["processed_count"] == 95

    def test_create_layer_promotion(self, neo4j_service):
        """Test creating promotion relationships between layers."""
        batch_id = f"test_batch_{uuid.uuid4().hex[:8]}"

        # Create batch and two layers
        neo4j_service.upsert_batch({
            "batch_id": batch_id,
            "message_type": "pain.001",
            "source_system": "TEST",
            "status": "PROCESSING",
            "created_at": datetime.utcnow().isoformat(),
        })

        neo4j_service.upsert_batch_layer(
            batch_id=batch_id,
            layer="bronze",
            stats={"input_count": 100, "processed_count": 95, "failed_count": 5}
        )

        neo4j_service.upsert_batch_layer(
            batch_id=batch_id,
            layer="silver",
            stats={"input_count": 95, "processed_count": 90, "failed_count": 5}
        )

        # Create promotion
        result = neo4j_service.create_layer_promotion(
            batch_id=batch_id,
            source_layer="bronze",
            target_layer="silver",
            record_count=95,
            success_rate=0.95,
        )

        assert result is True

    def test_upsert_dq_metrics(self, neo4j_service):
        """Test creating DQ metrics."""
        batch_id = f"test_batch_{uuid.uuid4().hex[:8]}"

        # Create batch first
        neo4j_service.upsert_batch({
            "batch_id": batch_id,
            "message_type": "pain.001",
            "source_system": "TEST",
            "status": "PROCESSING",
            "created_at": datetime.utcnow().isoformat(),
        })

        # Add DQ metrics
        result = neo4j_service.upsert_dq_metrics(
            batch_id=batch_id,
            layer="silver",
            metrics={
                "entity_type": "stg_pain001",
                "overall_avg_score": 0.92,
                "completeness_avg": 0.95,
                "accuracy_avg": 0.90,
                "validity_avg": 0.91,
                "records_above_threshold": 85,
                "records_below_threshold": 15,
                "top_failing_rules": ["REQUIRED_FIELD", "FORMAT_CHECK"],
            }
        )

        assert result is True

        # Verify DQ metrics exist
        lineage = neo4j_service.get_batch_lineage(batch_id)
        assert len(lineage["dq_metrics"]) == 1

    def test_schema_lineage_query(self, neo4j_service):
        """Test querying schema lineage for a message type."""
        lineage = neo4j_service.get_schema_lineage("pain.001")

        assert lineage is not None
        assert lineage["message_type"]["type"] == "pain.001"
        # Should have entities (bronze, silver, gold)
        assert len(lineage["entities"]) >= 1

    def test_field_lineage_query(self, neo4j_service):
        """Test querying field lineage."""
        # Query for debtor_name field
        graph = neo4j_service.get_field_lineage_graph("pain.001", "debtor_name")

        # May be None if field not set up, but should not error
        if graph:
            assert "nodes" in graph
            assert "edges" in graph


class TestCeleryNeo4jIntegration:
    """Tests for Celery task Neo4j integration."""

    def test_aggregate_bronze_results_syncs_to_neo4j(self, neo4j_service):
        """Test that aggregate_bronze_results syncs to Neo4j."""
        from gps_cdm.orchestration.celery_tasks import aggregate_bronze_results

        batch_id = f"test_batch_{uuid.uuid4().hex[:8]}"

        # First create the batch in Neo4j
        neo4j_service.upsert_batch({
            "batch_id": batch_id,
            "message_type": "pain.001",
            "source_system": "TEST",
            "status": "PROCESSING",
            "created_at": datetime.utcnow().isoformat(),
        })

        # Simulate bronze results
        results = [
            {"status": "SUCCESS", "records_processed": 50, "errors": [], "duration_seconds": 1.5},
            {"status": "SUCCESS", "records_processed": 45, "errors": [{"file": "bad.xml", "error": "parse error"}], "duration_seconds": 1.2},
        ]

        # Call aggregate (note: this is the actual task, not async)
        result = aggregate_bronze_results.apply(args=(results, batch_id)).get()

        assert result["status"] == "PARTIAL"  # Has errors
        assert result["total_records"] == 95

        # Verify Neo4j was updated
        lineage = neo4j_service.get_batch_lineage(batch_id)
        assert len(lineage["layers"]) == 1
        bronze_layer = lineage["layers"][0]
        assert bronze_layer["layer"] == "bronze"
        assert bronze_layer["processed_count"] == 95

    def test_full_pipeline_neo4j_sync(self, neo4j_service):
        """Test full pipeline creates complete lineage in Neo4j."""
        from gps_cdm.orchestration.celery_tasks import (
            aggregate_bronze_results,
            aggregate_silver_results,
            aggregate_gold_results,
        )

        batch_id = f"test_batch_{uuid.uuid4().hex[:8]}"

        # Create batch
        neo4j_service.upsert_batch({
            "batch_id": batch_id,
            "message_type": "pain.001",
            "source_system": "TEST",
            "status": "PROCESSING",
            "created_at": datetime.utcnow().isoformat(),
        })

        # Bronze aggregate
        bronze_results = [
            {"status": "SUCCESS", "records_processed": 100, "errors": [], "duration_seconds": 2.0},
        ]
        aggregate_bronze_results.apply(args=(bronze_results, batch_id)).get()

        # Silver aggregate
        silver_results = [
            {"status": "SUCCESS", "records_processed": 98, "errors": [], "duration_seconds": 3.0},
        ]
        aggregate_silver_results.apply(args=(silver_results, batch_id)).get()

        # Gold aggregate
        gold_results = [
            {
                "status": "SUCCESS",
                "records_processed": 95,
                "errors": [],
                "entities_created": {"parties": 50, "accounts": 40, "financial_institutions": 10},
                "duration_seconds": 5.0,
            },
        ]
        aggregate_gold_results.apply(args=(gold_results, batch_id, "pain.001")).get()

        # Verify complete lineage
        lineage = neo4j_service.get_batch_lineage(batch_id)

        assert lineage is not None
        assert lineage["batch"]["status"] == "COMPLETED"
        assert len(lineage["layers"]) == 3

        layers_by_name = {l["layer"]: l for l in lineage["layers"]}
        assert "bronze" in layers_by_name
        assert "silver" in layers_by_name
        assert "gold" in layers_by_name

        assert layers_by_name["bronze"]["processed_count"] == 100
        assert layers_by_name["silver"]["processed_count"] == 98
        assert layers_by_name["gold"]["processed_count"] == 95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

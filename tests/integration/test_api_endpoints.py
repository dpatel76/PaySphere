"""
GPS CDM - API Endpoint Integration Tests
=========================================

Tests for the new dashboard and lineage API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Import the FastAPI app
from gps_cdm.api import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "GPS CDM API"
        assert "endpoints" in data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# ============================================================================
# Schema API Tests
# ============================================================================

class TestSchemaEndpoints:
    """Tests for schema API endpoints."""

    def test_get_message_types(self, client):
        """Test getting list of supported message types."""
        response = client.get("/api/v1/schema/message-types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_message_type_schema(self, client):
        """Test getting schema for a specific message type."""
        response = client.get("/api/v1/schema/message-types/pain.001")
        # May return 404 if YAML mapping file doesn't exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "message_type" in data

    def test_get_table_display_config(self, client):
        """Test getting table display configuration."""
        response = client.get("/api/v1/schema/tables/bronze/raw_payment")
        # May return 404 if table config doesn't exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "layer" in data
            assert "table_name" in data


# ============================================================================
# Graph API Tests
# ============================================================================

class TestGraphEndpoints:
    """Tests for Neo4j graph API endpoints."""

    def test_graph_health(self, client):
        """Test graph health check endpoint."""
        response = client.get("/api/v1/graph/health")
        assert response.status_code == 200
        data = response.json()
        assert "neo4j_available" in data
        assert "status" in data

    def test_get_schema_lineage(self, client):
        """Test getting schema lineage for message type."""
        response = client.get("/api/v1/graph/schema/pain.001")
        # May return 503 if Neo4j is not running, which is acceptable
        assert response.status_code in [200, 404, 503]

    def test_get_bottlenecks(self, client):
        """Test getting processing bottlenecks."""
        response = client.get("/api/v1/graph/bottlenecks?hours_back=24")
        # May return 503 if Neo4j is not running
        assert response.status_code in [200, 503]

    def test_get_dq_trends(self, client):
        """Test getting DQ trends."""
        response = client.get("/api/v1/graph/dq-trends?message_type=pain.001&days_back=7")
        # May return 503 if Neo4j is not running
        assert response.status_code in [200, 503]


# ============================================================================
# Pipeline API Tests
# ============================================================================

class TestPipelineEndpoints:
    """Tests for pipeline API endpoints."""

    def test_get_batches(self, client):
        """Test getting list of batches."""
        response = client.get("/api/v1/pipeline/batches")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_batches_with_filters(self, client):
        """Test getting batches with filters."""
        response = client.get("/api/v1/pipeline/batches?status=COMPLETED&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_pipeline_stats(self, client):
        """Test getting pipeline statistics."""
        response = client.get("/api/v1/pipeline/stats")
        assert response.status_code == 200


# ============================================================================
# Lineage API Tests
# ============================================================================

class TestLineageEndpoints:
    """Tests for lineage API endpoints."""

    def test_get_supported_message_types(self, client):
        """Test getting supported message types."""
        response = client.get("/api/v1/lineage/supported-message-types")
        assert response.status_code == 200
        data = response.json()
        assert "supported_types" in data
        assert "count" in data

    def test_get_message_type_lineage(self, client):
        """Test getting message type lineage."""
        response = client.get("/api/v1/lineage/message-type/pain.001")
        assert response.status_code == 200

    def test_get_cdm_entities(self, client):
        """Test getting CDM entities."""
        response = client.get("/api/v1/lineage/cdm-entities")
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data

    def test_get_supported_reports(self, client):
        """Test getting supported reports."""
        response = client.get("/api/v1/lineage/supported-reports")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data


# ============================================================================
# Exception API Tests
# ============================================================================

class TestExceptionEndpoints:
    """Tests for exception API endpoints."""

    def test_get_exception_summary(self, client):
        """Test getting exception summary."""
        response = client.get("/api/v1/exceptions/summary?hours_back=24")
        assert response.status_code == 200

    def test_get_exceptions_list(self, client):
        """Test getting list of exceptions."""
        response = client.get("/api/v1/exceptions?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ============================================================================
# Data Quality API Tests
# ============================================================================

class TestDataQualityEndpoints:
    """Tests for data quality API endpoints."""

    def test_get_dq_summary(self, client):
        """Test getting DQ summary."""
        response = client.get("/api/v1/dq/summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_dq_rules(self, client):
        """Test getting DQ rules."""
        response = client.get("/api/v1/dq/rules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ============================================================================
# Reconciliation API Tests
# ============================================================================

class TestReconciliationEndpoints:
    """Tests for reconciliation API endpoints."""

    def test_get_recon_summary(self, client):
        """Test getting reconciliation summary."""
        response = client.get("/api/v1/recon/summary?hours_back=24")
        assert response.status_code == 200

    def test_get_recon_history(self, client):
        """Test getting reconciliation history."""
        response = client.get("/api/v1/recon/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Test suite for JCode API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from api import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_health_check(client):
    """Test GET /health returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() is not None


def test_openapi_docs(client):
    """Test GET /docs returns 200."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_config_endpoint(client):
    """Test GET /api/v1/config returns 200."""
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    assert response.json() is not None


def test_analyze_endpoint(client):
    """Test POST /api/v1/jcode/analyze exists."""
    # Check endpoint exists (should return 422 or other expected code, not 404)
    response = client.post("/api/v1/jcode/analyze", json={})
    assert response.status_code != 404


def test_enable_endpoint(client):
    """Test POST /api/v1/config/enable exists."""
    # Check endpoint exists (should return 422 or other expected code, not 404)
    response = client.post("/api/v1/config/enable", json={})
    assert response.status_code != 404


def run_all_tests():
    """Run all tests programmatically."""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_all_tests()

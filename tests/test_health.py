"""Test the health check endpoint."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

# Mock the database connection for all tests
@pytest.fixture(autouse=True)
def mock_db():
    with patch('app.db.SessionLocal') as mock_db:
        mock_db.return_value.execute.return_value = MagicMock(scalar=MagicMock(return_value=1))
        yield mock_db

def test_health_check(mock_db):
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "db" in data
    assert "version" in data

def test_liveness_probe():
    """Test the liveness probe endpoint."""
    client = TestClient(app)
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_probe(mock_db):
    """Test the readiness probe endpoint."""
    client = TestClient(app)
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

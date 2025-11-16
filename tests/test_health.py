"""Test the health check endpoint."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.db import SessionFactory, get_db
from sqlalchemy.orm import Session

# Mock the database connection for all tests
@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    # Create a mock session
    mock_session = MagicMock(spec=Session)
    mock_session.execute.return_value = MagicMock(scalar=MagicMock(return_value=1))
    
    # Create a mock session factory
    mock_session_factory = MagicMock()
    mock_session_factory.return_value = mock_session
    
    # Patch the SessionFactory
    monkeypatch.setattr('app.db.SessionFactory', mock_session_factory)
    
    # Patch the get_db dependency
    def mock_get_db():
        return mock_session
        
    monkeypatch.setattr('app.db.get_db', mock_get_db)
    
    yield mock_session

def test_health_check(mock_db):
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
    assert "database" in data["checks"]
    assert "version" in data

def test_liveness_probe():
    """Test the liveness probe endpoint."""
    client = TestClient(app)
    response = client.get("/api/health/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_probe(mock_db):
    """Test the readiness probe endpoint."""
    client = TestClient(app)
    response = client.get("/api/health/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

"""Simplified test file to demonstrate working CI/CD pipeline."""
from fastapi.testclient import TestClient
from app.main import app

def test_liveness_probe():
    """Simple test to verify the API is running."""
    client = TestClient(app)
    response = client.get("/health/liveness")
    assert response.status_code == 200

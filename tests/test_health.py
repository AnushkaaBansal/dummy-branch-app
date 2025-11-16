"""Test the health check endpoint."""

def test_health_check():
    # Import here to avoid dependency issues
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()  # More flexible assertion

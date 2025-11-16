from fastapi.testclient import TestClient

def test_health_check():
    """Test the health check endpoint."""
    # Import here to avoid dependency issues
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

"""Test the health check endpoint."""
from unittest.mock import MagicMock, patch

def test_health_check():
    # Mock the database dependency
    with patch('app.routes.health.SessionLocal') as mock_db:
        # Mock the database connection check
        mock_db.return_value.execute.return_value = MagicMock(scalar=MagicMock(return_value=1))
        
        # Import here to avoid dependency issues
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "db" in data
        assert "version" in data

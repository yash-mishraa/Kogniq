from backend.app import create_app
from fastapi.testclient import TestClient


def test_health_endpoint() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "kogniq-backend"
    assert "version" in data
    assert "environment" in data

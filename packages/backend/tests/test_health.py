from backend.app import create_app
from backend.dependencies import get_authorization_service
from fastapi.testclient import TestClient


class MockAuthResult:
    def __init__(self, allowed: bool, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class MockAuthorizationService:
    async def require_permission(self, _user_id: str, _permission_id: str) -> MockAuthResult:
        return MockAuthResult(allowed=True, reason="")


def test_health_endpoint() -> None:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "kogniq-backend"
    assert "version" in data
    assert "environment" in data

from backend.app import create_app
from backend.core.exceptions import BackendError
from backend.dependencies import get_authorization_service
from fastapi.testclient import TestClient


class MockAuthResult:
    def __init__(self, allowed: bool, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class MockAuthorizationService:
    async def require_permission(self, _user_id: str, _permission_id: str) -> MockAuthResult:
        return MockAuthResult(allowed=True, reason="")


def test_create_app() -> None:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    assert app.title == "Kogniq API"
    assert app.version == "0.1.0"


def test_root_endpoint() -> None:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"name": "Kogniq API", "status": "running"}


def test_openapi_loads() -> None:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_swagger_ui_loads() -> None:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200


def test_global_exception_handler() -> None:
    app = create_app()
    app.dependency_overrides[get_authorization_service] = lambda: MockAuthorizationService()

    @app.get("/test-error")
    async def trigger_error() -> None:
        raise BackendError(code="test_error", message="Test message", status_code=400)

    client = TestClient(app)
    response = client.get("/test-error")

    assert response.status_code == 400
    assert response.json() == {"error": {"code": "test_error", "message": "Test message"}}

from backend.app import create_app
from backend.core.exceptions import BackendError
from fastapi.testclient import TestClient


def test_create_app() -> None:
    app = create_app()
    assert app.title == "Kogniq API"
    assert app.version == "0.1.0"


def test_root_endpoint() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"name": "Kogniq API", "status": "running"}


def test_openapi_loads() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_swagger_ui_loads() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200


def test_global_exception_handler() -> None:
    app = create_app()

    @app.get("/test-error")
    async def trigger_error() -> None:
        raise BackendError(code="test_error", message="Test message", status_code=400)

    client = TestClient(app)
    response = client.get("/test-error")

    assert response.status_code == 400
    assert response.json() == {"error": {"code": "test_error", "message": "Test message"}}

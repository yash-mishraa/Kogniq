"""Health endpoint tests."""

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/system/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert float(response.headers["X-Process-Time-Ms"]) >= 0
    assert response.json() == {
        "status": "ok",
        "version": "0.1.0",
        "environment": "test",
        "uptime_seconds": response.json()["uptime_seconds"],
        "application": "Kogniq API",
    }
    assert response.json()["uptime_seconds"] >= 0


def test_health_endpoint_failure(client: TestClient, mocker: MockerFixture) -> None:
    from backend.dependencies import get_uow_factory
    factory = get_uow_factory()
    mocker.patch.object(factory, "create", side_effect=Exception("Simulated SQLite failure"))
    response = client.get("/api/v1/system/health")
    assert response.status_code == 503
    assert response.json()["error"]["message"] == "Database is unavailable"

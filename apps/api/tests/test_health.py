"""Health endpoint tests."""

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


def test_health_endpoint(client: TestClient, mocker: MockerFixture) -> None:
    mocker.patch(
        "apps.api.app.routers.health.check_database_health",
        new_callable=AsyncMock,
        return_value=True,
    )
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

"""Version endpoint tests."""

from fastapi.testclient import TestClient


def test_version_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/system/version")

    assert response.status_code == 200
    assert response.json() == {
        "application": "Kogniq API",
        "version": "0.1.0",
        "build": "test",
        "commit": "test-commit",
        "api_version": "v1",
    }

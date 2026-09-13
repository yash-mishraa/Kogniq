from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.app.config import APISettings
from apps.api.app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    settings = APISettings()
    return create_app(settings)


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


def test_api_authorization_isolation(client: TestClient) -> None:
    # 1. Register User A
    response_a = client.post(
        "/api/v1/auth/register",
        json={"email": "userA@example.com", "password": "passwordA", "display_name": "User A"},
    )
    assert response_a.status_code == 200
    token_a = response_a.cookies.get("kogniq_session")

    # 2. Register User B
    response_b = client.post(
        "/api/v1/auth/register",
        json={"email": "userB@example.com", "password": "passwordB", "display_name": "User B"},
    )
    assert response_b.status_code == 200
    token_b = response_b.cookies.get("kogniq_session")

    # 3. User A uploads a document
    upload_resp = client.post(
        "/api/v1/documents/process",
        cookies={"kogniq_session": token_a},
        files={"file": ("test.txt", b"User A content", "text/plain")},
    )
    assert upload_resp.status_code == 200
    doc_id = upload_resp.json()["document_id"]

    # 4. User B tries to delete User A's document
    delete_resp = client.delete(f"/api/v1/documents/{doc_id}", cookies={"kogniq_session": token_b})

    # 5. Assert that it fails with 403 (or 404 if obscured)
    assert delete_resp.status_code in (403, 404), (
        "User B should not be able to delete User A's document"
    )

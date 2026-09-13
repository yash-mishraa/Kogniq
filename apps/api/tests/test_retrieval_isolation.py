from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from apps.api.app.config import APISettings
from apps.api.app.main import create_app
from shared.config import Environment


@pytest.fixture
def auth_client() -> Generator[TestClient, None, None]:
    settings = APISettings(
        environment=Environment.TEST,
        build="test",
        commit="test-commit",
        allowed_hosts=["testserver"],
        cors_origins=[],
    )
    with TestClient(create_app(settings)) as client:
        yield client


def test_retrieval_isolation_enforcement(auth_client: TestClient) -> None:
    # Register User A
    resp = auth_client.post(
        "/api/v1/auth/register",
        json={"email": "usera@example.com", "password": "passwordA", "display_name": "A"},
    )
    assert resp.status_code == 200
    token_a = resp.cookies.get("kogniq_session")

    # Register User B
    resp = auth_client.post(
        "/api/v1/auth/register",
        json={"email": "userb@example.com", "password": "passwordB", "display_name": "B"},
    )
    assert resp.status_code == 200
    token_b = resp.cookies.get("kogniq_session")

    # Upload doc as User A
    upload_resp_a = auth_client.post(
        "/api/v1/documents/process",
        files={"file": ("test_a.txt", b"User A content for document.", "text/plain")},
        cookies={"kogniq_session": token_a},
    )
    assert upload_resp_a.status_code == 200
    doc_id_a = upload_resp_a.json()["document_id"]

    # Upload doc as User B
    upload_resp_b = auth_client.post(
        "/api/v1/documents/process",
        files={"file": ("test_b.txt", b"User B content for document.", "text/plain")},
        cookies={"kogniq_session": token_b},
    )
    assert upload_resp_b.status_code == 200
    doc_id_b = upload_resp_b.json()["document_id"]

    # User A searches doc A -> success
    resp_a_a = auth_client.post(
        "/api/v1/retrieval/search",
        json={"document_id": doc_id_a, "query": "content"},
        cookies={"kogniq_session": token_a},
    )
    assert resp_a_a.status_code == 200

    # User B searches doc B -> success
    resp_b_b = auth_client.post(
        "/api/v1/retrieval/search",
        json={"document_id": doc_id_b, "query": "content"},
        cookies={"kogniq_session": token_b},
    )
    assert resp_b_b.status_code == 200

    # User B searches doc A -> 403 Forbidden
    resp_b_a = auth_client.post(
        "/api/v1/retrieval/search",
        json={"document_id": doc_id_a, "query": "content"},
        cookies={"kogniq_session": token_b},
    )
    assert resp_b_a.status_code == 403

    # User A searches doc B -> 403 Forbidden
    resp_a_b = auth_client.post(
        "/api/v1/retrieval/search",
        json={"document_id": doc_id_b, "query": "content"},
        cookies={"kogniq_session": token_a},
    )
    assert resp_a_b.status_code == 403

    # Nonexistent document -> 404 Not Found
    resp_404 = auth_client.post(
        "/api/v1/retrieval/search",
        json={"document_id": "nonexistent_id", "query": "content"},
        cookies={"kogniq_session": token_a},
    )
    assert resp_404.status_code == 404

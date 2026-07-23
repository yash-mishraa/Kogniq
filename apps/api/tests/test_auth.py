import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def unique_email() -> str:
    import uuid

    return f"test_{uuid.uuid4()}@example.com"


def test_auth_registration_and_login_flow(client: TestClient, unique_email: str) -> None:
    # 1. Register
    register_payload = {
        "email": unique_email,
        "password": "secure_password",
        "display_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
    assert data["display_name"] == "Test User"
    assert "id" in data

    # Verify cookie was set
    assert "kogniq_session" in response.cookies

    # 2. Duplicate registration fails
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "user_already_exists"

    # 3. Session restoration (we have the cookie from registration)
    response = client.get("/api/v1/auth/session")
    assert response.status_code == 200
    assert response.json()["email"] == unique_email

    # 4. Logout
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    # Cookie should be cleared
    assert not response.cookies.get("kogniq_session")

    # 5. Session is now invalid
    response = client.get("/api/v1/auth/session")
    assert response.status_code == 401

    # 6. Login
    login_payload = {
        "email": unique_email,
        "password": "secure_password",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    assert "kogniq_session" in response.cookies

    # 7. Invalid Login
    invalid_login = {
        "email": unique_email,
        "password": "wrong_password",
    }
    response = client.post("/api/v1/auth/login", json=invalid_login)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_credentials"

    # 8. Unregistered Login
    unregistered_login = {
        "email": "not_found@example.com",
        "password": "wrong_password",
    }
    response = client.post("/api/v1/auth/login", json=unregistered_login)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "user_not_found"


def test_auth_missing_cookie(client: TestClient) -> None:
    # Explicitly clear cookies if any
    client.cookies.clear()

    response = client.get("/api/v1/auth/session")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_session"


def test_auth_csrf_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    assert "CSRF protection" in response.json()["message"]

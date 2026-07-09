"""Shared test fixtures for the Kogniq API."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from apps.api.app.config import APISettings
from apps.api.app.main import create_app
from shared.config import Environment


@pytest.fixture
def settings() -> APISettings:
    """Return deterministic settings that do not read external services."""
    return APISettings(
        environment=Environment.TEST,
        build="test",
        commit="test-commit",
        allowed_hosts=["testserver"],
        cors_origins=[],
    )


@pytest.fixture
def client(settings: APISettings) -> Iterator[TestClient]:
    """Run the application lifespan around each client."""
    with TestClient(create_app(settings)) as test_client:
        yield test_client

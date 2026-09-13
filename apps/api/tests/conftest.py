"""Shared test fixtures for the Kogniq API."""

import os
import tempfile
from collections.abc import Iterator

os.environ["PERSISTENCE_PROVIDER"] = "sqlite"
os.environ["LEARNING_GENERATION_PROVIDER"] = "fake"
os.environ["KNOWLEDGE_EXTRACTION_PROVIDER"] = "fake"
import pytest
from fastapi.testclient import TestClient

from apps.api.app.config import APISettings
from apps.api.app.main import create_app
from shared.config import Environment

db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(db_fd)


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

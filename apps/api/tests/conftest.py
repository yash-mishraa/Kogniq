"""Shared test fixtures for the Kogniq API."""

import os
import tempfile
from collections.abc import Iterator

os.environ["PERSISTENCE_PROVIDER"] = "sqlite"
os.environ["LEARNING_GENERATION_PROVIDER"] = "fake"
os.environ["KNOWLEDGE_EXTRACTION_PROVIDER"] = "fake"
os.environ["KOGNIQ_API_ENVIRONMENT"] = "test"

db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(db_fd)
# Never point the test suite at the developer database. The backend settings
# object reads the environment before .env, so this wins over SQLITE_DATABASE_PATH.
os.environ["SQLITE_DATABASE_PATH"] = db_path
_chroma_dir = tempfile.mkdtemp(prefix="kogniq-test-chroma-")
os.environ["CHROMA_DB_PATH"] = _chroma_dir
os.environ["CHROMA_COLLECTION"] = "kogniq_test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from apps.api.app.config import APISettings  # noqa: E402
from apps.api.app.main import create_app  # noqa: E402
from shared.config import Environment  # noqa: E402


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

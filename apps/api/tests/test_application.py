"""Application factory and lifespan tests."""

from fastapi.testclient import TestClient

from apps.api.app.config import APISettings
from apps.api.app.main import create_app


def test_application_startup(settings: APISettings) -> None:
    application = create_app(settings)

    with TestClient(application):
        assert application.state.is_ready is True
        assert application.state.started_at > 0

    assert application.state.is_ready is False

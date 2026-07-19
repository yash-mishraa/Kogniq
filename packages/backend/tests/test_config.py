import os
from unittest import mock

from backend.core.settings import BackendConfig


def test_default_config() -> None:
    config = BackendConfig()
    assert config.app_name == "Kogniq API"
    assert config.environment == "development"
    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.cors_origins == ["*"]


@mock.patch.dict(os.environ, {"ENVIRONMENT": "production", "PORT": "8080"})
def test_config_overrides() -> None:
    config = BackendConfig()
    assert config.environment == "production"
    assert config.port == 8080

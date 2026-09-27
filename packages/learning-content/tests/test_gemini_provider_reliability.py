# ruff: noqa
from unittest.mock import MagicMock, patch

import pytest

from learning_content.providers.base import AgentMessage
from learning_content.providers.gemini.provider import GeminiTextGenerationProvider


class APIError(Exception):
    def __init__(self, code):
        self.code = code


@pytest.fixture
def provider():
    return GeminiTextGenerationProvider(api_key="fake")


def test_provider_transient_retry(provider):
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    mock_response = MagicMock()
    mock_response.text = "Success!"
    mock_response.function_calls = []

    # 2 failures (503), then success
    mock_models.generate_content.side_effect = [APIError(503), APIError(503), mock_response]

    # We patch time.sleep to run instantly in tests
    with patch("time.sleep", return_value=None):
        result = provider.generate_chat(messages=[AgentMessage(role="user", content="Hi")])

    assert result.content == "Success!"
    assert mock_models.generate_content.call_count == 3


def test_provider_timeout_exhaustion(provider):
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    mock_models.generate_content.side_effect = TimeoutError("Timed out!")

    with patch("time.sleep", return_value=None):
        with pytest.raises(RuntimeError, match="Gemini generation failed: Timed out!"):
            provider.generate_chat(messages=[AgentMessage(role="user", content="Hi")])

    assert mock_models.generate_content.call_count == 3


def test_provider_permanent_failure(provider):
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    # 400 is permanent, should fail immediately
    mock_models.generate_content.side_effect = APIError(400)

    with patch("time.sleep", return_value=None), pytest.raises(RuntimeError):
        provider.generate_chat(messages=[AgentMessage(role="user", content="Hi")])

    assert mock_models.generate_content.call_count == 1

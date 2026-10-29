# ruff: noqa
from unittest.mock import MagicMock, patch

import pytest

from learning_content.providers.base import AgentMessage
from learning_content.providers.gemini.provider import GeminiTextGenerationProvider


class APIError(Exception):
    def __init__(self, code: int, message: str = "") -> None:
        super().__init__(message)
        self.code = code


class ServerError(APIError):
    """Simulates google.genai.errors.ServerError."""
    pass


class ClientError(APIError):
    """Simulates google.genai.errors.ClientError."""
    pass


@pytest.fixture
def provider() -> GeminiTextGenerationProvider:
    return GeminiTextGenerationProvider(api_key="fake")


def test_provider_server_error_subclass_retry(provider: GeminiTextGenerationProvider) -> None:
    """Regression test: ServerError (503) subclass must be retried, not fail on __class__.__name__."""
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    mock_response = MagicMock()
    mock_response.text = "Success after 503!"
    mock_response.function_calls = []

    # Real Gemini error scenario: ServerError with 503
    mock_models.generate_content.side_effect = [
        ServerError(503, "The model is overloaded. Please try again later."),
        ServerError(503, "The model is overloaded."),
        mock_response,
    ]

    with patch("time.sleep", return_value=None):
        result = provider.generate_chat(messages=[AgentMessage(role="user", content="Hi")])

    assert result.content == "Success after 503!"
    assert mock_models.generate_content.call_count == 3


def test_provider_circuit_breaker(provider: GeminiTextGenerationProvider) -> None:
    """Circuit breaker trips after repeated failures and blocks requests during cooldown."""
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    mock_models.generate_content.side_effect = ServerError(503, "High demand")

    # 3 calls each exhausting 3 retries = 3 failure batches -> trips circuit breaker
    with patch("time.sleep", return_value=None):
        for _ in range(3):
            with pytest.raises(RuntimeError):
                provider.generate("Prompt")

    # 4th call should be immediately blocked by open circuit breaker without calling generate_content
    call_count_before = mock_models.generate_content.call_count
    with pytest.raises(RuntimeError, match="circuit breaker"):
        provider.generate("Prompt")
    assert mock_models.generate_content.call_count == call_count_before

    # Health reporting reflects circuit_open
    health = provider.health()
    assert health["status"] == "circuit_open"
    assert health["cooldown_remaining_seconds"] > 0


def test_provider_transient_retry(provider: GeminiTextGenerationProvider) -> None:
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


def test_provider_timeout_exhaustion(provider: GeminiTextGenerationProvider) -> None:
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    mock_models.generate_content.side_effect = TimeoutError("Timed out!")

    with patch("time.sleep", return_value=None):
        with pytest.raises(RuntimeError, match="Gemini generation failed: Timed out!"):
            provider.generate_chat(messages=[AgentMessage(role="user", content="Hi")])

    assert mock_models.generate_content.call_count == 3


def test_provider_permanent_failure(provider: GeminiTextGenerationProvider) -> None:
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    # 400 is permanent, should fail immediately
    mock_models.generate_content.side_effect = APIError(400)

    with patch("time.sleep", return_value=None), pytest.raises(RuntimeError):
        provider.generate_chat(messages=[AgentMessage(role="user", content="Hi")])

    assert mock_models.generate_content.call_count == 1


def test_provider_429_retry_and_success(provider: GeminiTextGenerationProvider) -> None:
    """Transient 429 ResourceExhausted must be retried and succeed."""
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    mock_response = MagicMock()
    mock_response.text = "Success after 429!"
    mock_response.function_calls = []

    mock_models.generate_content.side_effect = [
        ClientError(429, "Resource exhausted / quota exceeded"),
        mock_response,
    ]

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = provider.generate_chat(messages=[AgentMessage(role="user", content="Hi")])

    assert result.content == "Success after 429!"
    assert mock_models.generate_content.call_count == 2
    assert mock_sleep.call_count == 1


def test_provider_retry_after_header_handling(provider: GeminiTextGenerationProvider) -> None:
    """Retry-After header or property should override default exponential delay."""
    err = ClientError(429, "Rate limited")
    err.retry_after = 2.5

    assert provider._get_retry_after(err) == 2.5

    # Check header dict format
    err2 = Exception("Rate limited")
    err2.headers = {"retry-after": "4.0"}
    assert provider._get_retry_after(err2) == 4.0


def test_provider_permanent_401_403_not_retried(provider: GeminiTextGenerationProvider) -> None:
    """Permanent authentication (401) or permission (403) errors must never be retried."""
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    for code in (401, 403):
        mock_models.generate_content.reset_mock()
        mock_models.generate_content.side_effect = ClientError(code, f"Auth error {code}")
        with patch("time.sleep", return_value=None), pytest.raises(RuntimeError):
            provider.generate("Prompt")
        assert mock_models.generate_content.call_count == 1, f"Code {code} was retried!"


def test_circuit_breaker_half_open_recovery(provider: GeminiTextGenerationProvider) -> None:
    """When cooldown expires (half-open), a successful probe call closes the circuit breaker."""
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    # Force trip circuit breaker
    provider._consecutive_failures = 3
    provider._circuit_open_until = 1000.0

    # During cooldown -> blocked
    with patch("time.time", return_value=900.0):
        with pytest.raises(RuntimeError, match="circuit breaker open"):
            provider.generate("Prompt")
        assert mock_models.generate_content.call_count == 0

    # Cooldown expires -> probe call allowed through
    mock_response = MagicMock()
    mock_response.text = "Recovered!"
    mock_response.function_calls = []
    mock_models.generate_content.side_effect = None
    mock_models.generate_content.return_value = mock_response

    with patch("time.time", return_value=1050.0):
        result = provider.generate("Prompt")

    assert result == "Recovered!"
    assert provider._consecutive_failures == 0
    assert provider._circuit_open_until == 0.0
    assert provider.health()["status"] == "healthy"


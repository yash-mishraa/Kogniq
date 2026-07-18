from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from openai import APIConnectionError, APIError, AuthenticationError, RateLimitError

from learning_content.providers.openrouter import (
    OpenRouterAuthenticationError,
    OpenRouterConnectionError,
    OpenRouterError,
    OpenRouterRateLimitError,
    OpenRouterResponseError,
    OpenRouterTextGenerationProvider,
)


@pytest.fixture
def mock_openai() -> Iterator[MagicMock]:
    with patch("learning_content.providers.openrouter.client.OpenAI") as mock:
        yield mock


@pytest.fixture
def provider() -> OpenRouterTextGenerationProvider:
    return OpenRouterTextGenerationProvider(
        api_key="test-key",
        model_name="test-model",
    )


def test_provider_info(provider: OpenRouterTextGenerationProvider) -> None:
    info = provider.info
    assert info.provider_id == "openrouter"
    assert info.default_model == "test-model"
    assert info.context_window > 0


def test_generate_success(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    # Setup mock response
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test response."
    mock_client.chat.completions.create.return_value = mock_response

    result = provider.generate("Test prompt", temperature=0.5, max_tokens=100)

    assert result == "This is a test response."
    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "Test prompt"}],
        temperature=0.5,
        max_tokens=100,
    )


def test_generate_batch_success(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response

    results = provider.generate_batch(("Prompt 1", "Prompt 2"))

    assert len(results) == 2
    assert results == ("Response", "Response")
    assert mock_client.chat.completions.create.call_count == 2


@pytest.mark.parametrize("invalid_prompt", ["", "   ", "\n\t"])
def test_generate_empty_prompt(
    provider: OpenRouterTextGenerationProvider, invalid_prompt: str
) -> None:
    with pytest.raises(OpenRouterError, match="Prompt cannot be empty"):
        provider.generate(invalid_prompt)


def test_lazy_initialization(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    # Should not be initialized on creation
    mock_openai.assert_not_called()

    # Setup mock response
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Response"
    mock_client.chat.completions.create.return_value = mock_response

    # First call initializes
    provider.generate("Prompt 1")
    mock_openai.assert_called_once()

    # Second call reuses
    provider.generate("Prompt 2")
    mock_openai.assert_called_once()  # Call count stays 1


def test_empty_content_response(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = None
    mock_client.chat.completions.create.return_value = mock_response

    with pytest.raises(OpenRouterResponseError, match="empty content"):
        provider.generate("Test prompt")


def test_authentication_error(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = AuthenticationError(
        message="Auth failed", response=MagicMock(), body=None
    )

    with pytest.raises(OpenRouterAuthenticationError):
        provider.generate("Test prompt")


def test_rate_limit_error(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = RateLimitError(
        message="Rate limited", response=MagicMock(), body=None
    )

    with pytest.raises(OpenRouterRateLimitError):
        provider.generate("Test prompt")


def test_connection_error(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = APIConnectionError(
        message="Connection failed", request=MagicMock()
    )

    with pytest.raises(OpenRouterConnectionError):
        provider.generate("Test prompt")


def test_api_error(provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock) -> None:
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = APIError(
        message="API error", request=MagicMock(), body=None
    )

    with pytest.raises(OpenRouterResponseError):
        provider.generate("Test prompt")


def test_unexpected_error(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = ValueError("Some weird error")

    with pytest.raises(OpenRouterError, match="Unexpected error"):
        provider.generate("Test prompt")


def test_long_unicode_markdown_prompt(
    provider: OpenRouterTextGenerationProvider, mock_openai: MagicMock
) -> None:
    mock_client = mock_openai.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "OK"
    mock_client.chat.completions.create.return_value = mock_response

    long_prompt = "# Title 🌟\n\n" + "long content " * 1000
    result = provider.generate(long_prompt)

    assert result == "OK"
    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": long_prompt.strip()}],
    )

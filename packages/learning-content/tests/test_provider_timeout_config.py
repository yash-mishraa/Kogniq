from learning_content.providers.gemini.provider import GeminiTextGenerationProvider


def test_provider_timeout_configuration() -> None:
    provider = GeminiTextGenerationProvider(api_key="fake")
    client = provider.client

    # Assert that the timeout is passed correctly as a float/int seconds
    assert client._api_client._http_options is not None
    timeout = client._api_client._http_options.timeout

    # Needs to be 30 or 30.0, NOT 30000
    assert timeout == 30.0 or timeout == 30, f"Timeout was {timeout}, expected 30.0"

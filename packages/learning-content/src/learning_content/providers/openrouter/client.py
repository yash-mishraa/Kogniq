from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError

from learning_content.providers.openrouter.exceptions import (
    OpenRouterAuthenticationError,
    OpenRouterConnectionError,
    OpenRouterError,
    OpenRouterRateLimitError,
    OpenRouterResponseError,
)


class LazyOpenRouterClient:
    """
    Lazy client wrapper for the OpenAI SDK pointing to OpenRouter.

    This encapsulates the SDK usage so that the rest of the application
    does not directly depend on the `openai` package.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._client: OpenAI | None = None

    @property
    def _lazy_client(self) -> OpenAI:
        """Instantiate the OpenAI client lazily."""
        if self._client is None:
            self._client = OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
            )
        return self._client

    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Execute generation against OpenRouter and wrap any SDK errors.
        """
        try:
            kwargs = {}
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            response = self._lazy_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                **kwargs,  # type: ignore
            )

            content = response.choices[0].message.content
            if content is None:
                raise OpenRouterResponseError("Received empty content from OpenRouter")

            return str(content)

        except AuthenticationError as e:
            raise OpenRouterAuthenticationError("OpenRouter authentication failed") from e
        except RateLimitError as e:
            raise OpenRouterRateLimitError("OpenRouter rate limit exceeded") from e
        except APIConnectionError as e:
            raise OpenRouterConnectionError("Failed to connect to OpenRouter") from e
        except APIError as e:
            raise OpenRouterResponseError(f"OpenRouter API error: {e}") from e
        except Exception as e:
            if isinstance(e, OpenRouterError):
                raise
            raise OpenRouterError(f"Unexpected error communicating with OpenRouter: {e}") from e

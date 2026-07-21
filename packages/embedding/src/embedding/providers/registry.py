from .interfaces import AbstractEmbeddingProvider
from .registry_exceptions import (
    DuplicateProviderError,
    InvalidProviderDefinitionError,
    ProviderNotFoundError,
)


class EmbeddingProviderRegistry:
    """O(1) registry for managing and retrieving Embedding Providers by ID."""

    def __init__(self) -> None:
        self._providers: dict[str, AbstractEmbeddingProvider] = {}

    def register(self, provider: AbstractEmbeddingProvider) -> None:
        if not isinstance(provider, AbstractEmbeddingProvider):
            raise InvalidProviderDefinitionError(
                "Provider must implement AbstractEmbeddingProvider."
            )

        provider_id = provider.info.provider_id

        if provider_id in self._providers:
            raise DuplicateProviderError(f"Provider ID '{provider_id}' is already registered.")

        self._providers[provider_id] = provider

    def provider(self, provider_id: str) -> AbstractEmbeddingProvider:
        if provider_id not in self._providers:
            raise ProviderNotFoundError(f"Provider ID '{provider_id}' not found in registry.")
        return self._providers[provider_id]

    def available_providers(self) -> tuple[AbstractEmbeddingProvider, ...]:
        return tuple(self._providers.values())

    def provider_count(self) -> int:
        return len(self._providers)

    def has_provider(self, provider_id: str) -> bool:
        return provider_id in self._providers

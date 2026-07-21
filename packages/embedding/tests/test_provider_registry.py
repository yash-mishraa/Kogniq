import pytest
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.providers import (
    AbstractEmbeddingProvider,
    DuplicateProviderError,
    EmbeddingProviderRegistry,
    InvalidProviderDefinitionError,
    ProviderInfo,
    ProviderNotFoundError,
)

from content.chunking import Chunk, ChunkCollection


class DummyProvider(AbstractEmbeddingProvider):
    def __init__(self, provider_id: str) -> None:
        self._id = provider_id

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_id=self._id,
            provider_name=f"Name {self._id}",
            model_name="m",
            model_version="1",
            embedding_version="v1",
            dimensions=1,
            supports_batch_generation=False,
            supports_async_generation=False,
            maximum_batch_size=1,
            maximum_tokens=1,
            normalized_output=False,
        )

    def generate(self, chunk: Chunk) -> Embedding:
        raise NotImplementedError

    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        raise NotImplementedError


def test_registry_registration() -> None:
    reg = EmbeddingProviderRegistry()
    p = DummyProvider("dummy")
    reg.register(p)
    assert reg.provider_count() == 1
    assert reg.has_provider("dummy")
    assert reg.provider("dummy") is p


def test_registry_duplicate_provider() -> None:
    reg = EmbeddingProviderRegistry()
    p1 = DummyProvider("dummy")
    p2 = DummyProvider("dummy")
    reg.register(p1)
    with pytest.raises(DuplicateProviderError):
        reg.register(p2)


def test_registry_lookup_not_found() -> None:
    reg = EmbeddingProviderRegistry()
    with pytest.raises(ProviderNotFoundError):
        reg.provider("missing")


def test_registry_invalid_provider() -> None:
    reg = EmbeddingProviderRegistry()
    with pytest.raises(InvalidProviderDefinitionError):
        reg.register("Not A Provider")  # type: ignore[arg-type]


def test_registry_available_providers() -> None:
    reg = EmbeddingProviderRegistry()
    p1 = DummyProvider("dummy1")
    p2 = DummyProvider("dummy2")
    reg.register(p1)
    reg.register(p2)
    providers = reg.available_providers()
    assert len(providers) == 2
    assert p1 in providers
    assert p2 in providers

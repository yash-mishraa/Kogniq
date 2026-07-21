from datetime import UTC, datetime

import pytest
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.providers import (
    AbstractEmbeddingProvider,
    ProviderConfigurationError,
    ProviderInfo,
)
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector

from content.chunking import Chunk, ChunkCollection


class FakeProvider(AbstractEmbeddingProvider):
    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_id="fake",
            provider_name="Fake Provider",
            model_name="fake-model",
            model_version="1",
            embedding_version="v1",
            dimensions=2,
            supports_batch_generation=True,
            supports_async_generation=False,
            maximum_batch_size=10,
            maximum_tokens=1000,
            normalized_output=True,
        )

    def generate(self, chunk: Chunk) -> Embedding:
        vec = EmbeddingVector(values=(0.5, 0.5), dimension=2)
        meta = EmbeddingMetadata(
            provider=self.info.provider_name,
            model_name=self.info.model_name,
            model_version=self.info.model_version,
            embedding_version=self.info.embedding_version,
            created_at=datetime.now(UTC),
            dimensions=self.info.dimensions,
            normalized=self.info.normalized_output,
        )
        stats = EmbeddingStatistics(processing_time_ms=1.0)
        return Embedding(
            id="1",
            chunk_id=chunk.id,
            vector=vec,
            metadata=meta,
            statistics=stats,
            created_at=datetime.now(UTC),
        )

    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        embs = tuple(self.generate(c) for c in chunks.chunks)
        return EmbeddingCollection(embeddings=embs)


def test_provider_info_validation() -> None:
    with pytest.raises(ProviderConfigurationError):
        ProviderInfo(
            provider_id="bad",
            provider_name="Bad",
            model_name="m",
            model_version="1",
            embedding_version="v1",
            dimensions=0,
            supports_batch_generation=False,
            supports_async_generation=False,
            maximum_batch_size=1,
            maximum_tokens=1,
            normalized_output=False,
        )


def test_fake_provider_interface() -> None:
    provider = FakeProvider()
    assert provider.info.dimensions == 2
    assert provider.info.provider_id == "fake"

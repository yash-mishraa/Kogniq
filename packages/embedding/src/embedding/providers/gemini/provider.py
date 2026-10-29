import hashlib
import os
import time
from datetime import UTC, datetime
from typing import Any

from content.chunking import Chunk, ChunkCollection
from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.providers import (
    AbstractEmbeddingProvider,
    EmbeddingGenerationError,
    ProviderCapabilityError,
    ProviderInfo,
)
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector


class GeminiEmbeddingProvider(AbstractEmbeddingProvider):
    """
    Hosted Gemini embedding provider utilizing Google GenAI API.
    Zero server-side RAM footprint, ideal for memory-constrained cloud environments (e.g. Render free tier).
    Outputs 384-dimensional embeddings matching the standard Kogniq vector schema.
    """

    def __init__(self, api_key: str | None = None, model_name: str = "gemini-embedding-001") -> None:
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._model_name = model_name
        self._client: Any = None
        self._cache: dict[str, tuple[float, ...]] = {}

    def _get_client(self) -> Any:
        if self._client is None:
            if not self._api_key:
                raise EmbeddingGenerationError("GEMINI_API_KEY is not configured for GeminiEmbeddingProvider")
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            provider_id="gemini",
            provider_name="GeminiEmbeddingProvider",
            model_name=self._model_name,
            model_version="1.0",
            embedding_version="1.0",
            dimensions=384,
            supports_batch_generation=True,
            supports_async_generation=False,
            maximum_batch_size=100,
            maximum_tokens=2048,
            normalized_output=True,
        )

    def generate(self, chunk: Chunk) -> Embedding:
        collection = self.generate_batch(ChunkCollection(chunks=[chunk]))
        return collection.embeddings[0]

    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        if not chunks.chunks:
            raise ProviderCapabilityError("Cannot generate embeddings for an empty collection")

        client = self._get_client()
        info = self.info

        missing_texts: dict[str, str] = {}
        chunk_hashes: list[str] = []

        for c in chunks.chunks:
            text = c.text.strip()
            if not text:
                raise EmbeddingGenerationError("Cannot generate embedding for empty chunk")
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            chunk_hashes.append(h)
            if h not in self._cache:
                missing_texts[h] = text

        if missing_texts:
            from google.genai import types

            start = time.perf_counter()
            missing_hash_list = list(missing_texts.keys())
            texts_to_encode = [missing_texts[h] for h in missing_hash_list]

            try:
                # Batch request via embed_content
                response = client.models.embed_content(
                    model=self._model_name,
                    contents=texts_to_encode,
                    config=types.EmbedContentConfig(output_dimensionality=384),
                )
                for i, h in enumerate(missing_hash_list):
                    self._cache[h] = tuple(float(x) for x in response.embeddings[i].values)
            except Exception as e:
                raise EmbeddingGenerationError(f"Gemini embedding API call failed: {e}") from e

            end = time.perf_counter()
            total_time_ms = (end - start) * 1000.0
            time_per_chunk = total_time_ms / len(missing_texts)
        else:
            time_per_chunk = 0.0

        embeddings: list[Embedding] = []
        for i, chunk in enumerate(chunks.chunks):
            h = chunk_hashes[i]
            values = self._cache[h]
            vec = EmbeddingVector(values=values, dimension=info.dimensions)
            meta = EmbeddingMetadata(
                provider=info.provider_name,
                model_name=info.model_name,
                model_version=info.model_version,
                embedding_version=info.embedding_version,
                created_at=datetime.now(UTC),
                dimensions=info.dimensions,
                normalized=info.normalized_output,
                document_id=chunk.document_id,
                chunk_hash=h,
                document_checksum=chunk.metadata.checksum if chunk.metadata else None,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                section_id=getattr(chunk, "section_id", None),
                section_title=getattr(chunk, "section_title", None),
                section_path=getattr(chunk, "section_path", None),
                figure_id=getattr(chunk, "figure_id", None),
                figure_number=getattr(chunk, "figure_number", None),
            )
            stats = EmbeddingStatistics(
                processing_time_ms=time_per_chunk if h in missing_texts else 0.0,
                token_count=None,
            )
            emb = Embedding(
                id=chunk.id,
                chunk_id=chunk.id,
                vector=vec,
                metadata=meta,
                statistics=stats,
                created_at=datetime.now(UTC),
            )
            embeddings.append(emb)

        return EmbeddingCollection(embeddings=embeddings)

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


class LocalEmbeddingProvider(AbstractEmbeddingProvider):
    """
    Local embedding provider utilizing sentence-transformers.
    Model initialization is strictly lazy to avoid pulling ML frameworks
    into memory during purely domain-related bootstrapping.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model: Any = None
        self._info: ProviderInfo | None = None
        self._cache: dict[str, tuple[float, ...]] = {}

    def _load_model(self) -> Any:
        if self._model is None:
            try:
                import importlib

                st_module = importlib.import_module("sentence_transformers")
                self._model = st_module.SentenceTransformer(self._model_name)
            except Exception as e:
                raise EmbeddingGenerationError(
                    f"Failed to load local model '{self._model_name}': {e}"
                ) from e
        return self._model

    @property
    def info(self) -> ProviderInfo:
        if self._info is None:
            model = self._load_model()
            try:
                dimensions = model.get_embedding_dimension()
            except AttributeError:
                try:
                    dimensions = model.get_sentence_embedding_dimension()
                except Exception:
                    dimensions = 384
            except Exception:
                dimensions = 384

            self._info = ProviderInfo(
                provider_id="local",
                provider_name="SentenceTransformers",
                model_name=self._model_name,
                model_version="1",
                embedding_version="v1",
                dimensions=dimensions,
                supports_batch_generation=True,
                supports_async_generation=False,
                maximum_batch_size=32,
                maximum_tokens=8192,
                normalized_output=True,
            )
        return self._info

    def generate(self, chunk: Chunk) -> Embedding:
        if not chunk.text.strip():
            raise EmbeddingGenerationError("Cannot generate embedding for empty chunk")

        model = self._load_model()
        info = self.info

        start = time.perf_counter()
        try:
            raw_embedding = model.encode(chunk.text, normalize_embeddings=True)
            # Ensure numpy structures are entirely converted to Python natives
            values = tuple(float(x) for x in raw_embedding)
        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embedding: {e}") from e

        end = time.perf_counter()
        processing_time_ms = (end - start) * 1000.0

        vec = EmbeddingVector(values=values, dimension=info.dimensions)

        meta = EmbeddingMetadata(
            provider=info.provider_name,
            model_name=info.model_name,
            model_version=info.model_version,
            embedding_version=info.embedding_version,
            created_at=datetime.now(UTC),
            dimensions=info.dimensions,
            normalized=info.normalized_output,
        )

        stats = EmbeddingStatistics(
            processing_time_ms=processing_time_ms,
            token_count=None,
        )

        return Embedding(
            id=chunk.id,
            chunk_id=chunk.id,
            vector=vec,
            metadata=meta,
            statistics=stats,
            created_at=datetime.now(UTC),
        )

    def generate_batch(self, chunks: ChunkCollection) -> EmbeddingCollection:
        if not chunks.chunks:
            raise ProviderCapabilityError("Cannot generate embeddings for an empty collection")

        model = self._load_model()
        info = self.info

        import hashlib
        
        # Determine unique hashes and identify cache misses
        # To handle identical chunks inside the same batch, map hash to texts
        missing_texts: dict[str, str] = {}
        chunk_hashes: list[str] = []
        
        for c in chunks.chunks:
            text = c.text.strip()
            if not text:
                raise EmbeddingGenerationError("Cannot generate embedding for empty chunk")
            
            chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            chunk_hashes.append(chunk_hash)
            
            if chunk_hash not in self._cache:
                missing_texts[chunk_hash] = text
                
        # Generate missing vectors
        if missing_texts:
            start = time.perf_counter()
            try:
                # Keep deterministic order for ML batch processing
                missing_hash_list = list(missing_texts.keys())
                texts_to_encode = [missing_texts[h] for h in missing_hash_list]
                
                raw_embeddings = model.encode(texts_to_encode, normalize_embeddings=True)
                
                # Cache results
                for i, h in enumerate(missing_hash_list):
                    self._cache[h] = tuple(float(x) for x in raw_embeddings[i])
                    
            except Exception as e:
                raise EmbeddingGenerationError(f"Failed to generate batch embeddings: {e}") from e
                
            end = time.perf_counter()
            total_time_ms = (end - start) * 1000.0
            time_per_chunk = total_time_ms / len(missing_texts)
        else:
            time_per_chunk = 0.0

        embeddings = []
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

        return EmbeddingCollection(embeddings=tuple(embeddings))

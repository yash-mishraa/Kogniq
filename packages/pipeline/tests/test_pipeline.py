import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import UTC, datetime
from typing import cast
from unittest.mock import MagicMock

from embedding.collection import EmbeddingCollection
from embedding.embedding import Embedding
from embedding.metadata import EmbeddingMetadata
from embedding.providers.interfaces import AbstractEmbeddingProvider
from embedding.providers.provider_info import ProviderInfo
from embedding.statistics import EmbeddingStatistics
from embedding.vector import EmbeddingVector
from embedding.vectorstores.interfaces import AbstractVectorStore
from embedding.vectorstores.search_result import SearchResult
from embedding.vectorstores.storage_result import StorageResult
from embedding.vectorstores.store_info import StoreInfo
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from knowledge.extractors.provider_info import KnowledgeExtractorInfo
from knowledge.graph import KnowledgeGraph
from pipeline.pipeline import DocumentIntelligencePipeline

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.engine import HybridChunkEngine
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics
from content.normalized.document import NormalizedDocument
from content.plugins.interfaces import AbstractContentProcessor
from content.plugins.processor_info import ProcessorInfo
from content.plugins.registry import ProcessorRegistry
from content.resource.handle import ResourceHandle


class FakeProcessor(AbstractContentProcessor):
    def __init__(self) -> None:
        self._info = ProcessorInfo(
            name="Fake Processor",
            version="1.0",
            description="A fake processor",
            supported_extensions=(".txt",),
            supported_mime_types=("text/plain",),
        )

    @property
    def processor_info(self) -> ProcessorInfo:
        return self._info

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        doc = MagicMock(spec=NormalizedDocument)
        doc.id = handle.id
        doc.title = "Fake Title"
        doc.content = "Fake content"
        return cast(NormalizedDocument, doc)


class FakeChunkEngine(HybridChunkEngine):
    def __init__(self) -> None:
        pass

    def chunk(self, document: NormalizedDocument) -> ChunkCollection:
        c = Chunk(
            id="chunk_1",
            text="Fake content chunk",
            document_id=document.id,
            chunk_index=0,
            metadata=ChunkMetadata(
                processor="fake", document_version="1.0", source="fake", checksum="hash"
            ),
            statistics=ChunkStatistics(
                character_count=10,
                word_count=2,
                estimated_tokens=3,
                line_count=1,
                processing_timestamp=datetime.now(UTC),
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        )
        return ChunkCollection(chunks=(c,))


class FakeEmbeddingProvider(AbstractEmbeddingProvider):
    def __init__(self) -> None:
        self._info = ProviderInfo(
            provider_id="fake_provider",
            provider_name="Fake Provider",
            model_name="fake-model",
            model_version="1.0",
            embedding_version="1.0",
            dimensions=3,
            supports_batch_generation=True,
            supports_async_generation=False,
            maximum_batch_size=10,
            maximum_tokens=100,
            normalized_output=True,
        )

    @property
    def info(self) -> ProviderInfo:
        return self._info

    def generate(self, chunk: Chunk) -> Embedding:
        return Embedding(
            id=f"emb_{chunk.id}",
            chunk_id=chunk.id,
            vector=EmbeddingVector(values=(0.1, 0.2, 0.3), dimension=3),
            metadata=EmbeddingMetadata(
                provider="fake",
                model_name="fake-model",
                model_version="1.0",
                embedding_version="1.0",
                dimensions=3,
                normalized=True,
                language="en",
                created_at=datetime.now(UTC),
            ),
            statistics=EmbeddingStatistics(processing_time_ms=10.0),
            created_at=datetime.now(UTC),
        )

    def generate_batch(self, collection: ChunkCollection) -> EmbeddingCollection:
        embeddings = [self.generate(chunk) for chunk in collection.chunks]
        return EmbeddingCollection(embeddings=tuple(embeddings))


class FakeVectorStore(AbstractVectorStore):
    def __init__(self) -> None:
        self.storage: list[Embedding] = []
        self._info = StoreInfo(
            store_id="fake_store",
            store_name="Fake Store",
            implementation_version="1.0",
            supported_distance_metrics=("cosine",),
            supports_metadata_filtering=False,
            supports_batch_insert=True,
            supports_batch_delete=True,
            maximum_batch_size=10,
        )

    @property
    def info(self) -> StoreInfo:
        return self._info

    def store(self, embedding: Embedding) -> StorageResult:
        self.storage.append(embedding)
        return StorageResult(
            stored_count=1, collection_name="fake_col", metadata={"ids": [embedding.id]}
        )

    def store_batch(self, embeddings: EmbeddingCollection) -> StorageResult:
        self.storage.extend(embeddings.embeddings)
        ids = [e.id for e in embeddings.embeddings]
        return StorageResult(
            stored_count=len(ids), collection_name="fake_col", metadata={"ids": ids}
        )

    def delete(self, embedding_id: str) -> None:
        pass

    def delete_batch(self, embedding_ids: tuple[str, ...]) -> None:
        pass

    def search(self, vector: EmbeddingVector, *, limit: int = 10) -> tuple[SearchResult, ...]:
        _ = vector
        _ = limit
        return ()

    def count(self) -> int:
        return len(self.storage)

    def clear(self) -> None:
        self.storage.clear()


class FakeKnowledgeExtractor(AbstractKnowledgeExtractor):
    def __init__(self) -> None:
        self._info = KnowledgeExtractorInfo(
            extractor_id="fake_extractor",
            extractor_name="Fake Extractor",
            version="1.0",
            provider="Fake",
            supports_batch_processing=True,
            supports_streaming=False,
            maximum_chunks_per_request=10,
            maximum_tokens=100,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )

    @property
    def info(self) -> KnowledgeExtractorInfo:
        return self._info

    def extract(self, chunks: ChunkCollection) -> KnowledgeExtractionResult:
        return KnowledgeExtractionResult(
            graph=KnowledgeGraph(concepts=(), relationships=()),
            extractor_id=self.info.extractor_id,
            extractor_name=self.info.extractor_name,
            version=self.info.version,
            processing_time_ms=10.0,
            processed_chunks=chunks.total_chunks,
            created_at=datetime.now(UTC),
        )

    def extract_batch(
        self, collections: tuple[ChunkCollection, ...]
    ) -> tuple[KnowledgeExtractionResult, ...]:
        return tuple(self.extract(c) for c in collections)


def test_document_intelligence_pipeline_success() -> None:
    registry = ProcessorRegistry()
    registry.register(FakeProcessor())

    chunk_engine = FakeChunkEngine()
    embedding_provider = FakeEmbeddingProvider()
    vector_store = FakeVectorStore()
    knowledge_extractor = FakeKnowledgeExtractor()

    pipeline = DocumentIntelligencePipeline(
        processor_registry=registry,
        chunk_engine=chunk_engine,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        knowledge_extractor=knowledge_extractor,
    )

    handle = MagicMock(spec=ResourceHandle)
    handle.id = "res_1"
    handle.mime_type = "text/plain"
    handle.extension = ".txt"

    result = pipeline.run(cast(ResourceHandle, handle))

    # Verify Content
    assert result.content.document.id == "res_1"
    assert result.content.chunks.total_chunks == 1

    # Verify Embeddings
    assert len(result.embeddings.collection.embeddings) == 1
    assert result.embeddings.storage_result.stored_count == 1
    assert vector_store.count() == 1

    # Verify Knowledge
    assert result.knowledge.extraction_result.graph.concept_count == 0

    # Verify Metadata
    assert result.metadata.processor_name == "Fake Processor"
    assert result.metadata.embedding_provider_name == "Fake Provider"
    assert result.metadata.vector_store_name == "Fake Store"
    assert result.metadata.knowledge_extractor_name == "Fake Extractor"
    assert result.metadata.total_processing_time_ms > 0

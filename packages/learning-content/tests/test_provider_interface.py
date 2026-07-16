from datetime import UTC, datetime
from unittest.mock import MagicMock

from knowledge.graph import KnowledgeGraph

from content.chunking import Chunk, ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.metadata import LearningContentMetadata
from learning_content.providers.interfaces import AbstractLearningGenerator
from learning_content.providers.provider_info import GeneratorInfo
from learning_content.statistics import LearningContentStatistics


class FakeLearningGenerator(AbstractLearningGenerator):
    def info(self) -> GeneratorInfo:
        return GeneratorInfo(
            generator_id="fake-gen",
            generator_name="Fake Generator",
            generator_version="1.0",
            provider_name="Fake Provider",
            supported_content_types=(ContentType.SUMMARY,),
            maximum_chunks=10,
            maximum_tokens=1000,
            supports_batch_generation=True,
        )

    def generate(
        self, chunks: ChunkCollection, graph: KnowledgeGraph
    ) -> LearningContent:
        return LearningContent(
            id="test-content-1",
            source_document_id=chunks.chunks[0].document_id if chunks.chunks else "unknown",
            source_chunk_ids=tuple(c.id for c in chunks.chunks),
            content_type=ContentType.SUMMARY,
            title="Test Summary",
            body="This is a test summary.",
            metadata=LearningContentMetadata(
                provider="Fake Provider",
                model="fake-model",
                model_version="1.0",
                generation_version="1.0",
                language="en",
                educational_level="all",
                subject="test",
                syllabus="test",
                tags=(),
            ),
            statistics=LearningContentStatistics(
                character_count=23,
                word_count=5,
                estimated_tokens=5,
                processing_time_ms=0.0,
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        )

    def generate_batch(
        self, collections: tuple[ChunkCollection, ...], graphs: tuple[KnowledgeGraph, ...]
    ) -> LearningContentCollection:
            return LearningContentCollection(
                contents=tuple(
                    self.generate(c, g) 
                    for c, g in zip(collections, graphs, strict=True)
                )
            )


def test_fake_generator() -> None:
    generator = FakeLearningGenerator()
    assert generator.info().generator_id == "fake-gen"

    chunk_mock = MagicMock(spec=Chunk)
    chunk_mock.id = "chunk-1"
    chunk_mock.document_id = "doc-1"
    
    chunks = ChunkCollection(chunks=(chunk_mock,))
    graph = MagicMock(spec=KnowledgeGraph)

    content = generator.generate(chunks, graph)
    assert content.title == "Test Summary"

    batch = generator.generate_batch((chunks,), (graph,))
    assert batch.total_items == 1

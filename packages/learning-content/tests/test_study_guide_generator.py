from datetime import UTC, datetime

import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.enums import ContentType
from learning_content.generators.base import GenerationContext
from learning_content.generators.base.exceptions import LearningGenerationError
from learning_content.generators.study_guide.generator import StudyGuideGenerator
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class MockProvider(AbstractTextGenerationProvider):
    def __init__(self, response: str, fail: bool = False) -> None:
        self._response = response
        self.fail = fail

    @property
    def info(self) -> TextGenerationProviderInfo:
        return TextGenerationProviderInfo(
            provider_id="mock",
            provider_name="Mock",
            default_model="mock-model",
            model_version="1.0",
            context_window=1000,
        )

    def generate(self, prompt: str, **kwargs: object) -> str:
        if self.fail:
            raise Exception("Mock provider failure")
        return self._response


def create_sample_context() -> GenerationContext:
    chunks = ChunkCollection(
        chunks=(
            Chunk(
                id="chunk-1",
                document_id="doc1",
                chunk_index=0,
                text="Test content",
                metadata=ChunkMetadata(
                    processor="txt", document_version="1.0", source="test", checksum="123"
                ),
                statistics=ChunkStatistics(
                    character_count=100,
                    line_count=1,
                    word_count=20,
                    estimated_tokens=26,
                    processing_timestamp=datetime.now(UTC),
                    confidence=1.0,
                ),
                created_at=datetime.now(UTC),
            ),
        )
    )
    graph = KnowledgeGraph(
        concepts=(
            KnowledgeConcept(
                id="c1",
                document_id="doc1",
                name="Test",
                description="Test",
                concept_type=ConceptType.ALGORITHM,
                aliases=(),
                confidence=1.0,
                created_at=datetime.now(UTC),
                metadata=KnowledgeMetadata(
                    source_document="doc1",
                    source_chunk="chunk-1",
                    language="en",
                    confidence=1.0,
                    extraction_version="1.0",
                    created_by="test",
                ),
            ),
        ),
        relationships=(),
    )
    return GenerationContext(chunks=chunks, graph=graph)


@pytest.fixture
def study_guide_generator() -> StudyGuideGenerator:
    sg_markdown = "# Comprehensive Study Guide\n## Introduction\nTesting study guide."
    provider = MockProvider(sg_markdown)
    return StudyGuideGenerator(provider)


def test_study_guide_generation(study_guide_generator: StudyGuideGenerator) -> None:
    context = create_sample_context()
    content = study_guide_generator.generate(context.chunks, context.graph)

    assert content.content_type == ContentType.STUDY_GUIDE
    assert "Comprehensive Study Guide" in content.title

    body = content.body
    assert "Testing study guide" in body
    assert content.metadata.provider == "mock"
    assert "study-guide-v1" in content.metadata.prompt_version


def test_study_guide_failure() -> None:
    provider = MockProvider("Empty", fail=True)
    sg_generator = StudyGuideGenerator(provider)

    context = create_sample_context()

    with pytest.raises(LearningGenerationError, match="Failed to generate learning content"):
        sg_generator.generate(context.chunks, context.graph)

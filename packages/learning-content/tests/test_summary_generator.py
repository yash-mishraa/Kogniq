from datetime import UTC, datetime

import pytest
from knowledge.graph import KnowledgeGraph

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.enums import ContentType
from learning_content.generators.summary import (
    EmptyResponseError,
    SummaryGenerationError,
    SummaryGenerator,
)
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class FakeTextGenerationProvider(AbstractTextGenerationProvider):
    def __init__(self, response: str = "Fake generated summary.") -> None:
        self._response = response
        self.last_prompt = ""

    @property
    def info(self) -> TextGenerationProviderInfo:
        return TextGenerationProviderInfo(
            provider_id="fake-provider",
            provider_name="Fake Provider",
            default_model="fake-model-v1",
            model_version="1.0",
            context_window=4096,
        )

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        self.last_prompt = prompt
        return self._response


def create_empty_chunks() -> ChunkCollection:
    return ChunkCollection(
        chunks=(),
    )


def create_sample_chunks(n: int = 2) -> ChunkCollection:
    chunks = tuple(
        Chunk(
            id=f"chunk-{i}",
            document_id="sample-doc",
            chunk_index=i,
            text=f"Sample chunk content {i}.",
            metadata=ChunkMetadata(
                processor="test", document_version="1.0", source="test", checksum="123"
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
        )
        for i in range(n)
    )
    return ChunkCollection(
        chunks=chunks,
    )


def create_unicode_chunks() -> ChunkCollection:
    chunks = (
        Chunk(
            id="chunk-unicode",
            document_id="unicode-doc",
            chunk_index=0,
            text="こんにちは世界! This is a test of ✅ unicode emojis.",
            metadata=ChunkMetadata(
                processor="test", document_version="1.0", source="test", checksum="123"
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
    return ChunkCollection(
        chunks=chunks,
    )


def test_generator_info() -> None:
    provider = FakeTextGenerationProvider()
    generator = SummaryGenerator(provider=provider)
    info = generator.info()

    assert info.generator_id == "summary-generator-v1"
    assert info.provider_name == "fake-provider"
    assert info.supported_content_types == (ContentType.SUMMARY,)


def test_generate_summary_success() -> None:
    provider = FakeTextGenerationProvider("This is a summary.")
    generator = SummaryGenerator(provider=provider)

    chunks = create_sample_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    content = generator.generate(chunks, graph)

    assert content.content_type == ContentType.SUMMARY
    assert content.body == "This is a summary."
    assert content.title == "Generated Summary"

    # Metadata population
    assert content.metadata.provider == "fake-provider"
    assert content.metadata.model == "fake-model-v1"
    assert content.metadata.model_version == "1.0"
    assert content.metadata.prompt_version == "summary-v1"

    # Statistics
    assert content.statistics.word_count == 4
    assert content.statistics.character_count == 18
    assert content.statistics.confidence == 0.5
    assert content.statistics.estimated_tokens == int(4 * 1.3)


def test_generate_empty_chunks() -> None:
    provider = FakeTextGenerationProvider("Summary of nothing.")
    generator = SummaryGenerator(provider=provider)

    chunks = create_empty_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    with pytest.raises(SummaryGenerationError, match="Source chunk IDs must not be empty"):
        generator.generate(chunks, graph)


def test_generate_empty_graph() -> None:
    provider = FakeTextGenerationProvider("Summary without graph.")
    generator = SummaryGenerator(provider=provider)

    chunks = create_sample_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    generator.generate(chunks, graph)
    generator.generate(chunks, graph)
    assert "KEY CONCEPTS" not in provider.last_prompt
    assert "RELATIONSHIPS" not in provider.last_prompt


def test_generate_large_chunks() -> None:
    provider = FakeTextGenerationProvider("Summary of large chunk.")
    generator = SummaryGenerator(provider=provider)

    chunks = create_sample_chunks(100)
    graph = KnowledgeGraph(concepts=(), relationships=())

    generator.generate(chunks, graph)
    assert "Sample chunk content 99" in provider.last_prompt


def test_generate_unicode_content() -> None:
    provider = FakeTextGenerationProvider("こんにちは世界 Summary ✅")
    generator = SummaryGenerator(provider=provider)

    chunks = create_unicode_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    content = generator.generate(chunks, graph)
    assert content.body == "こんにちは世界 Summary ✅"
    assert "こんにちは世界!" in provider.last_prompt


def test_generate_multiline_response() -> None:
    provider = FakeTextGenerationProvider("Line 1\nLine 2\n\nLine 3")
    generator = SummaryGenerator(provider=provider)

    chunks = create_sample_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    content = generator.generate(chunks, graph)
    assert content.body == "Line 1\nLine 2\n\nLine 3"
    assert content.statistics.word_count == 6


def test_generate_whitespace_only_response() -> None:
    provider = FakeTextGenerationProvider("   \n\t  ")
    generator = SummaryGenerator(provider=provider)

    chunks = create_sample_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    with pytest.raises(EmptyResponseError):
        generator.generate(chunks, graph)


def test_generate_placeholder_response() -> None:
    provider = FakeTextGenerationProvider("I cannot answer.")
    generator = SummaryGenerator(provider=provider)
    chunks = create_sample_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    with pytest.raises(EmptyResponseError, match="placeholder response"):
        generator.generate(chunks, graph)


def test_generate_markdown_response() -> None:
    provider = FakeTextGenerationProvider("# Summary\n\n- Point 1\n- Point 2")
    generator = SummaryGenerator(provider=provider)
    chunks = create_sample_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    content = generator.generate(chunks, graph)
    assert content.body == "# Summary\n\n- Point 1\n- Point 2"
    assert content.statistics.word_count == 8


def test_generate_provider_exception() -> None:
    class FailingProvider(FakeTextGenerationProvider):
        def generate(
            self,
            prompt: str,
            *,
            temperature: float | None = None,
            max_tokens: int | None = None,
        ) -> str:
            raise ValueError("Provider failed")

    provider = FailingProvider()
    generator = SummaryGenerator(provider=provider)
    chunks = create_sample_chunks()
    graph = KnowledgeGraph(concepts=(), relationships=())

    with pytest.raises(SummaryGenerationError, match="Failed to generate summary: Provider failed"):
        generator.generate(chunks, graph)


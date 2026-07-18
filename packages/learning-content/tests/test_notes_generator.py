from datetime import UTC, datetime

import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.enums import ContentType
from learning_content.generators.base import GenerationContext, ParsingError
from learning_content.generators.notes.generator import NotesGenerator
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class FakeTextGenerationProvider(AbstractTextGenerationProvider):
    def __init__(self, response: str = "Fake generated notes.") -> None:
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
        _ = (temperature, max_tokens)
        self.last_prompt = prompt
        return self._response


def create_sample_context() -> GenerationContext:
    chunks = ChunkCollection(
        chunks=(
            Chunk(
                id="chunk-1",
                document_id="doc1",
                chunk_index=0,
                text="Sample text for notes.",
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
                title="Concept1",
                description="Desc1",
                concept_type=ConceptType.FACT,
                aliases=(),
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


def test_generator_info() -> None:
    provider = FakeTextGenerationProvider()
    generator = NotesGenerator(provider=provider)
    info = generator.info()

    assert info.generator_id == "notes-generator-v1"
    assert info.provider_name == "fake-provider"
    assert info.supported_content_types == (ContentType.NOTES,)


def test_generate_notes_success() -> None:
    response = "# Topic\n\n## Subtopic\n- Bullet 1\n- Bullet 2"
    provider = FakeTextGenerationProvider(response)
    generator = NotesGenerator(provider=provider)

    context = create_sample_context()
    content = generator.generate(context.chunks, context.graph)

    assert content.content_type == ContentType.NOTES
    assert content.body == response
    assert content.title == "Topic"
    assert content.metadata.prompt_version == "notes-v1"


def test_markdown_preservation() -> None:
    response = (
        "# Math Notes\n\n"
        "## Code Block\n"
        "```python\n"
        "def hello():\n"
        "    pass\n"
        "```\n\n"
        "## Math\n"
        "$$x = \\frac{1}{2}$$\n\n"
        "## Lists\n"
        "- Level 1\n"
        "  - Level 2\n"
        "    - Level 3"
    )
    provider = FakeTextGenerationProvider(response)
    generator = NotesGenerator(provider=provider)
    context = create_sample_context()
    content = generator.generate(context.chunks, context.graph)

    assert content.body == response


def test_placeholder_rejection() -> None:
    placeholders = ["I cannot answer", "As an AI language model", "N/A", "Unknown"]
    for p in placeholders:
        provider = FakeTextGenerationProvider(p)
        generator = NotesGenerator(provider=provider)
        context = create_sample_context()
        with pytest.raises(ParsingError, match="placeholder response"):
            generator.generate(context.chunks, context.graph)


def test_empty_rejection() -> None:
    provider = FakeTextGenerationProvider("   \n\n   ")
    generator = NotesGenerator(provider=provider)
    context = create_sample_context()
    with pytest.raises(ParsingError, match="empty or whitespace-only"):
        generator.generate(context.chunks, context.graph)


def test_unicode_support() -> None:
    response = "# こんにちは世界\n\n- これはテストです 🚀"
    provider = FakeTextGenerationProvider(response)
    generator = NotesGenerator(provider=provider)
    context = create_sample_context()
    content = generator.generate(context.chunks, context.graph)
    assert content.title == "こんにちは世界"
    assert "🚀" in content.body


def test_large_source_material() -> None:
    large_text = "Word " * 1000
    chunks = ChunkCollection(
        chunks=tuple(
            Chunk(
                id=f"chunk-{i}",
                document_id="doc1",
                chunk_index=i,
                text=large_text,
                metadata=ChunkMetadata(
                    processor="txt", document_version="1.0", source="test", checksum="123"
                ),
                statistics=ChunkStatistics(
                    character_count=5000,
                    line_count=1,
                    word_count=1000,
                    estimated_tokens=1300,
                    processing_timestamp=datetime.now(UTC),
                    confidence=1.0,
                ),
                created_at=datetime.now(UTC),
            )
            for i in range(10)
        )
    )
    context = GenerationContext(chunks=chunks, graph=KnowledgeGraph(concepts=(), relationships=()))
    provider = FakeTextGenerationProvider("# Large Notes\n- Done")
    generator = NotesGenerator(provider=provider)
    generator.generate(context.chunks, context.graph)
    assert "Word Word" in provider.last_prompt
    assert "chunk-9" in provider.last_prompt

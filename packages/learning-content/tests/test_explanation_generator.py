from datetime import UTC, datetime

import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.enums import ContentType
from learning_content.generators.base import GenerationContext
from learning_content.generators.explanation.exceptions import InvalidExplanationError
from learning_content.generators.explanation.generator import ExplanationGenerator
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class FakeTextGenerationProvider(AbstractTextGenerationProvider):
    def __init__(self, response: str) -> None:
        self._response = response
        self.last_prompt = ""

    @property
    def info(self) -> TextGenerationProviderInfo:
        return TextGenerationProviderInfo(
            provider_id="fake-provider",
            provider_name="Fake Provider",
            default_model="fake-model",
            model_version="1.0",
            context_window=4096,
        )

    def generate(
        self, prompt: str, *, temperature: float | None = None, max_tokens: int | None = None
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
                text="Gradient descent is an optimization algorithm used to minimize loss.",
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
                title="Gradient Descent",
                description="Optimization algorithm",
                concept_type=ConceptType.ALGORITHM,
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


VALID_EXPLANATION = """# Concept
Gradient Descent is an algorithm.

## Why It Matters
It trains models.

## Intuition
Like walking down a hill.

## Detailed Explanation
Calculates the gradient of the loss function.

## Example
Linear regression.

## Common Mistakes
Learning rate too high.

## Related Concepts
Backpropagation.

## Key Takeaways
- Minimizes loss.
- Uses gradients."""


def test_generator_info() -> None:
    provider = FakeTextGenerationProvider(VALID_EXPLANATION)
    generator = ExplanationGenerator(provider)
    assert generator.info().generator_id == "explanation-generator-v1"
    assert generator.info().supported_content_types == (ContentType.EXPLANATION,)


def test_successful_parsing() -> None:
    provider = FakeTextGenerationProvider(VALID_EXPLANATION)
    generator = ExplanationGenerator(provider)
    context = create_sample_context()

    content = generator.generate(context.chunks, context.graph)

    assert content.content_type == ContentType.EXPLANATION
    assert content.title == "Concept"
    assert content.body == VALID_EXPLANATION
    assert content.statistics.heading_count == 8


def test_fenced_markdown_parsing() -> None:
    response = f"```markdown\n{VALID_EXPLANATION}\n```"
    provider = FakeTextGenerationProvider(response)
    generator = ExplanationGenerator(provider)
    context = create_sample_context()

    content = generator.generate(context.chunks, context.graph)
    assert content.body == VALID_EXPLANATION


def test_missing_heading() -> None:
    response = VALID_EXPLANATION.replace("## Why It Matters", "")
    provider = FakeTextGenerationProvider(response)
    generator = ExplanationGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidExplanationError, match="Missing required markdown heading"):
        generator.generate(context.chunks, context.graph)


def test_placeholder_rejection() -> None:
    response = "As an AI, I cannot fulfill this request."
    provider = FakeTextGenerationProvider(response)
    generator = ExplanationGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidExplanationError, match="too short"):
        generator.generate(context.chunks, context.graph)


def test_empty_rejection() -> None:
    provider = FakeTextGenerationProvider("   \n  ")
    generator = ExplanationGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidExplanationError, match="empty response"):
        generator.generate(context.chunks, context.graph)


def test_short_rejection() -> None:
    response = "# Concept\nToo short."
    provider = FakeTextGenerationProvider(response)
    generator = ExplanationGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidExplanationError, match="too short"):
        generator.generate(context.chunks, context.graph)

import json
from datetime import UTC, datetime

import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.enums import ContentType
from learning_content.generators.base import GenerationContext
from learning_content.generators.flashcards.exceptions import (
    InvalidFlashcardError,
    InvalidFlashcardJsonError,
)
from learning_content.generators.flashcards.generator import FlashcardsGenerator
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


def test_generator_info() -> None:
    provider = FakeTextGenerationProvider("[]")
    generator = FlashcardsGenerator(provider)
    assert generator.info().generator_id == "flashcards-generator-v1"
    assert generator.info().supported_content_types == (ContentType.FLASHCARDS,)


def test_successful_json_parsing() -> None:
    response = json.dumps(
        [
            {
                "question": "What is gradient descent?",
                "answer": "An optimization algorithm.",
                "difficulty": "medium",
            },
            {"question": "Why use it?", "answer": "To minimize loss.", "difficulty": "hard"},
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    content = generator.generate(context.chunks, context.graph)

    assert content.content_type == ContentType.FLASHCARDS
    assert "Flashcards" in content.title

    parsed_body = json.loads(content.body)
    assert len(parsed_body) == 2
    assert parsed_body[0]["difficulty"] == "medium"
    assert parsed_body[1]["difficulty"] == "hard"


def test_fenced_json_parsing() -> None:
    response = (
        "```json\n"
        + json.dumps([{"question": "Q1", "answer": "A1", "difficulty": "easy"}])
        + "\n```"
    )
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    content = generator.generate(context.chunks, context.graph)
    parsed_body = json.loads(content.body)
    assert len(parsed_body) == 1
    assert parsed_body[0]["question"] == "Q1"


def test_malformed_json() -> None:
    provider = FakeTextGenerationProvider("[{missing quotes}]")
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidFlashcardJsonError, match="malformed JSON"):
        generator.generate(context.chunks, context.graph)


def test_object_instead_of_array() -> None:
    response = json.dumps({"question": "Q1", "answer": "A1"})
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidFlashcardJsonError, match="instead of an array"):
        generator.generate(context.chunks, context.graph)


def test_duplicate_questions() -> None:
    response = json.dumps(
        [
            {"question": "What is AI?", "answer": "A field."},
            {"question": "what is ai?", "answer": "Artificial intelligence."},
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidFlashcardError, match="Duplicate question"):
        generator.generate(context.chunks, context.graph)


def test_invalid_difficulty() -> None:
    response = json.dumps([{"question": "Q1", "answer": "A1", "difficulty": "extreme"}])
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidFlashcardError, match="Invalid difficulty"):
        generator.generate(context.chunks, context.graph)


def test_missing_fields() -> None:
    response = json.dumps([{"question": "Q1"}])
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidFlashcardError, match="missing a valid 'answer'"):
        generator.generate(context.chunks, context.graph)


def test_identical_qa() -> None:
    response = json.dumps([{"question": "Hello", "answer": "hello", "difficulty": "easy"}])
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidFlashcardError, match="identical to the question"):
        generator.generate(context.chunks, context.graph)


def test_unicode_support() -> None:
    response = json.dumps([{"question": "こんにちは", "answer": "世界 🌍", "difficulty": "easy"}])
    provider = FakeTextGenerationProvider(response)
    generator = FlashcardsGenerator(provider)
    context = create_sample_context()

    content = generator.generate(context.chunks, context.graph)
    parsed_body = json.loads(content.body)
    assert parsed_body[0]["answer"] == "世界 🌍"

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
from learning_content.generators.quiz.exceptions import (
    InvalidQuizJsonError,
    InvalidQuizQuestionError,
)
from learning_content.generators.quiz.generator import QuizGenerator
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
    generator = QuizGenerator(provider)
    assert generator.info().generator_id == "quiz-generator-v1"
    assert generator.info().supported_content_types == (ContentType.QUIZ,)


def test_successful_json_parsing() -> None:
    response = json.dumps(
        [
            {
                "question": "What is gradient descent?",
                "options": ["Algorithm", "Data", "Model", "Layer"],
                "correct_answer": "Algorithm",
                "explanation": "It minimizes loss.",
                "difficulty": "medium",
            }
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    content = generator.generate(context.chunks, context.graph)

    assert content.content_type == ContentType.QUIZ
    assert "Quiz" in content.title

    parsed_body = json.loads(content.body)
    assert len(parsed_body) == 1
    assert parsed_body[0]["difficulty"] == "medium"
    assert len(parsed_body[0]["options"]) == 4


def test_fenced_json_parsing() -> None:
    response = (
        "```json\n"
        + json.dumps(
            [
                {
                    "question": "Q1",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Exp",
                    "difficulty": "easy",
                }
            ]
        )
        + "\n```"
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    content = generator.generate(context.chunks, context.graph)
    parsed_body = json.loads(content.body)
    assert len(parsed_body) == 1
    assert parsed_body[0]["question"] == "Q1"


def test_malformed_json() -> None:
    provider = FakeTextGenerationProvider("[{missing quotes}]")
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizJsonError, match="malformed JSON"):
        generator.generate(context.chunks, context.graph)


def test_object_instead_of_array() -> None:
    response = json.dumps({"question": "Q1"})
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizJsonError, match="instead of an array"):
        generator.generate(context.chunks, context.graph)


def test_fewer_than_four_options() -> None:
    response = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "B", "C"],
                "correct_answer": "A",
                "explanation": "Exp",
            }
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="exactly four options"):
        generator.generate(context.chunks, context.graph)


def test_duplicate_options() -> None:
    response = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "A", "C", "D"],
                "correct_answer": "A",
                "explanation": "Exp",
            }
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="options must be unique"):
        generator.generate(context.chunks, context.graph)


def test_duplicate_questions() -> None:
    response = json.dumps(
        [
            {
                "question": "What is AI?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Exp1",
            },
            {
                "question": "what is ai?",
                "options": ["E", "F", "G", "H"],
                "correct_answer": "E",
                "explanation": "Exp2",
            },
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="Duplicate question"):
        generator.generate(context.chunks, context.graph)


def test_invalid_correct_answer() -> None:
    response = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "E",
                "explanation": "Exp",
            }
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="must match one of the options"):
        generator.generate(context.chunks, context.graph)


def test_invalid_difficulty() -> None:
    response = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Exp",
                "difficulty": "extreme",
            }
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="Invalid difficulty"):
        generator.generate(context.chunks, context.graph)


def test_missing_explanation() -> None:
    response = json.dumps(
        [{"question": "Q1", "options": ["A", "B", "C", "D"], "correct_answer": "A"}]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="missing a valid 'explanation'"):
        generator.generate(context.chunks, context.graph)


def test_explanation_identical_to_answer() -> None:
    response = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "a",
            }
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="identical to the correct answer"):
        generator.generate(context.chunks, context.graph)


def test_duplicate_explanation() -> None:
    response = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because it is true.",
            },
            {
                "question": "Q2",
                "options": ["E", "F", "G", "H"],
                "correct_answer": "E",
                "explanation": "because it is true.",
            },
        ]
    )
    provider = FakeTextGenerationProvider(response)
    generator = QuizGenerator(provider)
    context = create_sample_context()

    with pytest.raises(InvalidQuizQuestionError, match="Duplicate explanation"):
        generator.generate(context.chunks, context.graph)

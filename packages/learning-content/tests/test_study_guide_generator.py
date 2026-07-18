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
from learning_content.generators.explanation.generator import ExplanationGenerator
from learning_content.generators.flashcards.generator import FlashcardsGenerator
from learning_content.generators.notes.generator import NotesGenerator
from learning_content.generators.quiz.generator import QuizGenerator
from learning_content.generators.study_guide.composer import StudyGuideComposer
from learning_content.generators.study_guide.exceptions import (
    CompositionError,
    StudyGuideGenerationError,
)
from learning_content.generators.study_guide.generator import StudyGuideGenerator
from learning_content.generators.summary.generator import SummaryGenerator
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
                title="Test",
                description="Test",
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


@pytest.fixture
def study_guide_generator() -> StudyGuideGenerator:
    summary_provider = MockProvider("This is a summary.")
    notes_provider = MockProvider("# Note 1\nNote text.")

    flashcards_json = json.dumps([{"question": "Q1", "answer": "A1", "difficulty": "easy"}])
    flashcards_provider = MockProvider(flashcards_json)

    quiz_json = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Exp",
                "difficulty": "medium",
            }
        ]
    )
    quiz_provider = MockProvider(quiz_json)

    explanation_markdown = (
        "# Concept\n## Why It Matters\n## Intuition\n## Detailed Explanation\n"
        "## Example\n## Common Mistakes\n## Related Concepts\n## Key Takeaways\n"
    )
    explanation_provider = MockProvider(explanation_markdown)

    return StudyGuideGenerator(
        summary_generator=SummaryGenerator(summary_provider),
        notes_generator=NotesGenerator(notes_provider),
        flashcards_generator=FlashcardsGenerator(flashcards_provider),
        quiz_generator=QuizGenerator(quiz_provider),
        explanation_generator=ExplanationGenerator(explanation_provider),
    )


def test_study_guide_orchestration(study_guide_generator: StudyGuideGenerator) -> None:
    context = create_sample_context()
    content = study_guide_generator.generate(context.chunks, context.graph)

    assert content.content_type == ContentType.STUDY_GUIDE
    assert "Comprehensive Study Guide" in content.title

    body = content.body
    # Ensure correct deterministic rendering order
    assert "# Summary" in body
    assert "# Notes" in body
    assert "# Explanation" in body
    assert "# Flashcards" in body
    assert "# Quiz" in body

    # Check flashcard rendering
    assert "**Question:**\nQ1" in body
    assert "**Answer:**\nA1" in body

    # Check quiz rendering
    assert "**Question 1:**\nQ1" in body
    assert "A. A" in body

    # Check aggregated metadata
    assert content.metadata.provider == "mock"
    assert "summary-v1" in content.metadata.prompt_version
    assert "quiz-v1" in content.metadata.prompt_version


def test_study_guide_failure() -> None:
    summary_provider = MockProvider("This is a summary.", fail=True)
    notes_provider = MockProvider("# Note 1\nNote text.")

    flashcards_json = json.dumps([{"question": "Q1", "answer": "A1", "difficulty": "easy"}])
    flashcards_provider = MockProvider(flashcards_json)

    quiz_json = json.dumps(
        [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Exp",
                "difficulty": "medium",
            }
        ]
    )
    quiz_provider = MockProvider(quiz_json)

    explanation_markdown = (
        "# Concept\n## Why It Matters\n## Intuition\n## Detailed Explanation\n"
        "## Example\n## Common Mistakes\n## Related Concepts\n## Key Takeaways\n"
    )
    explanation_provider = MockProvider(explanation_markdown)

    sg_generator = StudyGuideGenerator(
        summary_generator=SummaryGenerator(summary_provider),
        notes_generator=NotesGenerator(notes_provider),
        flashcards_generator=FlashcardsGenerator(flashcards_provider),
        quiz_generator=QuizGenerator(quiz_provider),
        explanation_generator=ExplanationGenerator(explanation_provider),
    )

    context = create_sample_context()

    with pytest.raises(StudyGuideGenerationError, match="Failed to generate study guide"):
        sg_generator.generate(context.chunks, context.graph)


def test_composer_empty_rejection() -> None:
    composer = StudyGuideComposer()
    with pytest.raises(CompositionError, match="empty sequence"):
        composer.compose("Title", [])

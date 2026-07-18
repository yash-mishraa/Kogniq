import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "shared" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "content" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "learning-content" / "src"))

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata

from content.chunking import Chunk, ChunkCollection, ChunkMetadata, ChunkStatistics
from learning_content.generators.explanation.generator import ExplanationGenerator
from learning_content.generators.flashcards.generator import FlashcardsGenerator
from learning_content.generators.notes.generator import NotesGenerator
from learning_content.generators.quiz.generator import QuizGenerator
from learning_content.generators.study_guide.generator import StudyGuideGenerator
from learning_content.generators.summary.generator import SummaryGenerator
from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class MockProvider(AbstractTextGenerationProvider):
    def __init__(self, response: str) -> None:
        self._response = response

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
        _ = (prompt, kwargs)
        return self._response


if __name__ == "__main__":
    print("============================================================")
    print("Study Guide Composer Demo")
    print("============================================================")

    # 1. Instantiate the generators with mocked providers for the demo
    summary_provider = MockProvider("Gradient descent minimizes the loss function iteratively.")
    notes_provider = MockProvider(
        "# Gradient Descent Notes\n- Iterative optimization\n- Stepping towards minimum loss"
    )

    flashcards_json = json.dumps(
        [
            {
                "question": "What does gradient descent minimize?",
                "answer": "The loss function.",
                "difficulty": "easy",
            }
        ]
    )
    flashcards_provider = MockProvider(flashcards_json)

    quiz_json = json.dumps(
        [
            {
                "question": "Which of these is minimized by gradient descent?",
                "options": ["Accuracy", "Loss", "Data", "Epochs"],
                "correct_answer": "Loss",
                "explanation": "Gradient descent computes the gradient of the loss.",
                "difficulty": "medium",
            }
        ]
    )
    quiz_provider = MockProvider(quiz_json)

    explanation_markdown = (
        "# Concept\nGradient Descent.\n## Why It Matters\nIt trains neural networks.\n"
        "## Intuition\nWalking down a hill.\n## Detailed Explanation\nIt calculates derivatives.\n"
        "## Example\nLinear regression.\n## Common Mistakes\nHigh learning rate.\n"
        "## Related Concepts\nBackpropagation.\n## Key Takeaways\n- Minimizes loss.\n"
    )
    explanation_provider = MockProvider(explanation_markdown)

    study_guide_gen = StudyGuideGenerator(
        summary_generator=SummaryGenerator(summary_provider),
        notes_generator=NotesGenerator(notes_provider),
        flashcards_generator=FlashcardsGenerator(flashcards_provider),
        quiz_generator=QuizGenerator(quiz_provider),
        explanation_generator=ExplanationGenerator(explanation_provider),
    )

    chunks = ChunkCollection(
        chunks=(
            Chunk(
                id="chunk-1",
                document_id="ml-intro",
                chunk_index=0,
                text="Gradient descent minimizes the loss.",
                metadata=ChunkMetadata(
                    processor="txt", document_version="1", source="demo", checksum="123"
                ),
                statistics=ChunkStatistics(
                    character_count=70,
                    line_count=1,
                    word_count=10,
                    estimated_tokens=13,
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
                    source_document="ml-intro",
                    source_chunk="chunk-1",
                    language="en",
                    confidence=1.0,
                    extraction_version="1.0",
                    created_by="demo",
                ),
            ),
        ),
        relationships=(),
    )

    print("\n[1] Composing Study Guide...")
    start = time.perf_counter()
    content = study_guide_gen.generate(chunks, graph)
    end = time.perf_counter()

    print(f"\n[2] Generation Complete in {end - start:.2f}s!")
    print(f"Title: {content.title}")

    print(
        f"Metadata: Provider={content.metadata.provider}, "
        f"PromptVersions={content.metadata.prompt_version}"
    )

    stats = content.statistics
    print(f"Statistics: Words={stats.word_count}, Sections={stats.heading_count}")

    print("\n[3] Generated Study Guide:\n")
    print(content.body)

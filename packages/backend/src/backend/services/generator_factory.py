from unittest.mock import MagicMock

from backend.core.exceptions import BackendError

from learning_content.generators.explanation.generator import ExplanationGenerator
from learning_content.generators.flashcards.generator import FlashcardsGenerator
from learning_content.generators.notes.generator import NotesGenerator
from learning_content.generators.quiz.generator import QuizGenerator
from learning_content.generators.study_guide.generator import StudyGuideGenerator
from learning_content.generators.summary.generator import SummaryGenerator
from learning_content.providers.base import AbstractTextGenerationProvider
from learning_content.providers.interfaces import AbstractLearningGenerator


class GeneratorFactory:
    """
    Constructs and resolves requested learning generators.
    Injects providers natively.
    """

    def __init__(self) -> None:
        # Tomorrow this will be injected or resolved via app settings.
        # Today we construct a mock provider to satisfy the tests and demo.
        self._provider = self._create_mock_provider()

    def _create_mock_provider(self) -> AbstractTextGenerationProvider:
        provider = MagicMock(spec=AbstractTextGenerationProvider)

        from learning_content.providers.base import TextGenerationProviderInfo

        provider.info = TextGenerationProviderInfo(
            provider_id="mock-provider",
            provider_name="Mock Provider",
            default_model="mock-model-v1",
            model_version="1.0",
            context_window=16000,
            supports_streaming=False,
        )

        def mock_generate(prompt: str) -> str:
            lower = prompt.lower()
            if "flashcard" in lower:
                return '[{"question": "Q", "answer": "A"}]'
            elif "multiple-choice" in lower or "quiz" in lower:
                return (
                    '[{"question": "Q", "options": ["A", "B", "C", "D"], '
                    '"correct_answer": "A", "explanation": "E"}]'
                )
            elif "concept" in lower or "intuition" in lower or "explanation" in lower:
                return """# Concept
## Why It Matters
## Intuition
## Detailed Explanation
## Example
## Common Mistakes
## Related Concepts
## Key Takeaways"""
            return '{"title": "Fake Title", "content": "Fake content"}'

        provider.generate.side_effect = mock_generate
        return provider

    def get_generator(self, generator_name: str) -> AbstractLearningGenerator:
        """
        Resolves the generator by name, constructing it with its dependencies.
        """
        name = generator_name.lower()

        if name == "summary":
            return SummaryGenerator(self._provider)
        elif name == "notes":
            return NotesGenerator(self._provider)
        elif name == "flashcards":
            return FlashcardsGenerator(self._provider)
        elif name == "quiz":
            return QuizGenerator(self._provider)
        elif name == "explanation":
            return ExplanationGenerator(self._provider)
        elif name == "study_guide":
            # Composition engine requires all other generators
            return StudyGuideGenerator(
                summary_generator=SummaryGenerator(self._provider),
                notes_generator=NotesGenerator(self._provider),
                flashcards_generator=FlashcardsGenerator(self._provider),
                quiz_generator=QuizGenerator(self._provider),
                explanation_generator=ExplanationGenerator(self._provider),
            )

        raise BackendError(
            "unsupported_generator",
            f"Generator '{generator_name}' is not supported.",
            status_code=400,
        )

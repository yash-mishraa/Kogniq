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

    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        self._provider = provider

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
            return StudyGuideGenerator(self._provider)

        raise BackendError(
            "unsupported_generator",
            f"Generator '{generator_name}' is not supported.",
            status_code=400,
        )

from learning_content.generators.base import LearningGenerationError


class FlashcardGenerationError(LearningGenerationError):
    """Base exception for flashcard generation failures."""


class InvalidFlashcardError(FlashcardGenerationError):
    """Raised when a parsed flashcard fails domain validation (e.g. empty answer)."""


class InvalidFlashcardJsonError(FlashcardGenerationError):
    """Raised when the provider fails to return valid, parsable JSON."""

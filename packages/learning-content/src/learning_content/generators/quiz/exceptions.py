from learning_content.generators.base import LearningGenerationError


class QuizGenerationError(LearningGenerationError):
    """Base exception for quiz generation failures."""


class InvalidQuizQuestionError(QuizGenerationError):
    """Raised when a parsed quiz question fails domain validation."""


class InvalidQuizJsonError(QuizGenerationError):
    """Raised when the provider fails to return valid, parsable JSON."""

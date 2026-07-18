from learning_content.generators.base import LearningGenerationError


class ExplanationGenerationError(LearningGenerationError):
    """Base exception for explanation generation failures."""


class InvalidExplanationError(ExplanationGenerationError):
    """Raised when the generated explanation fails parser validation."""

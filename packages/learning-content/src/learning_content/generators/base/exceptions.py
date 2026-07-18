from learning_content.exceptions import LearningContentError


class LearningGenerationError(LearningContentError):
    """Base exception for all generation-related errors."""


class PromptBuildingError(LearningGenerationError):
    """Raised when the PromptBuilder fails to construct a valid prompt."""


class ParsingError(LearningGenerationError):
    """Raised when the Parser fails to parse the provider's response."""

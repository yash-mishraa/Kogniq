from learning_content.exceptions import LearningContentError


class SummaryGenerationError(LearningContentError):
    """Raised when summary generation fails for any reason."""

class EmptyResponseError(SummaryGenerationError):
    """Raised when the text generation provider returns an empty or whitespace-only response."""

class LearningContentError(Exception):
    """Base exception for learning content errors."""

class InvalidLearningContentError(LearningContentError):
    """Raised when learning content fails validation."""

class GenerationConfigurationError(LearningContentError):
    """Raised when generator configuration is invalid."""

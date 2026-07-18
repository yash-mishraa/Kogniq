from learning_content.exceptions import LearningContentError


class StudyGuideGenerationError(LearningContentError):
    """Base exception for study guide generation failures."""


class CompositionError(StudyGuideGenerationError):
    """Raised when the composer fails to assemble the study guide correctly."""

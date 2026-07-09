class LearningDomainError(Exception):
    """Base exception for all learning domain errors."""


class CyclicPrerequisiteError(LearningDomainError):
    """Raised when adding a prerequisite would create a cycle."""


class InvalidQuestionEvaluationError(LearningDomainError):
    """Raised when a question is created without evaluating any learning objective."""

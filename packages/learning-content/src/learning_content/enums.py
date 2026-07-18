from enum import Enum, auto


class ContentType(Enum):
    """Types of educational content that can be generated."""

    SUMMARY = auto()
    NOTES = auto()
    FLASHCARDS = auto()
    QUIZ = auto()
    EXPLANATION = auto()
    STUDY_GUIDE = auto()

from enum import Enum, auto


class ConceptType(Enum):
    """Core pedagogical type of the concept."""

    THEORETICAL = auto()
    PRACTICAL = auto()
    FACTUAL = auto()
    PROCEDURAL = auto()


class RelationshipType(Enum):
    """Defines how two educational entities relate."""

    PREREQUISITE = auto()
    DEPENDS_ON = auto()
    EXPLAINS = auto()
    EXTENDS = auto()
    USES = auto()
    SIMILAR_TO = auto()
    CONTRADICTS = auto()
    REFERENCES = auto()


class ExerciseType(Enum):
    """Type of educational exercise or assessment."""

    MULTIPLE_CHOICE = auto()
    SHORT_ANSWER = auto()
    NUMERICAL = auto()
    MATCHING = auto()


class DifficultyBand(Enum):
    """Broad classification of difficulty."""

    BEGINNER = auto()
    INTERMEDIATE = auto()
    ADVANCED = auto()
    EXPERT = auto()

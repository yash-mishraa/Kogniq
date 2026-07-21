from enum import Enum, auto


class ConceptType(Enum):
    """Types of educational concepts."""

    DEFINITION = auto()
    ALGORITHM = auto()
    FORMULA = auto()
    DATA_STRUCTURE = auto()
    THEORY = auto()
    EXAMPLE = auto()
    EXERCISE = auto()
    FACT = auto()
    PRINCIPLE = auto()
    UNKNOWN = auto()


class RelationshipType(Enum):
    """Types of relationships between educational concepts."""

    DEPENDS_ON = auto()
    USES = auto()
    DEFINES = auto()
    REFERENCES = auto()
    EXTENDS = auto()
    IMPLEMENTS = auto()
    EXPLAINS = auto()
    RELATED_TO = auto()

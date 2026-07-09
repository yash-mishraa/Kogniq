from dataclasses import dataclass, field

from .enums import ConceptType, ExerciseType
from .exceptions import InvalidConceptError, validate_not_empty
from .value_objects import DifficultyLevel, EducationalMetadata, ImportanceScore


@dataclass(frozen=True, kw_only=True)
class EducationalConcept:
    """Root entity modeling an independent educational idea."""

    id: str
    title: str
    concept_type: ConceptType
    description: str | None = None
    difficulty: DifficultyLevel | None = None
    importance: ImportanceScore | None = None
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.title, "title")


@dataclass(frozen=True, kw_only=True)
class EducationalDefinition:
    """A formal definition belonging to a concept."""

    id: str
    concept_id: str
    text: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.concept_id, "concept_id")
        validate_not_empty(self.text, "text")


@dataclass(frozen=True, kw_only=True)
class EducationalExample:
    """An example demonstrating a concept."""

    id: str
    concept_id: str
    content: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.concept_id, "concept_id")
        validate_not_empty(self.content, "content")


@dataclass(frozen=True, kw_only=True)
class EducationalExercise:
    """An assessment or practice exercise."""

    id: str
    concept_ids: tuple[str, ...]
    exercise_type: ExerciseType
    content: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.content, "content")
        if not self.concept_ids:
            raise InvalidConceptError("Exercises must reference at least one concept.")


@dataclass(frozen=True, kw_only=True)
class EducationalObjective:
    """A learning goal referencing concepts."""

    id: str
    concept_ids: tuple[str, ...]
    description: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.description, "description")
        if not self.concept_ids:
            raise InvalidConceptError("Objectives must reference at least one concept.")


@dataclass(frozen=True, kw_only=True)
class EducationalFormula:
    """A mathematical or scientific formula."""

    id: str
    concept_id: str
    latex_content: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.concept_id, "concept_id")
        validate_not_empty(self.latex_content, "latex_content")


@dataclass(frozen=True, kw_only=True)
class EducationalDiagram:
    """A visual diagram representing a concept."""

    id: str
    concept_id: str
    description: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.concept_id, "concept_id")


@dataclass(frozen=True, kw_only=True)
class EducationalTable:
    """Structured tabular data for a concept."""

    id: str
    concept_id: str
    content: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.concept_id, "concept_id")


@dataclass(frozen=True, kw_only=True)
class EducationalHint:
    """A hint associated with an exercise or concept."""

    id: str
    target_id: str
    content: str
    metadata: EducationalMetadata = field(default_factory=EducationalMetadata)

    def __post_init__(self) -> None:
        validate_not_empty(self.id, "id")
        validate_not_empty(self.target_id, "target_id")
        validate_not_empty(self.content, "content")

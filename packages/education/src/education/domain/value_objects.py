from dataclasses import dataclass, field

from .enums import DifficultyBand
from .exceptions import InvalidConceptError


@dataclass(frozen=True, kw_only=True)
class DifficultyLevel:
    """Wrapper for difficulty band and continuous score."""

    band: DifficultyBand
    score: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise InvalidConceptError("Difficulty score must be between 0.0 and 1.0.")


@dataclass(frozen=True, kw_only=True)
class ImportanceScore:
    """Topic weighting and importance."""

    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 1.0):
            raise InvalidConceptError("Importance score must be between 0.0 and 1.0.")


@dataclass(frozen=True, kw_only=True)
class ConfidenceScore:
    """Extraction or AI certainty."""

    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 1.0):
            raise InvalidConceptError("Confidence score must be between 0.0 and 1.0.")


@dataclass(frozen=True, kw_only=True)
class EducationalMetadata:
    """Generic source references for educational objects."""

    attributes: dict[str, str] = field(default_factory=dict)

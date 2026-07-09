from dataclasses import dataclass
from enum import StrEnum


class DifficultyLevel(StrEnum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


@dataclass(frozen=True)
class Difficulty:
    """
    Represents the difficulty of a learning resource, concept, or question.
    Encapsulates both a qualitative level and an optional quantitative score
    (e.g., item response theory parameter).
    """

    level: DifficultyLevel
    score: float | None = None

    def __post_init__(self) -> None:
        if self.score is not None and (self.score < 0.0 or self.score > 100.0):
            raise ValueError("Difficulty score must be between 0.0 and 100.0 if provided.")

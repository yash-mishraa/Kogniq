import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class FlashcardDifficulty(Enum):
    """The difficulty level of a flashcard."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True, kw_only=True)
class Flashcard:
    """An immutable study flashcard."""

    id: str
    question: str
    answer: str
    difficulty: FlashcardDifficulty
    tags: tuple[str, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.question or not self.question.strip():
            raise ValueError("Flashcard question cannot be empty.")
        if not self.answer or not self.answer.strip():
            raise ValueError("Flashcard answer cannot be empty.")
        if self.question.strip().lower() == self.answer.strip().lower():
            raise ValueError("Flashcard answer cannot be identical to the question.")


@dataclass(frozen=True, kw_only=True)
class FlashcardCollection:
    """An immutable collection of flashcards."""

    flashcards: tuple[Flashcard, ...]

    @property
    def total_flashcards(self) -> int:
        return len(self.flashcards)

    @property
    def total_questions(self) -> int:
        # Currently identical to total_flashcards, but could diverge if
        # cards have multiple questions
        return len(self.flashcards)

    def to_json(self) -> str:
        """Serialize the collection to a canonical JSON string."""

        class EnumEncoder(json.JSONEncoder):
            def default(self, obj: Any) -> Any:
                if isinstance(obj, Enum):
                    return obj.value
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        return json.dumps([asdict(c) for c in self.flashcards], cls=EnumEncoder, indent=2)

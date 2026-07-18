import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from learning_content.content import LearningContent


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


@dataclass(frozen=True, kw_only=True)
class QuizOption:
    """An immutable quiz option."""

    id: str
    text: str


@dataclass(frozen=True, kw_only=True)
class QuizQuestion:
    """An immutable multiple-choice quiz question."""

    id: str
    question: str
    options: tuple[QuizOption, ...]
    correct_answer: str
    explanation: str
    difficulty: FlashcardDifficulty
    tags: tuple[str, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.question or not self.question.strip():
            raise ValueError("Quiz question cannot be empty.")
        if len(self.options) != 4:
            raise ValueError("Quiz question must have exactly four options.")

        option_texts = [opt.text.strip().lower() for opt in self.options]
        if len(set(option_texts)) != 4:
            raise ValueError("Quiz question options must be unique.")

        if not self.correct_answer or not self.correct_answer.strip():
            raise ValueError("Quiz correct answer cannot be empty.")

        correct_lower = self.correct_answer.strip().lower()
        if correct_lower not in option_texts:
            raise ValueError("Quiz correct answer must match one of the options.")

        if not self.explanation or not self.explanation.strip():
            raise ValueError("Quiz explanation cannot be empty.")

        if self.explanation.strip().lower() == correct_lower:
            raise ValueError("Quiz explanation cannot be identical to the correct answer.")


@dataclass(frozen=True, kw_only=True)
class QuizCollection:
    """An immutable collection of quiz questions."""

    questions: tuple[QuizQuestion, ...]

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def total_options(self) -> int:
        return sum(len(q.options) for q in self.questions)

    def to_json(self) -> str:
        """Serialize the collection to a canonical JSON string."""

        class EnumEncoder(json.JSONEncoder):
            def default(self, obj: Any) -> Any:
                if isinstance(obj, Enum):
                    return obj.value
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        return json.dumps([asdict(q) for q in self.questions], cls=EnumEncoder, indent=2)


@dataclass(frozen=True, kw_only=True)
class StudyGuideSection:
    """An immutable section of a study guide."""

    id: str
    title: str
    content: LearningContent
    order: int

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("StudyGuideSection title cannot be empty.")
        if self.order < 0:
            raise ValueError("StudyGuideSection order cannot be negative.")


@dataclass(frozen=True, kw_only=True)
class StudyGuide:
    """An immutable study guide composed of multiple sections."""

    id: str
    title: str
    sections: tuple[StudyGuideSection, ...]
    created_at: datetime

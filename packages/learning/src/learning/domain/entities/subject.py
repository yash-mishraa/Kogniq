from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import AIMetadata, SubjectId, generate_id


@dataclass
class Subject:
    """
    Root entity representing a broad area of study (e.g., Computer Science).
    """

    name: str
    description: str
    id: SubjectId = field(default_factory=lambda: SubjectId(generate_id()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Subject name cannot be empty.")

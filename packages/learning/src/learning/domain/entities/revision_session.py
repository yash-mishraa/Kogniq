from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import AIMetadata, ConceptId, RevisionSessionId, generate_id


@dataclass
class RevisionSession:
    """
    Domain concept for tracking a student's study or spaced-repetition session.
    """

    student_id: str  # Kept generic as str/uuid depending on Student domain contract
    id: RevisionSessionId = field(default_factory=lambda: RevisionSessionId(generate_id()))
    target_concept_ids: list[ConceptId] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

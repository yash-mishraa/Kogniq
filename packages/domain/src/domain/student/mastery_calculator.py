from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from domain.analytics.models import (
    FlashcardReviewedEvent,
    LearnerEvent,
    QuizCompletedEvent,
)
from domain.student.entities import KnowledgeState


def calculate_mastery(events: Sequence[LearnerEvent], user_id: str, resource_id: str) -> KnowledgeState | None:
    """
    Calculates deterministic mastery score for a user and resource based on historical evidence.
    Returns None if no events exist.
    """
    if not events:
        return None

    evidence_scores = []
    last_reviewed_at = None

    for event in events:
        # Ignore events that do not match the target scope (just as a safeguard)
        if event.user_id != user_id or event.document_id != resource_id:
            continue

        timestamp = event.occurred_at or event.created_at
        
        # Track last review date for any event (even progress events) to show recent activity?
        # The prompt says: last_reviewed_at: The maximum occurred_at (or created_at) of the incorporated evidence events.
        
        score: float | None = None
        
        if isinstance(event, QuizCompletedEvent):
            if event.total_questions > 0:
                score = event.score / event.total_questions
        elif isinstance(event, FlashcardReviewedEvent):
            if event.difficulty == "easy":
                score = 1.0
            elif event.difficulty == "good":
                score = 0.75
            elif event.difficulty == "hard":
                score = 0.25
            elif event.difficulty == "again":
                score = 0.0

        if score is not None:
            evidence_scores.append(max(0.0, min(1.0, score)))
            if last_reviewed_at is None or timestamp > last_reviewed_at:
                last_reviewed_at = timestamp

    # If there is no evidence (e.g. only resource_viewed events), what should mastery be?
    # Prompt: "Initial Score: If no valid evidence events exist, mastery_score evaluates to 0.0."
    review_count = len(evidence_scores)
    mastery_score = sum(evidence_scores) / review_count if review_count > 0 else 0.0
    
    from domain.student.srs_policy import calculate_next_review_due
    next_review_due = calculate_next_review_due(
        mastery_score=mastery_score,
        review_count=review_count,
        last_reviewed_at=last_reviewed_at
    )

    now = datetime.now(UTC)
    return KnowledgeState(
        id=f"ks-{user_id}-{resource_id}",
        user_id=user_id,
        resource_id=resource_id,
        mastery_score=mastery_score,
        created_at=now,
        updated_at=now,
        last_reviewed_at=last_reviewed_at,
        next_review_due=next_review_due,
    )

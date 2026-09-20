from datetime import UTC, datetime

from domain.analytics.models import (
    FlashcardReviewedEvent,
    QuizCompletedEvent,
    ResourceViewedEvent,
)
from domain.student.mastery_calculator import calculate_mastery


def test_calculate_mastery_no_events() -> None:
    assert calculate_mastery([], "user-1", "doc-1") is None

def test_calculate_mastery_no_evidence() -> None:
    events = [
        ResourceViewedEvent(
            event_id="e1", user_id="user-1", document_id="doc-1", event_type="resource_viewed",
            event_data={}, created_at=datetime.now(UTC)
        )
    ]
    state = calculate_mastery(events, "user-1", "doc-1")
    assert state is not None
    assert state.mastery_score == 0.0

def test_calculate_mastery_with_evidence() -> None:
    now = datetime.now(UTC)
    events = [
        QuizCompletedEvent(
            event_id="e1", user_id="user-1", document_id="doc-1", event_type="quiz_completed",
            event_data={"score": 8, "total_questions": 10}, created_at=now
        ),
        FlashcardReviewedEvent(
            event_id="e2", user_id="user-1", document_id="doc-1", event_type="flashcard_reviewed",
            event_data={"difficulty": "hard"}, created_at=now
        ),
        FlashcardReviewedEvent(
            event_id="e3", user_id="user-1", document_id="doc-1", event_type="flashcard_reviewed",
            event_data={"difficulty": "easy"}, created_at=now
        )
    ]
    
    state = calculate_mastery(events, "user-1", "doc-1")
    assert state is not None
    
    # 0.8 + 0.25 + 1.0 = 2.05 / 3 = 0.68333...
    assert abs(state.mastery_score - 0.6833) < 0.001

def test_calculate_mastery_ignores_other_users_and_resources() -> None:
    now = datetime.now(UTC)
    events = [
        QuizCompletedEvent(
            event_id="e1", user_id="user-1", document_id="doc-1", event_type="quiz_completed",
            event_data={"score": 10, "total_questions": 10}, created_at=now
        ),
        QuizCompletedEvent(
            event_id="e2", user_id="user-2", document_id="doc-1", event_type="quiz_completed",
            event_data={"score": 5, "total_questions": 10}, created_at=now
        )
    ]
    
    state = calculate_mastery(events, "user-1", "doc-1")
    assert state is not None
    assert state.mastery_score == 1.0  # Should ignore user-2's event


def test_calculate_mastery_edge_cases() -> None:
    now = datetime.now(UTC)
    events = [
        # Score > total
        QuizCompletedEvent(
            event_id="e1", user_id="user-1", document_id="doc-1", event_type="quiz_completed",
            event_data={"score": 15, "total_questions": 10}, created_at=now
        ),
        # Negative score
        QuizCompletedEvent(
            event_id="e2", user_id="user-1", document_id="doc-1", event_type="quiz_completed",
            event_data={"score": -5, "total_questions": 10}, created_at=now
        ),
        # Missing data (defaults to 0 / 0, so should be ignored)
        QuizCompletedEvent(
            event_id="e3", user_id="user-1", document_id="doc-1", event_type="quiz_completed",
            event_data={}, created_at=now
        ),
        # Invalid difficulty (ignored)
        FlashcardReviewedEvent(
            event_id="e4", user_id="user-1", document_id="doc-1", event_type="flashcard_reviewed",
            event_data={"difficulty": "nonsense"}, created_at=now
        ),
    ]
    
    state = calculate_mastery(events, "user-1", "doc-1")
    assert state is not None
    # 1.0 (clamped from 1.5) and 0.0 (clamped from -0.5). Missing ignored, nonsense ignored.
    # Total evidence: 2 events. (1.0 + 0.0) / 2 = 0.5
    assert state.mastery_score == 0.5

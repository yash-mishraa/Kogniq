from datetime import UTC, datetime, timedelta

from content.domain.entities import LearningResource
from content.domain.enums import ProcessingStatus, ResourceType
from domain.student.entities import KnowledgeState
from domain.student.recommendations import RecommendationActionType, generate_recommendations


def test_recommendations_empty() -> None:
    now = datetime.now(UTC)
    recs = generate_recommendations([], {}, now)
    assert len(recs) == 0


def test_recommendations_new_resource() -> None:
    now = datetime.now(UTC)
    res = LearningResource(
        id="r1", title="Res 1", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk"
    )
    recs = generate_recommendations([res], {}, now)
    assert len(recs) == 1
    assert recs[0].resource_id == "r1"
    assert recs[0].action_type == RecommendationActionType.NEW_RESOURCE
    assert recs[0].priority_score == 10.0


def test_recommendations_overdue_review() -> None:
    now = datetime.now(UTC)
    res = LearningResource(
        id="r1", title="Res 1", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk"
    )
    state = KnowledgeState(
        id="ks1", user_id="u1", resource_id="r1", mastery_score=0.8, created_at=now, updated_at=now,
        last_reviewed_at=now - timedelta(days=5),
        next_review_due=now - timedelta(days=1)
    )
    
    recs = generate_recommendations([res], {"r1": state}, now)
    assert len(recs) == 1
    assert recs[0].action_type == RecommendationActionType.OVERDUE_REVIEW
    # Overdue by 1 day -> score = 101.0
    assert abs(recs[0].priority_score - 101.0) < 0.01


def test_recommendations_upcoming_review() -> None:
    now = datetime.now(UTC)
    res = LearningResource(
        id="r1", title="Res 1", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk"
    )
    state = KnowledgeState(
        id="ks1", user_id="u1", resource_id="r1", mastery_score=0.8, created_at=now, updated_at=now,
        last_reviewed_at=now,
        next_review_due=now + timedelta(days=1)
    )
    
    recs = generate_recommendations([res], {"r1": state}, now)
    assert len(recs) == 1
    assert recs[0].action_type == RecommendationActionType.UPCOMING_REVIEW
    # 1 day until -> 50.0 - 1.0 = 49.0
    assert abs(recs[0].priority_score - 49.0) < 0.01


def test_recommendations_low_mastery() -> None:
    now = datetime.now(UTC)
    res = LearningResource(
        id="r1", title="Res 1", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk"
    )
    state = KnowledgeState(
        id="ks1", user_id="u1", resource_id="r1", mastery_score=0.3, created_at=now, updated_at=now,
        last_reviewed_at=now,
        next_review_due=now + timedelta(days=10) # Not upcoming
    )
    
    recs = generate_recommendations([res], {"r1": state}, now)
    assert len(recs) == 1
    assert recs[0].action_type == RecommendationActionType.LOW_MASTERY
    # 40.0 + (0.5 - 0.3)*10 = 42.0
    assert abs(recs[0].priority_score - 42.0) < 0.01


def test_recommendations_sorting() -> None:
    now = datetime.now(UTC)
    r1 = LearningResource(id="r1", title="A", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk")
    r2 = LearningResource(id="r2", title="B", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk")
    r3 = LearningResource(id="r3", title="C", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk")
    r4 = LearningResource(id="r4", title="D", resource_type=ResourceType.DOCUMENT, source="src", checksum="chk")
    
    # r1 -> low mastery (score 42.0)
    ks1 = KnowledgeState(id="ks1", user_id="u1", resource_id="r1", mastery_score=0.3, created_at=now, updated_at=now, next_review_due=now + timedelta(days=10))
    # r2 -> upcoming (score 49.0)
    ks2 = KnowledgeState(id="ks2", user_id="u1", resource_id="r2", mastery_score=0.8, created_at=now, updated_at=now, next_review_due=now + timedelta(days=1))
    # r3 -> overdue (score 102.0)
    ks3 = KnowledgeState(id="ks3", user_id="u1", resource_id="r3", mastery_score=0.8, created_at=now, updated_at=now, next_review_due=now - timedelta(days=2))
    # r4 -> new (score 10.0)
    
    recs = generate_recommendations([r1, r2, r3, r4], {"r1": ks1, "r2": ks2, "r3": ks3}, now)
    
    assert len(recs) == 4
    # Expected order: Overdue (r3), Upcoming (r2), Low Mastery (r1), New (r4)
    assert recs[0].resource_id == "r3"
    assert recs[1].resource_id == "r2"
    assert recs[2].resource_id == "r1"
    assert recs[3].resource_id == "r4"

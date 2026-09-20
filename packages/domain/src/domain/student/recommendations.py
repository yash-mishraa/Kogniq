from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from content.domain.entities import LearningResource
from domain.student.entities import KnowledgeState


class RecommendationActionType(str, Enum):
    OVERDUE_REVIEW = "overdue_review"
    UPCOMING_REVIEW = "upcoming_review"
    LOW_MASTERY = "low_mastery"
    NEW_RESOURCE = "new_resource"


@dataclass(frozen=True)
class LearnerRecommendation:
    resource_id: str
    resource_title: str
    action_type: RecommendationActionType
    priority_score: float  # Higher is higher priority
    reason: str


def generate_recommendations(
    resources: Sequence[LearningResource],
    knowledge_states: dict[str, KnowledgeState],
    reference_time: datetime,
) -> list[LearnerRecommendation]:
    """
    Generates deterministic, rule-based recommendations for a user.
    """
    recommendations = []

    for resource in resources:
        state = knowledge_states.get(resource.id)

        if state is None:
            recommendations.append(
                LearnerRecommendation(
                    resource_id=resource.id,
                    resource_title=resource.title,
                    action_type=RecommendationActionType.NEW_RESOURCE,
                    priority_score=10.0,
                    reason="Start learning this new resource."
                )
            )
            continue

        if state.next_review_due is not None and state.next_review_due <= reference_time:
            days_overdue = (reference_time - state.next_review_due).total_seconds() / 86400.0
            recommendations.append(
                LearnerRecommendation(
                    resource_id=resource.id,
                    resource_title=resource.title,
                    action_type=RecommendationActionType.OVERDUE_REVIEW,
                    priority_score=100.0 + days_overdue,
                    reason="This review is overdue."
                )
            )
            continue
            
        if state.next_review_due is not None:
            time_until = state.next_review_due - reference_time
            time_until_days = time_until.total_seconds() / 86400.0
            if time_until_days < 2.0:
                recommendations.append(
                    LearnerRecommendation(
                        resource_id=resource.id,
                        resource_title=resource.title,
                        action_type=RecommendationActionType.UPCOMING_REVIEW,
                        priority_score=50.0 - time_until_days,
                        reason="Review coming up soon."
                    )
                )
                continue

        if state.mastery_score < 0.5:
            recommendations.append(
                LearnerRecommendation(
                    resource_id=resource.id,
                    resource_title=resource.title,
                    action_type=RecommendationActionType.LOW_MASTERY,
                    priority_score=40.0 + (0.5 - state.mastery_score) * 10,
                    reason="Improve your low mastery score."
                )
            )
            continue

    recommendations.sort(key=lambda r: (-r.priority_score, r.resource_title, r.resource_id))
    
    return recommendations

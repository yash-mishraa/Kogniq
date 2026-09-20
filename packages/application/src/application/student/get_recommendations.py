from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from backend.services.auth_service import AuthenticationService
from persistence.uow_factory import AbstractUnitOfWorkFactory
from domain.student.recommendations import LearnerRecommendation, generate_recommendations


@dataclass(frozen=True)
class GetRecommendationsRequest:
    token: str
    limit: int = 5


@dataclass(frozen=True)
class GetRecommendationsResponse:
    recommendations: Sequence[LearnerRecommendation]


class GetRecommendationsUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: GetRecommendationsRequest) -> GetRecommendationsResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError
            raise SessionExpiredError("Invalid session")

        user_id = session.user_id

        with self.uow_factory.create() as uow:
            # Load resources available to user
            # Hard limit of 100 to avoid unbounded scans for the baseline
            resources = await uow.learning_resources.list(user_id=user_id, limit=100)
            
            # Load KnowledgeStates
            states = await uow.knowledge_states.list_by_user(user_id=user_id)
            state_map = {s.resource_id: s for s in states}
            
            # Generate recommendations deterministically
            now = datetime.now(UTC)
            all_recs = generate_recommendations(resources, state_map, now)
            
            # Limit results
            limited_recs = all_recs[:request.limit]
            
        return GetRecommendationsResponse(recommendations=limited_recs)

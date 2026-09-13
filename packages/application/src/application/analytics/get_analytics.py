from dataclasses import dataclass

from backend.services.auth_service import AuthenticationService
from domain.analytics.models import AnalyticsMetrics
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class GetAnalyticsRequest:
    time_range: str
    token: str

@dataclass(frozen=True)
class GetAnalyticsResponse:
    metrics: AnalyticsMetrics

class GetAnalyticsUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: GetAnalyticsRequest) -> GetAnalyticsResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError
            raise SessionExpiredError("Invalid session")

        user_id = session.user_id
        days = None
        if request.time_range == "7d":
            days = 7
        elif request.time_range == "30d":
            days = 30
        elif request.time_range == "all":
            days = None
        else:
            raise ValueError(f"Invalid time range: {request.time_range}")

        with self.uow_factory.create() as uow:
            metrics = await uow.analytics.get_metrics(user_id=user_id, days=days)

        return GetAnalyticsResponse(metrics=metrics)

from dataclasses import dataclass

from backend.services.auth_service import AuthenticationService
from domain.analytics.models import AnalyticsMetrics
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class GetAnalyticsRequest:
    time_range: str
    token: str
    document_id: str | None = None


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

        # Authorize document_id if provided
        with self.uow_factory.create() as uow:
            if request.document_id:
                from backend.core.exceptions import BackendError

                doc = await uow.documents.get(request.document_id)
                if not doc:
                    raise BackendError("not_found", "Document not found", status_code=404)
                if doc.user_id and doc.user_id != user_id:
                    raise BackendError("unauthorized", "Not authorized", status_code=403)

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
            metrics = await uow.analytics.get_metrics(
                user_id=user_id, days=days, document_id=request.document_id
            )

        return GetAnalyticsResponse(metrics=metrics)

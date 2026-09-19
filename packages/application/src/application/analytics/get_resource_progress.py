from dataclasses import dataclass
from typing import Any

from backend.core.exceptions import BackendError
from backend.services.auth_service import AuthenticationService
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass
class GetResourceProgressRequest:
    token: str
    resource_id: str

class GetResourceProgressUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: GetResourceProgressRequest) -> dict[str, Any]:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError
            raise SessionExpiredError("Invalid session")

        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.resource_id)
            if not doc:
                raise BackendError("not_found", "Resource not found", status_code=404)
            if doc.user_id and doc.user_id != session.user_id:
                raise BackendError("unauthorized", "Not authorized to access this resource", status_code=403)
            
            return await uow.analytics.get_resource_progress(session.user_id, request.resource_id)

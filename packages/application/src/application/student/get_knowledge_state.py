from dataclasses import dataclass

from backend.services.auth_service import AuthenticationService
from domain.student.entities import KnowledgeState
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class GetKnowledgeStateRequest:
    token: str
    resource_id: str


@dataclass(frozen=True)
class GetKnowledgeStateResponse:
    state: KnowledgeState | None


class GetKnowledgeStateUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: GetKnowledgeStateRequest) -> GetKnowledgeStateResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError
            raise SessionExpiredError("Invalid session")

        user_id = session.user_id

        with self.uow_factory.create() as uow:
            state = await uow.knowledge_states.get(user_id=user_id, resource_id=request.resource_id)

        return GetKnowledgeStateResponse(state=state)

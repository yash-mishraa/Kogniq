from collections.abc import Sequence
from dataclasses import dataclass

from backend.services.auth_service import AuthenticationService
from domain.student.entities import KnowledgeState
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class ListKnowledgeStatesRequest:
    token: str


@dataclass(frozen=True)
class ListKnowledgeStatesResponse:
    states: Sequence[KnowledgeState]


class ListKnowledgeStatesUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: ListKnowledgeStatesRequest) -> ListKnowledgeStatesResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError
            raise SessionExpiredError("Invalid session")

        user_id = session.user_id

        with self.uow_factory.create() as uow:
            states = await uow.knowledge_states.list_by_user(user_id=user_id)

        return ListKnowledgeStatesResponse(states=states)

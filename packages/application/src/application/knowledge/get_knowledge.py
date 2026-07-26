from dataclasses import dataclass

from backend.services.auth_service import AuthenticationService
from backend.services.authorization_service import AuthorizationService
from backend.services.knowledge_service import KnowledgeService
from knowledge.graph import KnowledgeGraph


@dataclass(frozen=True)
class GetKnowledgeRequest:
    document_id: str
    token: str


@dataclass(frozen=True)
class GetKnowledgeResponse:
    graph: KnowledgeGraph


class GetKnowledgeUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        authorization_service: AuthorizationService,
        knowledge_service: KnowledgeService,
    ) -> None:
        self.auth_service = auth_service
        self.authorization_service = authorization_service
        self.knowledge_service = knowledge_service

    async def execute(self, request: GetKnowledgeRequest) -> GetKnowledgeResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError
            raise SessionExpiredError("Invalid session")
        # Authorization can be added here

        graph = await self.knowledge_service.get_knowledge_graph(request.document_id)

        return GetKnowledgeResponse(graph=graph)

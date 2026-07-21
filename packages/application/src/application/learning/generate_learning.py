from typing import Any

from application.exceptions import ApplicationError
from application.interfaces import (
    AuthenticationServiceProtocol,
    AuthorizationServiceProtocol,
    LearningServiceProtocol,
)
from application.learning.commands import GenerateLearningCommand
from application.learning.responses import LearningGenerationResult

LEARNING_GENERATE = "learning:generate"


class GenerateLearningUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        authorization_service: AuthorizationServiceProtocol,
        learning_service: LearningServiceProtocol,
    ) -> None:
        self._auth_service = auth_service
        self._authorization_service = authorization_service
        self._learning_service = learning_service

    async def execute(self, command: GenerateLearningCommand) -> LearningGenerationResult:
        auth_result = await self._authorization_service.require_permission(
            command.user_id, LEARNING_GENERATE
        )
        if not auth_result.allowed:
            raise ApplicationError(f"Permission denied: {auth_result.reason}")

        class _RequestProxy:
            def __init__(self, doc_id: str, gen: str) -> None:
                self.document_id = doc_id
                self.generator = gen
                self.options: dict[str, Any] = {}

        result = await self._learning_service.generate_artifact(
            _RequestProxy(command.document_id, command.generator)
        )
        return LearningGenerationResult(
            status=getattr(result, "status", "completed"),
            document_id=getattr(result, "document_id", command.document_id),
            generator=getattr(result, "generator", command.generator),
            title=getattr(result, "title", "Untitled"),
            content_type=getattr(result, "content_type", "text/plain"),
            content=getattr(result, "generated_content", ""),
            metadata=getattr(result, "metadata", {}),
            statistics=getattr(result, "statistics", {}),
            processing_time_ms=getattr(result, "processing_time_ms", 0.0),
            warnings=getattr(result, "warnings", []),
        )

from application.document.commands import ProcessDocumentCommand
from application.document.responses import ProcessDocumentResult
from application.exceptions import ApplicationError
from application.interfaces import (
    AuthenticationServiceProtocol,
    AuthorizationServiceProtocol,
    DocumentServiceProtocol,
)

DOCUMENTS_WRITE = "documents:write"


class ProcessDocumentUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        authorization_service: AuthorizationServiceProtocol,
        document_service: DocumentServiceProtocol,
    ) -> None:
        self._auth_service = auth_service
        self._authorization_service = authorization_service
        self._document_service = document_service

    async def execute(self, command: ProcessDocumentCommand) -> ProcessDocumentResult:
        # 1. Authorization
        auth_result = await self._authorization_service.require_permission(
            command.user_id, DOCUMENTS_WRITE
        )
        if not auth_result.allowed:
            raise ApplicationError(f"Permission denied: {auth_result.reason}")

        # 2. Business Logic
        # We pass the command directly, duck-typed to avoid dependency on backend
        result = await self._document_service.process_document(command)

        # 3. Map to Response DTO
        return ProcessDocumentResult(
            status=result.status,
            document_id=result.document_id,
            filename=result.filename,
            title=result.title,
            source=result.source,
            processor=result.processor,
            chunk_count=result.chunk_count,
            processing_time_ms=result.processing_time_ms,
            warnings=result.warnings,
        )

from application.exceptions import ApplicationError
from application.interfaces import (
    AuthenticationServiceProtocol,
    AuthorizationServiceProtocol,
    RetrievalServiceProtocol,
)
from application.retrieval.commands import RetrievalCommand
from application.retrieval.responses import ChunkData, RetrievalResult

RETRIEVAL_SEARCH = "retrieval:search"


class RetrieveUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        authorization_service: AuthorizationServiceProtocol,
        retrieval_service: RetrievalServiceProtocol,
    ) -> None:
        self._auth_service = auth_service
        self._authorization_service = authorization_service
        self._retrieval_service = retrieval_service

    async def execute(self, command: RetrievalCommand) -> RetrievalResult:
        auth_result = await self._authorization_service.require_permission(
            command.user_id, RETRIEVAL_SEARCH
        )
        if not auth_result.allowed:
            raise ApplicationError(f"Permission denied: {auth_result.reason}")

        class _RequestProxy:
            def __init__(self, doc_id: str, query: str, top_k: int, min_sim: float | None) -> None:
                self.document_id = doc_id
                self.query = query
                self.top_k = top_k
                self.minimum_similarity = min_sim

        results = await self._retrieval_service.search(
            _RequestProxy(
                command.document_id or "", command.query, command.top_k, command.minimum_similarity
            )
        )
        # Normally result should have these properties or it's a domain object.
        # In Kogniq, retrieval_service returns a RetrievalResult schema
        # (temporarily) or similar domain model.
        items = getattr(results, "results", []) if hasattr(results, "results") else results
        mapped_results = [
            ChunkData(
                chunk_id=getattr(r, "chunk_id", ""),
                document_id=getattr(r, "document_id", command.document_id or ""),
                content=getattr(r, "chunk_text", getattr(r, "content", "")),
                chunk_index=getattr(r, "chunk_index", 0),
                score=getattr(r, "similarity_score", getattr(r, "score", 0.0)),
                metadata=getattr(r, "metadata", {}),
            )
            for r in items
        ]

        return RetrievalResult(
            status=getattr(results, "status", "completed"),
            query=command.query,
            document_id=getattr(results, "document_id", command.document_id or ""),
            total_results=len(mapped_results),
            results=mapped_results,
            processing_time_ms=getattr(results, "processing_time_ms", 0.0),
            warnings=getattr(results, "warnings", []),
        )

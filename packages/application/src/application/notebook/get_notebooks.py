import json
from dataclasses import dataclass
from typing import Any

from backend.services.auth_service import AuthenticationService
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class GetNotebooksRequest:
    document_id: str
    token: str


@dataclass(frozen=True)
class GetNotebooksResponse:
    notebooks: list[dict[str, Any]]


class GetNotebooksUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: GetNotebooksRequest) -> GetNotebooksResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from backend.core.exceptions import BackendError
            raise BackendError("unauthorized", "Invalid session", status_code=401)

        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if not doc:
                from backend.core.exceptions import BackendError
                raise BackendError("not_found", f"Document {request.document_id} not found", status_code=404)

            if doc.user_id and doc.user_id != session.user_id:
                from backend.core.exceptions import BackendError
                raise BackendError("unauthorized", "Not authorized to access this document", status_code=403)

            entries = await uow.notebook.list_by_document(request.document_id)

            # Assemble frontend-expected Notebook read model
            # Notebook: id, title, history, entries
            # NotebookEntry: id, title, createdAt, thoughts
            formatted_entries = []
            for entry in entries:
                try:
                    thoughts = json.loads(entry.thoughts_json)
                except json.JSONDecodeError:
                    thoughts = []

                formatted_entries.append(
                    {
                        "id": entry.id,
                        "title": entry.title,
                        # Format as user-friendly string for the UI or standard ISO
                        # The UI typically wants a readable string like "Today" or ISO 8601
                        "createdAt": entry.created_at.isoformat(),
                        "thoughts": thoughts,
                    }
                )

            # Return a single notebook representing the document
            notebook = {
                "id": doc.id,
                "title": doc.title,
                "history": [],
                "entries": formatted_entries,
            }

            return GetNotebooksResponse(notebooks=[notebook])

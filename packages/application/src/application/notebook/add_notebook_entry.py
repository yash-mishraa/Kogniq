import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional

from backend.services.auth_service import AuthenticationService
from persistence.uow_factory import AbstractUnitOfWorkFactory
from learning_content.notebook import NotebookEntry


@dataclass(frozen=True)
class AddNotebookEntryRequest:
    document_id: str
    token: str
    title: str
    content: str
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class AddNotebookEntryResponse:
    status: str
    entry_id: str | None
    error: str | None = None


class AddNotebookEntryUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: AddNotebookEntryRequest) -> AddNotebookEntryResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from backend.core.exceptions import BackendError
            raise BackendError("unauthorized", "Invalid session", status_code=401)

        if not request.title or len(request.title) > 100:
            from backend.core.exceptions import BackendError
            raise BackendError("validation_error", "Title must be between 1 and 100 characters", status_code=422)

        if not request.content or len(request.content) > 2000:
            from backend.core.exceptions import BackendError
            raise BackendError("validation_error", "Content must be between 1 and 2000 characters", status_code=422)

        # Build thoughts structure matching frontend expectations
        # A NotebookThought has id, type ("observation"), content
        thought_id = f"thought-{uuid.uuid4()}"
        thoughts = [
            {
                "id": thought_id,
                "type": "observation",
                "content": request.content.strip()
            }
        ]
        thoughts_json = json.dumps(thoughts)

        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if not doc:
                from backend.core.exceptions import BackendError
                raise BackendError("not_found", f"Document {request.document_id} not found", status_code=404)

            if doc.user_id and doc.user_id != session.user_id:
                from backend.core.exceptions import BackendError
                raise BackendError("unauthorized", "Not authorized to access this document", status_code=403)

            new_id = f"entry-{uuid.uuid4()}"
            idempotency_key = request.idempotency_key

            entry = NotebookEntry(
                id=new_id,
                user_id=session.user_id,
                document_id=request.document_id,
                title=request.title.strip(),
                thoughts_json=thoughts_json,
                created_at=datetime.now(UTC),
                idempotency_key=idempotency_key,
            )

            try:
                await uow.notebook.create(entry)
                uow.commit()
            except sqlite3.IntegrityError:
                # Catch uniqueness violations, such as idempotency duplicate or primary key collision
                uow.rollback()
                return AddNotebookEntryResponse(status="duplicate", entry_id=None)

            return AddNotebookEntryResponse(status="success", entry_id=new_id)

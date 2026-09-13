from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from backend.services.auth_service import AuthenticationService
from domain.analytics.models import FlashcardReviewedEvent, QuizCompletedEvent
from persistence.uow_factory import AbstractUnitOfWorkFactory


@dataclass(frozen=True)
class RecordEventRequest:
    event_id: str
    event_type: str
    document_id: str
    data: dict[str, Any]
    token: str


class RecordEventUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: RecordEventRequest) -> None:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError

            raise SessionExpiredError("Invalid session")

        user_id = session.user_id
        created_at = datetime.now(UTC)

        from domain.analytics.models import LearnerEvent

        event: LearnerEvent | None = None
        if request.event_type == "quiz_completed":
            event = QuizCompletedEvent(
                event_id=request.event_id,
                user_id=user_id,
                document_id=request.document_id,
                event_type=request.event_type,
                event_data=request.data,
                created_at=created_at,
            )
        elif request.event_type == "flashcard_reviewed":
            event = FlashcardReviewedEvent(
                event_id=request.event_id,
                user_id=user_id,
                document_id=request.document_id,
                event_type=request.event_type,
                event_data=request.data,
                created_at=created_at,
            )
        else:
            raise ValueError(f"Unsupported event type: {request.event_type}")

        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if not doc:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    "not_found", f"Document {request.document_id} not found", status_code=404
                )
            if doc.user_id and doc.user_id != user_id:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    "unauthorized", "Not authorized to access this document", status_code=403
                )

            await uow.analytics.save_event(event)

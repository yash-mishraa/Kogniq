from dataclasses import dataclass
from enum import StrEnum

from backend.services.auth_service import AuthenticationService
from persistence.uow_factory import AbstractUnitOfWorkFactory


class NextActionType(StrEnum):
    PROCESSING = "processing"
    STUDY = "study"
    QUIZ = "quiz"
    FLASHCARDS = "flashcards"
    REVIEW = "review"


@dataclass(frozen=True)
class GetNextActionRequest:
    document_id: str
    token: str


@dataclass(frozen=True)
class GetNextActionResponse:
    action: NextActionType


class GetNextActionUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory

    async def execute(self, request: GetNextActionRequest) -> GetNextActionResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from auth.exceptions import SessionExpiredError

            raise SessionExpiredError("Invalid session")

        user_id = session.user_id

        # 1. Authorize document and check status
        is_processing = False
        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if doc:
                if doc.user_id and doc.user_id != user_id:
                    from backend.core.exceptions import BackendError

                    raise BackendError("unauthorized", "Not authorized", status_code=403)
            else:
                job = uow.document_jobs.get(request.document_id)
                if not job:
                    from backend.core.exceptions import BackendError

                    raise BackendError("not_found", "Document not found", status_code=404)

                status = job.status
                if status == "Processing":
                    is_processing = True

        if is_processing:
            return GetNextActionResponse(action=NextActionType.PROCESSING)

        # 2. Document is Ready. Fetch analytics.
        with self.uow_factory.create() as uow:
            # Check study_session_completed
            # We can use the events repository if it exists, or fetch all metrics.
            # But the requirement is to check if it's completed.
            metrics = await uow.analytics.get_metrics(
                user_id=user_id, days=None, document_id=request.document_id
            )

            # If the user completed a quiz, they must have completed the study session.
            # Wait, the frontend explicitly fires "study_session_completed" which we need to track.
            # The raw SQL was:
            # uow.connection.execute("SELECT 1 FROM learner_activity WHERE document_id = ?
            # AND event_type = 'study_session_completed' LIMIT 1")
            # This is also a Clean Architecture violation.
            study_completed = await uow.analytics.has_completed_study(user_id, request.document_id)

            if not study_completed:
                return GetNextActionResponse(action=NextActionType.STUDY)

            # Study is completed. Check Quiz.
            metrics = await uow.analytics.get_metrics(
                user_id=user_id, days=None, document_id=request.document_id
            )

            if metrics.quizzes_completed == 0:
                return GetNextActionResponse(action=NextActionType.QUIZ)

            if metrics.average_quiz_accuracy < 0.70:
                return GetNextActionResponse(action=NextActionType.FLASHCARDS)

            return GetNextActionResponse(action=NextActionType.REVIEW)

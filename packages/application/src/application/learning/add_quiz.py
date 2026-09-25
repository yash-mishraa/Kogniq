import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from backend.services.auth_service import AuthenticationService
from backend.services.authorization_service import AuthorizationService
from persistence.uow_factory import AbstractUnitOfWorkFactory

from learning_content.entities import FlashcardDifficulty, QuizCollection, QuizOption, QuizQuestion


@dataclass(frozen=True)
class AddQuizQuestionRequest:
    document_id: str
    token: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str
    difficulty: str
    idempotency_key: str


@dataclass(frozen=True)
class AddQuizQuestionResponse:
    status: str
    question_id: str | None
    error: str | None = None


class AddQuizQuestionUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        authorization_service: AuthorizationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.authorization_service = authorization_service
        self.uow_factory = uow_factory

    async def execute(self, request: AddQuizQuestionRequest) -> AddQuizQuestionResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from backend.core.exceptions import BackendError

            raise BackendError("unauthorized", "Invalid session", status_code=401)

        # Validate inputs
        if not request.question or len(request.question) > 500:
            from backend.core.exceptions import BackendError

            raise BackendError(
                "validation_error", "Question must be between 1 and 500 characters", status_code=422
            )

        if not isinstance(request.options, list) or len(request.options) != 4:
            from backend.core.exceptions import BackendError

            raise BackendError(
                "validation_error", "Question must have exactly four options", status_code=422
            )
            
        for opt in request.options:
            if not isinstance(opt, str) or not opt.strip() or len(opt) > 200:
                from backend.core.exceptions import BackendError
                raise BackendError("validation_error", "Each option must be between 1 and 200 characters", status_code=422)

        if not request.correct_answer or len(request.correct_answer) > 200:
            from backend.core.exceptions import BackendError

            raise BackendError(
                "validation_error", "Correct answer must be between 1 and 200 characters", status_code=422
            )

        if not request.explanation or len(request.explanation) > 500:
            from backend.core.exceptions import BackendError

            raise BackendError(
                "validation_error",
                "Explanation must be between 1 and 500 characters",
                status_code=422,
            )

        difficulty_val = request.difficulty
        if difficulty_val not in ["easy", "medium", "hard"]:
            from backend.core.exceptions import BackendError

            raise BackendError("validation_error", "Invalid difficulty", status_code=422)

        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if not doc:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    "not_found", f"Document {request.document_id} not found", status_code=404
                )

            if doc.user_id and doc.user_id != session.user_id:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    "unauthorized", "Not authorized to access this document", status_code=403
                )

            # Retrieve existing quizzes
            materials_list = await uow.learning.list_by_document(request.document_id)
            if not materials_list:
                from backend.core.exceptions import BackendError

                raise BackendError("not_found", "Learning content not found", status_code=404)

            quiz_content = None
            for m in materials_list:
                if m.content_type.name.lower() == "quiz":
                    quiz_content = m
                    break

            if not quiz_content:
                from backend.core.exceptions import BackendError

                raise BackendError("not_found", "Quiz learning content not found", status_code=404)

            # Check idempotency
            tags = quiz_content.metadata.tags
            idempotency_tag = f"idempotency:{request.idempotency_key}"
            if idempotency_tag in tags:
                # Already processed
                return AddQuizQuestionResponse(status="duplicate", question_id=None)

            # Deserialize
            questions = []
            try:
                parsed_json = json.loads(quiz_content.body)
                for item in parsed_json:
                    options = [QuizOption(id=o["id"], text=o["text"]) for o in item["options"]]
                    questions.append(
                        QuizQuestion(
                            id=item["id"],
                            question=item["question"],
                            options=tuple(options),
                            correct_answer=item["correct_answer"],
                            explanation=item["explanation"],
                            difficulty=FlashcardDifficulty(item["difficulty"]),
                            tags=tuple(item.get("tags", [])),
                            created_at=datetime.fromisoformat(item["created_at"]),
                        )
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                from backend.core.exceptions import BackendError
                import logging
                logging.error(f"Failed to decode existing quizzes: {e}")
                raise BackendError(
                    "internal_error", "Failed to decode existing quizzes", status_code=500
                ) from e

            # Add new quiz question
            new_id = str(uuid.uuid4())
            labels = ["A", "B", "C", "D"]
            parsed_options = []
            for i, opt in enumerate(request.options):
                parsed_options.append(QuizOption(id=labels[i], text=opt.strip()))

            try:
                new_q = QuizQuestion(
                    id=new_id,
                    question=request.question.strip(),
                    options=tuple(parsed_options),
                    correct_answer=request.correct_answer.strip(),
                    explanation=request.explanation.strip(),
                    difficulty=FlashcardDifficulty(difficulty_val),
                    tags=("ai-generated",),
                    created_at=datetime.now(UTC),
                )
            except ValueError as e:
                from backend.core.exceptions import BackendError
                raise BackendError("validation_error", str(e), status_code=422) from e

            questions.append(new_q)

            collection = QuizCollection(questions=tuple(questions))
            new_body = collection.to_json()

            # Add idempotency tag
            new_tags = tuple(list(tags) + [idempotency_tag])
            import dataclasses

            new_metadata = dataclasses.replace(quiz_content.metadata, tags=new_tags)

            new_content = dataclasses.replace(
                quiz_content, body=new_body, metadata=new_metadata
            )

            await uow.learning.save(new_content)
            uow.commit()

            return AddQuizQuestionResponse(status="success", question_id=new_id)

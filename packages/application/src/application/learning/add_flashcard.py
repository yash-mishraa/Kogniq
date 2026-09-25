import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from backend.services.auth_service import AuthenticationService
from backend.services.authorization_service import AuthorizationService
from persistence.uow_factory import AbstractUnitOfWorkFactory

from learning_content.entities import Flashcard, FlashcardCollection, FlashcardDifficulty


@dataclass(frozen=True)
class AddFlashcardRequest:
    document_id: str
    token: str
    question: str
    answer: str
    difficulty: str
    idempotency_key: str


@dataclass(frozen=True)
class AddFlashcardResponse:
    status: str
    flashcard_id: str | None
    error: str | None = None


class AddFlashcardUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        authorization_service: AuthorizationService,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.auth_service = auth_service
        self.authorization_service = authorization_service
        self.uow_factory = uow_factory

    async def execute(self, request: AddFlashcardRequest) -> AddFlashcardResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            from backend.core.exceptions import BackendError
            raise BackendError("unauthorized", "Invalid session", status_code=401)

        # Validate input lengths
        if not request.question or len(request.question) > 500:
            from backend.core.exceptions import BackendError
            raise BackendError("validation_error", "Question must be between 1 and 500 characters", status_code=422)

        if not request.answer or len(request.answer) > 2000:
            from backend.core.exceptions import BackendError
            raise BackendError("validation_error", "Answer must be between 1 and 2000 characters", status_code=422)

        difficulty_val = request.difficulty
        if difficulty_val not in ["easy", "medium", "hard"]:
            from backend.core.exceptions import BackendError
            raise BackendError("validation_error", "Invalid difficulty", status_code=422)

        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if not doc:
                from backend.core.exceptions import BackendError
                raise BackendError("not_found", f"Document {request.document_id} not found", status_code=404)

            if doc.user_id and doc.user_id != session.user_id:
                from backend.core.exceptions import BackendError
                raise BackendError("unauthorized", "Not authorized to access this document", status_code=403)

            # Retrieve existing flashcards
            materials_list = await uow.learning.list_by_document(request.document_id)
            if not materials_list:
                from backend.core.exceptions import BackendError
                raise BackendError("not_found", "Learning content not found", status_code=404)

            flashcards_content = None
            for m in materials_list:
                if m.content_type.name.lower() == "flashcards":
                    flashcards_content = m
                    break
            
            if not flashcards_content:
                from backend.core.exceptions import BackendError
                raise BackendError("not_found", "Flashcards learning content not found", status_code=404)

            # Check idempotency
            tags = flashcards_content.metadata.tags
            idempotency_tag = f"idempotency:{request.idempotency_key}"
            if idempotency_tag in tags:
                # Already processed
                return AddFlashcardResponse(status="duplicate", flashcard_id=None)

            # Deserialize
            cards = []
            try:
                parsed_json = json.loads(flashcards_content.body)
                for item in parsed_json:
                    cards.append(Flashcard(
                        id=item["id"],
                        question=item["question"],
                        answer=item["answer"],
                        difficulty=FlashcardDifficulty(item["difficulty"]),
                        tags=tuple(item.get("tags", [])),
                        created_at=datetime.fromisoformat(item["created_at"])
                    ))
            except json.JSONDecodeError:
                from backend.core.exceptions import BackendError
                raise BackendError("internal_error", "Failed to decode existing flashcards", status_code=500)

            # Add new flashcard
            new_id = str(uuid.uuid4())
            new_card = Flashcard(
                id=new_id,
                question=request.question.strip(),
                answer=request.answer.strip(),
                difficulty=FlashcardDifficulty(difficulty_val),
                tags=("ai-generated",),
                created_at=datetime.now(UTC)
            )
            cards.append(new_card)

            collection = FlashcardCollection(flashcards=tuple(cards))
            new_body = collection.to_json()

            # Add idempotency tag
            new_tags = tuple(list(tags) + [idempotency_tag])
            import dataclasses
            new_metadata = dataclasses.replace(flashcards_content.metadata, tags=new_tags)

            new_content = dataclasses.replace(
                flashcards_content, 
                body=new_body, 
                metadata=new_metadata
            )

            await uow.learning.save(new_content)
            uow.commit()

            return AddFlashcardResponse(status="success", flashcard_id=new_id)



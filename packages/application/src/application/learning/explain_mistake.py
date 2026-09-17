import json
from dataclasses import dataclass

from backend.core.exceptions import BackendError
from backend.services.auth_service import AuthenticationService
from persistence.uow_factory import AbstractUnitOfWorkFactory

from learning_content.providers.base import AbstractTextGenerationProvider


@dataclass(frozen=True)
class ExplainMistakeRequest:
    document_id: str
    question_id: str
    selected_option_id: str
    token: str


@dataclass(frozen=True)
class ExplainMistakeResponse:
    explanation: str


class ExplainMistakeUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        uow_factory: AbstractUnitOfWorkFactory,
        provider: AbstractTextGenerationProvider,
    ) -> None:
        self.auth_service = auth_service
        self.uow_factory = uow_factory
        self.provider = provider

    async def execute(self, request: ExplainMistakeRequest) -> ExplainMistakeResponse:
        session = await self.auth_service.validate_session(request.token)
        if not session:
            raise BackendError("unauthorized", "Invalid session", status_code=401)

        user_id = session.user_id

        # 1. Authorize document
        with self.uow_factory.create() as uow:
            doc = await uow.documents.get(request.document_id)
            if not doc:
                raise BackendError("not_found", "Document not found", status_code=404)
            if doc.user_id and doc.user_id != user_id:
                raise BackendError("unauthorized", "Not authorized", status_code=403)

            # 2. Retrieve quiz
            materials = await uow.learning.list_by_document(request.document_id)
            quiz = None
            for m in materials:
                if m.content_type.name.lower() == "quiz":
                    quiz = m
                    break

            if not quiz:
                raise BackendError("not_found", "Quiz material not found", status_code=404)

            try:
                quiz_data = json.loads(quiz.body)
            except json.JSONDecodeError:
                raise BackendError(
                    "internal_error", "Invalid quiz data in database", status_code=500
                ) from None

        # 3. Find question and option
        question = None
        for i, q in enumerate(quiz_data):
            # Fallback to q{i} if id doesn't exist
            q_id = q.get("id", f"q{i}")
            if q_id == request.question_id:
                question = q
                break

        if not question:
            raise BackendError("not_found", "Question not found", status_code=404)

        selected_option = None
        correct_option = None
        for o in question.get("options", []):
            if o.get("id") == request.selected_option_id:
                selected_option = o
            if o.get("id") == question.get("correct_answer"):
                correct_option = o

        if not selected_option:
            raise BackendError("not_found", "Selected option not found", status_code=404)
        if not correct_option:
            raise BackendError("not_found", "Correct option not found", status_code=404)

        # 4. Prompt Gemini to explain
        prompt = (
            f"A learner taking a quiz made a mistake.\n"
            f"Question: {question.get('question')}\n"
            f"Correct Answer: {correct_option.get('text')}\n"
            f"Selected Incorrect Answer: {selected_option.get('text')}\n\n"
            f"Please explain in 2-3 sentences why their answer is incorrect "
            f"and why the correct answer is correct."
        )

        try:
            response = self.provider.generate(prompt=prompt, temperature=0.3, max_tokens=200)
            return ExplainMistakeResponse(explanation=response)
        except Exception as e:
            raise BackendError("generation_failed", str(e), status_code=500) from e

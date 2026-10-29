from typing import Any

from backend.dependencies import (
    get_add_flashcard_use_case,
    get_add_quiz_question_use_case,
    get_explain_mistake_use_case,
    get_generate_learning_use_case,
    get_get_learning_materials_use_case,
    get_next_action_use_case,
)
from backend.schemas.learning import (
    LearningGenerationRequest,
    LearningGenerationResponse,
    LearningMaterialsResponse,
)
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel

from application.learning.commands import GenerateLearningCommand
from application.learning.generate_learning import GenerateLearningUseCase
from application.learning.get_learning_materials import (
    GetLearningMaterialsRequest,
    GetLearningMaterialsUseCase,
)

learning_router = APIRouter(prefix="/learning", tags=["Learning"])


def _session_token(request: Request, authorization: str | None) -> str:
    cookie = request.cookies.get("kogniq_session", "")
    if cookie:
        return cookie
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return authorization or ""


def _raise_backend_error(error: Exception) -> None:
    if type(error).__name__ == "BackendError":
        raise HTTPException(
            status_code=getattr(error, "status_code", 500), detail=str(error)
        ) from error


@learning_router.post("/generate", response_model=LearningGenerationResponse)
async def generate_learning_content(
    request: LearningGenerationRequest,
    x_user_id: str = Header("demo-user-1", alias="X-User-Id"),
    use_case: GenerateLearningUseCase = Depends(get_generate_learning_use_case),  # noqa: B008
) -> LearningGenerationResponse:
    """Generate an educational artifact from a processed document."""
    command = GenerateLearningCommand(
        user_id=x_user_id,
        document_id=request.document_id,
        generator=request.generator,
    )
    result = await use_case.execute(command)
    return LearningGenerationResponse(
        status=result.status,
        document_id=result.document_id,
        generator=result.generator,
        title=result.title,
        content_type=result.content_type,
        generated_content=result.content,
        metadata=result.metadata,
        statistics=result.statistics,
        processing_time_ms=result.processing_time_ms,
        warnings=result.warnings,
    )


@learning_router.get("/{document_id}", response_model=LearningMaterialsResponse)
async def get_learning_materials(
    document_id: str,
    request: Request,
    use_case: GetLearningMaterialsUseCase = Depends(  # noqa: B008
        get_get_learning_materials_use_case
    ),
) -> LearningMaterialsResponse:
    """Retrieve all generated learning materials for a document."""
    token = _session_token(request, None)
    request_dto = GetLearningMaterialsRequest(document_id=document_id, token=token)
    try:
        response = await use_case.execute(request_dto)
    except Exception as error:
        _raise_backend_error(error)
        raise

    materials_dict = None
    if response.materials is not None:
        from backend.schemas.learning import LearningMaterialItem

        materials_dict = {
            key: LearningMaterialItem(title=value.title, body=value.body)
            for key, value in response.materials.items()
        }

    return LearningMaterialsResponse(status=response.status, materials=materials_dict)


class NextActionResponse(BaseModel):
    action: str


@learning_router.get("/{document_id}/next-action", response_model=NextActionResponse)
async def get_next_action(
    document_id: str,
    request_obj: Request,
    authorization: str | None = Header(None, description="Bearer token"),
    use_case: Any = Depends(get_next_action_use_case),  # noqa: B008
) -> NextActionResponse:
    from application.learning.get_next_action import GetNextActionRequest

    token = _session_token(request_obj, authorization)
    request_dto = GetNextActionRequest(document_id=document_id, token=token)
    try:
        response = await use_case.execute(request_dto)
        return NextActionResponse(action=response.action.value)
    except Exception as error:
        _raise_backend_error(error)
        raise


class ExplainMistakeRequestDto(BaseModel):
    document_id: str
    question_id: str
    selected_option_id: str


class ExplainMistakeResponseDto(BaseModel):
    explanation: str


@learning_router.post("/explain-mistake", response_model=ExplainMistakeResponseDto)
async def explain_mistake(
    request: ExplainMistakeRequestDto,
    request_obj: Request,
    authorization: str | None = Header(None, description="Bearer token"),
    use_case: Any = Depends(get_explain_mistake_use_case),  # noqa: B008
) -> ExplainMistakeResponseDto:
    from application.learning.explain_mistake import ExplainMistakeRequest

    token = _session_token(request_obj, authorization)
    request_dto = ExplainMistakeRequest(
        document_id=request.document_id,
        question_id=request.question_id,
        selected_option_id=request.selected_option_id,
        token=token,
    )
    try:
        response = await use_case.execute(request_dto)
        return ExplainMistakeResponseDto(explanation=response.explanation)
    except Exception as error:
        _raise_backend_error(error)
        raise


class AddFlashcardPayload(BaseModel):
    question: str
    answer: str
    difficulty: str
    idempotency_key: str


@learning_router.post("/{document_id}/flashcards")
async def add_flashcard(
    document_id: str,
    payload: AddFlashcardPayload,
    request: Request,
    use_case: Any = Depends(get_add_flashcard_use_case),  # noqa: B008
) -> Any:
    from application.learning.add_flashcard import AddFlashcardRequest

    token = _session_token(request, None)
    req = AddFlashcardRequest(
        document_id=document_id,
        token=token,
        question=payload.question,
        answer=payload.answer,
        difficulty=payload.difficulty,
        idempotency_key=payload.idempotency_key,
    )

    try:
        return await use_case.execute(req)
    except Exception as error:
        _raise_backend_error(error)
        raise


class AddQuizPayload(BaseModel):
    question: str
    options: list[str]
    correct_answer: str
    explanation: str
    difficulty: str
    idempotency_key: str


@learning_router.post("/{document_id}/quizzes")
async def add_quiz(
    document_id: str,
    payload: AddQuizPayload,
    request: Request,
    use_case: Any = Depends(get_add_quiz_question_use_case),  # noqa: B008
) -> Any:
    from application.learning.add_quiz import AddQuizQuestionRequest

    token = _session_token(request, None)
    req = AddQuizQuestionRequest(
        document_id=document_id,
        token=token,
        question=payload.question,
        options=payload.options,
        correct_answer=payload.correct_answer,
        explanation=payload.explanation,
        difficulty=payload.difficulty,
        idempotency_key=payload.idempotency_key,
    )

    try:
        return await use_case.execute(req)
    except Exception as error:
        _raise_backend_error(error)
        raise

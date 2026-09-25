from typing import Any

import backend.dependencies
from backend.dependencies import (
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
from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel

from application.learning.commands import GenerateLearningCommand
from application.learning.generate_learning import GenerateLearningUseCase
from application.learning.get_learning_materials import (
    GetLearningMaterialsRequest,
    GetLearningMaterialsUseCase,
)

learning_router = APIRouter(prefix="/learning", tags=["Learning"])


@learning_router.post("/generate", response_model=LearningGenerationResponse)
async def generate_learning_content(
    request: LearningGenerationRequest,
    x_user_id: str = Header("demo-user-1", alias="X-User-Id"),
    use_case: GenerateLearningUseCase = Depends(get_generate_learning_use_case),  # noqa: B008
) -> LearningGenerationResponse:
    """
    Generate an educational artifact from a processed document.
    """
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
    use_case: GetLearningMaterialsUseCase = Depends(get_get_learning_materials_use_case),  # noqa: B008
) -> LearningMaterialsResponse:
    """
    Retrieve all generated learning materials for a document.
    """
    # Read token from cookies instead of explicit header to avoid Swagger UI stripping
    # the 'authorization' parameter, which caused 422 errors. This also allows the
    # Next.js frontend to poll the endpoint naturally using credentials.
    token = request.cookies.get("kogniq_session", "")
    request_dto = GetLearningMaterialsRequest(document_id=document_id, token=token)
    try:
        response = await use_case.execute(request_dto)
    except Exception as e:
        # If it's a BackendError (like unauthorized), raise it as HTTPException
        if type(e).__name__ == "BackendError":
            from fastapi import HTTPException

            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e)) from e
        raise

    # Convert LearningMaterialItemResult to LearningMaterialItem
    materials_dict = None
    if response.materials is not None:
        from backend.schemas.learning import LearningMaterialItem

        materials_dict = {
            k: LearningMaterialItem(title=v.title, body=v.body)
            for k, v in response.materials.items()
        }

    return LearningMaterialsResponse(status=response.status, materials=materials_dict)


class NextActionResponse(BaseModel):
    action: str


@learning_router.get("/{document_id}/next-action", response_model=NextActionResponse)
async def get_next_action(
    document_id: str,
    authorization: str = Header(..., description="Bearer token"),
    use_case: Any = Depends(get_next_action_use_case),  # noqa: B008
) -> NextActionResponse:
    from application.learning.get_next_action import GetNextActionRequest

    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    request_dto = GetNextActionRequest(document_id=document_id, token=token)
    try:
        response = await use_case.execute(request_dto)
        return NextActionResponse(action=response.action.value)
    except Exception as e:
        if type(e).__name__ == "BackendError":
            from fastapi import HTTPException

            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e)) from e
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
    authorization: str = Header(..., description="Bearer token"),
    use_case: Any = Depends(get_explain_mistake_use_case),  # noqa: B008
) -> ExplainMistakeResponseDto:
    from application.learning.explain_mistake import ExplainMistakeRequest

    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    request_dto = ExplainMistakeRequest(
        document_id=request.document_id,
        question_id=request.question_id,
        selected_option_id=request.selected_option_id,
        token=token,
    )
    try:
        response = await use_case.execute(request_dto)
        return ExplainMistakeResponseDto(explanation=response.explanation)
    except Exception as e:
        if type(e).__name__ == "BackendError":
            from fastapi import HTTPException

            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e)) from e
        raise

from pydantic import BaseModel


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
    use_case = Depends(backend.dependencies.get_add_flashcard_use_case)
):
    token = request.cookies.get("kogniq_session", "")
    from application.learning.add_flashcard import AddFlashcardRequest
    req = AddFlashcardRequest(
        document_id=document_id,
        token=token,
        question=payload.question,
        answer=payload.answer,
        difficulty=payload.difficulty,
        idempotency_key=payload.idempotency_key
    )
    
    try:
        response = await use_case.execute(req)
        return response
    except Exception as e:
        if type(e).__name__ == "BackendError":
            from fastapi import HTTPException
            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e)) from e
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
    use_case = Depends(backend.dependencies.get_add_quiz_question_use_case)
):
    token = request.cookies.get("kogniq_session", "")
    from application.learning.add_quiz import AddQuizQuestionRequest
    req = AddQuizQuestionRequest(
        document_id=document_id,
        token=token,
        question=payload.question,
        options=payload.options,
        correct_answer=payload.correct_answer,
        explanation=payload.explanation,
        difficulty=payload.difficulty,
        idempotency_key=payload.idempotency_key
    )
    
    try:
        response = await use_case.execute(req)
        return response
    except Exception as e:
        if type(e).__name__ == "BackendError":
            from fastapi import HTTPException
            raise HTTPException(status_code=getattr(e, "status_code", 500), detail=str(e)) from e
        raise

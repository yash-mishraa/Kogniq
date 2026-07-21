from fastapi import APIRouter, Depends, Header

from application.learning.commands import GenerateLearningCommand
from application.learning.generate_learning import GenerateLearningUseCase
from backend.dependencies import get_generate_learning_use_case
from backend.schemas.learning import LearningGenerationRequest, LearningGenerationResponse

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

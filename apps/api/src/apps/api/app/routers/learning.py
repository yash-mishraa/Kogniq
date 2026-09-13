from backend.dependencies import get_generate_learning_use_case, get_get_learning_materials_use_case
from backend.schemas.learning import (
    LearningGenerationRequest,
    LearningGenerationResponse,
    LearningMaterialsResponse,
)
from fastapi import APIRouter, Depends, Header, Request

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

from fastapi import APIRouter

from backend.dependencies import LearningDependency
from backend.schemas.learning import LearningGenerationRequest, LearningGenerationResponse

learning_router = APIRouter(prefix="/learning", tags=["Learning"])


@learning_router.post("/generate", response_model=LearningGenerationResponse)
async def generate_learning_content(
    request: LearningGenerationRequest,
    learning_service: LearningDependency,
) -> LearningGenerationResponse:
    """
    Generate an educational artifact from a processed document.
    """
    return await learning_service.generate_artifact(request)

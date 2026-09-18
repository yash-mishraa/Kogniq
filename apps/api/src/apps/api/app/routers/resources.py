from typing import Annotated

from backend.dependencies import (
    get_get_learning_resource_use_case,
    get_list_learning_resources_use_case,
    get_resource_chunks_use_case,
    get_resource_sections_use_case,
    get_resource_statistics_use_case,
)
from backend.schemas.resources import (
    LearningResourceResponse,
    ResourceChunkResponse,
    ResourceSectionResponse,
    ResourceStatisticsResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query

from application.exceptions import ApplicationError
from apps.api.app.core.errors import APIError
from apps.api.app.dependencies.auth import CurrentUserDependency

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("", response_model=list[LearningResourceResponse])
async def list_resources(
    current_user: CurrentUserDependency,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    use_case: Any = Depends(get_list_learning_resources_use_case),
) -> list[LearningResourceResponse]:
    """List all learning resources."""
    try:
        resources = await use_case.execute(user_id=current_user.user_id, limit=limit, offset=offset)
        # Assuming resource.resource_type and status are enums, we convert them to str implicitly by Pydantic
        return [LearningResourceResponse.model_validate(r) for r in resources]
    except Exception as e:
        raise APIError(
            status_code=500, code="INTERNAL_ERROR", message="An unexpected error occurred."
        ) from e


@router.get("/{resource_id}", response_model=LearningResourceResponse)
async def get_resource(
    resource_id: str,
    current_user: CurrentUserDependency,
    use_case=Depends(get_get_learning_resource_use_case),
) -> LearningResourceResponse:
    """Get a specific learning resource."""
    try:
        resource = await use_case.execute(user_id=current_user.user_id, resource_id=resource_id)
        return LearningResourceResponse.model_validate(resource)
    except ApplicationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise APIError(
            status_code=500, code="INTERNAL_ERROR", message="An unexpected error occurred."
        ) from e


@router.get("/{resource_id}/sections", response_model=list[ResourceSectionResponse])
async def get_resource_sections(
    resource_id: str,
    current_user: CurrentUserDependency,
    use_case=Depends(get_resource_sections_use_case),
) -> list[ResourceSectionResponse]:
    """Get sections for a learning resource."""
    try:
        sections = await use_case.execute(user_id=current_user.user_id, resource_id=resource_id)
        return [ResourceSectionResponse.model_validate(s) for s in sections]
    except ApplicationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise APIError(
            status_code=500, code="INTERNAL_ERROR", message="An unexpected error occurred."
        ) from e


@router.get("/{resource_id}/chunks", response_model=list[ResourceChunkResponse])
async def get_resource_chunks(
    resource_id: str,
    current_user: CurrentUserDependency,
    use_case=Depends(get_resource_chunks_use_case),
) -> list[ResourceChunkResponse]:
    """Get chunks for a learning resource."""
    try:
        chunks = await use_case.execute(user_id=current_user.user_id, resource_id=resource_id)
        return [ResourceChunkResponse.model_validate(c) for c in chunks]
    except ApplicationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise APIError(
            status_code=500, code="INTERNAL_ERROR", message="An unexpected error occurred."
        ) from e


@router.get("/{resource_id}/statistics", response_model=ResourceStatisticsResponse)
async def get_resource_statistics(
    resource_id: str,
    current_user: CurrentUserDependency,
    use_case=Depends(get_resource_statistics_use_case),
) -> ResourceStatisticsResponse:
    """Get statistics for a learning resource."""
    try:
        stats = await use_case.execute(user_id=current_user.user_id, resource_id=resource_id)
        return ResourceStatisticsResponse(**stats)
    except ApplicationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise APIError(
            status_code=500, code="INTERNAL_ERROR", message="An unexpected error occurred."
        ) from e

from typing import Any

from backend.dependencies import get_analytics_use_case
from fastapi import APIRouter, Depends, Header, Response, status
from pydantic import BaseModel

from application.analytics.get_analytics import GetAnalyticsRequest, GetAnalyticsUseCase

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

class AnalyticsMetricsResponse(BaseModel):
    quizzes_completed: int
    average_quiz_accuracy: float
    flashcards_reviewed: int


@analytics_router.get("", response_model=AnalyticsMetricsResponse)
async def get_analytics(
    time_range: str = "7d",
    document_id: str | None = None,
    authorization: str = Header(..., description="Bearer token"),
    use_case: GetAnalyticsUseCase = Depends(get_analytics_use_case),  # noqa: B008
) -> AnalyticsMetricsResponse:
    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    request = GetAnalyticsRequest(time_range=time_range, token=token, document_id=document_id)
    response = await use_case.execute(request)
    return AnalyticsMetricsResponse(
        quizzes_completed=response.metrics.quizzes_completed,
        average_quiz_accuracy=response.metrics.average_quiz_accuracy,
        flashcards_reviewed=response.metrics.flashcards_reviewed,
    )

class EventBatchItem(BaseModel):
    event_id: str
    event_type: str
    resource_id: str
    data: dict[str, Any]
    section_id: str | None = None
    chunk_id: str | None = None
    idempotency_key: str | None = None

class BatchEventsData(BaseModel):
    events: list[EventBatchItem]

class ResourceProgressResponse(BaseModel):
    resource_opened: bool
    total_sections: int
    total_chunks: int
    viewed_sections: int
    viewed_chunks: int
    last_activity: str | None = None

from backend.dependencies import get_record_events_batch_use_case, get_resource_progress_use_case

from application.analytics.get_resource_progress import GetResourceProgressRequest
from application.analytics.record_events_batch import EventPayload, RecordEventsBatchRequest


@analytics_router.post("/events/batch", status_code=status.HTTP_204_NO_CONTENT)
async def record_events_batch(
    payload: BatchEventsData,
    authorization: str = Header(..., description="Bearer token"),
    use_case: Any = Depends(get_record_events_batch_use_case),
) -> Response:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    request = RecordEventsBatchRequest(
        token=token,
        events=[
            EventPayload(
                event_id=e.event_id,
                event_type=e.event_type,
                resource_id=e.resource_id,
                data=e.data,
                section_id=e.section_id,
                chunk_id=e.chunk_id,
                idempotency_key=e.idempotency_key
            ) for e in payload.events
        ]
    )
    await use_case.execute(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@analytics_router.get("/progress/{resource_id}", response_model=ResourceProgressResponse)
async def get_resource_progress(
    resource_id: str,
    authorization: str = Header(..., description="Bearer token"),
    use_case: Any = Depends(get_resource_progress_use_case),
) -> ResourceProgressResponse:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    request = GetResourceProgressRequest(token=token, resource_id=resource_id)
    progress_dict = await use_case.execute(request)
    return ResourceProgressResponse.model_validate(progress_dict)

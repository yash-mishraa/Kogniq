from typing import Any

from backend.dependencies import get_analytics_use_case, get_record_event_use_case
from fastapi import APIRouter, Depends, Header, Response, status
from pydantic import BaseModel

from application.analytics.get_analytics import GetAnalyticsRequest, GetAnalyticsUseCase
from application.analytics.record_event import RecordEventRequest, RecordEventUseCase

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


class EventData(BaseModel):
    event_id: str
    event_type: str
    document_id: str
    data: dict[str, Any]


class AnalyticsMetricsResponse(BaseModel):
    quizzes_completed: int
    average_quiz_accuracy: float
    flashcards_reviewed: int


@analytics_router.post("/events", status_code=status.HTTP_204_NO_CONTENT)
async def record_event(
    event: EventData,
    authorization: str = Header(..., description="Bearer token"),
    use_case: RecordEventUseCase = Depends(get_record_event_use_case),  # noqa: B008
) -> Response:
    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    request = RecordEventRequest(
        event_id=event.event_id,
        event_type=event.event_type,
        document_id=event.document_id,
        data=event.data,
        token=token,
    )
    await use_case.execute(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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

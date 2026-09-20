from typing import Any

from backend.dependencies import get_knowledge_state_use_case, list_knowledge_states_use_case
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from application.student.get_knowledge_state import GetKnowledgeStateRequest
from application.student.list_knowledge_states import ListKnowledgeStatesRequest

student_router = APIRouter(prefix="/student", tags=["Student"])


class KnowledgeStateResponse(BaseModel):
    id: str
    user_id: str
    resource_id: str
    mastery_score: float
    created_at: str
    updated_at: str
    last_reviewed_at: str | None
    next_review_due: str | None


class ListKnowledgeStatesResponse(BaseModel):
    states: list[KnowledgeStateResponse]


def _format_state(state: Any) -> KnowledgeStateResponse:
    return KnowledgeStateResponse(
        id=state.id,
        user_id=state.user_id,
        resource_id=state.resource_id,
        mastery_score=state.mastery_score,
        created_at=state.created_at.isoformat(),
        updated_at=state.updated_at.isoformat(),
        last_reviewed_at=state.last_reviewed_at.isoformat() if state.last_reviewed_at else None,
        next_review_due=state.next_review_due.isoformat() if state.next_review_due else None,
    )


@student_router.get("/knowledge-states", response_model=ListKnowledgeStatesResponse)
async def list_knowledge_states(
    authorization: str = Header(..., description="Bearer token"),
    use_case: Any = Depends(list_knowledge_states_use_case),  # noqa: B008
) -> ListKnowledgeStatesResponse:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    request = ListKnowledgeStatesRequest(token=token)
    response = await use_case.execute(request)
    
    return ListKnowledgeStatesResponse(states=[_format_state(s) for s in response.states])


@student_router.get("/knowledge-states/{resource_id}", response_model=KnowledgeStateResponse)
async def get_knowledge_state(
    resource_id: str,
    authorization: str = Header(..., description="Bearer token"),
    use_case: Any = Depends(get_knowledge_state_use_case),  # noqa: B008
) -> KnowledgeStateResponse:
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    request = GetKnowledgeStateRequest(token=token, resource_id=resource_id)
    response = await use_case.execute(request)
    
    if not response.state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge state not found")
        
    return _format_state(response.state)

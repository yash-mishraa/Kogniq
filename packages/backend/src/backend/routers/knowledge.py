
from fastapi import APIRouter, Depends, Header
from knowledge.concept import KnowledgeConcept
from knowledge.graph import KnowledgeGraph
from knowledge.relationship import KnowledgeRelationship

from application.knowledge.get_knowledge import GetKnowledgeRequest, GetKnowledgeUseCase
from backend.dependencies import get_knowledge_use_case

knowledge_router = APIRouter(prefix="/knowledge", tags=["Knowledge"])




@knowledge_router.get("/{document_id}", response_model=KnowledgeGraph)
async def get_knowledge(
    document_id: str,
    authorization: str = Header(..., description="Bearer token"),
    use_case: GetKnowledgeUseCase = Depends(get_knowledge_use_case),  # noqa: B008
) -> KnowledgeGraph:
    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    request = GetKnowledgeRequest(document_id=document_id, token=token)
    response = await use_case.execute(request)
    return response.graph


@knowledge_router.get("/{document_id}/concepts", response_model=list[KnowledgeConcept])
async def get_knowledge_concepts(
    document_id: str,
    authorization: str = Header(..., description="Bearer token"),
    use_case: GetKnowledgeUseCase = Depends(get_knowledge_use_case),  # noqa: B008
) -> list[KnowledgeConcept]:
    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    request = GetKnowledgeRequest(document_id=document_id, token=token)
    response = await use_case.execute(request)
    return list(response.graph.concepts)


@knowledge_router.get("/{document_id}/relationships", response_model=list[KnowledgeRelationship])
async def get_knowledge_relationships(
    document_id: str,
    authorization: str = Header(..., description="Bearer token"),
    use_case: GetKnowledgeUseCase = Depends(get_knowledge_use_case),  # noqa: B008
) -> list[KnowledgeRelationship]:
    token = (
        authorization.replace("Bearer ", "")
        if authorization.startswith("Bearer ")
        else authorization
    )
    request = GetKnowledgeRequest(document_id=document_id, token=token)
    response = await use_case.execute(request)
    return list(response.graph.relationships)

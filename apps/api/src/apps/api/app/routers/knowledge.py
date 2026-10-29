from backend.dependencies import (
    get_authentication_service,
    get_knowledge_extractor,
    get_knowledge_service,
    get_knowledge_use_case,
    get_uow_factory,
)
from content.chunking.collection import ChunkCollection
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from knowledge.concept import KnowledgeConcept
from knowledge.graph import KnowledgeGraph
from knowledge.relationship import KnowledgeRelationship

from application.knowledge.get_knowledge import GetKnowledgeRequest, GetKnowledgeUseCase
from application.learning.query_knowledge_graph import (
    QueryKnowledgeGraphRequest,
    QueryKnowledgeGraphUseCase,
)

knowledge_router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


def _session_token(request: Request, authorization: str | None) -> str:
    cookie = request.cookies.get("kogniq_session", "")
    if cookie:
        return cookie
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return authorization or ""


@knowledge_router.get("/{document_id}", response_model=KnowledgeGraph)
async def get_knowledge(
    document_id: str,
    request_obj: Request,
    authorization: str | None = Header(None, description="Bearer token"),
    use_case: GetKnowledgeUseCase = Depends(get_knowledge_use_case),  # noqa: B008
) -> KnowledgeGraph:
    request = GetKnowledgeRequest(
        document_id=document_id, token=_session_token(request_obj, authorization)
    )
    response = await use_case.execute(request)
    return response.graph


@knowledge_router.post("/{document_id}/extract", response_model=KnowledgeGraph)
async def extract_knowledge(
    document_id: str,
    request_obj: Request,
    authorization: str | None = Header(None, description="Bearer token"),
    auth_service=Depends(get_authentication_service),
    uow_factory=Depends(get_uow_factory),
    extractor=Depends(get_knowledge_extractor),
) -> KnowledgeGraph:
    """Extract concepts and relationships on demand for a document."""
    token = _session_token(request_obj, authorization)
    session = await auth_service.validate_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    uow = uow_factory.create()
    with uow:
        doc = await uow.documents.get(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.user_id and doc.user_id != session.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this document")

        chunk_coll = await uow.chunks.get_by_document(document_id)
        if not chunk_coll:
            raise HTTPException(status_code=400, detail="Document has no chunks to extract concepts from")

        if isinstance(chunk_coll, ChunkCollection):
            raw_chunks = chunk_coll.chunks
        elif hasattr(chunk_coll, "chunks"):
            raw_chunks = tuple(chunk_coll.chunks)
            chunk_coll = ChunkCollection(chunks=raw_chunks)
        elif isinstance(chunk_coll, (list, tuple)):
            raw_chunks = tuple(chunk_coll)
            chunk_coll = ChunkCollection(chunks=raw_chunks)
        else:
            raw_chunks = ()

        if not raw_chunks:
            raise HTTPException(status_code=400, detail="Document has no chunks to extract concepts from")

    extraction_result = await extractor.extract(chunk_coll)

    import dataclasses
    concepts = [
        dataclasses.replace(c, document_id=document_id)
        if dataclasses.is_dataclass(c) and not isinstance(c, type)
        else c
        for c in extraction_result.graph.concepts
    ]
    relationships = [
        dataclasses.replace(r, document_id=document_id)
        if dataclasses.is_dataclass(r) and not isinstance(r, type)
        else r
        for r in extraction_result.graph.relationships
    ]

    with uow_factory.create() as uow:
        if concepts:
            await uow.concepts.save_all(concepts)
        if relationships:
            await uow.relationships.save_all(relationships)

    return KnowledgeGraph(concepts=tuple(concepts), relationships=tuple(relationships))


@knowledge_router.get("/{document_id}/query")
async def query_knowledge_graph(
    document_id: str,
    request_obj: Request,
    concept: str = Query(..., description="Concept to query"),
    depth: int = Query(1, ge=1, le=3),
    query_type: str = Query("neighbors", description="Query type"),
    authorization: str | None = Header(None, description="Bearer token"),
    auth_service=Depends(get_authentication_service),
    knowledge_service=Depends(get_knowledge_service),
) -> dict:
    """Query bounded subgraph around a concept."""
    token = _session_token(request_obj, authorization)
    session = await auth_service.validate_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    use_case = QueryKnowledgeGraphUseCase(knowledge_service=knowledge_service)
    req = QueryKnowledgeGraphRequest(
        document_id=document_id,
        user_id=session.user_id,
        query_type=query_type,
        concept=concept,
        depth=depth,
    )
    res = await use_case.execute(req)
    return res.to_dict()


@knowledge_router.get("/{document_id}/concepts", response_model=list[KnowledgeConcept])
async def get_knowledge_concepts(
    document_id: str,
    request_obj: Request,
    authorization: str | None = Header(None, description="Bearer token"),
    use_case: GetKnowledgeUseCase = Depends(get_knowledge_use_case),  # noqa: B008
) -> list[KnowledgeConcept]:
    request = GetKnowledgeRequest(
        document_id=document_id, token=_session_token(request_obj, authorization)
    )
    response = await use_case.execute(request)
    return list(response.graph.concepts)


@knowledge_router.get("/{document_id}/relationships", response_model=list[KnowledgeRelationship])
async def get_knowledge_relationships(
    document_id: str,
    request_obj: Request,
    authorization: str | None = Header(None, description="Bearer token"),
    use_case: GetKnowledgeUseCase = Depends(get_knowledge_use_case),  # noqa: B008
) -> list[KnowledgeRelationship]:
    request = GetKnowledgeRequest(
        document_id=document_id, token=_session_token(request_obj, authorization)
    )
    response = await use_case.execute(request)
    return list(response.graph.relationships)

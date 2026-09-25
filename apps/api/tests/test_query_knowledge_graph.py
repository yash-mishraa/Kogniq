import pytest
from datetime import datetime, UTC

from backend.services.knowledge_service import KnowledgeService
from application.learning.query_knowledge_graph import QueryKnowledgeGraphUseCase, QueryKnowledgeGraphRequest
from knowledge.graph import KnowledgeGraph
from knowledge.concept import KnowledgeConcept
from knowledge.relationship import KnowledgeRelationship
from knowledge.enums import ConceptType, RelationshipType
from knowledge.metadata import KnowledgeMetadata

class MockUoW:
    pass

class MockUoWFactory:
    def create(self):
        return MockUoW()

class MockKnowledgeService:
    def __init__(self, graph):
        self.graph = graph

    async def get_knowledge_graph(self, document_id: str, user_id: str | None = None) -> KnowledgeGraph:
        if document_id != "doc_1":
            raise Exception("not_found: Document not found")
        if user_id != "user_1":
            raise Exception("unauthorized: Not authorized to access this document")
        return self.graph

def make_concept(c_id: str, name: str, aliases: tuple = ()):
    return KnowledgeConcept(
        id=c_id,
        document_id="doc_1",
        name=name,
        description=f"Desc of {name}",
        concept_type=ConceptType.UNKNOWN,
        aliases=aliases,
        confidence=1.0,
        created_at=datetime.now(UTC),
        metadata=KnowledgeMetadata(source_document="doc_1", source_chunk="chunk_1", language="en", confidence=1.0, extraction_version="1.0", created_by="test")
    )

def make_rel(r_id: str, source: str, target: str, type: RelationshipType):
    return KnowledgeRelationship(
        id=r_id,
        document_id="doc_1",
        source_concept=source,
        target_concept=target,
        relationship_type=type,
        confidence=1.0,
        created_at=datetime.now(UTC),
        metadata=KnowledgeMetadata(source_document="doc_1", source_chunk="chunk_1", language="en", confidence=1.0, extraction_version="1.0", created_by="test")
    )

@pytest.fixture
def mock_graph():
    c_cnn = make_concept("c1", "CNN", ("Convolutional Neural Network",))
    c_backprop = make_concept("c2", "Backpropagation")
    c_grad = make_concept("c3", "Gradient Descent")
    c_math = make_concept("c4", "Calculus")
    
    r1 = make_rel("r1", "c1", "c2", RelationshipType.DEPENDS_ON)
    r2 = make_rel("r2", "c2", "c3", RelationshipType.DEPENDS_ON)
    r3 = make_rel("r3", "c3", "c4", RelationshipType.DEPENDS_ON)
    
    # Loop for cycle testing
    r4 = make_rel("r4", "c4", "c1", RelationshipType.RELATED_TO)
    
    return KnowledgeGraph(
        concepts=(c_cnn, c_backprop, c_grad, c_math),
        relationships=(r1, r2, r3, r4)
    )

@pytest.fixture
def use_case(mock_graph):
    svc = MockKnowledgeService(mock_graph)
    return QueryKnowledgeGraphUseCase(knowledge_service=svc)

@pytest.mark.asyncio
async def test_concept_resolution_exact(use_case):
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "prerequisites", "CNN")
    res = await use_case.execute(req)
    assert res.status == "success"
    assert res.resolved_concept["name"] == "CNN"

@pytest.mark.asyncio
async def test_concept_resolution_alias(use_case):
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "prerequisites", "convolutional neural network")
    res = await use_case.execute(req)
    assert res.status == "success"
    assert res.resolved_concept["name"] == "CNN"

@pytest.mark.asyncio
async def test_concept_resolution_not_found(use_case):
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "prerequisites", "Transformers")
    res = await use_case.execute(req)
    assert res.status == "not_found"

@pytest.mark.asyncio
async def test_prerequisites_depth_1(use_case):
    # CNN -> Backprop
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "prerequisites", "CNN", depth=1)
    res = await use_case.execute(req)
    assert res.status == "success"
    assert len(res.concepts) == 1
    assert res.concepts[0]["name"] == "Backpropagation"

@pytest.mark.asyncio
async def test_prerequisites_depth_2(use_case):
    # CNN -> Backprop -> Gradient Descent
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "prerequisites", "CNN", depth=2)
    res = await use_case.execute(req)
    assert res.status == "success"
    assert len(res.concepts) == 2
    names = [c["name"] for c in res.concepts]
    assert "Backpropagation" in names
    assert "Gradient Descent" in names

@pytest.mark.asyncio
async def test_dependents(use_case):
    # Calculus is depended on by Gradient Descent
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "dependents", "Calculus", depth=1)
    res = await use_case.execute(req)
    assert res.status == "success"
    assert len(res.concepts) == 1
    assert res.concepts[0]["name"] == "Gradient Descent"

@pytest.mark.asyncio
async def test_neighbors_with_cycle(use_case):
    # Neighbors of Calculus should include Gradient Descent (incoming DEPENDS_ON) and CNN (outgoing RELATED_TO)
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "neighbors", "Calculus", depth=1)
    res = await use_case.execute(req)
    assert res.status == "success"
    assert len(res.concepts) == 2
    names = [c["name"] for c in res.concepts]
    assert "Gradient Descent" in names
    assert "CNN" in names

@pytest.mark.asyncio
async def test_unauthorized(use_case):
    req = QueryKnowledgeGraphRequest("doc_1", "user_2", "prerequisites", "CNN")
    res = await use_case.execute(req)
    assert res.status == "error"
    assert "unauthorized" in res.message

@pytest.mark.asyncio
async def test_node_limit_truncation(use_case):
    # Temporarily force MAX_CONCEPTS to 1
    use_case.MAX_CONCEPTS = 1
    req = QueryKnowledgeGraphRequest("doc_1", "user_1", "prerequisites", "CNN", depth=2)
    res = await use_case.execute(req)
    assert res.truncated is True
    use_case.MAX_CONCEPTS = 20  # restore

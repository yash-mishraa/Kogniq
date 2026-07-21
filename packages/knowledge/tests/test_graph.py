import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.exceptions import InvalidGraphError
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship


@pytest.fixture
def valid_metadata() -> KnowledgeMetadata:
    return KnowledgeMetadata(
        source_document="doc_1",
        source_chunk="chunk_1",
        language="en",
        confidence=0.9,
        extraction_version="1.0",
        created_by="test",
    )


def test_valid_graph(valid_metadata: KnowledgeMetadata) -> None:
    c1 = KnowledgeConcept(
        id="c1",
        title="Concept 1",
        description="",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=valid_metadata,
    )
    c2 = KnowledgeConcept(
        id="c2",
        title="Concept 2",
        description="",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=valid_metadata,
    )
    r1 = KnowledgeRelationship(
        id="r1",
        source_concept="c1",
        target_concept="c2",
        relationship_type=RelationshipType.RELATED_TO,
        confidence=0.8,
        metadata=valid_metadata,
    )

    graph = KnowledgeGraph(concepts=(c1, c2), relationships=(r1,))

    assert graph.concept_count == 2
    assert graph.relationship_count == 1


def test_duplicate_concept_id_raises_error(valid_metadata: KnowledgeMetadata) -> None:
    c1 = KnowledgeConcept(
        id="c1",
        title="Concept 1",
        description="",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=valid_metadata,
    )
    c2 = KnowledgeConcept(
        id="c1",
        title="Concept 2 (Duplicate ID)",
        description="",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=valid_metadata,
    )

    with pytest.raises(InvalidGraphError, match="Duplicate concept id found: c1"):
        KnowledgeGraph(concepts=(c1, c2), relationships=())


def test_duplicate_relationship_id_raises_error(valid_metadata: KnowledgeMetadata) -> None:
    c1 = KnowledgeConcept(
        id="c1",
        title="Concept 1",
        description="",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=valid_metadata,
    )
    c2 = KnowledgeConcept(
        id="c2",
        title="Concept 2",
        description="",
        concept_type=ConceptType.FACT,
        aliases=(),
        metadata=valid_metadata,
    )
    r1 = KnowledgeRelationship(
        id="r1",
        source_concept="c1",
        target_concept="c2",
        relationship_type=RelationshipType.RELATED_TO,
        confidence=0.8,
        metadata=valid_metadata,
    )
    r2 = KnowledgeRelationship(
        id="r1",
        source_concept="c2",
        target_concept="c1",
        relationship_type=RelationshipType.DEPENDS_ON,
        confidence=0.7,
        metadata=valid_metadata,
    )

    with pytest.raises(InvalidGraphError, match="Duplicate relationship id found: r1"):
        KnowledgeGraph(concepts=(c1, c2), relationships=(r1, r2))

import pytest
from knowledge.enums import RelationshipType
from knowledge.exceptions import InvalidRelationshipError, KnowledgeDomainError
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


def test_valid_relationship(valid_metadata: KnowledgeMetadata) -> None:
    relationship = KnowledgeRelationship(
        id="r1",
        source_concept="c1",
        target_concept="c2",
        relationship_type=RelationshipType.DEPENDS_ON,
        confidence=0.8,
        metadata=valid_metadata,
    )
    assert relationship.id == "r1"
    assert relationship.source_concept == "c1"
    assert relationship.target_concept == "c2"
    assert relationship.relationship_type == RelationshipType.DEPENDS_ON
    assert relationship.confidence == 0.8


def test_self_referential_relationship_raises_error(valid_metadata: KnowledgeMetadata) -> None:
    with pytest.raises(
        InvalidRelationshipError, match="Source and target concepts cannot be the same"
    ):
        KnowledgeRelationship(
            id="r2",
            source_concept="c1",
            target_concept="c1",
            relationship_type=RelationshipType.RELATED_TO,
            confidence=0.9,
            metadata=valid_metadata,
        )


def test_invalid_relationship_confidence(valid_metadata: KnowledgeMetadata) -> None:
    with pytest.raises(InvalidRelationshipError, match=r"Confidence must be between 0\.0 and 1\.0"):
        KnowledgeRelationship(
            id="r3",
            source_concept="c1",
            target_concept="c2",
            relationship_type=RelationshipType.USES,
            confidence=1.5,
            metadata=valid_metadata,
        )


def test_invalid_metadata_confidence() -> None:
    with pytest.raises(KnowledgeDomainError, match=r"Confidence must be between 0\.0 and 1\.0"):
        KnowledgeMetadata(
            source_document="doc_1",
            source_chunk="chunk_1",
            language="en",
            confidence=-0.1,
            extraction_version="1.0",
            created_by="test",
        )

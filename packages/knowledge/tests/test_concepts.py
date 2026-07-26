from datetime import UTC, datetime

import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.exceptions import InvalidConceptError
from knowledge.metadata import KnowledgeMetadata


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


def test_valid_concept(valid_metadata: KnowledgeMetadata) -> None:
    concept = KnowledgeConcept(
        id="c1",
        document_id="doc_1",
        name="Concept 1",
        description="A test concept",
        concept_type=ConceptType.FACT,
        aliases=("C1", "First Concept"),
        confidence=0.9,
        created_at=datetime.now(UTC),
        metadata=valid_metadata,
    )
    assert concept.id == "c1"
    assert concept.name == "Concept 1"


def test_empty_name_raises_error(valid_metadata: KnowledgeMetadata) -> None:
    with pytest.raises(InvalidConceptError, match="Concept name cannot be empty"):
        KnowledgeConcept(
            id="c2",
            document_id="doc_1",
            name="",
            description="desc",
            concept_type=ConceptType.ALGORITHM,
            aliases=(),
            confidence=0.9,
            created_at=datetime.now(UTC),
            metadata=valid_metadata,
        )


def test_invalid_aliases_type(valid_metadata: KnowledgeMetadata) -> None:
    with pytest.raises(InvalidConceptError, match="Aliases must be an immutable tuple"):
        KnowledgeConcept(
            id="c3",
            document_id="doc_1",
            name="Concept 3",
            description="desc",
            concept_type=ConceptType.THEORY,
            aliases=["C3"],  # type: ignore
            confidence=0.9,
            created_at=datetime.now(UTC),
            metadata=valid_metadata,
        )

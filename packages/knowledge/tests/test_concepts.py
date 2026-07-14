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
        title="Valid Concept",
        description="A valid description.",
        concept_type=ConceptType.FACT,
        aliases=("Alias 1", "Alias 2"),
        metadata=valid_metadata,
    )
    assert concept.id == "c1"
    assert concept.title == "Valid Concept"
    assert concept.concept_type == ConceptType.FACT
    assert len(concept.aliases) == 2


def test_empty_title_raises_error(valid_metadata: KnowledgeMetadata) -> None:
    with pytest.raises(InvalidConceptError, match="Concept title cannot be empty"):
        KnowledgeConcept(
            id="c2",
            title="",
            description="Empty title.",
            concept_type=ConceptType.FACT,
            aliases=(),
            metadata=valid_metadata,
        )


def test_invalid_aliases_type(valid_metadata: KnowledgeMetadata) -> None:
    with pytest.raises(InvalidConceptError, match="Aliases must be an immutable tuple"):
        KnowledgeConcept(
            id="c3",
            title="Valid Title",
            description="Invalid aliases type.",
            concept_type=ConceptType.FACT,
            aliases=["List", "not", "allowed"],  # type: ignore[arg-type]
            metadata=valid_metadata,
        )

import sqlite3
from datetime import UTC, datetime

import pytest
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship
from persistence.sqlite.concept_repository import SQLiteConceptRepository
from persistence.sqlite.relationship_repository import SQLiteRelationshipRepository
from persistence.sqlite.schema import init_db


@pytest.fixture
def sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


@pytest.fixture
def concept_repo(sqlite_conn: sqlite3.Connection) -> SQLiteConceptRepository:
    return SQLiteConceptRepository(sqlite_conn)


@pytest.fixture
def relationship_repo(sqlite_conn: sqlite3.Connection) -> SQLiteRelationshipRepository:
    return SQLiteRelationshipRepository(sqlite_conn)


# --- Test Concept Repository ---
@pytest.mark.asyncio
async def test_concept_repository_operations(
    concept_repo: SQLiteConceptRepository,
    sqlite_conn: sqlite3.Connection,  # noqa: ARG001
) -> None:
    meta = KnowledgeMetadata(
        source_document="doc-3",
        source_chunk="c1",
        language="en",
        confidence=0.9,
        extraction_version="1",
        created_by="test",
    )
    c1 = KnowledgeConcept(
        id="c1",
        document_id="doc-3",
        name="test",
        description="desc",
        concept_type=ConceptType.FACT,
        aliases=("alias1",),
        confidence=0.9,
        created_at=datetime.now(UTC),
        metadata=meta,
    )

    # Save new
    res = await concept_repo.save_all([c1])
    assert res.is_new is True

    # Get by document
    retrieved = await concept_repo.get_by_document("doc-3")
    assert len(retrieved) == 1
    assert retrieved[0].id == "c1"
    assert retrieved[0].name == "test"
    assert retrieved[0].description == "desc"
    assert retrieved[0].concept_type == ConceptType.FACT
    assert "alias1" in retrieved[0].aliases

    # Statistics
    stats = await concept_repo.statistics()
    assert stats.total_items == 1

    # Overwrite (save_all should be idempotent)
    c1_updated = KnowledgeConcept(
        id="c1",
        document_id="doc-3",
        name="test_updated",
        description="desc_updated",
        concept_type=ConceptType.FACT,
        aliases=(),
        confidence=0.9,
        created_at=datetime.now(UTC),
        metadata=meta,
    )
    await concept_repo.save_all([c1_updated])

    retrieved2 = await concept_repo.get_by_document("doc-3")
    assert len(retrieved2) == 1
    assert retrieved2[0].name == "test_updated"
    assert retrieved2[0].description == "desc_updated"

    # Delete
    del_res = await concept_repo.delete("doc-3")
    assert del_res.was_deleted is True

    retrieved_after_del = await concept_repo.get_by_document("doc-3")
    assert len(retrieved_after_del) == 0

    # Delete non-existent
    del_res2 = await concept_repo.delete("doc-3")
    assert del_res2.was_deleted is False


# --- Test Relationship Repository ---
@pytest.mark.asyncio
async def test_relationship_repository_operations(
    relationship_repo: SQLiteRelationshipRepository,
    sqlite_conn: sqlite3.Connection,  # noqa: ARG001
) -> None:
    meta = KnowledgeMetadata(
        source_document="doc-3",
        source_chunk="c1",
        language="en",
        confidence=0.9,
        extraction_version="1",
        created_by="test",
    )
    r1 = KnowledgeRelationship(
        id="r1",
        document_id="doc-3",
        source_concept="c1",
        target_concept="c2",
        relationship_type=RelationshipType.RELATED_TO,
        confidence=0.9,
        created_at=datetime.now(UTC),
        metadata=meta,
    )

    # Save new
    res = await relationship_repo.save_all([r1])
    assert res.is_new is True

    # Get by document
    retrieved = await relationship_repo.get_by_document("doc-3")
    assert len(retrieved) == 1
    assert retrieved[0].id == "r1"
    assert retrieved[0].source_concept == "c1"
    assert retrieved[0].target_concept == "c2"

    # Statistics
    stats = await relationship_repo.statistics()
    assert stats.total_items == 1

    # Overwrite (idempotent)
    r1_updated = KnowledgeRelationship(
        id="r1",
        document_id="doc-3",
        source_concept="c1",
        target_concept="c3",
        relationship_type=RelationshipType.RELATED_TO,
        confidence=0.95,
        created_at=datetime.now(UTC),
        metadata=meta,
    )
    await relationship_repo.save_all([r1_updated])

    retrieved2 = await relationship_repo.get_by_document("doc-3")
    assert len(retrieved2) == 1
    assert retrieved2[0].target_concept == "c3"
    assert retrieved2[0].confidence == 0.95

    # Delete
    del_res = await relationship_repo.delete("doc-3")
    assert del_res.was_deleted is True

    retrieved_after_del = await relationship_repo.get_by_document("doc-3")
    assert len(retrieved_after_del) == 0

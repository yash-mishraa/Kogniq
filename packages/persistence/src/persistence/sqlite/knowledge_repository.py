import sqlite3
from typing import Any

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship

from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractKnowledgeRepository
from persistence.sqlite.serialization import deserialize, serialize


class SQLiteKnowledgeRepository(AbstractKnowledgeRepository):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _parse_metadata(self, meta_raw: dict[str, Any]) -> KnowledgeMetadata:
        return KnowledgeMetadata(
            source_document=meta_raw["source_document"],
            source_chunk=meta_raw["source_chunk"],
            language=meta_raw["language"],
            confidence=meta_raw["confidence"],
            extraction_version=meta_raw["extraction_version"],
            created_by=meta_raw["created_by"],
        )

    async def save(self, document_id: str, graph: KnowledgeGraph) -> SaveResult:
        row = self._conn.execute(
            "SELECT 1 FROM knowledge_graphs WHERE document_id = ?", (document_id,)
        ).fetchone()
        is_new = row is None

        self._conn.execute(
            """
            INSERT INTO knowledge_graphs (document_id, concepts_json, relationships_json)
            VALUES (?, ?, ?)
            ON CONFLICT(document_id) DO UPDATE SET
                concepts_json=excluded.concepts_json,
                relationships_json=excluded.relationships_json
            """,
            (document_id, serialize(graph.concepts), serialize(graph.relationships)),
        )
        return SaveResult(id=document_id, is_new=is_new)

    async def get(self, document_id: str) -> KnowledgeGraph | None:
        row = self._conn.execute(
            "SELECT concepts_json, relationships_json FROM knowledge_graphs WHERE document_id = ?",
            (document_id,),
        ).fetchone()

        if not row:
            return None

        concepts_raw = deserialize(row["concepts_json"])
        relationships_raw = deserialize(row["relationships_json"])

        concepts = []
        for c in concepts_raw:
            c["concept_type"] = ConceptType[c["concept_type"]]
            c["aliases"] = tuple(c["aliases"])
            c["metadata"] = self._parse_metadata(c["metadata"])
            concepts.append(KnowledgeConcept(**c))

        relationships = []
        for r in relationships_raw:
            r["relationship_type"] = RelationshipType[r["relationship_type"]]
            r["metadata"] = self._parse_metadata(r["metadata"])
            relationships.append(KnowledgeRelationship(**r))

        return KnowledgeGraph(concepts=tuple(concepts), relationships=tuple(relationships))

    async def delete(self, document_id: str) -> DeleteResult:
        cursor = self._conn.execute(
            "DELETE FROM knowledge_graphs WHERE document_id = ?", (document_id,)
        )
        return DeleteResult(id=document_id, was_deleted=cursor.rowcount > 0)

    async def statistics(self) -> RepositoryStatistics:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM knowledge_graphs").fetchone()
        return RepositoryStatistics(total_items=row["cnt"])

import json
import logging
import sqlite3
from collections.abc import Sequence
from datetime import datetime

from knowledge.enums import RelationshipType
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship

from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractRelationshipRepository

logger = logging.getLogger(__name__)


class SQLiteRelationshipRepository(AbstractRelationshipRepository):
    """SQLite implementation of the relationship repository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    async def save_all(self, relationships: Sequence[KnowledgeRelationship]) -> SaveResult:
        if not relationships:
            return SaveResult(id="batch", is_new=True)

        try:
            cursor = self._conn.cursor()
            for rel in relationships:
                metadata_json = json.dumps(
                    {
                        "source_document": rel.metadata.source_document,
                        "source_chunk": rel.metadata.source_chunk,
                        "language": rel.metadata.language,
                        "confidence": rel.metadata.confidence,
                        "extraction_version": rel.metadata.extraction_version,
                        "created_by": rel.metadata.created_by,
                    }
                )

                cursor.execute(
                    """
                    INSERT INTO knowledge_relationships (
                        id, document_id, source_concept, target_concept, 
                        relationship_type, confidence, created_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        source_concept = excluded.source_concept,
                        target_concept = excluded.target_concept,
                        relationship_type = excluded.relationship_type,
                        confidence = excluded.confidence,
                        created_at = excluded.created_at,
                        metadata_json = excluded.metadata_json
                    """,
                    (
                        rel.id,
                        rel.document_id,
                        rel.source_concept,
                        rel.target_concept,
                        rel.relationship_type.name,
                        rel.confidence,
                        rel.created_at.isoformat(),
                        metadata_json,
                    ),
                )
            return SaveResult(id=f"batch_{len(relationships)}", is_new=True)
        except sqlite3.Error as e:
            logger.error("Failed to save relationships: %s", e)
            return SaveResult(id="", is_new=False)

    async def get_by_document(self, document_id: str) -> Sequence[KnowledgeRelationship]:
        try:
            cursor = self._conn.execute(
                "SELECT * FROM knowledge_relationships WHERE document_id = ?", (document_id,)
            )
            rows = cursor.fetchall()

            relationships = []
            for row in rows:
                r_id, doc_id, source, target, r_type, conf, created_at, metadata_json = row
                meta_dict = json.loads(metadata_json)
                metadata = KnowledgeMetadata(
                    source_document=meta_dict["source_document"],
                    source_chunk=meta_dict["source_chunk"],
                    language=meta_dict["language"],
                    confidence=meta_dict["confidence"],
                    extraction_version=meta_dict["extraction_version"],
                    created_by=meta_dict["created_by"],
                )
                relationships.append(
                    KnowledgeRelationship(
                        id=r_id,
                        document_id=doc_id,
                        source_concept=source,
                        target_concept=target,
                        relationship_type=RelationshipType[r_type],
                        confidence=conf,
                        created_at=datetime.fromisoformat(created_at),
                        metadata=metadata,
                    )
                )
            return relationships
        except sqlite3.Error as e:
            logger.error("Failed to fetch relationships for document %s: %s", document_id, e)
            return []

    async def delete(self, document_id: str) -> DeleteResult:
        try:
            cursor = self._conn.execute(
                "DELETE FROM knowledge_relationships WHERE document_id = ?", (document_id,)
            )
            return DeleteResult(id=document_id, was_deleted=(cursor.rowcount > 0))
        except sqlite3.Error as e:
            logger.error("Failed to delete relationships for document %s: %s", document_id, e)
            return DeleteResult(id=document_id, was_deleted=False)

    async def statistics(self) -> RepositoryStatistics:
        try:
            cursor = self._conn.execute(
                "SELECT COUNT(*), COUNT(DISTINCT document_id) FROM knowledge_relationships"
            )
            total, _docs = cursor.fetchone()
            return RepositoryStatistics(total_items=total, storage_size_bytes=total * 1024)
        except sqlite3.Error:
            return RepositoryStatistics(total_items=0, storage_size_bytes=0)

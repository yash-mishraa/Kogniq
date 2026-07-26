import json
import logging
import sqlite3
from collections.abc import Sequence
from datetime import datetime

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType
from knowledge.metadata import KnowledgeMetadata

from persistence.models import DeleteResult, RepositoryStatistics, SaveResult
from persistence.repositories.base import AbstractConceptRepository

logger = logging.getLogger(__name__)


class SQLiteConceptRepository(AbstractConceptRepository):
    """SQLite implementation of the concept repository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    async def save_all(self, concepts: Sequence[KnowledgeConcept]) -> SaveResult:
        if not concepts:
            return SaveResult(id="batch", is_new=True)

        try:
            cursor = self._conn.cursor()
            for concept in concepts:
                metadata_json = json.dumps(
                    {
                        "source_document": concept.metadata.source_document,
                        "source_chunk": concept.metadata.source_chunk,
                        "language": concept.metadata.language,
                        "confidence": concept.metadata.confidence,
                        "extraction_version": concept.metadata.extraction_version,
                        "created_by": concept.metadata.created_by,
                    }
                )
                aliases_json = json.dumps(concept.aliases)

                cursor.execute(
                    """
                    INSERT INTO knowledge_concepts (
                        id, document_id, name, description, concept_type, 
                        aliases_json, confidence, created_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        description = excluded.description,
                        concept_type = excluded.concept_type,
                        aliases_json = excluded.aliases_json,
                        confidence = excluded.confidence,
                        created_at = excluded.created_at,
                        metadata_json = excluded.metadata_json
                    """,
                    (
                        concept.id,
                        concept.document_id,
                        concept.name,
                        concept.description,
                        concept.concept_type.name,
                        aliases_json,
                        concept.confidence,
                        concept.created_at.isoformat(),
                        metadata_json,
                    ),
                )
            return SaveResult(id=f"batch_{len(concepts)}", is_new=True)
        except sqlite3.Error as e:
            logger.error(
                "Failed to save concepts for document_id %s: %s",
                concepts[0].document_id,
                e,
            )
            return SaveResult(id="", is_new=False)

    async def get_by_document(self, document_id: str) -> Sequence[KnowledgeConcept]:
        try:
            cursor = self._conn.execute(
                "SELECT * FROM knowledge_concepts WHERE document_id = ?", (document_id,)
            )
            rows = cursor.fetchall()

            concepts = []
            for row in rows:
                c_id, doc_id, name, desc, c_type, aliases_json, conf, created_at, metadata_json = (
                    row
                )
                meta_dict = json.loads(metadata_json)
                metadata = KnowledgeMetadata(
                    source_document=meta_dict["source_document"],
                    source_chunk=meta_dict["source_chunk"],
                    language=meta_dict["language"],
                    confidence=meta_dict["confidence"],
                    extraction_version=meta_dict["extraction_version"],
                    created_by=meta_dict["created_by"],
                )
                aliases = tuple(json.loads(aliases_json))
                concepts.append(
                    KnowledgeConcept(
                        id=c_id,
                        document_id=doc_id,
                        name=name,
                        description=desc,
                        concept_type=ConceptType[c_type],
                        aliases=aliases,
                        confidence=conf,
                        created_at=datetime.fromisoformat(created_at),
                        metadata=metadata,
                    )
                )
            return concepts
        except sqlite3.Error as e:
            logger.error("Failed to fetch concepts for document %s: %s", document_id, e)
            return []

    async def delete(self, document_id: str) -> DeleteResult:
        try:
            cursor = self._conn.execute(
                "DELETE FROM knowledge_concepts WHERE document_id = ?", (document_id,)
            )
            return DeleteResult(id=document_id, was_deleted=(cursor.rowcount > 0))
        except sqlite3.Error as e:
            logger.error("Failed to delete concepts for document %s: %s", document_id, e)
            return DeleteResult(id=document_id, was_deleted=False)

    async def statistics(self) -> RepositoryStatistics:
        try:
            cursor = self._conn.execute(
                "SELECT COUNT(*), COUNT(DISTINCT document_id) FROM knowledge_concepts"
            )
            total, _docs = cursor.fetchone()
            return RepositoryStatistics(total_items=total, storage_size_bytes=total * 1024)
        except sqlite3.Error:
            return RepositoryStatistics(total_items=0, storage_size_bytes=0)

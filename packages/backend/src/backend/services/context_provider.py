from datetime import UTC, datetime

from backend.core.exceptions import BackendError
from knowledge.graph import KnowledgeGraph

from content.chunking.chunk import Chunk
from content.chunking.collection import ChunkCollection
from content.chunking.metadata import ChunkMetadata
from content.chunking.statistics import ChunkStatistics
from learning_content.generators.base.models import GenerationContext


class LearningContextProvider:
    """
    Resolves the domain objects required for learning generation.
    Today it generates fakes. Tomorrow it queries a database.
    """

    def resolve_context(self, document_id: str) -> GenerationContext:
        """
        Loads the chunks and knowledge graph for the specified document ID.
        """
        # Validate that we don't proceed with unsupported IDs
        if document_id == "unsupported":
            raise BackendError(
                "document_not_found", f"Document {document_id} not found", status_code=404
            )

        if not document_id:
            raise BackendError("invalid_request", "document_id cannot be empty", status_code=400)

        chunk_mock = Chunk(
            id=f"chunk-{document_id}-1",
            document_id=document_id,
            chunk_index=0,
            text="This is simulated chunk content for generation.",
            metadata=ChunkMetadata(
                processor="mock", document_version="v1", source="mock", checksum="123"
            ),
            statistics=ChunkStatistics(
                character_count=45,
                line_count=1,
                word_count=7,
                estimated_tokens=10,
                processing_timestamp=datetime.now(UTC),
                confidence=1.0,
            ),
            created_at=datetime.now(UTC),
        )

        chunks = ChunkCollection(chunks=(chunk_mock,))
        graph = KnowledgeGraph(concepts=(), relationships=())

        return GenerationContext(chunks=chunks, graph=graph)

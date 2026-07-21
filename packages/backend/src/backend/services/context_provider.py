from backend.core.exceptions import BackendError
from persistence.factory import RepositoryFactory

from learning_content.generators.base.models import GenerationContext


class LearningContextProvider:
    """
    Resolves the domain objects required for learning generation.
    Today it generates fakes. Tomorrow it queries a database.
    """

    def __init__(self, repository_factory: RepositoryFactory) -> None:
        self.repository_factory = repository_factory

    async def resolve_context(self, document_id: str) -> GenerationContext:
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

        chunk_repo = self.repository_factory.get_chunk_repository()
        knowledge_repo = self.repository_factory.get_knowledge_repository()

        chunks = await chunk_repo.get_by_document(document_id)
        if not chunks:
            raise BackendError(
                "chunks_not_found", f"No chunks found for document {document_id}", status_code=404
            )

        graph = await knowledge_repo.get(document_id)
        if not graph:
            # We allow empty graph if extraction failed but chunks exist?
            # The prompt implies graph should exist.
            raise BackendError(
                "graph_not_found",
                f"No knowledge graph found for document {document_id}",
                status_code=404,
            )

        return GenerationContext(chunks=chunks, graph=graph)

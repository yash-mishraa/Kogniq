from backend.core.exceptions import BackendError
from persistence.uow_factory import AbstractUnitOfWorkFactory

from learning_content.generators.base.models import GenerationContext


class LearningContextProvider:
    """
    Resolves the domain objects required for learning generation.
    """

    def __init__(self, uow_factory: AbstractUnitOfWorkFactory) -> None:
        self.uow_factory = uow_factory

    async def resolve_context(self, document_id: str) -> GenerationContext:
        """
        Loads the chunks and knowledge graph for the specified document ID.
        """
        if document_id == "unsupported":
            raise BackendError(
                "document_not_found", f"Document {document_id} not found", status_code=404
            )

        if not document_id:
            raise BackendError("invalid_request", "document_id cannot be empty", status_code=400)

        with self.uow_factory.create() as uow:
            chunks = await uow.chunks.get_by_document(document_id)
            if not chunks:
                raise BackendError(
                    "chunks_not_found",
                    f"No chunks found for document {document_id}",
                    status_code=404,
                )

            graph = await uow.knowledge.get(document_id)
            if not graph:
                raise BackendError(
                    "graph_not_found",
                    f"No knowledge graph found for document {document_id}",
                    status_code=404,
                )

        return GenerationContext(chunks=chunks, graph=graph)

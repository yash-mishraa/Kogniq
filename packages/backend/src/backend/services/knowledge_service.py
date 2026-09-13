from knowledge.graph import KnowledgeGraph
from persistence.uow_factory import AbstractUnitOfWorkFactory


class KnowledgeService:
    def __init__(self, uow_factory: AbstractUnitOfWorkFactory) -> None:
        self.uow_factory = uow_factory

    async def get_knowledge_graph(
        self, document_id: str, user_id: str | None = None
    ) -> KnowledgeGraph:
        """Fetch all concepts and relationships for a document to construct the knowledge graph."""
        uow = self.uow_factory.create()
        with uow:
            doc = await uow.documents.get(document_id)
            if not doc:
                from backend.core.exceptions import BackendError

                raise BackendError("not_found", "Document not found", status_code=404)
            if doc.user_id and doc.user_id != user_id:
                from backend.core.exceptions import BackendError

                raise BackendError(
                    "unauthorized", "Not authorized to access this document", status_code=403
                )

            concepts = await uow.concepts.get_by_document(document_id)
            relationships = await uow.relationships.get_by_document(document_id)

        return KnowledgeGraph(
            concepts=tuple(concepts),
            relationships=tuple(relationships),
        )

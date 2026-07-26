from knowledge.graph import KnowledgeGraph
from persistence.uow_factory import AbstractUnitOfWorkFactory


class KnowledgeService:
    def __init__(self, uow_factory: AbstractUnitOfWorkFactory) -> None:
        self.uow_factory = uow_factory

    async def get_knowledge_graph(self, document_id: str) -> KnowledgeGraph:
        """Fetch all concepts and relationships for a document to construct the knowledge graph."""
        uow = self.uow_factory.create()
        with uow:
            concepts = await uow.concepts.get_by_document(document_id)
            relationships = await uow.relationships.get_by_document(document_id)

        return KnowledgeGraph(
            concepts=tuple(concepts),
            relationships=tuple(relationships),
        )

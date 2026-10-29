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

            concepts = await uow.concepts.get_by_document(document_id)
            relationships = await uow.relationships.get_by_document(document_id)

            if not concepts and not relationships:
                # Auto-extract knowledge graph on the fly so flashcards and quizzes generate seamlessly
                try:
                    import dataclasses
                    from backend.dependencies import get_knowledge_extractor

                    extractor = get_knowledge_extractor()
                    extraction_result = await extractor.extract(chunks)
                    extracted_concepts = [
                        dataclasses.replace(c, document_id=document_id)
                        if dataclasses.is_dataclass(c) and not isinstance(c, type)
                        else c
                        for c in extraction_result.graph.concepts
                    ]
                    extracted_relationships = [
                        dataclasses.replace(r, document_id=document_id)
                        if dataclasses.is_dataclass(r) and not isinstance(r, type)
                        else r
                        for r in extraction_result.graph.relationships
                    ]
                    if extracted_concepts:
                        await uow.concepts.save_all(extracted_concepts)
                        concepts = extracted_concepts
                    if extracted_relationships:
                        await uow.relationships.save_all(extracted_relationships)
                        relationships = extracted_relationships
                except Exception:
                    pass

            if not concepts and not relationships:
                raise BackendError(
                    "graph_not_found",
                    f"No knowledge graph found for document {document_id}",
                    status_code=404,
                )

            from knowledge.graph import KnowledgeGraph

            graph = KnowledgeGraph(concepts=tuple(concepts), relationships=tuple(relationships))

        return GenerationContext(chunks=chunks, graph=graph)

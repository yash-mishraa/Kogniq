from typing import Any

from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from persistence.uow_factory import AbstractUnitOfWorkFactory

from content.chunking.collection import ChunkCollection
from pipeline.interfaces import PipelineContext, RetryPolicy, StageResult


class ExtractionRetryPolicy:
    @property
    def max_retries(self) -> int:
        return 2

    @property
    def delay_seconds(self) -> int:
        return 2


class ExtractionStageResult:
    def __init__(self, success: bool, data: dict[str, Any], error: str | None = None) -> None:
        self._success = success
        self._data = data
        self._error = error

    @property
    def success(self) -> bool:
        return self._success

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def error(self) -> str | None:
        return self._error


class KnowledgeExtractionStage:
    def __init__(
        self,
        extractor: AbstractKnowledgeExtractor,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.extractor = extractor
        self.uow_factory = uow_factory
        self._retry_policy = ExtractionRetryPolicy()

    @property
    def stage_name(self) -> str:
        return "KnowledgeExtraction"

    async def can_skip(self, context: PipelineContext) -> bool:
        chunk_collection: ChunkCollection | None = context.get("chunk_collection")
        return bool(not chunk_collection or not chunk_collection.chunks)

    async def execute(self, context: PipelineContext) -> StageResult:
        chunk_collection: ChunkCollection | None = context.get("chunk_collection")
        if not chunk_collection:
            return ExtractionStageResult(False, {}, "No chunk_collection provided in context")

        if not chunk_collection.chunks:
            return ExtractionStageResult(True, {"message": "No chunks to extract knowledge from"})

        try:
            # 1. Extract knowledge graph
            extraction_result = await self.extractor.extract(chunk_collection)

            document_id = context.get("document_id") or "unknown-doc"

            # Replace document_id in concepts and relationships
            import dataclasses

            concepts = [
                dataclasses.replace(c, document_id=document_id)
                for c in extraction_result.graph.concepts
            ]
            relationships = [
                dataclasses.replace(r, document_id=document_id)
                for r in extraction_result.graph.relationships
            ]

            # 2. Persist concepts and relationships
            uow = self.uow_factory.create()
            with uow:
                # Save concepts
                if concepts:
                    await uow.concepts.save_all(concepts)

                # Save relationships
                if relationships:
                    await uow.relationships.save_all(relationships)

            # 3. Add to context
            context.set("knowledge_graph", extraction_result.graph)

            return ExtractionStageResult(
                success=True,
                data={
                    "concepts_extracted": len(concepts),
                    "relationships_extracted": len(relationships),
                    "extractor": extraction_result.extractor_name,
                    "processing_time_ms": extraction_result.processing_time_ms,
                },
            )
        except Exception as e:
            # We return True but include the error in the data or as an error string,
            import logging

            logging.getLogger(__name__).error(
                "Knowledge extraction failed with exception: %r", e, exc_info=True
            )
            return ExtractionStageResult(
                success=True,
                data={"warning": f"Knowledge extraction failed: {e!s}"},
            )

    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

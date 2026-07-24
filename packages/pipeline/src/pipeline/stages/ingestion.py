from typing import Any

from persistence.uow_factory import AbstractUnitOfWorkFactory

from content.chunking.engine import HybridChunkEngine
from content.plugins.registry import ProcessorRegistry
from content.resource.handle import ResourceHandle
from pipeline.interfaces import PipelineContext, RetryPolicy, StageResult


class IngestionRetryPolicy:
    @property
    def max_retries(self) -> int:
        return 0

    @property
    def delay_seconds(self) -> int:
        return 0


class IngestionStageResult:
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


class IngestionStage:
    def __init__(
        self,
        processor_registry: ProcessorRegistry,
        chunk_engine: HybridChunkEngine,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.processor_registry = processor_registry
        self.chunk_engine = chunk_engine
        self.uow_factory = uow_factory
        self._retry_policy = IngestionRetryPolicy()

    @property
    def stage_name(self) -> str:
        return "Ingestion"

    async def can_skip(self, context: PipelineContext) -> bool:  # noqa: ARG002
        return False

    async def execute(self, context: PipelineContext) -> StageResult:
        handle: ResourceHandle | None = context.get("resource_handle")
        if not handle:
            return IngestionStageResult(False, {}, "No resource_handle provided")

        try:
            processor = self.processor_registry.processor_for_resource(handle)
            document = processor.process(handle)
            chunks = self.chunk_engine.chunk(document)

            uow = self.uow_factory.create()
            with uow:
                await uow.documents.save(document)
                await uow.chunks.save(chunks)

            context.set("document_id", document.id)
            context.set("chunk_collection", chunks)

            return IngestionStageResult(
                success=True,
                data={
                    "document_id": document.id,
                    "processor_name": processor.processor_info.name,
                    "chunk_count": chunks.total_chunks,
                },
            )
        except Exception as e:
            return IngestionStageResult(False, {}, str(e))

    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

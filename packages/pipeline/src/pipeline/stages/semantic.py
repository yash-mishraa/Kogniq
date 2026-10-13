import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from persistence.uow_factory import AbstractUnitOfWorkFactory

from content.normalized.semantics import DocumentSemantics
from pipeline.interfaces import PipelineContext, PipelineStage, RetryPolicy, StageResult

logger = logging.getLogger(__name__)

class NoRetryPolicy(RetryPolicy):
    @property
    def max_retries(self) -> int: return 0
    @property
    def delay_seconds(self) -> int: return 0

class SemanticStageResult(StageResult):
    def __init__(self, success: bool, data: dict[str, Any], error: str | None = None) -> None:
        self._success = success
        self._data = data
        self._error = error
    @property
    def success(self) -> bool: return self._success
    @property
    def data(self) -> dict[str, Any]: return self._data
    @property
    def error(self) -> str | None: return self._error

class SemanticExtractionStage(PipelineStage):
    def __init__(self, uow_factory: AbstractUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory
        self._extractor_version = "2"  # P1-D2 version
        self._retry_policy = NoRetryPolicy()

    @property
    def stage_name(self) -> str:
        return "SemanticExtraction"

    async def can_skip(self, context: PipelineContext) -> bool:
        return False

    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

    async def execute(self, context: PipelineContext) -> StageResult:
        document_id = context.get("document_id")
        if not document_id:
            # Fallback for older tests
            document_id = getattr(context, "document_id", None)
            if not document_id:
                raise Exception("document_id not set in context")

        semantic_id = str(uuid.uuid4())
        
        running_semantics = DocumentSemantics(
            id=semantic_id,
            document_id=document_id,
            semantic_version=self._extractor_version,
            status="running",
            is_active=False,
            semantics_json=json.dumps({"info": "Processing started"}),
            created_at=datetime.now(UTC)
        )

        with self._uow_factory.create() as uow:
            await uow.semantics.save(running_semantics)
            uow.commit()
        
        try:
            import asyncio

            from content.processors.pdf.semantic_extractor import SemanticExtractor
            
            handle = context.get("resource_handle")
            if not handle:
                raise Exception("resource_handle not set in context")
                
            with handle.stream_reference.open_stream() as f:
                stream_bytes = f.read()

            extractor = SemanticExtractor(stream_bytes, document_id)
            extraction_result = await asyncio.to_thread(extractor.extract)

            success_semantics = DocumentSemantics(
                id=semantic_id,
                document_id=document_id,
                semantic_version=self._extractor_version,
                status="completed",
                is_active=False,
                semantics_json=json.dumps(extraction_result),
                created_at=running_semantics.created_at,
                completed_at=datetime.now(UTC)
            )

            with self._uow_factory.create() as uow:
                await uow.semantics.save(success_semantics)
                uow.commit()

            with self._uow_factory.create() as uow:
                activated = await uow.semantics.activate_version(document_id, semantic_id)
                if activated:
                    logger.info("Activated new semantic version %s for document %s", self._extractor_version, document_id)
                uow.commit()
            
            return SemanticStageResult(True, {"semantic_id": semantic_id})

        except Exception as e:
            logger.error(
                "semantic_extraction_failed",
                extra={"document_id": document_id, "error": str(e)},
                exc_info=True
            )
            failed_semantics = DocumentSemantics(
                id=semantic_id,
                document_id=document_id,
                semantic_version=self._extractor_version,
                status="failed",
                is_active=False,
                semantics_json=json.dumps({
                    "error_code": "SEMANTIC_EXTRACTION_FAILED",
                    "message": "Semantic document processing failed."
                }),
                created_at=running_semantics.created_at,
                completed_at=datetime.now(UTC)
            )
            with self._uow_factory.create() as uow:
                await uow.semantics.save(failed_semantics)
                uow.commit()
            
            # Fail-open: Return success=True so pipeline continues!
            # The document baseline remains unaffected.
            return SemanticStageResult(True, {"semantic_id": semantic_id, "warning": "Semantic extraction failed"})

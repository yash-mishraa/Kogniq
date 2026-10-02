import logging
import uuid
import traceback
from datetime import datetime, timezone
import json
from typing import Any

from persistence.uow_factory import AbstractUnitOfWorkFactory
from content.normalized.semantics import DocumentSemantics
from pipeline.interfaces import PipelineStage, PipelineContext, StageResult, RetryPolicy

logger = logging.getLogger(__name__)

class NoRetryPolicy(RetryPolicy):
    @property
    def max_retries(self) -> int: return 0
    @property
    def delay_seconds(self) -> int: return 0

class SemanticStageResult(StageResult):
    def __init__(self, success: bool, data: dict[str, Any], error: str | None = None):
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
        self._extractor_version = "1"
        self._retry_policy = NoRetryPolicy()

    @property
    def stage_name(self) -> str:
        return "SemanticExtraction"

    async def can_skip(self, context: PipelineContext) -> bool:
        return False

    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

    async def execute(self, context: PipelineContext) -> StageResult:
        document_id = context.document_id
        semantic_id = str(uuid.uuid4())
        
        running_semantics = DocumentSemantics(
            id=semantic_id,
            document_id=document_id,
            semantic_version=self._extractor_version,
            status="running",
            is_active=False,
            semantics_json=json.dumps({"info": "Processing started"}),
            created_at=datetime.now(timezone.utc)
        )

        with self._uow_factory.create() as uow:
            await uow.semantics.save(running_semantics)
            uow.commit()
        
        try:
            success_semantics = DocumentSemantics(
                id=semantic_id,
                document_id=document_id,
                semantic_version=self._extractor_version,
                status="completed",
                is_active=False,
                semantics_json=json.dumps({
                    "schema_version": 1,
                    "sections": [],
                    "figures": []
                }),
                created_at=running_semantics.created_at,
                completed_at=datetime.now(timezone.utc)
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
                completed_at=datetime.now(timezone.utc)
            )
            with self._uow_factory.create() as uow:
                await uow.semantics.save(failed_semantics)
                uow.commit()
            
            # Fail-open: Return success=True so pipeline continues!
            # The document baseline remains unaffected.
            return SemanticStageResult(True, {"semantic_id": semantic_id, "warning": "Semantic extraction failed"})

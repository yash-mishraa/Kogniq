import logging
from typing import Any

from backend.schemas.document import DocumentInput
from backend.services.document_service import DocumentService

from jobs.interfaces import AbstractJobManager
from jobs.models import Job, JobResult

logger = logging.getLogger(__name__)


class JobService:
    """
    Orchestrates job execution.
    Strictly coordinates between the API boundary and domain logic.
    """

    def __init__(self, job_manager: AbstractJobManager, document_service: DocumentService) -> None:
        self._manager = job_manager
        self._document_service = document_service

    async def get_job_status(self, job_id: str) -> Job | None:
        """Fetch a job by ID."""
        return await self._manager.get(job_id)

    async def process_document_background(self, payload: dict[str, Any]) -> Job:
        """
        Creates a new document processing job and queues it for background execution.
        """
        doc_input = DocumentInput(**payload)
        job = await self._manager.submit("document_processing")

        # Enqueue the background task
        import asyncio

        self._bg_task = asyncio.create_task(
            self._process_document_background(job_id=job.id, doc_input=doc_input)
        )

        return job

    async def _process_document_background(self, job_id: str, doc_input: DocumentInput) -> None:
        """
        The background task that actually processes the document.
        Updates job status accordingly.
        """
        try:
            await self._manager.update_progress(
                job_id,
                current_stage="Initialization",
                completed_stages=0,
                total_stages=1,  # Or dynamic if known
                stage_status="running",
                message="Starting document processing",
            )

            # Since PipelineService is now instrumented with the job manager,
            # we just pass the job_id down.

            result = await self._document_service.process_document(doc_input, job_id=job_id)

            # Convert result to dict for JobResult
            result_dict = {
                "document_id": result.document_id,
                "filename": result.filename,
                "processor": result.processor,
                "chunk_count": result.chunk_count,
                "processing_time_ms": result.processing_time_ms,
                "status": result.status,
                "warnings": result.warnings,
            }

            await self._manager.complete(job_id, JobResult(data=result_dict))

        except Exception as e:
            logger.exception(f"Job {job_id} failed during document processing")
            await self._manager.fail(job_id, error_message=str(e))

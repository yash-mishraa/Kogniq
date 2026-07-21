import logging

from backend.schemas.document import DocumentInput
from backend.services.document_service import DocumentService
from fastapi import BackgroundTasks

from jobs.interfaces import AbstractJobManager
from jobs.models import Job, JobResult

logger = logging.getLogger(__name__)


class JobService:
    """
    Orchestrates job execution using FastAPI BackgroundTasks.
    Strictly coordinates between the API boundary and domain logic.
    """

    def __init__(self, job_manager: AbstractJobManager, document_service: DocumentService) -> None:
        self._manager = job_manager
        self._document_service = document_service

    async def get_job(self, job_id: str) -> Job | None:
        """Fetch a job by ID."""
        return await self._manager.get(job_id)

    async def submit_document_processing(
        self, doc_input: DocumentInput, background_tasks: BackgroundTasks
    ) -> Job:
        """
        Creates a new document processing job and queues it for background execution.
        """
        job = await self._manager.submit("document_processing")
        
        # Enqueue the background task
        background_tasks.add_task(
            self._process_document_background,
            job_id=job.id,
            doc_input=doc_input
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
                percentage=10,
                message="Starting document processing",
                milestone="Processing started",
            )
            
            # Since PipelineService currently isn't natively instrumented with the job manager,
            # we'll just run the whole processing and mark as complete when done.
            # In the future, PipelineService itself could accept the job_id and report progress.
            
            result = await self._document_service.process_document(doc_input)
            
            # Convert result to dict for JobResult
            result_dict = {
                "document_id": result.document_id,
                "filename": result.filename,
                "processor": result.processor,
                "chunk_count": result.chunk_count,
                "embedding_count": result.embedding_count,
                "knowledge_concepts": result.knowledge_concepts,
                "knowledge_relationships": result.knowledge_relationships,
                "processing_time_ms": result.processing_time_ms,
                "status": result.status,
                "warnings": result.warnings,
            }
            
            await self._manager.complete(job_id, JobResult(data=result_dict))
            
        except Exception as e:
            logger.exception(f"Job {job_id} failed during document processing")
            await self._manager.fail(job_id, error_message=str(e))

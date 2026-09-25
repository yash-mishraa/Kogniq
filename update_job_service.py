import sys
import re

with open('packages/backend/src/backend/services/job_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''    async def _process_document_background(self, job_id: str, doc_input: DocumentInput) -> None:
        """
        The background task that actually processes the document.
        Updates job status accordingly.
        """
        import time
        from shared.logging.context import set_telemetry_context, reset_telemetry_context
        
        token = set_telemetry_context({"job_id": job_id})
        start_time = time.monotonic()
        logger.info("ingestion_job_started")
        
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
            
            logger.info("ingestion_job_completed", extra={
                "duration_ms": (time.monotonic() - start_time) * 1000,
                "status": "success",
            })

        except Exception as e:
            logger.error("ingestion_job_failed", extra={
                "duration_ms": (time.monotonic() - start_time) * 1000,
                "status": "failure",
                "failure_category": "unknown_error"
            })
            await self._manager.fail(job_id, error_message=str(e))
        finally:
            reset_telemetry_context(token)'''

content = re.sub(r'    async def _process_document_background\(self, job_id: str, doc_input: DocumentInput\) -> None:.*?await self\._manager\.fail\(job_id, error_message=str\(e\)\)', replacement, content, flags=re.DOTALL)

with open('packages/backend/src/backend/services/job_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

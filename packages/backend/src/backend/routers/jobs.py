from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.dependencies import JobDependency
from backend.schemas.document import DocumentInput

jobs_router = APIRouter(prefix="/jobs", tags=["Jobs"])

class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: int | None = None
    message: str | None = None

@jobs_router.post("/process-document", response_model=JobResponse)
async def process_document_job(
    job_service: JobDependency,
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
) -> JobResponse:
    content = await file.read()
    doc_input = DocumentInput(
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        content=content,
    )
    
    job = await job_service.submit_document_processing(doc_input, background_tasks)
    
    return JobResponse(
        job_id=job.id,
        status=job.status.value,
        progress=job.progress.percentage if job.progress else 0,
        message=job.progress.message if job.progress else "Job created",
    )

@jobs_router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, job_service: JobDependency) -> JobResponse:
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return JobResponse(
        job_id=job.id,
        status=job.status.value,
        progress=job.progress.percentage if job.progress else 0,
        message=job.progress.message if job.progress else None,
    )

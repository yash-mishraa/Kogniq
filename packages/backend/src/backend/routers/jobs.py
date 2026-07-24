from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from pydantic import BaseModel

from application.exceptions import ApplicationError
from application.jobs.commands import GetJobStatusCommand, JobCommand
from application.jobs.get_job_status import GetJobStatusUseCase
from application.jobs.submit_job import SubmitJobUseCase
from backend.dependencies import get_job_status_use_case, get_submit_job_use_case

jobs_router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: int | None = None
    current_stage: str | None = None
    completed_stages: int | None = None
    total_stages: int | None = None
    stage_status: str | None = None
    message: str | None = None


@jobs_router.post("/process-document", response_model=JobResponse)
async def process_document_job(
    file: Annotated[UploadFile, File(...)],
    x_user_id: str = Header("demo-user-1", alias="X-User-Id"),
    use_case: SubmitJobUseCase = Depends(get_submit_job_use_case),  # noqa: B008
) -> JobResponse:
    content = await file.read()
    payload = {
        "filename": file.filename or "unknown",
        "content_type": file.content_type or "application/octet-stream",
        "size_bytes": len(content),
        "content": content,
    }

    command = JobCommand(
        user_id=x_user_id,
        job_type="PROCESS_DOCUMENT",
        payload=payload,
    )
    result = await use_case.execute(command)

    return JobResponse(
        job_id=result.job_id,
        status=result.status,
        progress=0,
        current_stage="Initialization",
        completed_stages=0,
        total_stages=1,
        stage_status="queued",
        message=result.message,
    )


@jobs_router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    x_user_id: str = Header("demo-user-1", alias="X-User-Id"),
    use_case: GetJobStatusUseCase = Depends(get_job_status_use_case),  # noqa: B008
) -> JobResponse:
    command = GetJobStatusCommand(user_id=x_user_id, job_id=job_id)
    try:
        result = await use_case.execute(command)
        progress_percentage = 0
        if result.total_stages > 0:
            progress_percentage = int((result.completed_stages / result.total_stages) * 100)

        return JobResponse(
            job_id=result.job_id,
            status=result.status,
            progress=progress_percentage,
            current_stage=result.current_stage,
            completed_stages=result.completed_stages,
            total_stages=result.total_stages,
            stage_status=result.stage_status,
            message=result.message,
        )
    except ApplicationError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Job not found") from e
        raise HTTPException(status_code=500, detail=str(e)) from e

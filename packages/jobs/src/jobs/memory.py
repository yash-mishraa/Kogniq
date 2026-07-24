import threading
import uuid
from dataclasses import replace
from datetime import UTC, datetime

from .interfaces import AbstractJobManager
from .models import Job, JobProgress, JobResult, JobStatus, StageStatus


class MemoryJobManager(AbstractJobManager):
    """
    Thread-safe, in-memory implementation of AbstractJobManager.
    Uses O(1) dictionary lookup and immutable job updates.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.RLock()

    async def submit(self, job_type: str) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, job_type=job_type)

        with self._lock:
            self._jobs[job_id] = job

        return job

    async def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    async def update_progress(
        self,
        job_id: str,
        current_stage: str | None = None,
        completed_stages: int | None = None,
        total_stages: int | None = None,
        stage_status: str | None = None,
        message: str | None = None,
    ) -> Job:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")

            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                # Don't update progress on terminal states, but maybe just log it or ignore
                pass

            now = datetime.now(UTC)

            # If this is the first progress update, mark as started
            started_at = job.started_at
            status = job.status
            stats = job.statistics

            if status == JobStatus.PENDING:
                status = JobStatus.RUNNING
                started_at = now
                stats = replace(stats, started_at=now)

            progress = JobProgress(
                current_stage=current_stage
                if current_stage is not None
                else job.progress.current_stage,
                completed_stages=completed_stages
                if completed_stages is not None
                else job.progress.completed_stages,
                total_stages=total_stages
                if total_stages is not None
                else job.progress.total_stages,
                status=StageStatus(stage_status)
                if stage_status is not None
                else job.progress.status,
                message=message,
                updated_at=now,
            )

            updated_job = replace(
                job, status=status, started_at=started_at, progress=progress, statistics=stats
            )

            self._jobs[job_id] = updated_job
            return updated_job

    async def complete(self, job_id: str, result: JobResult) -> Job:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")

            now = datetime.now(UTC)

            started_at = job.started_at or now
            processing_time = (now - started_at).total_seconds() * 1000.0

            stats = replace(
                job.statistics,
                started_at=started_at,
                completed_at=now,
                processing_time_ms=processing_time,
            )

            progress = JobProgress(
                current_stage=job.progress.current_stage,
                completed_stages=job.progress.total_stages,
                total_stages=job.progress.total_stages,
                status=StageStatus.COMPLETED,
                message="Job completed",
                updated_at=now,
            )

            updated_job = replace(
                job,
                status=JobStatus.COMPLETED,
                completed_at=now,
                result=result,
                progress=progress,
                statistics=stats,
            )

            self._jobs[job_id] = updated_job
            return updated_job

    async def fail(self, job_id: str, error_message: str) -> Job:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")

            now = datetime.now(UTC)

            started_at = job.started_at or now
            processing_time = (now - started_at).total_seconds() * 1000.0

            stats = replace(
                job.statistics,
                started_at=started_at,
                completed_at=now,
                processing_time_ms=processing_time,
            )

            updated_job = replace(
                job,
                status=JobStatus.FAILED,
                completed_at=now,
                error_message=error_message,
                statistics=stats,
            )

            self._jobs[job_id] = updated_job
            return updated_job

    async def cancel(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                raise ValueError(f"Job {job_id} not found")

            now = datetime.now(UTC)

            updated_job = replace(job, status=JobStatus.CANCELLED, completed_at=now)

            self._jobs[job_id] = updated_job
            return updated_job

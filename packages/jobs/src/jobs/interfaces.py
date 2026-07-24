from abc import ABC, abstractmethod

from .models import Job, JobResult


class AbstractJobManager(ABC):
    """
    Core abstraction for job state orchestration.
    Maintains the lifecycle of jobs and their progress.
    """

    @abstractmethod
    async def submit(self, job_type: str) -> Job:
        """Create a new job in PENDING state."""

    @abstractmethod
    async def get(self, job_id: str) -> Job | None:
        """Retrieve the current state of a job."""

    @abstractmethod
    async def update_progress(
        self,
        job_id: str,
        current_stage: str | None = None,
        completed_stages: int | None = None,
        total_stages: int | None = None,
        stage_status: str | None = None,
        message: str | None = None,
    ) -> Job:
        """Update job progress and transition to RUNNING if not already."""

    @abstractmethod
    async def complete(self, job_id: str, result: JobResult) -> Job:
        """Mark a job as COMPLETED and store its result."""

    @abstractmethod
    async def fail(self, job_id: str, error_message: str) -> Job:
        """Mark a job as FAILED and store the error."""

    @abstractmethod
    async def cancel(self, job_id: str) -> Job:
        """Mark a job as CANCELLED."""

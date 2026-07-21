from dataclasses import dataclass


@dataclass(frozen=True)
class JobSubmissionResult:
    job_id: str
    status: str
    message: str


@dataclass(frozen=True)
class JobStatusResult:
    job_id: str
    job_type: str
    status: str
    progress_percentage: int
    message: str | None
    error_message: str | None

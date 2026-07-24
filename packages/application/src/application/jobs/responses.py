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
    current_stage: str | None
    completed_stages: int
    total_stages: int
    stage_status: str
    message: str | None
    error_message: str | None

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, kw_only=True)
class JobProgress:
    current_stage: str | None = None
    completed_stages: int = 0
    total_stages: int = 0
    status: StageStatus = StageStatus.QUEUED
    message: str | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class JobResult:
    data: dict[str, Any]
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class JobStatistics:
    started_at: datetime | None = None
    completed_at: datetime | None = None
    processing_time_ms: float | None = None


@dataclass(frozen=True, kw_only=True)
class Job:
    id: str
    job_type: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    progress: JobProgress = field(default_factory=lambda: JobProgress(message="Job created"))
    result: JobResult | None = None
    error_message: str | None = None
    statistics: JobStatistics = field(default_factory=JobStatistics)

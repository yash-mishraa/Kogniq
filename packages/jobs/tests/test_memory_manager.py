import asyncio

import pytest

from jobs.memory import MemoryJobManager
from jobs.models import JobResult, JobStatus


@pytest.mark.asyncio
async def test_job_lifecycle_success() -> None:
    manager = MemoryJobManager()

    # Submit
    job = await manager.submit("test_type")
    assert job.status == JobStatus.PENDING
    assert job.id is not None

    # Progress
    job = await manager.update_progress(
        job.id, current_stage="A", completed_stages=1, total_stages=2, message="Halfway"
    )
    assert job.status == JobStatus.RUNNING
    assert job.progress.completed_stages == 1
    assert job.progress.message == "Halfway"

    # Complete
    result = JobResult(data={"success": True})
    job = await manager.complete(job.id, result)
    assert job.status == JobStatus.COMPLETED
    assert job.progress.status == "completed"
    assert job.result is not None
    assert job.result.data["success"] is True
    assert job.statistics.started_at is not None
    assert job.statistics.completed_at is not None
    assert job.statistics.processing_time_ms is not None


@pytest.mark.asyncio
async def test_job_failure() -> None:
    manager = MemoryJobManager()
    job = await manager.submit("test_type")
    job = await manager.fail(job.id, "Something went wrong")
    assert job.status == JobStatus.FAILED
    assert job.error_message == "Something went wrong"


@pytest.mark.asyncio
async def test_job_cancellation() -> None:
    manager = MemoryJobManager()
    job = await manager.submit("test_type")
    job = await manager.cancel(job.id)
    assert job.status == JobStatus.CANCELLED


@pytest.mark.asyncio
async def test_job_not_found() -> None:
    manager = MemoryJobManager()
    with pytest.raises(ValueError):
        await manager.update_progress("invalid", current_stage="A")


@pytest.mark.asyncio
async def test_concurrent_jobs() -> None:
    manager = MemoryJobManager()

    async def run_job(i: int) -> None:
        job = await manager.submit(f"type_{i}")
        await manager.update_progress(job.id, current_stage="Parse")
        await asyncio.sleep(0.01)
        await manager.complete(job.id, JobResult(data={}))

    tasks = [run_job(i) for i in range(10)]
    await asyncio.gather(*tasks)

    # All 10 should be completed
    assert len(manager._jobs) == 10

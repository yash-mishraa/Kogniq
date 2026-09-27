# ruff: noqa
from datetime import UTC, datetime, timedelta

import pytest
from backend.services.document_service import DocumentService
from persistence.memory.document_job_repo import MemoryDocumentJobRepository
from persistence.memory_uow import MemoryUnitOfWork
from persistence.factory import MemoryRepositoryFactory
from persistence.uow_factory import AbstractUnitOfWorkFactory
from persistence.models import DocumentJob
from pipeline.pipeline import DocumentIntelligencePipeline

from typing import Any

class DummyUowFactory(AbstractUnitOfWorkFactory):
    def __init__(self) -> None:
        self.factory = MemoryRepositoryFactory()

    def create(self) -> MemoryUnitOfWork:
        return MemoryUnitOfWork(self.factory)

class DummyPipeline(DocumentIntelligencePipeline):
    def __init__(self) -> None:
        pass

    async def run(self, handle: Any, job_id: str | None = None) -> dict[str, Any]:
        return {"stages": {}}


@pytest.fixture
def service() -> DocumentService:
    uow = DummyUowFactory()
    pipeline = DummyPipeline()
    return DocumentService(pipeline=pipeline, uow_factory=uow)


@pytest.mark.asyncio
async def test_recover_failed_jobs(service: DocumentService) -> None:
    # Setup some test jobs
    now = datetime.now(UTC)

    with service.uow_factory.create() as uow:
        # 1. Error job -> should be recovered (deleted)
        uow.document_jobs.save(
            DocumentJob(
                id="job-1", user_id="user-1", filename="a.pdf", status="Error", created_at=now
            )
        )
        # 2. Stale processing job -> should be recovered (deleted)
        uow.document_jobs.save(
            DocumentJob(
                id="job-2",
                user_id="user-1",
                filename="b.pdf",
                status="Processing",
                created_at=now - timedelta(hours=2),
            )
        )
        # 3. Active processing job -> should NOT be recovered
        uow.document_jobs.save(
            DocumentJob(
                id="job-3", user_id="user-1", filename="c.pdf", status="Processing", created_at=now
            )
        )
        # 4. Error job but for DIFFERENT user -> should NOT be recovered
        uow.document_jobs.save(
            DocumentJob(
                id="job-4", user_id="user-2", filename="d.pdf", status="Error", created_at=now
            )
        )
        uow.commit()

    recovered_count = service.recover_failed_jobs(user_id="user-1")

    assert recovered_count == 2

    # Check remaining active jobs for user-1
    with service.uow_factory.create() as uow:
        jobs = uow.document_jobs.list_active(user_id="user-1")
        assert len(jobs) == 1
        assert jobs[0].id == "job-3"

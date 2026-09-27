# ruff: noqa
from datetime import UTC, datetime, timedelta

import pytest
from backend.services.document_service import DocumentService
from evaluation.harness.fakes import FakeUowFactory
from persistence.models import DocumentJob
from pipeline.pipeline import DocumentIntelligencePipeline


class DummyPipeline(DocumentIntelligencePipeline):
    def __init__(self):
        pass

    async def run(self, handle):
        return {"stages": {}}


@pytest.fixture
def service():
    uow = FakeUowFactory()
    pipeline = DummyPipeline()
    return DocumentService(pipeline=pipeline, uow_factory=uow)


@pytest.mark.asyncio
async def test_recover_failed_jobs(service):
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

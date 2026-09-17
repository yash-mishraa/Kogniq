from collections.abc import Sequence

from persistence.models import DocumentJob
from persistence.repositories.base import AbstractDocumentJobRepository


class MemoryDocumentJobRepository(AbstractDocumentJobRepository):
    def __init__(self) -> None:
        self._jobs: dict[str, DocumentJob] = {}

    def save(self, job: DocumentJob) -> None:
        self._jobs[job.id] = job

    def get(self, job_id: str) -> DocumentJob | None:
        return self._jobs.get(job_id)

    def list_active(self, user_id: str | None = None) -> Sequence[DocumentJob]:
        return [
            j
            for j in self._jobs.values()
            if j.status != "Ready" and (user_id is None or j.user_id == user_id)
        ]

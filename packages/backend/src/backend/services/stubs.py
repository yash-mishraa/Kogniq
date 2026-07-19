from typing import Protocol

# These protocols act as structural interfaces for future dependency injection.
# They allow the FastAPI layer to remain blissfully unaware of concrete backend logic.


class PipelineService(Protocol):
    """Protocol for the core intelligence pipeline."""

    async def process_document(self, document_id: str) -> None: ...


class LearningService(Protocol):
    """Protocol for the learning content generation orchestration."""

    async def generate_study_guide(self, document_id: str) -> dict[str, str]: ...


class RetrievalService(Protocol):
    """Protocol for retrieval and search."""

    async def search(self, query: str) -> list[str]: ...


# --- Lightweight Stub Implementations --- #


class StubPipelineService:
    async def process_document(self, document_id: str) -> None:
        pass


class StubLearningService:
    async def generate_study_guide(self, document_id: str) -> dict[str, str]:
        _ = document_id
        return {"status": "stubbed"}


class StubRetrievalService:
    async def search(self, query: str) -> list[str]:
        _ = query
        return []

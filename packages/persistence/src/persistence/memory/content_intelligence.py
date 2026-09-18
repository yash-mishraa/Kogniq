from collections.abc import Sequence

from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from persistence.models import SaveResult
from persistence.repositories.base import (
    AbstractLearningResourceRepository,
    AbstractResourceChunkRepository,
    AbstractResourceSectionRepository,
)


class MemoryLearningResourceRepository(AbstractLearningResourceRepository):
    def __init__(self) -> None:
        self._resources: dict[str, LearningResource] = {}

    async def save(self, resource: LearningResource) -> SaveResult:
        self._resources[resource.id] = resource
        return SaveResult(id=resource.id, is_new=True)

    async def get(self, resource_id: str, user_id: str) -> LearningResource | None:
        # In memory, we don't have user_id strictly mapped unless we join with documents.
        # But this is just for testing.
        return self._resources.get(resource_id)

    async def list(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[LearningResource]:
        return list(self._resources.values())[offset : offset + limit]


class MemoryResourceSectionRepository(AbstractResourceSectionRepository):
    def __init__(self) -> None:
        self._sections: dict[str, ResourceSection] = {}

    async def save_all(self, sections: Sequence[ResourceSection]) -> SaveResult:
        if not sections:
            return SaveResult(id="", is_new=False)
        for s in sections:
            self._sections[s.id] = s
        return SaveResult(id=sections[0].resource_id, is_new=True)

    async def get_by_resource(self, resource_id: str, user_id: str) -> Sequence[ResourceSection]:
        return sorted(
            [s for s in self._sections.values() if s.resource_id == resource_id],
            key=lambda x: x.order,
        )


class MemoryResourceChunkRepository(AbstractResourceChunkRepository):
    def __init__(self) -> None:
        self._chunks: dict[str, ResourceChunk] = {}

    async def save_all(self, chunks: Sequence[ResourceChunk]) -> SaveResult:
        if not chunks:
            return SaveResult(id="", is_new=False)
        for c in chunks:
            self._chunks[c.id] = c
        return SaveResult(id=chunks[0].resource_id, is_new=True)

    async def get_by_resource(self, resource_id: str, user_id: str) -> Sequence[ResourceChunk]:
        return sorted(
            [c for c in self._chunks.values() if c.resource_id == resource_id],
            key=lambda x: x.order,
        )

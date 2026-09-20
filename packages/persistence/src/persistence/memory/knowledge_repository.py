from collections.abc import Sequence

from domain.student.entities import KnowledgeState

from persistence.models import SaveResult
from persistence.repositories.student import AbstractKnowledgeStateRepository


class MemoryKnowledgeStateRepository(AbstractKnowledgeStateRepository):
    def __init__(self) -> None:
        # dict mapped by (user_id, resource_id) -> KnowledgeState
        self._states: dict[tuple[str, str], KnowledgeState] = {}

    async def save(self, state: KnowledgeState) -> SaveResult:
        key = (state.user_id, state.resource_id)
        is_new = key not in self._states
        self._states[key] = state
        return SaveResult(id=state.id, is_new=is_new)

    async def get(self, user_id: str, resource_id: str) -> KnowledgeState | None:
        return self._states.get((user_id, resource_id))

    async def list_by_user(self, user_id: str) -> Sequence[KnowledgeState]:
        return [s for key, s in self._states.items() if key[0] == user_id]

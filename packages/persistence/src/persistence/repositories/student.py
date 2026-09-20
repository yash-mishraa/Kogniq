import abc
from collections.abc import Sequence

from domain.student.entities import KnowledgeState

from persistence.models import SaveResult


class AbstractKnowledgeStateRepository(abc.ABC):
    """Abstract repository for storing and querying KnowledgeState entities."""

    @abc.abstractmethod
    async def save(self, state: KnowledgeState) -> SaveResult:
        """Upsert a KnowledgeState."""

    @abc.abstractmethod
    async def get(self, user_id: str, resource_id: str) -> KnowledgeState | None:
        """Retrieve a KnowledgeState by user and resource."""

    @abc.abstractmethod
    async def list_by_user(self, user_id: str) -> Sequence[KnowledgeState]:
        """List all knowledge states for a given user."""

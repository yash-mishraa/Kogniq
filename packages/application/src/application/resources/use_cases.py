from collections.abc import Sequence

from persistence.uow_factory import AbstractUnitOfWorkFactory

from application.exceptions import ApplicationError
from application.interfaces import AuthenticationServiceProtocol
from content.domain.entities import LearningResource, ResourceChunk, ResourceSection


class GetLearningResourceUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._uow_factory = uow_factory

    async def execute(self, user_id: str, resource_id: str) -> LearningResource:
        with self._uow_factory.create() as uow:
            resource = await uow.learning_resources.get(resource_id=resource_id, user_id=user_id)
            if not resource:
                raise ApplicationError(f"Resource {resource_id} not found or access denied.")
            return resource


class ListLearningResourcesUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._uow_factory = uow_factory

    async def execute(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> Sequence[LearningResource]:
        with self._uow_factory.create() as uow:
            return await uow.learning_resources.list(user_id=user_id, limit=limit, offset=offset)


class GetResourceSectionsUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._uow_factory = uow_factory

    async def execute(self, user_id: str, resource_id: str) -> Sequence[ResourceSection]:
        with self._uow_factory.create() as uow:
            # Validates ownership inside the repository
            sections = await uow.resource_sections.get_by_resource(
                resource_id=resource_id, user_id=user_id
            )
            if not sections:
                # Also check if resource exists to throw proper 404
                resource = await uow.learning_resources.get(
                    resource_id=resource_id, user_id=user_id
                )
                if not resource:
                    raise ApplicationError(f"Resource {resource_id} not found or access denied.")
            return sections


class GetResourceChunksUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._uow_factory = uow_factory

    async def execute(self, user_id: str, resource_id: str) -> Sequence[ResourceChunk]:
        with self._uow_factory.create() as uow:
            chunks = await uow.resource_chunks.get_by_resource(
                resource_id=resource_id, user_id=user_id
            )
            if not chunks:
                resource = await uow.learning_resources.get(
                    resource_id=resource_id, user_id=user_id
                )
                if not resource:
                    raise ApplicationError(f"Resource {resource_id} not found or access denied.")
            return chunks


class GetResourceStatisticsUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self._auth_service = auth_service
        self._uow_factory = uow_factory

    async def execute(self, user_id: str, resource_id: str) -> dict[str, int]:
        with self._uow_factory.create() as uow:
            # Enforce ownership first
            resource = await uow.learning_resources.get(resource_id=resource_id, user_id=user_id)
            if not resource:
                raise ApplicationError(f"Resource {resource_id} not found or access denied.")

            sections = await uow.resource_sections.get_by_resource(
                resource_id=resource_id, user_id=user_id
            )
            chunks = await uow.resource_chunks.get_by_resource(
                resource_id=resource_id, user_id=user_id
            )

            total_tokens = sum(c.token_estimate for c in chunks if c.token_estimate)

            return {
                "section_count": len(sections),
                "chunk_count": len(chunks),
                "total_tokens": total_tokens,
            }

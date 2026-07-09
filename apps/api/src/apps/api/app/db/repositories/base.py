"""Base repository interfaces and generic SQLAlchemy implementations."""

import abc
from collections.abc import Sequence
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType](abc.ABC):
    """Abstract generic repository for data access."""

    @abc.abstractmethod
    async def get(self, ident: Any) -> ModelType | None:
        """Fetch a single record by its primary key."""

    @abc.abstractmethod
    async def get_all(self) -> Sequence[ModelType]:
        """Fetch all records."""

    @abc.abstractmethod
    async def add(self, entity: ModelType) -> None:
        """Add a new entity."""

    @abc.abstractmethod
    async def delete(self, entity: ModelType) -> None:
        """Delete an existing entity."""


class SQLAlchemyRepository(BaseRepository[ModelType]):
    """SQLAlchemy generic repository implementation."""

    def __init__(self, session: AsyncSession, model_cls: type[ModelType]) -> None:
        self.session = session
        self.model_cls = model_cls

    async def get(self, ident: Any) -> ModelType | None:
        return await self.session.get(self.model_cls, ident)

    async def get_all(self) -> Sequence[ModelType]:
        stmt = select(self.model_cls)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add(self, entity: ModelType) -> None:
        self.session.add(entity)
        # Flushing forces constraints to be checked immediately without committing
        await self.session.flush()

    async def delete(self, entity: ModelType) -> None:
        await self.session.delete(entity)
        await self.session.flush()

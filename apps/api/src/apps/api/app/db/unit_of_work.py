"""Unit of Work abstractions for managing transactions."""

import abc
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork(abc.ABC):
    """Abstract Unit of Work context manager."""

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the underlying transaction."""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Roll back the underlying transaction."""


class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of the Unit of Work."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        """Commit the SQLAlchemy session."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the SQLAlchemy session."""
        await self._session.rollback()

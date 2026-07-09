"""Database engine and session factory configuration."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from apps.api.app.config import APISettings


def get_engine(settings: APISettings) -> AsyncEngine:
    """Create and configure the SQLAlchemy async engine."""
    return create_async_engine(
        str(settings.database_url),
        echo=settings.sqlalchemy_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        future=True,
    )


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create the session factory tied to the async engine."""
    return async_sessionmaker(
        engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

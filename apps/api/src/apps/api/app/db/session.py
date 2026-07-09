"""Database session dependency for FastAPI."""

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session to a FastAPI endpoint from the application state."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session

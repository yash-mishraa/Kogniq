"""Database health checking."""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def check_database_health(engine: AsyncEngine) -> bool:
    """Execute a simple query to verify database connectivity.

    Returns:
        True if the database is reachable and responsive, False otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

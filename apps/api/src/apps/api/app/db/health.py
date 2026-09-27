"""Database health checking."""

import logging

from backend.dependencies import get_uow_factory

logger = logging.getLogger(__name__)


async def check_database_health() -> bool:
    """Execute a simple query to verify database connectivity.

    Returns:
        True if the database is reachable and responsive, False otherwise.
    """
    try:
        factory = get_uow_factory()
        with factory.create() as uow:
            conn = getattr(uow, "_conn", None)
            if conn:
                conn.execute("SELECT 1").fetchone()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

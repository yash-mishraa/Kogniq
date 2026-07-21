import sqlite3
from collections.abc import Generator
from contextlib import contextmanager


class SQLiteConnectionManager:
    """Manages SQLite connections, ensuring WAL mode and foreign keys are enabled."""

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provides a configured SQLite connection."""
        conn = sqlite3.connect(
            self.database_path,
            # Let the caller or Unit of Work manage transactions explicitly
            isolation_level=None,
            check_same_thread=False,
        )
        # Configure connection
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        # Return rows as dicts
        conn.row_factory = sqlite3.Row

        try:
            yield conn
        finally:
            conn.close()

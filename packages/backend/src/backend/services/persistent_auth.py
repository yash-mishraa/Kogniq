"""SQLite-backed authentication adapters.

The historical application used process-local dictionaries for users and
sessions. That made every restart log the user out and orphan documents whose
``user_id`` referenced a user that no longer existed. This module keeps the
domain interfaces intact while persisting identity in the same SQLite database
as documents and chunks.
"""

from __future__ import annotations

import sqlite3
import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

from persistence.sqlite.schema import init_db

from auth.interfaces import AbstractUserRepository
from auth.memory import MemoryAuthenticationProvider
from auth.models import Session, User


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


class PersistentUserRepository(AbstractUserRepository):
    """Durable user + credential repository."""

    def __init__(self, sqlite_path: str) -> None:
        self._path = sqlite_path
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self._connection() as conn:
            init_db(conn)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            yield conn
        finally:
            conn.close()

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            user_id=row["id"],
            email=row["email"],
            display_name=row["display_name"],
            is_active=bool(row["is_active"]),
            created_at=_parse(row["created_at"]),
            updated_at=_parse(row["updated_at"]),
        )

    async def create_user(self, user: User) -> User:
        now = datetime.now(UTC)
        with self._lock, self._connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO users (id, email, display_name, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user.user_id,
                        user.email.strip().lower(),
                        user.display_name,
                        1 if user.is_active else 0,
                        _iso(user.created_at or now),
                        _iso(user.updated_at or now),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                from auth.exceptions import UserAlreadyExistsError

                raise UserAlreadyExistsError(
                    f"User with email {user.email} already exists"
                ) from exc
        return user

    async def get_user(self, user_id: str) -> User | None:
        with self._lock, self._connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._row_to_user(row) if row else None

    async def get_user_by_email(self, email: str) -> User | None:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
            ).fetchone()
        return self._row_to_user(row) if row else None

    async def update_user(self, user: User) -> User:
        with self._lock, self._connection() as conn:
            cursor = conn.execute(
                """
                UPDATE users SET email = ?, display_name = ?, is_active = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    user.email.strip().lower(),
                    user.display_name,
                    1 if user.is_active else 0,
                    _iso(datetime.now(UTC)),
                    user.user_id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"User with id {user.user_id} not found")
        return user

    async def delete_user(self, user_id: str) -> None:
        with self._lock, self._connection() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    async def list_users(self) -> list[User]:
        with self._lock, self._connection() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY created_at").fetchall()
        return [self._row_to_user(row) for row in rows]

    async def exists(self, email: str) -> bool:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM users WHERE email = ?", (email.strip().lower(),)
            ).fetchone()
        return row is not None

    async def set_password_hash(self, user_id: str, password_hash: str) -> None:
        with self._lock, self._connection() as conn:
            conn.execute(
                """
                INSERT INTO auth_credentials (user_id, password_hash) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET password_hash = excluded.password_hash
                """,
                (user_id, password_hash),
            )

    async def get_password_hash(self, user_id: str) -> str | None:
        with self._lock, self._connection() as conn:
            row = conn.execute(
                "SELECT password_hash FROM auth_credentials WHERE user_id = ?", (user_id,)
            ).fetchone()
        return row["password_hash"] if row else None


class PersistentAuthenticationProvider(MemoryAuthenticationProvider):
    """Session provider that persists sessions alongside users."""

    def __init__(self, user_repo: PersistentUserRepository, sqlite_path: str) -> None:
        super().__init__(user_repo)
        self._path = sqlite_path
        self._session_lock = threading.RLock()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        finally:
            conn.close()

    async def create_session(self, user_id: str) -> Session:
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            expires_at=datetime.now(UTC) + timedelta(hours=24),
            created_at=datetime.now(UTC),
        )
        with self._session_lock, self._connection() as conn:
            conn.execute(
                """
                INSERT INTO auth_sessions (session_id, user_id, created_at, expires_at, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                (
                    session.session_id,
                    session.user_id,
                    _iso(session.created_at),
                    _iso(session.expires_at),
                ),
            )
        return session

    async def validate_session(self, session_id: str) -> Session | None:
        with self._session_lock, self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM auth_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not row:
                return None
            session = Session(
                session_id=row["session_id"],
                user_id=row["user_id"],
                expires_at=_parse(row["expires_at"]),
                is_active=bool(row["is_active"]),
                created_at=_parse(row["created_at"]),
            )
            if not session.is_active:
                return None
            if session.expires_at < datetime.now(UTC):
                conn.execute(
                    "UPDATE auth_sessions SET is_active = 0 WHERE session_id = ?",
                    (session_id,),
                )
                return None
            return session

    async def revoke_session(self, session_id: str) -> None:
        with self._session_lock, self._connection() as conn:
            conn.execute(
                "UPDATE auth_sessions SET is_active = 0 WHERE session_id = ?", (session_id,)
            )


__all__ = ["PersistentAuthenticationProvider", "PersistentUserRepository"]

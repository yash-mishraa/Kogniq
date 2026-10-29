"""Authoritative per-document indexing state and index configuration metadata.

A document is only "Ready" when parsing, chunking, embedding and vector writes
have all succeeded. This module is the single writer of that state so the list
endpoint can never infer readiness from the mere existence of a document row.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from backend.core.settings import settings
from persistence.sqlite.schema import init_db

READY = "Ready"
PROCESSING = "Processing"
FAILED = "Failed"
UNINDEXED = "Unindexed"


@dataclass(frozen=True)
class DocumentIndexState:
    document_id: str
    user_id: str | None
    status: str
    error_message: str | None
    chunk_count: int
    embedding_model: str | None
    embedding_dimensions: int | None
    chunker_config: str | None
    indexed_at: str | None
    updated_at: str


def _connect() -> sqlite3.Connection:
    Path(settings.sqlite_database_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.sqlite_database_path, timeout=30.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def ensure_schema() -> None:
    with _connect() as conn:
        init_db(conn)


def _upsert(
    *,
    document_id: str,
    user_id: str | None,
    status: str,
    error_message: str | None = None,
    chunk_count: int = 0,
    embedding_model: str | None = None,
    embedding_dimensions: int | None = None,
    chunker_config: str | None = None,
    indexed_at: str | None = None,
) -> None:
    ensure_schema()
    now = datetime.now(UTC).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO document_index_state (
                document_id, user_id, status, error_message, chunk_count,
                embedding_model, embedding_dimensions, chunker_config, indexed_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(document_id) DO UPDATE SET
                user_id = excluded.user_id,
                status = excluded.status,
                error_message = excluded.error_message,
                chunk_count = excluded.chunk_count,
                embedding_model = excluded.embedding_model,
                embedding_dimensions = excluded.embedding_dimensions,
                chunker_config = excluded.chunker_config,
                indexed_at = excluded.indexed_at,
                updated_at = excluded.updated_at
            """,
            (
                document_id,
                user_id,
                status,
                error_message,
                chunk_count,
                embedding_model,
                embedding_dimensions,
                chunker_config,
                indexed_at,
                now,
            ),
        )


def mark_processing(document_id: str, user_id: str | None) -> None:
    _upsert(document_id=document_id, user_id=user_id, status=PROCESSING)


def mark_ready(
    document_id: str,
    user_id: str | None,
    *,
    chunk_count: int = 0,
    embedding_model: str = "unknown",
    embedding_dimensions: int = 0,
    chunker_config: str = "{}",
) -> None:
    _upsert(
        document_id=document_id,
        user_id=user_id,
        status=READY,
        chunk_count=chunk_count,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions,
        chunker_config=chunker_config,
        indexed_at=datetime.now(UTC).isoformat(),
    )
    set_index_metadata("embedding_model", embedding_model)
    set_index_metadata("embedding_dimensions", str(embedding_dimensions))
    set_index_metadata("chunker_config", chunker_config)


def mark_failed(document_id: str, user_id: str | None, error: str) -> None:
    _upsert(
        document_id=document_id,
        user_id=user_id,
        status=FAILED,
        error_message=error[:2000],
    )


def mark_unindexed(document_id: str, user_id: str | None, reason: str) -> None:
    _upsert(
        document_id=document_id,
        user_id=user_id,
        status=UNINDEXED,
        error_message=reason[:2000],
    )


def get_state(document_id: str) -> DocumentIndexState | None:
    ensure_schema()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM document_index_state WHERE document_id = ?", (document_id,)
        ).fetchone()
    return _row_to_state(row) if row else None


def list_states(user_id: str | None = None) -> dict[str, DocumentIndexState]:
    ensure_schema()
    with _connect() as conn:
        if user_id:
            rows = conn.execute(
                "SELECT * FROM document_index_state WHERE user_id = ?", (user_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM document_index_state").fetchall()
    return {row["document_id"]: _row_to_state(row) for row in rows}


def delete_state(document_id: str) -> None:
    ensure_schema()
    with _connect() as conn:
        conn.execute("DELETE FROM document_index_state WHERE document_id = ?", (document_id,))


def _row_to_state(row: sqlite3.Row) -> DocumentIndexState:
    return DocumentIndexState(
        document_id=row["document_id"],
        user_id=row["user_id"],
        status=row["status"],
        error_message=row["error_message"],
        chunk_count=int(row["chunk_count"] or 0),
        embedding_model=row["embedding_model"],
        embedding_dimensions=row["embedding_dimensions"],
        chunker_config=row["chunker_config"],
        indexed_at=row["indexed_at"],
        updated_at=row["updated_at"],
    )


def set_index_metadata(key: str, value: str) -> None:
    ensure_schema()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO index_metadata (key, value, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """,
            (key, value, datetime.now(UTC).isoformat()),
        )


def get_index_metadata(key: str) -> str | None:
    ensure_schema()
    with _connect() as conn:
        row = conn.execute("SELECT value FROM index_metadata WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def all_index_metadata() -> dict[str, str]:
    ensure_schema()
    with _connect() as conn:
        rows = conn.execute("SELECT key, value FROM index_metadata").fetchall()
    return {row["key"]: row["value"] for row in rows}

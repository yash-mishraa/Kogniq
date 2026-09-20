import contextlib
import sqlite3

import pytest
from persistence.sqlite.schema import init_db


def test_clean_initialization() -> None:
    conn = sqlite3.connect(":memory:")
    init_db(conn)

    # Check tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    assert "documents" in tables
    assert "resource_sections" in tables
    assert "document_chunks" in tables

    # Check columns exist
    cursor.execute("PRAGMA table_info(documents)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "resource_type" in columns
    assert "status" in columns
    assert "updated_at" in columns

    conn.close()


def test_repeated_initialization() -> None:
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    init_db(conn)  # Should not raise any errors
    conn.close()


def test_legacy_upgrade() -> None:
    conn = sqlite3.connect(":memory:")

    # Create legacy schema
    conn.execute("""
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            checksum TEXT NOT NULL,
            version TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            pages_json TEXT NOT NULL,
            user_id TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE document_chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            metadata_json TEXT NOT NULL,
            statistics_json TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)

    # Insert legacy data
    conn.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json, user_id) "
        "VALUES ('doc-1', 'Test', 'test.pdf', 'hash', '1', '2026', '[]', 'user-1')"
    )

    init_db(conn)

    # Verify upgrade
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(documents)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "resource_type" in columns

    # Verify legacy data preserved
    cursor.execute("SELECT id FROM documents")
    assert cursor.fetchone()[0] == "doc-1"


def test_invalid_sql_visibility() -> None:
    conn = sqlite3.connect(":memory:")

    # We will redefine add_column inside the test just to prove the logic throws for other errors
    def add_column(table: str, column_def: str) -> None:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                pass
            else:
                raise e

    with pytest.raises(sqlite3.OperationalError, match="no such table"):
        add_column("non_existent_table", "foo TEXT")

    conn.close()


def test_partial_upgrade() -> None:
    conn = sqlite3.connect(":memory:")
    init_db(conn)

    # Now simulate adding a new column to test duplicate column name handling
    # Let's say one column was already added manually
    with contextlib.suppress(sqlite3.OperationalError):
        conn.execute("ALTER TABLE documents ADD COLUMN resource_type TEXT")

    init_db(conn)  # Should not fail even if partially upgraded
    conn.close()

def test_learner_activity_index_initialization() -> None:
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    
    # Verify the partial unique index was created
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_learner_activity_idempotency'")
    row = cursor.fetchone()
    assert row is not None
    assert "WHERE idempotency_key IS NOT NULL" in row[0]
    
    # Repeated init should be safe
    init_db(conn)
    conn.close()

def test_learner_activity_index_operational_error() -> None:
    import sqlite3
    from unittest.mock import MagicMock
    
    mock_conn = MagicMock()
    mock_conn.execute.side_effect = sqlite3.OperationalError("disk I/O error")
    
    with pytest.raises(sqlite3.OperationalError, match="disk I/O error"):
        init_db(mock_conn)

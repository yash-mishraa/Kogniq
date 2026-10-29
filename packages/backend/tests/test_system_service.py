"""Regression tests for operational read models used by the RAG console."""

import sqlite3

from backend.core.settings import settings
from backend.services.system_service import SystemService


def test_document_chunks_reads_the_persisted_schema(tmp_path, monkeypatch) -> None:
    database = tmp_path / "kogniq.db"
    connection = sqlite3.connect(database)
    connection.execute(
        """
        CREATE TABLE document_chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            title TEXT,
            page_number INTEGER,
            section_title TEXT,
            section_id TEXT,
            created_at TIMESTAMP NOT NULL,
            metadata_json TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO document_chunks (
            id, document_id, chunk_index, text, title, page_number,
            section_title, section_id, created_at, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "chunk-1",
            "doc-1",
            0,
            "Attention relates tokens to each other.",
            "Attention Is All You Need",
            2,
            "Introduction",
            None,
            "2026-01-01T00:00:00Z",
            "{}",
        ),
    )
    connection.commit()
    connection.close()

    monkeypatch.setattr(settings, "sqlite_database_path", str(database))

    chunks = SystemService().document_chunks("doc-1")

    assert len(chunks) == 1
    assert chunks[0]["text"] == "Attention relates tokens to each other."
    assert chunks[0]["page_number"] == 2
    # The stored schema has no materialised breadcrumb path; the contract field
    # must stay present without inventing one.
    assert chunks[0]["section_path"] is None

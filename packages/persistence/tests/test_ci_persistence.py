import sqlite3
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any

import pytest
from persistence.sqlite.content_intelligence import (
    SQLiteLearningResourceRepository,
    SQLiteResourceChunkRepository,
    SQLiteResourceSectionRepository,
)
from persistence.sqlite.schema import init_db

from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from content.domain.enums import ProcessingStatus, ResourceType


@pytest.fixture
def sqlite_conn() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def repositories(
    sqlite_conn: sqlite3.Connection,
) -> tuple[
    SQLiteLearningResourceRepository,
    SQLiteResourceSectionRepository,
    SQLiteResourceChunkRepository,
]:
    return (
        SQLiteLearningResourceRepository(sqlite_conn),
        SQLiteResourceSectionRepository(sqlite_conn),
        SQLiteResourceChunkRepository(sqlite_conn),
    )


@pytest.mark.asyncio
async def test_learning_resource_repository(
    sqlite_conn: sqlite3.Connection, repositories: tuple[Any, Any, Any]
) -> None:
    res_repo, _, _ = repositories

    # Needs a parent document first because we reuse documents table
    sqlite_conn.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json, user_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "doc-1",
            "Old Title",
            "test.pdf",
            "hash",
            "1",
            datetime.now(UTC).isoformat(),
            "[]",
            "user-1",
        ),
    )

    resource = LearningResource(
        id="doc-1",
        title="New Title",
        resource_type=ResourceType.TEXT,
        source="test.pdf",
        checksum="new-hash",
        status=ProcessingStatus.PROCESSED,
    )

    await res_repo.save(resource)

    # User 1 can get it
    saved = await res_repo.get("doc-1", "user-1")
    assert saved is not None
    assert saved.status == ProcessingStatus.PROCESSED
    assert saved.resource_type == ResourceType.TEXT

    # User 2 cannot get it
    not_found = await res_repo.get("doc-1", "user-2")
    assert not_found is None


@pytest.mark.asyncio
async def test_resource_section_and_chunk_repository(
    sqlite_conn: sqlite3.Connection, repositories: tuple[Any, Any, Any]
) -> None:
    _res_repo, sec_repo, chunk_repo = repositories

    # Insert document
    sqlite_conn.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json, user_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "doc-1",
            "Old Title",
            "test.pdf",
            "hash",
            "1",
            datetime.now(UTC).isoformat(),
            "[]",
            "user-1",
        ),
    )

    # Insert legacy chunk
    sqlite_conn.execute(
        "INSERT INTO document_chunks (id, document_id, chunk_index, text, created_at, metadata_json, statistics_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("chunk-1", "doc-1", 0, "Hello World", datetime.now(UTC).isoformat(), "{}", "{}"),
    )

    section = ResourceSection(
        id="sec-1",
        resource_id="doc-1",
        title="Introduction",
        order=0,
    )

    await sec_repo.save_all([section])

    chunk = ResourceChunk(
        id="chunk-1",
        resource_id="doc-1",
        section_id="sec-1",
        text="Hello World",
        order=0,
        checksum="hash-chk",
    )

    await chunk_repo.save_all([chunk])

    # Verify ownership isolation
    sections = await sec_repo.get_by_resource("doc-1", "user-1")
    assert len(sections) == 1
    assert sections[0].id == "sec-1"

    chunks = await chunk_repo.get_by_resource("doc-1", "user-1")
    assert len(chunks) == 1
    assert chunks[0].id == "chunk-1"
    assert chunks[0].section_id == "sec-1"
    assert chunks[0].checksum == "hash-chk"

    # User 2 shouldn't see them
    sections_u2 = await sec_repo.get_by_resource("doc-1", "user-2")
    assert len(sections_u2) == 0

    chunks_u2 = await chunk_repo.get_by_resource("doc-1", "user-2")
    assert len(chunks_u2) == 0

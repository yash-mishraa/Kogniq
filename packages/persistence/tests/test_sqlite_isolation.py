import sqlite3
from datetime import UTC, datetime

import pytest
from persistence.sqlite.document_repository import SQLiteDocumentRepository
from persistence.sqlite.schema import init_db

from content.normalized.block import NormalizedBlock
from content.normalized.document import NormalizedDocument
from content.normalized.enums import BlockType
from content.normalized.page import NormalizedPage


@pytest.fixture
def sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


@pytest.fixture
def doc_repo(sqlite_conn: sqlite3.Connection) -> SQLiteDocumentRepository:
    return SQLiteDocumentRepository(sqlite_conn)


@pytest.mark.asyncio
async def test_document_ownership_isolation(doc_repo: SQLiteDocumentRepository) -> None:
    doc_a = NormalizedDocument(
        id="doc_A",
        title="Doc A",
        source="test",
        checksum="aaa",
        version="1.0",
        created_at=datetime.now(UTC),
        pages=(
            NormalizedPage(
                page_number=1,
                blocks=(
                    NormalizedBlock(
                        block_id="b1", block_type=BlockType.PARAGRAPH, text="hello A", order=1
                    ),
                ),
            ),
        ),
        user_id="user_A",
    )
    await doc_repo.save(doc_a)

    doc_b = NormalizedDocument(
        id="doc_B",
        title="Doc B",
        source="test",
        checksum="bbb",
        version="1.0",
        created_at=datetime.now(UTC),
        pages=(
            NormalizedPage(
                page_number=1,
                blocks=(
                    NormalizedBlock(
                        block_id="b2", block_type=BlockType.PARAGRAPH, text="hello B", order=1
                    ),
                ),
            ),
        ),
        user_id="user_B",
    )
    await doc_repo.save(doc_b)

    retrieved_a = await doc_repo.get("doc_A")
    assert retrieved_a is not None
    assert retrieved_a.user_id == "user_A"

    list_a = await doc_repo.list(user_id="user_A")
    assert len(list_a) == 1
    assert list_a[0].id == "doc_A"

    list_b = await doc_repo.list(user_id="user_B")
    assert len(list_b) == 1
    assert list_b[0].id == "doc_B"

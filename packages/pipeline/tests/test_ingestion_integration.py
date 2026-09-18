import sqlite3
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from persistence.factory import SQLiteRepositoryFactory
from persistence.sqlite.schema import init_db
from persistence.uow import SQLiteUnitOfWork
from pipeline.pipeline import DefaultPipelineContext
from pipeline.stages.ingestion import IngestionStage

from content.chunking.engine import HybridChunkEngine
from content.chunking.strategies.fixed_size import FixedSizeChunkStrategy
from content.chunking.strategies.structural import StructuralChunkStrategy
from content.normalized.document import NormalizedDocument
from content.normalized.page import NormalizedPage
from content.plugins.interfaces import AbstractContentProcessor
from content.plugins.processor_info import ProcessorInfo
from content.plugins.registry import ProcessorRegistry
from content.resource.handle import ResourceHandle


class FakeProcessor(AbstractContentProcessor):
    def __init__(self) -> None:
        self._info = ProcessorInfo(
            name="Fake Processor",
            version="1.0",
            description="A fake processor",
            supported_extensions=(".txt",),
            supported_mime_types=("text/plain",),
        )

    @property
    def processor_info(self) -> ProcessorInfo:
        return self._info

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        from content.normalized.block import NormalizedBlock
        from content.normalized.enums import BlockType

        doc = NormalizedDocument(
            id=handle.id,
            title="Fake Title",
            source="mock",
            checksum="123456",
            version="1.0",
            created_at=datetime.now(UTC),
            pages=(
                NormalizedPage(
                    page_number=1,
                    blocks=(
                        NormalizedBlock(
                            block_id="b1",
                            block_type=BlockType.PARAGRAPH,
                            text="Hello integration test.",
                            order=0,
                        ),
                    ),
                ),
            ),
        )
        return doc


from contextlib import nullcontext

from persistence.uow import AbstractUnitOfWork
from persistence.uow_factory import AbstractUnitOfWorkFactory


class FakeUoWFactory(AbstractUnitOfWorkFactory):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.repo_factory = SQLiteRepositoryFactory()

    def create(self) -> AbstractUnitOfWork:
        return SQLiteUnitOfWork(nullcontext(self.conn), self.repo_factory)


@pytest.mark.asyncio
async def test_real_ingestion_integration() -> None:
    # Setup clean db
    conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.row_factory = sqlite3.Row
    init_db(conn)

    # Dependencies
    registry = ProcessorRegistry()
    registry.register(FakeProcessor())

    # Real chunk engine
    chunk_engine = HybridChunkEngine(
        structural_strategy=StructuralChunkStrategy(),
        fixed_strategy=FixedSizeChunkStrategy(),
    )

    uow_factory = FakeUoWFactory(conn)

    stage = IngestionStage(
        processor_registry=registry,
        chunk_engine=chunk_engine,
        uow_factory=uow_factory,
    )

    # Execution context
    handle = MagicMock(spec=ResourceHandle)
    handle.id = "doc-integr-1"
    handle.mime_type = "text/plain"
    handle.extension = ".txt"
    handle.checksum = None

    context = DefaultPipelineContext()
    context.set("resource_handle", handle)

    # Execute stage
    result = await stage.execute(context)

    assert result.success is True, result.error

    # Verify legacy records
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = 'doc-integr-1'")
    doc_row = cursor.fetchone()
    assert doc_row is not None
    assert doc_row["title"] == "Fake Title"
    assert doc_row["resource_type"] == "TEXT"  # Content intelligence added field
    assert doc_row["status"] == "PROCESSED"  # Content intelligence added field

    # Verify content intelligence records
    cursor.execute("SELECT * FROM resource_sections WHERE document_id = 'doc-integr-1'")
    sections = cursor.fetchall()
    assert len(sections) == 1
    assert sections[0]["title"] == "Document Start"

    cursor.execute("SELECT * FROM document_chunks WHERE document_id = 'doc-integr-1'")
    chunks = cursor.fetchall()
    assert len(chunks) > 0
    assert chunks[0]["section_id"] == sections[0]["id"]
    assert chunks[0]["checksum"] is not None

    conn.close()

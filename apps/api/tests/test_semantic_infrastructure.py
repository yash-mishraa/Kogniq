import asyncio
import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from content.normalized.semantics import DocumentSemantics
from persistence.factory import SQLiteRepositoryFactory
from persistence.uow import SQLiteUnitOfWork
from persistence.uow_factory import AbstractUnitOfWorkFactory
from persistence.sqlite.schema import init_db
from pipeline.stages.semantic import SemanticExtractionStage
from pipeline.interfaces import PipelineContext

class MockContext(PipelineContext):
    def __init__(self, doc_id: str) -> None:
        self._doc_id = doc_id
        self._metadata: dict[str, Any] = {}

        class MockStreamRef:
            def open_stream(self) -> Any:
                import io

                import fitz  # type: ignore

                doc = fitz.open()
                doc.new_page()
                return io.BytesIO(doc.write())

        class MockHandle:
            def __init__(self, handle_id: str) -> None:
                self.id = handle_id
                self.stream_reference = MockStreamRef()

        self._metadata["resource_handle"] = MockHandle(doc_id)
        self._metadata["document_id"] = doc_id

    @property
    def document_id(self) -> str:
        return self._doc_id

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    def get(self, key: str) -> Any:
        return self._metadata.get(key)

    def set(self, key: str, value: Any) -> None:
        self._metadata[key] = value


class MockUoWFactory(AbstractUnitOfWorkFactory):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._factory = SQLiteRepositoryFactory()

    def create(self) -> SQLiteUnitOfWork:
        class CM:
            def __init__(self, c: sqlite3.Connection) -> None:
                self.conn = c

            def __enter__(self) -> sqlite3.Connection:
                return self.conn

            def __exit__(self, *args: Any) -> None:
                pass

        return SQLiteUnitOfWork(CM(self._conn), self._factory)


@pytest.fixture
def memory_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


@pytest.fixture
def uow_factory(memory_db: sqlite3.Connection) -> MockUoWFactory:
    return MockUoWFactory(memory_db)

@pytest.mark.asyncio
async def test_schema_and_basic_execution(
    memory_db: sqlite3.Connection, uow_factory: MockUoWFactory
) -> None:
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "2", datetime.now(UTC).isoformat(), "[]")
    )
    stage = SemanticExtractionStage(uow_factory=uow_factory)
    
    result = await stage.execute(MockContext(doc_id))
    assert result.success
    
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active is not None
        assert active.status == "completed"
        assert active.is_active is True
        assert active.semantic_version == "2"
        payload = json.loads(active.semantics_json)
        assert payload["schema_version"] == 1
        assert "p1_d1_status" not in payload

@pytest.mark.asyncio
async def test_stale_version_ignored(
    memory_db: sqlite3.Connection, uow_factory: MockUoWFactory
) -> None:
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "2", datetime.now(UTC).isoformat(), "[]")
    )
    
    # Insert active version "2"
    v2 = DocumentSemantics(id=str(uuid.uuid4()), document_id=doc_id, semantic_version="2", status="completed", is_active=True, semantics_json="{}", created_at=datetime.now(UTC))
    with uow_factory.create() as uow:
        await uow.semantics.save(v2)
        uow.commit()

    # Simulate older version "1" completing late
    v1 = DocumentSemantics(id=str(uuid.uuid4()), document_id=doc_id, semantic_version="1", status="completed", is_active=False, semantics_json="{}", created_at=datetime.now(UTC))
    with uow_factory.create() as uow:
        await uow.semantics.save(v1)
        activated = await uow.semantics.activate_version(doc_id, v1.id)
        assert not activated
        uow.commit()

    # Verify active is still 2
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active is not None
        assert active.semantic_version == "2"

@pytest.mark.asyncio
async def test_same_version_behavior(
    memory_db: sqlite3.Connection, uow_factory: MockUoWFactory
) -> None:
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "2", datetime.now(UTC).isoformat(), "[]")
    )
    
    # Insert active version "2"
    id1 = str(uuid.uuid4())
    v1_a = DocumentSemantics(id=id1, document_id=doc_id, semantic_version="2", status="completed", is_active=True, semantics_json="{}", created_at=datetime.now(UTC))
    with uow_factory.create() as uow:
        await uow.semantics.save(v1_a)
        uow.commit()

    # Another job completes for version "2"
    id2 = str(uuid.uuid4())
    v1_b = DocumentSemantics(id=id2, document_id=doc_id, semantic_version="2", status="completed", is_active=False, semantics_json="{}", created_at=datetime.now(UTC))
    with uow_factory.create() as uow:
        await uow.semantics.save(v1_b)
        activated = await uow.semantics.activate_version(doc_id, id2)
        assert activated
        uow.commit()

    # Verify active is id2 and exactly one active exists
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active is not None
        assert active.id == id2
        cursor = memory_db.execute("SELECT COUNT(*) as c FROM document_semantics WHERE document_id=? AND is_active=1", (doc_id,))
        assert cursor.fetchone()["c"] == 1

@pytest.mark.asyncio
async def test_concurrency_activation() -> None:
    # To test SQLite concurrency effectively, we will simulate two coroutines interleaving activate_version logic
    # using a shared SQLite memory connection in serialized mode (which is thread-safe).
    # Since we use asyncio, they execute on the same thread, but we can prove the UoW boundaries and unique constraint.
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    doc_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "2", datetime.now(UTC).isoformat(), "[]")
    )
    
    factory1 = MockUoWFactory(conn)
    
    async def worker(version: int, uow_factory: MockUoWFactory) -> None:
        await asyncio.sleep(0.01) # provoke context switch
        sem = DocumentSemantics(id=str(uuid.uuid4()), document_id=doc_id, semantic_version=str(version), status="completed", is_active=False, semantics_json="{}", created_at=datetime.now(UTC))
        try:
            with uow_factory.create() as uow:
                await uow.semantics.save(sem)
                res = await uow.semantics.activate_version(doc_id, sem.id)
                uow.commit()
                print(f"Worker {version} activated: {res}")
        except Exception as e:
            print(f"Worker {version} failed: {e}")


    # Run version 1 and 2 concurrently
    await asyncio.gather(worker(1, factory1), worker(2, factory1))
    
    # Verify unique constraint holds and exactly one is active
    cursor = conn.execute("SELECT * FROM document_semantics WHERE document_id=? AND is_active=1", (doc_id,))
    active_rows = cursor.fetchall()
    assert len(active_rows) == 1
    # Because worker 2 might run before or after worker 1, we just verify the invariant:
    # If 2 finished last, active is 2. If 1 finished last, active is 2 (because 1 doesn't overwrite 2).
    # Therefore, active MUST be 2.
    assert active_rows[0]["semantic_version"] == "2"

@pytest.mark.asyncio
async def test_fail_open_and_error_payload(
    memory_db: sqlite3.Connection, uow_factory: MockUoWFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "2", datetime.now(UTC).isoformat(), "[]")
    )
    stage = SemanticExtractionStage(uow_factory=uow_factory)
    
    # Monkeypatch to force an exception
    async def _mock_save(*args: Any, **kwargs: Any) -> None:
        raise ValueError("Simulated catastrophic failure")
    
    # We patch activate_version to throw, to simulate mid-process failure
    # Actually, we can patch uow.semantics.activate_version
    import persistence.sqlite.semantic_repository
    monkeypatch.setattr(persistence.sqlite.semantic_repository.SQLiteSemanticRepository, "activate_version", _mock_save)

    result = await stage.execute(MockContext(doc_id))
    
    # The stage itself MUST succeed to keep baseline pipeline open
    assert result.success is True
    assert "warning" in result.data
    
    with uow_factory.create() as uow:
        cursor = memory_db.execute("SELECT * FROM document_semantics WHERE document_id=? ORDER BY created_at DESC LIMIT 1", (doc_id,))
        row = cursor.fetchone()
        assert row["status"] == "failed"
        assert row["is_active"] == 0
        
        payload = json.loads(row["semantics_json"])
        assert "error_code" in payload
        assert "message" in payload
        assert "traceback" not in payload
        assert "Simulated catastrophic failure" not in str(payload)



@pytest.mark.asyncio
async def test_pipeline_integration(
    memory_db: sqlite3.Connection, uow_factory: MockUoWFactory
) -> None:
    from pipeline.pipeline import DocumentIntelligencePipeline
    from pipeline.interfaces import PipelineContext
    from content.resource.handle import ResourceHandle
    
    # 1. Provide a document
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "2", datetime.now(UTC).isoformat(), "[]")
    )
    
    class MockStreamRef:
        def open_stream(self) -> Any:
            import io

            import fitz

            doc = fitz.open()
            doc.new_page()
            return io.BytesIO(doc.write())

    class MockHandle:
        def __init__(self, handle_id: str) -> None:
            self.id = handle_id
            self.stream_reference = MockStreamRef()

    handle = MockHandle(doc_id)

    stage = SemanticExtractionStage(uow_factory=uow_factory)
    
    # We must provide a mock stage that sets document_id, since IngestionStage usually does this
    class MockIngestionStage:
        @property
        def stage_name(self) -> str:
            return "Ingestion"

        def retry_policy(self) -> Any:
            from pipeline.interfaces import RetryPolicy

            class Pol(RetryPolicy):
                @property
                def max_retries(self) -> int:
                    return 0

                @property
                def delay_seconds(self) -> int:
                    return 0

            return Pol()

        async def can_skip(self, ctx: PipelineContext) -> bool:
            return False

        async def execute(self, ctx: PipelineContext) -> Any:
            ctx.set("document_id", handle.id)
            from pipeline.interfaces import StageResult

            class Res(StageResult):
                @property
                def success(self) -> bool:
                    return True

                @property
                def data(self) -> dict[str, Any]:
                    return {}

                @property
                def error(self) -> str | None:
                    return None

            return Res()
            
    pipeline = DocumentIntelligencePipeline(stages=[MockIngestionStage(), stage])
    
    results = await pipeline.run(handle)  # type: ignore[arg-type]
    
    assert results["stages"]["SemanticExtraction"]["status"] == "completed"
    
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active is not None
        assert active.status == "completed"
        assert active.is_active is True
        assert active.semantic_version == "2"





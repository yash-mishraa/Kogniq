import pytest
import sqlite3
import json
from datetime import datetime, timezone
import uuid
import asyncio

from content.normalized.semantics import DocumentSemantics
from persistence.factory import SQLiteRepositoryFactory
from persistence.uow import SQLiteUnitOfWork
from persistence.sqlite.schema import init_db
from pipeline.stages.semantic import SemanticExtractionStage
from pipeline.interfaces import PipelineContext

class MockContext(PipelineContext):
    def __init__(self, doc_id):
        self._doc_id = doc_id
        self._metadata = {}

    @property
    def document_id(self) -> str: return self._doc_id
    @property
    def metadata(self) -> dict: return self._metadata
    def get(self, key): return self._metadata.get(key)
    def set(self, key, value): self._metadata[key] = value

class MockUoWFactory:
    def __init__(self, conn):
        self._conn = conn
        self._factory = SQLiteRepositoryFactory()
    
    def create(self):
        class CM:
            def __enter__(self): return self.conn
            def __exit__(self, *args): pass
            def __init__(self, c): self.conn = c
        return SQLiteUnitOfWork(CM(self._conn), self._factory)

@pytest.fixture
def memory_db():
    conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn

@pytest.fixture
def uow_factory(memory_db):
    return MockUoWFactory(memory_db)

@pytest.mark.asyncio
async def test_schema_and_basic_execution(memory_db, uow_factory):
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "1", datetime.now(timezone.utc).isoformat(), "[]")
    )
    stage = SemanticExtractionStage(uow_factory=uow_factory)
    
    result = await stage.execute(MockContext(doc_id))
    assert result.success
    
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active is not None
        assert active.status == "completed"
        assert active.is_active is True
        assert active.semantic_version == "1"
        payload = json.loads(active.semantics_json)
        assert payload["schema_version"] == 1
        assert "p1_d1_status" not in payload

@pytest.mark.asyncio
async def test_stale_version_ignored(memory_db, uow_factory):
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "1", datetime.now(timezone.utc).isoformat(), "[]")
    )
    
    # Insert active version "2"
    v2 = DocumentSemantics(id=str(uuid.uuid4()), document_id=doc_id, semantic_version="2", status="completed", is_active=True, semantics_json="{}", created_at=datetime.now(timezone.utc))
    with uow_factory.create() as uow:
        await uow.semantics.save(v2)
        uow.commit()

    # Simulate older version "1" completing late
    v1 = DocumentSemantics(id=str(uuid.uuid4()), document_id=doc_id, semantic_version="1", status="completed", is_active=False, semantics_json="{}", created_at=datetime.now(timezone.utc))
    with uow_factory.create() as uow:
        await uow.semantics.save(v1)
        activated = await uow.semantics.activate_version(doc_id, v1.id)
        assert not activated
        uow.commit()

    # Verify active is still 2
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active.semantic_version == "2"

@pytest.mark.asyncio
async def test_same_version_behavior(memory_db, uow_factory):
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "1", datetime.now(timezone.utc).isoformat(), "[]")
    )
    
    # Insert active version "1"
    id1 = str(uuid.uuid4())
    v1_a = DocumentSemantics(id=id1, document_id=doc_id, semantic_version="1", status="completed", is_active=True, semantics_json="{}", created_at=datetime.now(timezone.utc))
    with uow_factory.create() as uow:
        await uow.semantics.save(v1_a)
        uow.commit()

    # Another job completes for version "1"
    id2 = str(uuid.uuid4())
    v1_b = DocumentSemantics(id=id2, document_id=doc_id, semantic_version="1", status="completed", is_active=False, semantics_json="{}", created_at=datetime.now(timezone.utc))
    with uow_factory.create() as uow:
        await uow.semantics.save(v1_b)
        activated = await uow.semantics.activate_version(doc_id, id2)
        assert activated
        uow.commit()

    # Verify active is id2 and exactly one active exists
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active.id == id2
        cursor = memory_db.execute("SELECT COUNT(*) as c FROM document_semantics WHERE document_id=? AND is_active=1", (doc_id,))
        assert cursor.fetchone()["c"] == 1

@pytest.mark.asyncio
async def test_concurrency_activation():
    # To test SQLite concurrency effectively, we will simulate two coroutines interleaving activate_version logic
    # using a shared SQLite memory connection in serialized mode (which is thread-safe).
    # Since we use asyncio, they execute on the same thread, but we can prove the UoW boundaries and unique constraint.
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    doc_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "1", datetime.now(timezone.utc).isoformat(), "[]")
    )
    
    factory1 = MockUoWFactory(conn)
    
    async def worker(version, uow_factory):
        import asyncio
        await asyncio.sleep(0.01) # provoke context switch
        sem = DocumentSemantics(id=str(uuid.uuid4()), document_id=doc_id, semantic_version=str(version), status="completed", is_active=False, semantics_json="{}", created_at=datetime.now(timezone.utc))
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
async def test_fail_open_and_error_payload(memory_db, uow_factory, monkeypatch):
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "1", datetime.now(timezone.utc).isoformat(), "[]")
    )
    stage = SemanticExtractionStage(uow_factory=uow_factory)
    
    # Monkeypatch to force an exception
    async def _mock_save(*args, **kwargs):
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
async def test_pipeline_integration(memory_db, uow_factory):
    from pipeline.pipeline import DocumentIntelligencePipeline
    from pipeline.interfaces import PipelineContext
    from content.resource.handle import ResourceHandle
    
    # 1. Provide a document
    doc_id = str(uuid.uuid4())
    memory_db.execute(
        "INSERT INTO documents (id, title, source, checksum, version, created_at, pages_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, "Test Doc", "upload", "123", "1", datetime.now(timezone.utc).isoformat(), "[]")
    )
    
    class MockHandle:
        def __init__(self, id):
            self.id = id
            
    handle = MockHandle(doc_id)

    stage = SemanticExtractionStage(uow_factory=uow_factory)
    
    # We must provide a mock stage that sets document_id, since IngestionStage usually does this
    class MockIngestionStage:
        @property
        def stage_name(self) -> str: return "Ingestion"
        def retry_policy(self):
            from pipeline.interfaces import RetryPolicy
            class Pol(RetryPolicy):
                @property
                def max_retries(self): return 0
                @property
                def delay_seconds(self): return 0
            return Pol()
        async def can_skip(self, ctx): return False
        async def execute(self, ctx):
            ctx.set("document_id", handle.id)
            from pipeline.interfaces import StageResult
            class Res(StageResult):
                @property
                def success(self): return True
                @property
                def data(self): return {}
                @property
                def error(self): return None
            return Res()
            
    pipeline = DocumentIntelligencePipeline(stages=[MockIngestionStage(), stage])
    
    results = await pipeline.run(handle)
    
    assert results["stages"]["SemanticExtraction"]["status"] == "completed"
    
    with uow_factory.create() as uow:
        active = await uow.semantics.get_active(doc_id)
        assert active is not None
        assert active.status == "completed"
        assert active.is_active is True
        assert active.semantic_version == "1"



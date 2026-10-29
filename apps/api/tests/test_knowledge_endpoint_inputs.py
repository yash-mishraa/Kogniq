from unittest.mock import AsyncMock, MagicMock
import pytest
from content.chunking import ChunkCollection
from fastapi import HTTPException
from apps.api.app.routers.knowledge import extract_knowledge


@pytest.mark.asyncio
async def test_extract_knowledge_handles_chunk_collection() -> None:
    session = MagicMock(user_id="user-1")
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = session

    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value = uow
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    uow.concepts.save_all = AsyncMock()
    uow.relationships.save_all = AsyncMock()

    doc = MagicMock(user_id="user-1")
    uow.documents.get = AsyncMock(return_value=doc)

    mock_chunk = MagicMock(id="c1", text="Chunk content")
    chunk_coll = ChunkCollection(chunks=(mock_chunk,))
    uow.chunks.get_by_document = AsyncMock(return_value=chunk_coll)

    extractor = AsyncMock()
    mock_concept = MagicMock(id="con-1", document_id="doc-1")
    mock_rel = MagicMock(id="rel-1", document_id="doc-1")
    extractor.extract.return_value = MagicMock(
        graph=MagicMock(concepts=[mock_concept], relationships=[mock_rel])
    )

    req_obj = MagicMock()
    req_obj.cookies = {}

    result = await extract_knowledge(
        document_id="doc-1",
        request_obj=req_obj,
        authorization="Bearer test",
        auth_service=auth_service,
        uow_factory=uow_factory,
        extractor=extractor,
    )

    extractor.extract.assert_called_once()
    passed_collection = extractor.extract.call_args[0][0]
    assert isinstance(passed_collection, ChunkCollection)
    assert len(passed_collection.chunks) == 1


@pytest.mark.asyncio
async def test_extract_knowledge_handles_raw_tuple() -> None:
    session = MagicMock(user_id="user-1")
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = session

    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value = uow
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    uow.concepts.save_all = AsyncMock()
    uow.relationships.save_all = AsyncMock()

    doc = MagicMock(user_id="user-1")
    uow.documents.get = AsyncMock(return_value=doc)

    mock_chunk = MagicMock(id="c1", text="Raw tuple chunk")
    uow.chunks.get_by_document = AsyncMock(return_value=(mock_chunk,))

    extractor = AsyncMock()
    extractor.extract.return_value = MagicMock(
        graph=MagicMock(concepts=[], relationships=[])
    )

    req_obj = MagicMock()
    req_obj.cookies = {}

    result = await extract_knowledge(
        document_id="doc-1",
        request_obj=req_obj,
        authorization="Bearer test",
        auth_service=auth_service,
        uow_factory=uow_factory,
        extractor=extractor,
    )

    extractor.extract.assert_called_once()
    passed_collection = extractor.extract.call_args[0][0]
    assert isinstance(passed_collection, ChunkCollection)
    assert len(passed_collection.chunks) == 1


@pytest.mark.asyncio
async def test_extract_knowledge_rejects_empty_chunks() -> None:
    session = MagicMock(user_id="user-1")
    auth_service = AsyncMock()
    auth_service.validate_session.return_value = session

    uow_factory = MagicMock()
    uow = MagicMock()
    uow_factory.create.return_value = uow
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    uow.concepts.save_all = AsyncMock()
    uow.relationships.save_all = AsyncMock()

    doc = MagicMock(user_id="user-1")
    uow.documents.get = AsyncMock(return_value=doc)
    uow.chunks.get_by_document = AsyncMock(return_value=ChunkCollection(chunks=()))

    extractor = AsyncMock()
    req_obj = MagicMock()
    req_obj.cookies = {}

    with pytest.raises(HTTPException) as exc_info:
        await extract_knowledge(
            document_id="doc-1",
            request_obj=req_obj,
            authorization="Bearer test",
            auth_service=auth_service,
            uow_factory=uow_factory,
            extractor=extractor,
        )

    assert exc_info.value.status_code == 400
    assert "no chunks" in exc_info.value.detail.lower()

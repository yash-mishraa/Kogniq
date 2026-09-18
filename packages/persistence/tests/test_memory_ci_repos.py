import pytest
from persistence.factory import MemoryRepositoryFactory

from content.domain.entities import LearningResource, ResourceChunk, ResourceSection
from content.domain.enums import ProcessingStatus, ResourceType


@pytest.mark.asyncio
async def test_memory_ci_repositories() -> None:
    factory = MemoryRepositoryFactory()

    res_repo = factory.create_learning_resource_repository()
    sec_repo = factory.create_resource_section_repository()
    chunk_repo = factory.create_resource_chunk_repository()

    # Save resource
    res = LearningResource(
        id="res-1",
        title="Memory",
        resource_type=ResourceType.TEXT,
        source="memory.txt",
        checksum="mem",
        status=ProcessingStatus.PROCESSED,
    )
    await res_repo.save(res)

    # Verify get
    got_res = await res_repo.get("res-1", "user-1")
    assert got_res is not None
    assert got_res.title == "Memory"

    # Save sections
    sec = ResourceSection(
        id="sec-1",
        resource_id="res-1",
        title="Sec 1",
        order=0,
    )
    await sec_repo.save_all([sec])

    # Verify section
    sections = await sec_repo.get_by_resource("res-1", "user-1")
    assert len(sections) == 1
    assert sections[0].id == "sec-1"

    # Save chunks
    chunk = ResourceChunk(
        id="chunk-1",
        resource_id="res-1",
        section_id="sec-1",
        text="Text",
        order=0,
        checksum="hash",
    )
    await chunk_repo.save_all([chunk])

    # Verify chunks
    chunks = await chunk_repo.get_by_resource("res-1", "user-1")
    assert len(chunks) == 1
    assert chunks[0].id == "chunk-1"

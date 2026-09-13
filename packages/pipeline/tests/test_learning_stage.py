from collections.abc import Sequence
from typing import Any
from unittest.mock import AsyncMock, MagicMock

# ruff: noqa: ARG002
import pytest
from knowledge.graph import KnowledgeGraph
from pipeline.pipeline import DefaultPipelineContext
from pipeline.stages.learning import LearningGenerationStage

from content.chunking.collection import ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.generators.base.exceptions import LearningGenerationError
from learning_content.providers.interfaces import AbstractLearningGenerator


class MockUoW:
    def __init__(self) -> None:
        self.learning = MagicMock()
        self.learning.save = AsyncMock()
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> "MockUoW":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type:
            self.rolled_back = True
        else:
            self.committed = True


class MockUoWFactory:
    def __init__(self) -> None:
        self.uow = MockUoW()

    def create(self) -> MockUoW:
        return self.uow


class MockGenerator1(AbstractLearningGenerator):
    def __init__(self, name: str, should_fail: bool = False) -> None:
        self._name = name
        self.should_fail = should_fail

    def generate(self, chunks: ChunkCollection, graph: KnowledgeGraph) -> LearningContent:
        if self.should_fail:
            raise LearningGenerationError(f"Mock failure in {self._name}")
        content = MagicMock(spec=LearningContent)
        content.title = f"{self._name} Content"
        return content

    def generate_batch(
        self, chunks_batch: Sequence[ChunkCollection], graphs: Sequence[KnowledgeGraph]
    ) -> LearningContentCollection:
        # Returning MagicMock to satisfy types for this mock
        return MagicMock(spec=LearningContentCollection)

    @property
    def info(self) -> Any:
        return MagicMock()


class MockGenerator2(MockGenerator1):
    pass


@pytest.fixture
def uow_factory() -> MockUoWFactory:
    return MockUoWFactory()


@pytest.fixture
def context() -> DefaultPipelineContext:
    ctx = DefaultPipelineContext()
    ctx.set("chunk_collection", MagicMock(spec=ChunkCollection))
    ctx.set("knowledge_graph", MagicMock(spec=KnowledgeGraph))
    return ctx


@pytest.mark.asyncio
async def test_learning_generation_stage_success(
    uow_factory: MockUoWFactory, context: DefaultPipelineContext
) -> None:
    generators: list[AbstractLearningGenerator] = [MockGenerator1("Gen1"), MockGenerator2("Gen2")]
    stage = LearningGenerationStage(generators, uow_factory)  # type: ignore

    assert stage.stage_name == "LearningGeneration"
    assert not await stage.can_skip(context)

    result = await stage.execute(context)

    assert result.success is True
    assert result.data["status"] == "COMPLETED"
    assert "MockGenerator1" in result.data["generated"]
    assert "MockGenerator2" in result.data["generated"]
    assert not result.data["failed"]

    materials = context.get("learning_materials")
    assert len(materials) == 2
    assert materials[0].title == "Gen1 Content"

    assert uow_factory.uow.committed is True
    assert uow_factory.uow.learning.save.call_count == 2


@pytest.mark.asyncio
async def test_learning_generation_stage_partial_failure(
    uow_factory: MockUoWFactory, context: DefaultPipelineContext
) -> None:
    generators: list[AbstractLearningGenerator] = [
        MockGenerator1("SuccessGen"),
        MockGenerator2("FailGen", should_fail=True),
    ]
    stage = LearningGenerationStage(generators, uow_factory)  # type: ignore

    result = await stage.execute(context)

    assert result.success is True
    assert result.data["status"] == "COMPLETED_WITH_WARNINGS"
    assert "MockGenerator1" in result.data["generated"]

    failed_generators = [f["generator"] for f in result.data["failed"]]
    assert "MockGenerator2" in failed_generators

    materials = context.get("learning_materials")
    assert len(materials) == 1
    assert materials[0].title == "SuccessGen Content"

    assert uow_factory.uow.committed is True
    assert uow_factory.uow.learning.save.call_count == 1


@pytest.mark.asyncio
async def test_learning_generation_stage_skip(uow_factory: MockUoWFactory) -> None:
    stage = LearningGenerationStage([], uow_factory)  # type: ignore

    ctx = DefaultPipelineContext()
    assert await stage.can_skip(ctx) is True

    ctx.set("chunk_collection", MagicMock(spec=ChunkCollection))
    assert await stage.can_skip(ctx) is True

    ctx.set("knowledge_graph", MagicMock(spec=KnowledgeGraph))
    assert await stage.can_skip(ctx) is False

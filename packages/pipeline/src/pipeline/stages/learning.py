import logging
from collections.abc import Sequence
from typing import Any

from knowledge.graph import KnowledgeGraph
from persistence.uow_factory import AbstractUnitOfWorkFactory

from content.chunking.collection import ChunkCollection
from learning_content.generators.base.exceptions import LearningGenerationError
from learning_content.providers.interfaces import AbstractLearningGenerator
from pipeline.interfaces import PipelineContext, RetryPolicy, StageResult

logger = logging.getLogger(__name__)


class LearningGenerationRetryPolicy:
    @property
    def max_retries(self) -> int:
        return 0

    @property
    def delay_seconds(self) -> int:
        return 0


class LearningGenerationStageResult:
    def __init__(self, success: bool, data: dict[str, Any], error: str | None = None) -> None:
        self._success = success
        self._data = data
        self._error = error

    @property
    def success(self) -> bool:
        return self._success

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def error(self) -> str | None:
        return self._error


class LearningGenerationStage:
    """
    Pipeline stage for generating learning content (notes, summary, flashcards, study_guide, etc.).
    Iterates over the provided generators, producing content using
    the ChunkCollection and KnowledgeGraph.
    Isolates errors so one failing generator doesn't fail the entire pipeline.
    """

    def __init__(
        self,
        generators: Sequence[AbstractLearningGenerator],
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.generators = generators
        self.uow_factory = uow_factory
        self._retry_policy = LearningGenerationRetryPolicy()

    @property
    def stage_name(self) -> str:
        return "LearningGeneration"

    async def can_skip(self, context: PipelineContext) -> bool:
        chunk_collection: ChunkCollection | None = context.get("chunk_collection")
        graph: KnowledgeGraph | None = context.get("knowledge_graph")
        return not bool(chunk_collection) or not bool(graph)

    async def execute(self, context: PipelineContext) -> StageResult:
        chunk_collection: ChunkCollection | None = context.get("chunk_collection")
        graph: KnowledgeGraph | None = context.get("knowledge_graph")

        if not chunk_collection or not graph:
            return LearningGenerationStageResult(
                False, {}, "Missing chunk_collection or knowledge_graph in context"
            )

        results_data: dict[str, Any] = {
            "generated": [],
            "failed": [],
        }

        materials = []

        for generator in self.generators:
            generator_name = generator.__class__.__name__
            try:
                logger.info(f"Generating learning material with {generator_name}...")
                content = generator.generate(chunk_collection, graph)
                materials.append(content)
                results_data["generated"].append(generator_name)
            except LearningGenerationError as e:
                logger.error(f"Failed to generate material with {generator_name}: {e}")
                results_data["failed"].append({"generator": generator_name, "error": str(e)})
            except Exception as e:
                logger.exception(f"Unexpected error while generating with {generator_name}: {e}")
                results_data["failed"].append({"generator": generator_name, "error": str(e)})

        if materials:
            uow = self.uow_factory.create()
            with uow:
                for material in materials:
                    await uow.learning.save(material)

        # Append to context
        existing_materials = context.get("learning_materials") or []
        context.set("learning_materials", existing_materials + materials)

        if results_data["failed"]:
            results_data["status"] = "COMPLETED_WITH_WARNINGS"
        else:
            results_data["status"] = "COMPLETED"

        return LearningGenerationStageResult(success=True, data=results_data)

    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

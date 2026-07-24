import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Any

from content.resource.handle import ResourceHandle
from jobs.interfaces import AbstractJobManager

from .exceptions import PipelineExecutionError
from .interfaces import PipelineStage

logger = logging.getLogger(__name__)


class DefaultPipelineContext:
    def __init__(self) -> None:
        self._document_id: str | None = None
        self._metadata: dict[str, Any] = {}

    @property
    def document_id(self) -> str:
        if not self._document_id:
            raise ValueError("document_id not set in context")
        return self._document_id

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    def get(self, key: str) -> Any:
        return self._metadata.get(key)

    def set(self, key: str, value: Any) -> None:
        self._metadata[key] = value
        if key == "document_id":
            self._document_id = value


class DocumentIntelligencePipeline:
    """
    Orchestration layer that handles the execution of independent pipeline stages.
    Coordinates between domain stages (Parse, Chunk, Embed, Extract, Generate) and the JobManager.
    """

    def __init__(
        self,
        stages: list[PipelineStage],
        job_manager: AbstractJobManager | None = None,
    ) -> None:
        self.stages = stages
        self.job_manager = job_manager

    async def run(self, handle: ResourceHandle, job_id: str | None = None) -> dict[str, Any]:
        """
        Executes the intelligence pipeline sequentially across configured stages.
        """
        start_time = time.perf_counter()
        started_at = datetime.now(UTC)

        logger.info(f"Starting pipeline execution for resource: {handle.id}")

        context = DefaultPipelineContext()
        context.set("resource_handle", handle)

        total_stages = len(self.stages)
        results: dict[str, Any] = {}

        try:
            for i, stage in enumerate(self.stages):
                stage_name = stage.stage_name
                logger.info(f"Evaluating stage: {stage_name}")

                if job_id and self.job_manager:
                    await self.job_manager.update_progress(
                        job_id=job_id,
                        current_stage=stage_name,
                        completed_stages=i,
                        total_stages=total_stages,
                        stage_status="running",
                        message=f"Starting stage: {stage_name}",
                    )

                if await stage.can_skip(context):
                    logger.info(f"Skipping stage: {stage_name}")
                    if job_id and self.job_manager:
                        await self.job_manager.update_progress(
                            job_id=job_id,
                            current_stage=stage_name,
                            completed_stages=i + 1,
                            total_stages=total_stages,
                            stage_status="skipped",
                            message=f"Skipped stage: {stage_name}",
                        )
                    results[stage_name] = {"status": "skipped"}
                    continue

                retry_policy = stage.retry_policy()
                max_retries = retry_policy.max_retries
                delay = retry_policy.delay_seconds

                retries = 0

                while retries <= max_retries:
                    try:
                        logger.info(
                            f"Stage {stage_name} Attempt {retries + 1}/{max_retries + 1}"
                        )
                        result = await stage.execute(context)

                        if result.success:
                            logger.info(f"Stage {stage_name} completed successfully.")
                            results[stage_name] = {"status": "completed", "data": result.data}
                            break
                        else:
                            logger.warning(f"Stage {stage_name} reported error: {result.error}")
                            raise Exception(result.error)

                    except Exception as e:
                        retries += 1
                        logger.error(f"Stage {stage_name} failed: {e}")
                        if retries <= max_retries:
                            logger.info(f"Retrying stage {stage_name} in {delay} seconds...")
                            await asyncio.sleep(delay)
                        else:
                            if job_id and self.job_manager:
                                await self.job_manager.update_progress(
                                    job_id=job_id,
                                    current_stage=stage_name,
                                    completed_stages=i,
                                    total_stages=total_stages,
                                    stage_status="failed",
                                    message=str(e),
                                )
                            # Halt pipeline on failure
                            raise PipelineExecutionError(
                                f"Pipeline failed at stage {stage_name}: {e}"
                            ) from e

                if job_id and self.job_manager:
                    await self.job_manager.update_progress(
                        job_id=job_id,
                        current_stage=stage_name,
                        completed_stages=i + 1,
                        total_stages=total_stages,
                        stage_status="completed",
                        message=f"Completed stage: {stage_name}",
                    )

            completed_at = datetime.now(UTC)
            end_time = time.perf_counter()

            execution_metadata = {
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "total_processing_time_ms": (end_time - start_time) * 1000,
                "document_id": context.get("document_id"),
            }

            logger.info("Pipeline execution completed successfully.")
            return {"metadata": execution_metadata, "stages": results}

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise PipelineExecutionError(f"Pipeline execution failed: {e}") from e

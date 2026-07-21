from backend.core.exceptions import BackendError
from backend.schemas.learning import LearningGenerationRequest, LearningGenerationResponse
from backend.services.context_provider import LearningContextProvider
from backend.services.generator_factory import GeneratorFactory
from persistence.uow_factory import AbstractUnitOfWorkFactory


class LearningService:
    """
    Orchestrates learning artifact generation.
    Does not construct objects or prompts; delegates to providers and factories.
    """

    def __init__(
        self,
        context_provider: LearningContextProvider,
        generator_factory: GeneratorFactory,
        uow_factory: AbstractUnitOfWorkFactory,
    ) -> None:
        self.context_provider = context_provider
        self.generator_factory = generator_factory
        self.uow_factory = uow_factory

    async def generate_artifact(
        self, request: LearningGenerationRequest
    ) -> LearningGenerationResponse:
        # 1. Resolve Generator
        generator = self.generator_factory.get_generator(request.generator)

        # 2. Resolve Context
        context = await self.context_provider.resolve_context(request.document_id)

        # 3. Generate
        try:
            # We bypass the batching for the simple single-document case
            # StudyGuideGenerator uses the same BaseLearningGenerator or
            # AbstractLearningGenerator interface.
            content = generator.generate(context.chunks, context.graph)
        except BackendError:
            raise
        except Exception as e:
            raise BackendError(
                "generation_failed", f"Failed to generate artifact: {e}", status_code=500
            ) from e

        # Persist content
        try:
            with self.uow_factory.create() as uow:
                await uow.learning.save(content)
                uow.commit()
        except Exception as e:
            raise BackendError(
                "persistence_failed", f"Failed to persist learning artifact: {e}", status_code=500
            ) from e

        # 4. Map Response
        metadata_dict = {
            "prompt_version": content.metadata.prompt_version,
            "generation_version": content.metadata.generation_version,
            "language": content.metadata.language,
        }

        stats_dict = {
            "word_count": content.statistics.word_count,
            "character_count": content.statistics.character_count,
            "estimated_tokens": content.statistics.estimated_tokens,
            "confidence": content.statistics.confidence,
        }

        return LearningGenerationResponse(
            status="completed",
            document_id=request.document_id,
            generator=request.generator,
            title=content.title,
            content_type=str(content.content_type.value),
            generated_content=content.body,
            metadata=metadata_dict,
            statistics=stats_dict,
            processing_time_ms=content.statistics.processing_time_ms,
            warnings=[],
        )

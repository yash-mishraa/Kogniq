import time
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection
from learning_content.collection import LearningContentCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.generators.base.models import GenerationContext
from learning_content.generators.explanation.generator import ExplanationGenerator
from learning_content.generators.flashcards.generator import FlashcardsGenerator
from learning_content.generators.notes.generator import NotesGenerator
from learning_content.generators.quiz.generator import QuizGenerator
from learning_content.generators.study_guide.composer import StudyGuideComposer
from learning_content.generators.study_guide.exceptions import StudyGuideGenerationError
from learning_content.generators.study_guide.renderer import StudyGuideRenderer
from learning_content.generators.summary.generator import SummaryGenerator
from learning_content.metadata import LearningContentMetadata
from learning_content.providers.interfaces import AbstractLearningGenerator
from learning_content.providers.provider_info import GeneratorInfo
from learning_content.statistics import LearningContentStatistics


class StudyGuideGenerator(AbstractLearningGenerator):
    """
    Kogniq's first composition engine. Orchestrates multiple sub-generators
    and composes their output into a unified Study Guide artifact.
    Does NOT contain provider invocation or parsing logic itself.
    """

    def __init__(
        self,
        summary_generator: SummaryGenerator,
        notes_generator: NotesGenerator,
        flashcards_generator: FlashcardsGenerator,
        quiz_generator: QuizGenerator,
        explanation_generator: ExplanationGenerator,
    ) -> None:
        self._summary_gen = summary_generator
        self._notes_gen = notes_generator
        self._flashcards_gen = flashcards_generator
        self._quiz_gen = quiz_generator
        self._explanation_gen = explanation_generator

        self._composer = StudyGuideComposer()
        self._renderer = StudyGuideRenderer()

    def info(self) -> GeneratorInfo:
        return GeneratorInfo(
            generator_id="study-guide-generator-v1",
            generator_name="Study Guide Composer",
            generator_version="1.0",
            provider_name="composite",
            supported_content_types=(ContentType.STUDY_GUIDE,),
            maximum_chunks=150,
            maximum_tokens=16000,
            supports_batch_generation=False,
        )

    def generate(self, chunks: ChunkCollection, graph: KnowledgeGraph) -> LearningContent:
        context = GenerationContext(chunks=chunks, graph=graph)
        start_time = time.perf_counter()

        try:
            # Encapsulated generation strategy (allows parallelization later)
            artifacts = self._generate_sections(context)

            # Assembly
            guide = self._composer.compose("Comprehensive Study Guide", artifacts)

            # Rendering
            markdown_body = self._renderer.to_markdown(guide)

            end_time = time.perf_counter()
            total_time_ms = (end_time - start_time) * 1000.0

            # Aggregation
            stats = self._aggregate_statistics(artifacts, total_time_ms)
            meta = self._aggregate_metadata(artifacts)

            source_chunk_ids = tuple(c.id for c in chunks.chunks)
            source_document_id = chunks.chunks[0].document_id if chunks.chunks else "unknown"

            return LearningContent(
                id=str(uuid.uuid4()),
                title=guide.title,
                body=markdown_body,
                content_type=ContentType.STUDY_GUIDE,
                source_document_id=source_document_id,
                source_chunk_ids=source_chunk_ids,
                metadata=meta,
                statistics=stats,
                created_at=datetime.now(UTC),
            )
        except Exception as e:
            raise StudyGuideGenerationError(f"Failed to generate study guide: {e}") from e

    def generate_batch(
        self, collections: tuple[ChunkCollection, ...], graphs: tuple[KnowledgeGraph, ...]
    ) -> LearningContentCollection:
        if len(collections) != len(graphs):
            raise StudyGuideGenerationError("Mismatched collections and graphs lengths.")

        contents = []
        for chunks, graph in zip(collections, graphs, strict=True):
            contents.append(self.generate(chunks, graph))

        return LearningContentCollection(contents=tuple(contents))

    def _generate_sections(self, context: GenerationContext) -> Sequence[LearningContent]:
        """
        Executes the sub-generators.
        Currently sequential. Future-proofed for concurrent execution.
        """
        artifacts = []
        # Any failure here will appropriately bubble up and abort composition.
        artifacts.append(self._summary_gen.generate(context.chunks, context.graph))
        artifacts.append(self._notes_gen.generate(context.chunks, context.graph))
        artifacts.append(self._explanation_gen.generate(context.chunks, context.graph))
        artifacts.append(self._flashcards_gen.generate(context.chunks, context.graph))
        artifacts.append(self._quiz_gen.generate(context.chunks, context.graph))
        return artifacts

    def _aggregate_statistics(
        self, artifacts: Sequence[LearningContent], total_time_ms: float
    ) -> LearningContentStatistics:
        total_chars = sum(a.statistics.character_count for a in artifacts)
        total_words = sum(a.statistics.word_count for a in artifacts)
        total_tokens = sum(a.statistics.estimated_tokens for a in artifacts)

        # Average confidence
        confidence = sum(a.statistics.confidence for a in artifacts) / max(len(artifacts), 1)

        return LearningContentStatistics(
            character_count=total_chars,
            word_count=total_words,
            estimated_tokens=total_tokens,
            processing_time_ms=total_time_ms,
            confidence=confidence,
            heading_count=len(artifacts),  # Represents the number of composite sections
        )

    def _aggregate_metadata(self, artifacts: Sequence[LearningContent]) -> LearningContentMetadata:
        # Use the first artifact's provider/model as representative if available
        first = artifacts[0].metadata if artifacts else None

        provider = first.provider if first else "unknown"
        model = first.model if first else "unknown"
        model_version = first.model_version if first else "unknown"

        prompt_versions = tuple(
            sorted({a.metadata.prompt_version for a in artifacts if a.metadata.prompt_version})
        )

        return LearningContentMetadata(
            provider=provider,
            model=model,
            model_version=model_version,
            generation_version="1.0",
            language=first.language if first else "en",
            educational_level="unknown",
            subject="unknown",
            syllabus="unknown",
            tags=(),
            generation_id=str(uuid.uuid4()),
            prompt_version=",".join(prompt_versions),
            template_version="1.0",
        )

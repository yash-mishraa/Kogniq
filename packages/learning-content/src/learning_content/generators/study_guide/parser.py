import uuid
from datetime import UTC, datetime

from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.generators.base.interfaces import AbstractContentParser
from learning_content.generators.base.models import GenerationContext, GenerationMetadata
from learning_content.generators.study_guide.exceptions import StudyGuideGenerationError
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


class StudyGuideParser(AbstractContentParser):
    """
    Parses the generated Study Guide.
    """

    def parse(
        self, raw_response: str, context: GenerationContext, metadata: GenerationMetadata
    ) -> LearningContent:
        if not raw_response.strip():
            raise StudyGuideGenerationError("Received empty response from provider")

        stats = LearningContentStatistics(
            character_count=len(raw_response),
            word_count=len(raw_response.split()),
            estimated_tokens=int(len(raw_response.split()) * 1.3),
            processing_time_ms=metadata.generation_time_ms,
            confidence=0.85,
            heading_count=raw_response.count("#"),
        )

        content_meta = LearningContentMetadata(
            provider=metadata.provider_name,
            model=metadata.model_name,
            model_version=metadata.model_version,
            generation_version=metadata.generation_version,
            language="en",
            educational_level="unknown",
            subject="unknown",
            syllabus="unknown",
            tags=(),
            generation_id=str(uuid.uuid4()),
            prompt_version=metadata.prompt_version,
            template_version="1.0",
        )

        source_chunk_ids = tuple(c.id for c in context.chunks.chunks)
        source_document_id = (
            context.chunks.chunks[0].document_id if context.chunks.chunks else "unknown"
        )

        # Extract title or default
        lines = raw_response.strip().split("\n")
        title = "Comprehensive Study Guide"
        if lines and lines[0].startswith("#"):
            title = lines[0].replace("#", "").strip()

        return LearningContent(
            id=str(uuid.uuid4()),
            title=title,
            body=raw_response,
            content_type=ContentType.STUDY_GUIDE,
            source_document_id=source_document_id,
            source_chunk_ids=source_chunk_ids,
            metadata=content_meta,
            statistics=stats,
            created_at=datetime.now(UTC),
        )

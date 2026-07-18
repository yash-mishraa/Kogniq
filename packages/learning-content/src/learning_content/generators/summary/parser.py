import uuid
from datetime import UTC, datetime

from content.chunking import ChunkCollection
from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.generators.summary.exceptions import EmptyResponseError
from learning_content.metadata import LearningContentMetadata
from learning_content.providers.base import AbstractTextGenerationProvider
from learning_content.statistics import LearningContentStatistics


class SummaryParser:
    """
    Parses and validates the raw text response for the Summary Generator.
    """

    def parse(
        self,
        raw_text: str,
        chunks: ChunkCollection,
        provider: AbstractTextGenerationProvider,
    ) -> LearningContent:
        """
        Parse raw text into LearningContent.

        Args:
            raw_text: The raw text from the generator.
            chunks: The source chunk collection used for generation.
            provider: The provider used for generation.

        Returns:
            The constructed LearningContent object.

        Raises:
            EmptyResponseError: If the raw text is empty or whitespace only.
        """
        cleaned_text = raw_text.strip()
        if not cleaned_text:
            raise EmptyResponseError(
                "Received empty or whitespace-only response from the provider."
            )

        statistics = self._calculate_statistics(cleaned_text)
        metadata = self._build_metadata(provider)

        # Determine source_chunk_ids
        source_chunk_ids = tuple(chunk.id for chunk in chunks.chunks)
        source_document_id = chunks.chunks[0].document_id if chunks.chunks else "unknown_document"

        return LearningContent(
            id=str(uuid.uuid4()),
            title="Generated Summary",
            body=cleaned_text,
            content_type=ContentType.SUMMARY,
            source_document_id=source_document_id,
            source_chunk_ids=source_chunk_ids,
            metadata=metadata,
            statistics=statistics,
            created_at=datetime.now(UTC),
        )

    def _calculate_statistics(self, text: str) -> LearningContentStatistics:
        """Calculate statistics for the generated text."""
        char_count = len(text)
        words = text.split()
        word_count = len(words)

        # Simple heuristic: ~1.3 tokens per word
        estimated_tokens = int(word_count * 1.3)

        return LearningContentStatistics(
            character_count=char_count,
            word_count=word_count,
            estimated_tokens=estimated_tokens,
            processing_time_ms=0.0,  # Placeholder
            # Placeholder: 0.5 until evaluation metrics are introduced
            confidence=0.5,
        )

    def _build_metadata(self, provider: AbstractTextGenerationProvider) -> LearningContentMetadata:
        """Build metadata incorporating provider details."""
        return LearningContentMetadata(
            provider=provider.info.provider_id,
            model=provider.info.default_model,
            model_version="1.0",
            generation_version="1.0",
            language="en",
            educational_level="unknown",
            subject="unknown",
            syllabus="unknown",
            tags=(),
            generation_id=str(uuid.uuid4()),
            prompt_version="1.0",
            template_version="1.0",
        )

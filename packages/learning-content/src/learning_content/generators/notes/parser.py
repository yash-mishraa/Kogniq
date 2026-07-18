import re
import uuid
from datetime import UTC, datetime

from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    GenerationContext,
    GenerationMetadata,
    ParsingError,
)
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics
from learning_content.utils import estimate_tokens


class NotesParser(AbstractContentParser):
    """
    Parses and validates the raw text response for the Notes Generator.
    """

    def parse(
        self,
        raw_text: str,
        context: GenerationContext,
        metadata: GenerationMetadata,
    ) -> LearningContent:
        """
        Parse raw text into LearningContent.

        Args:
            raw_text: The raw text from the generator.
            context: The generation context containing chunks and graph.
            metadata: Generation metadata (provider, model, timing).

        Returns:
            The constructed LearningContent object.

        Raises:
            ParsingError: If the raw text is empty, a placeholder, or invalid.
        """
        # Trimming leading/trailing whitespace and collapsing excessive blank lines
        cleaned_text = raw_text.strip()
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

        if not cleaned_text:
            raise ParsingError("Received empty or whitespace-only response from the provider.")

        # Reject common placeholder responses
        lower_text = cleaned_text.lower().strip(". ")
        placeholders = {
            "i cannot answer",
            "no information",
            "unknown",
            "n/a",
            "i don't have enough information",
            "as an ai language model",
            "i cannot fulfill this request",
            "i am unable to provide",
        }

        for placeholder in placeholders:
            if lower_text.startswith(placeholder) or lower_text == placeholder:
                raise ParsingError(f"Provider returned a placeholder response: '{cleaned_text}'")

        statistics = self._calculate_statistics(cleaned_text, metadata.generation_time_ms)
        learning_metadata = self._build_metadata(metadata)

        # Determine source_chunk_ids
        source_chunk_ids = tuple(chunk.id for chunk in context.chunks.chunks)
        source_document_id = (
            context.chunks.chunks[0].document_id if context.chunks.chunks else "unknown_document"
        )

        title = self._extract_title(cleaned_text)

        return LearningContent(
            id=str(uuid.uuid4()),
            title=title,
            body=cleaned_text,
            content_type=ContentType.NOTES,
            source_document_id=source_document_id,
            source_chunk_ids=source_chunk_ids,
            metadata=learning_metadata,
            statistics=statistics,
            created_at=datetime.now(UTC),
        )

    def _extract_title(self, text: str) -> str:
        """Extract the first heading as the title, or fallback."""
        lines = text.splitlines()
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return "Generated Notes"

    def _calculate_statistics(
        self, text: str, generation_time_ms: float
    ) -> LearningContentStatistics:
        """Calculate statistics for the generated text."""
        char_count = len(text)
        words = text.split()
        word_count = len(words)

        estimated_tokens = estimate_tokens(text)

        return LearningContentStatistics(
            character_count=char_count,
            word_count=word_count,
            estimated_tokens=estimated_tokens,
            processing_time_ms=generation_time_ms,
            # Placeholder: 0.5 until evaluation metrics are introduced
            confidence=0.5,
        )

    def _build_metadata(self, metadata: GenerationMetadata) -> LearningContentMetadata:
        """Build metadata incorporating provider details."""
        return LearningContentMetadata(
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

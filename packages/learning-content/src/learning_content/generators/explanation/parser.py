import re
import uuid
from datetime import UTC, datetime

from learning_content.content import LearningContent
from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    GenerationContext,
    GenerationMetadata,
)
from learning_content.generators.explanation.exceptions import InvalidExplanationError
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


class ExplanationParser(AbstractContentParser):
    """
    Parses and validates the raw text response for the Explanation Generator.
    """

    def parse(
        self,
        raw_text: str,
        context: GenerationContext,
        metadata: GenerationMetadata,
    ) -> LearningContent:
        cleaned_text = raw_text.strip()

        # Defensively strip Markdown fences if the provider ignored instructions
        if cleaned_text.startswith("```markdown"):
            cleaned_text = cleaned_text[11:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        if not cleaned_text:
            raise InvalidExplanationError("Received empty response from the provider.")

        if len(cleaned_text) < 80:
            raise InvalidExplanationError(f"Explanation is too short ({len(cleaned_text)} chars).")

        lower_text = cleaned_text.lower()
        if (
            "as an ai" in lower_text
            or "i cannot fulfill this request" in lower_text
            or "here is the explanation" in lower_text[:50]
        ) and len(cleaned_text) < 200:
            raise InvalidExplanationError("Received placeholder or rejection response.")

        required_headings = [
            "# Concept",
            "## Why It Matters",
            "## Intuition",
            "## Detailed Explanation",
            "## Example",
            "## Common Mistakes",
            "## Related Concepts",
            "## Key Takeaways",
        ]

        # Check for headings gracefully regardless of minor casing or whitespace differences
        for expected in required_headings:
            normalized = expected.lower().replace(" ", "")
            if normalized not in lower_text.replace(" ", ""):
                raise InvalidExplanationError(f"Missing required markdown heading: {expected}")

        # Extract title from the first heading if present, otherwise default
        title_match = re.search(r"^#\s+(.+)$", cleaned_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Explanation"

        statistics = self._calculate_statistics(cleaned_text, metadata.generation_time_ms)
        learning_metadata = self._build_metadata(metadata)

        source_chunk_ids = tuple(chunk.id for chunk in context.chunks.chunks)
        source_document_id = (
            context.chunks.chunks[0].document_id if context.chunks.chunks else "unknown_document"
        )

        return LearningContent(
            id=str(uuid.uuid4()),
            title=title,
            body=cleaned_text,
            content_type=ContentType.EXPLANATION,
            source_document_id=source_document_id,
            source_chunk_ids=source_chunk_ids,
            metadata=learning_metadata,
            statistics=statistics,
            created_at=datetime.now(UTC),
        )

    def _calculate_statistics(
        self, text: str, generation_time_ms: float
    ) -> LearningContentStatistics:
        char_count = len(text)
        word_count = len(text.split())
        estimated_tokens = int(word_count * 1.3)
        heading_count = len(re.findall(r"^#+\s+", text, re.MULTILINE))

        return LearningContentStatistics(
            character_count=char_count,
            word_count=word_count,
            estimated_tokens=estimated_tokens,
            processing_time_ms=generation_time_ms,
            confidence=0.9,
            heading_count=heading_count,
        )

    def _build_metadata(self, metadata: GenerationMetadata) -> LearningContentMetadata:
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

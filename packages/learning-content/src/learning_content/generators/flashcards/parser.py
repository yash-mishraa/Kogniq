import json
import uuid
from datetime import UTC, datetime

from learning_content.content import LearningContent
from learning_content.entities import Flashcard, FlashcardCollection, FlashcardDifficulty
from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    GenerationContext,
    GenerationMetadata,
)
from learning_content.generators.flashcards.exceptions import (
    InvalidFlashcardError,
    InvalidFlashcardJsonError,
)
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


class FlashcardsParser(AbstractContentParser):
    """
    Parses and validates the raw text response for the Flashcards Generator.
    """

    def parse(
        self,
        raw_text: str,
        context: GenerationContext,
        metadata: GenerationMetadata,
    ) -> LearningContent:
        cleaned_text = raw_text.strip()

        # Defensively strip Markdown fences if the provider ignored instructions
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        if not cleaned_text:
            raise InvalidFlashcardJsonError("Received empty response from the provider.")

        try:
            parsed_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise InvalidFlashcardJsonError(f"Provider returned malformed JSON: {e}") from e

        if not isinstance(parsed_json, list):
            raise InvalidFlashcardJsonError(
                f"Provider returned a JSON object instead of an array. Got: {type(parsed_json)}"
            )

        flashcards = []
        seen_questions = set()

        for index, item in enumerate(parsed_json):
            if not isinstance(item, dict):
                raise InvalidFlashcardJsonError(f"Item at index {index} is not an object.")

            question = item.get("question")
            answer = item.get("answer")
            difficulty_raw = item.get("difficulty", "medium")

            if not question or not isinstance(question, str) or not question.strip():
                raise InvalidFlashcardError(
                    f"Flashcard at index {index} is missing a valid 'question'."
                )

            if not answer or not isinstance(answer, str) or not answer.strip():
                raise InvalidFlashcardError(
                    f"Flashcard at index {index} is missing a valid 'answer'."
                )

            # Case-insensitive duplicate check
            q_lower = question.strip().lower()
            if q_lower in seen_questions:
                raise InvalidFlashcardError(f"Duplicate question detected: {question}")
            seen_questions.add(q_lower)

            try:
                difficulty = FlashcardDifficulty(difficulty_raw.lower())
            except ValueError as e:
                raise InvalidFlashcardError(f"Invalid difficulty value: {difficulty_raw}") from e

            try:
                card = Flashcard(
                    id=str(uuid.uuid4()),
                    question=question.strip(),
                    answer=answer.strip(),
                    difficulty=difficulty,
                    tags=(),
                    created_at=datetime.now(UTC),
                )
            except ValueError as e:
                # Catch domain validation errors (like identical Q/A)
                raise InvalidFlashcardError(str(e)) from e

            flashcards.append(card)

        collection = FlashcardCollection(flashcards=tuple(flashcards))

        statistics = self._calculate_statistics(collection, metadata.generation_time_ms)
        learning_metadata = self._build_metadata(metadata)

        source_chunk_ids = tuple(chunk.id for chunk in context.chunks.chunks)
        source_document_id = (
            context.chunks.chunks[0].document_id if context.chunks.chunks else "unknown_document"
        )

        return LearningContent(
            id=str(uuid.uuid4()),
            title=f"Flashcards ({collection.total_flashcards} cards)",
            body=collection.to_json(),
            content_type=ContentType.FLASHCARDS,
            source_document_id=source_document_id,
            source_chunk_ids=source_chunk_ids,
            metadata=learning_metadata,
            statistics=statistics,
            created_at=datetime.now(UTC),
        )

    def _calculate_statistics(
        self, collection: FlashcardCollection, generation_time_ms: float
    ) -> LearningContentStatistics:
        char_count = sum(len(c.question) + len(c.answer) for c in collection.flashcards)
        word_count = sum(
            len(c.question.split()) + len(c.answer.split()) for c in collection.flashcards
        )
        estimated_tokens = int(word_count * 1.3)

        return LearningContentStatistics(
            character_count=char_count,
            word_count=word_count,
            estimated_tokens=estimated_tokens,
            processing_time_ms=generation_time_ms,
            confidence=0.8,
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

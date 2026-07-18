import json
import uuid
from datetime import UTC, datetime

from learning_content.content import LearningContent
from learning_content.entities import (
    FlashcardDifficulty,
    QuizCollection,
    QuizOption,
    QuizQuestion,
)
from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    GenerationContext,
    GenerationMetadata,
)
from learning_content.generators.quiz.exceptions import (
    InvalidQuizJsonError,
    InvalidQuizQuestionError,
)
from learning_content.metadata import LearningContentMetadata
from learning_content.statistics import LearningContentStatistics


class QuizParser(AbstractContentParser):
    """
    Parses and validates the raw text response for the Quiz Generator.
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
            raise InvalidQuizJsonError("Received empty response from the provider.")

        try:
            parsed_json = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise InvalidQuizJsonError(f"Provider returned malformed JSON: {e}") from e

        if not isinstance(parsed_json, list):
            raise InvalidQuizJsonError(
                f"Provider returned a JSON object instead of an array. Got: {type(parsed_json)}"
            )

        questions = []
        seen_questions = set()
        seen_explanations = set()

        for index, item in enumerate(parsed_json):
            if not isinstance(item, dict):
                raise InvalidQuizJsonError(f"Item at index {index} is not an object.")

            question_text = item.get("question")
            options_raw = item.get("options")
            correct_answer = item.get("correct_answer")
            explanation = item.get("explanation")
            difficulty_raw = item.get("difficulty", "medium")

            if not question_text or not isinstance(question_text, str) or not question_text.strip():
                raise InvalidQuizQuestionError(
                    f"Question at index {index} is missing a valid 'question'."
                )

            if not isinstance(options_raw, list) or len(options_raw) != 4:
                raise InvalidQuizQuestionError(
                    f"Question at index {index} must have exactly four options."
                )

            if (
                not correct_answer
                or not isinstance(correct_answer, str)
                or not correct_answer.strip()
            ):
                raise InvalidQuizQuestionError(
                    f"Question at index {index} is missing a valid 'correct_answer'."
                )

            if not explanation or not isinstance(explanation, str) or not explanation.strip():
                raise InvalidQuizQuestionError(
                    f"Question at index {index} is missing a valid 'explanation'."
                )

            # Case-insensitive duplicate check for questions
            q_lower = question_text.strip().lower()
            if q_lower in seen_questions:
                raise InvalidQuizQuestionError(f"Duplicate question detected: {question_text}")
            seen_questions.add(q_lower)

            # Duplicate explanation check
            exp_lower = explanation.strip().lower()
            if exp_lower in seen_explanations:
                raise InvalidQuizQuestionError(f"Duplicate explanation detected: {explanation}")
            seen_explanations.add(exp_lower)

            try:
                difficulty = FlashcardDifficulty(difficulty_raw.lower())
            except ValueError as e:
                raise InvalidQuizQuestionError(f"Invalid difficulty value: {difficulty_raw}") from e

            labels = ["A", "B", "C", "D"]
            parsed_options = []
            for i, opt in enumerate(options_raw):
                if not isinstance(opt, str) or not opt.strip():
                    raise InvalidQuizQuestionError(
                        f"Option at index {i} in question {index} is empty or invalid."
                    )
                parsed_options.append(QuizOption(id=labels[i], text=opt.strip()))

            try:
                q = QuizQuestion(
                    id=str(uuid.uuid4()),
                    question=question_text.strip(),
                    options=tuple(parsed_options),
                    correct_answer=correct_answer.strip(),
                    explanation=explanation.strip(),
                    difficulty=difficulty,
                    tags=(),
                    created_at=datetime.now(UTC),
                )
            except ValueError as e:
                # Catch domain validation errors (duplicate options, no matching correct answer)
                raise InvalidQuizQuestionError(str(e)) from e

            questions.append(q)

        collection = QuizCollection(questions=tuple(questions))

        statistics = self._calculate_statistics(collection, metadata.generation_time_ms)
        learning_metadata = self._build_metadata(metadata)

        source_chunk_ids = tuple(chunk.id for chunk in context.chunks.chunks)
        source_document_id = (
            context.chunks.chunks[0].document_id if context.chunks.chunks else "unknown_document"
        )

        return LearningContent(
            id=str(uuid.uuid4()),
            title=f"Quiz ({collection.total_questions} questions)",
            body=collection.to_json(),
            content_type=ContentType.QUIZ,
            source_document_id=source_document_id,
            source_chunk_ids=source_chunk_ids,
            metadata=learning_metadata,
            statistics=statistics,
            created_at=datetime.now(UTC),
        )

    def _calculate_statistics(
        self, collection: QuizCollection, generation_time_ms: float
    ) -> LearningContentStatistics:
        char_count = sum(
            len(q.question) + len(q.explanation) + sum(len(o.text) for o in q.options)
            for q in collection.questions
        )
        word_count = sum(
            len(q.question.split())
            + len(q.explanation.split())
            + sum(len(o.text.split()) for o in q.options)
            for q in collection.questions
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

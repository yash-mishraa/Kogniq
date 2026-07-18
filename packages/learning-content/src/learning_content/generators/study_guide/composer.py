import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from learning_content.content import LearningContent
from learning_content.entities import StudyGuide, StudyGuideSection
from learning_content.generators.study_guide.exceptions import CompositionError


class StudyGuideComposer:
    """
    Assembles independent LearningContent artifacts into a unified StudyGuide.
    Contains no LLM invocation or prompting logic.
    """

    def compose(self, title: str, artifacts: Sequence[LearningContent]) -> StudyGuide:
        """
        Compose multiple artifacts into a StudyGuide.

        Args:
            title: The title for the composed guide.
            artifacts: A sequence of generated LearningContent artifacts.
                       (Expected: Summary, Notes, Explanation, Flashcards, Quiz).

        Returns:
            A new immutable StudyGuide.
        """
        if not artifacts:
            raise CompositionError(
                "Cannot compose a study guide from an empty sequence of artifacts."
            )

        sections = []
        for i, artifact in enumerate(artifacts):
            sections.append(
                StudyGuideSection(
                    id=str(uuid.uuid4()),
                    title=artifact.title,
                    content=artifact,
                    order=i,
                )
            )

        return StudyGuide(
            id=str(uuid.uuid4()),
            title=title,
            sections=tuple(sections),
            created_at=datetime.now(UTC),
        )

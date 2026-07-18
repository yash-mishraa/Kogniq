import json

from learning_content.entities import StudyGuide
from learning_content.enums import ContentType


class StudyGuideRenderer:
    """
    Renders a StudyGuide model into formatted representations.
    Isolates output formatting from domain modeling.
    """

    def to_markdown(self, guide: StudyGuide) -> str:
        """
        Renders the StudyGuide deterministically into Markdown.
        Ensures a specific order: Summary -> Notes -> Explanation -> Flashcards -> Quiz.
        """
        # Group sections by their artifact's content type
        sections_by_type = {}
        for section in guide.sections:
            sections_by_type[section.content.content_type] = section

        # Define the deterministic rendering order
        rendering_order = [
            ContentType.SUMMARY,
            ContentType.NOTES,
            ContentType.EXPLANATION,
            ContentType.FLASHCARDS,
            ContentType.QUIZ,
        ]

        parts = [f"# {guide.title}"]

        for content_type in rendering_order:
            if content_type in sections_by_type:
                section = sections_by_type[content_type]
                parts.append("---")
                # Use a specific title based on type to ensure consistency
                type_name = content_type.name.title()
                parts.append(f"# {type_name}")

                if content_type in (
                    ContentType.SUMMARY,
                    ContentType.NOTES,
                    ContentType.EXPLANATION,
                ):
                    parts.append(section.content.body)
                elif content_type == ContentType.FLASHCARDS:
                    parts.append(self._render_flashcards(section.content.body))
                elif content_type == ContentType.QUIZ:
                    parts.append(self._render_quiz(section.content.body))

        return "\n\n".join(parts)

    def _render_flashcards(self, json_body: str) -> str:
        try:
            cards = json.loads(json_body)
            lines = []
            for card in cards:
                lines.append(f"**Question:**\n{card.get('question')}\n")
                lines.append(f"**Answer:**\n{card.get('answer')}\n")
            return "\n".join(lines).strip()
        except (json.JSONDecodeError, AttributeError):
            return json_body

    def _render_quiz(self, json_body: str) -> str:
        try:
            questions = json.loads(json_body)
            lines = []
            for i, q in enumerate(questions, 1):
                lines.append(f"**Question {i}:**\n{q.get('question')}\n")
                lines.extend(
                    f"{opt.get('id', '-')}. {opt.get('text', '')}"
                    for opt in q.get("options", [])
                )
                lines.append(f"\n**Correct Answer:**\n{q.get('correct_answer')}\n")
                lines.append(f"**Explanation:**\n{q.get('explanation')}\n")
            return "\n".join(lines).strip()
        except (json.JSONDecodeError, AttributeError):
            return json_body

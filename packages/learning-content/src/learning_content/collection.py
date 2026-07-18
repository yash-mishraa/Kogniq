from dataclasses import dataclass

from learning_content.content import LearningContent


@dataclass(frozen=True, kw_only=True)
class LearningContentCollection:
    """Immutable collection of generated learning content."""

    contents: tuple[LearningContent, ...]

    @property
    def total_items(self) -> int:
        return len(self.contents)

    @property
    def total_words(self) -> int:
        return sum(content.statistics.word_count for content in self.contents)

    @property
    def total_characters(self) -> int:
        return sum(content.statistics.character_count for content in self.contents)

    @property
    def total_estimated_tokens(self) -> int:
        return sum(content.statistics.estimated_tokens for content in self.contents)

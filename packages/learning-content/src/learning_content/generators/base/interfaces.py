from abc import ABC, abstractmethod

from learning_content.content import LearningContent
from learning_content.generators.base.models import GenerationContext, GenerationMetadata


class AbstractPromptBuilder(ABC):
    """Generic interface for building prompts."""

    @abstractmethod
    def build(self, context: GenerationContext) -> str:
        """
        Constructs a deterministic prompt.
        """
        ...


class AbstractContentParser(ABC):
    """Generic interface for parsing provider responses."""

    @abstractmethod
    def parse(
        self, raw_text: str, context: GenerationContext, metadata: GenerationMetadata
    ) -> LearningContent:
        """
        Parses a raw LLM response into a structured LearningContent artifact.
        """
        ...

from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    AbstractPromptBuilder,
    BaseLearningGenerator,
)
from learning_content.generators.notes.parser import NotesParser
from learning_content.generators.notes.prompt_builder import PROMPT_VERSION, NotesPromptBuilder
from learning_content.providers.base import AbstractTextGenerationProvider
from learning_content.providers.provider_info import GeneratorInfo


class NotesGenerator(BaseLearningGenerator):
    """
    Concrete implementation for generating educational structured notes.
    Delegates all orchestration to BaseLearningGenerator.
    """

    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        """Initialize the notes generator."""
        super().__init__(provider)
        self._prompt_builder = NotesPromptBuilder()
        self._parser = NotesParser()

    @property
    def prompt_builder(self) -> AbstractPromptBuilder:
        return self._prompt_builder

    @property
    def parser(self) -> AbstractContentParser:
        return self._parser

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def info(self) -> GeneratorInfo:
        """Get metadata about this generator."""
        return GeneratorInfo(
            generator_id="notes-generator-v1",
            generator_name="Notes Generator",
            generator_version="1.0",
            provider_name=self._provider.info.provider_id,
            supported_content_types=(ContentType.NOTES,),
            maximum_chunks=150,
            maximum_tokens=8000,
            supports_batch_generation=False,
        )

from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    AbstractPromptBuilder,
    BaseLearningGenerator,
)
from learning_content.generators.summary.parser import SummaryParser
from learning_content.generators.summary.prompt_builder import SummaryPromptBuilder
from learning_content.providers.base import AbstractTextGenerationProvider
from learning_content.providers.provider_info import GeneratorInfo


class SummaryGenerator(BaseLearningGenerator):
    """
    Concrete implementation for generating educational summaries.
    Delegates all orchestration to BaseLearningGenerator.
    """

    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        """Initialize the summary generator."""
        super().__init__(provider)
        self._prompt_builder = SummaryPromptBuilder()
        self._parser = SummaryParser()

    @property
    def prompt_builder(self) -> AbstractPromptBuilder:
        return self._prompt_builder

    @property
    def parser(self) -> AbstractContentParser:
        return self._parser

    @property
    def prompt_version(self) -> str:
        return "summary-v1"

    def info(self) -> GeneratorInfo:
        """Get metadata about this generator."""
        return GeneratorInfo(
            generator_id="summary-generator-v1",
            generator_name="Summary Generator",
            generator_version="1.0",
            provider_name=self._provider.info.provider_id,
            supported_content_types=(ContentType.SUMMARY,),
            maximum_chunks=100,
            maximum_tokens=4000,
            supports_batch_generation=False,
        )

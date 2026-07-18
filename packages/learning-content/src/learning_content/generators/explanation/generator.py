from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    AbstractPromptBuilder,
    BaseLearningGenerator,
)
from learning_content.generators.explanation.parser import ExplanationParser
from learning_content.generators.explanation.prompt_builder import (
    PROMPT_VERSION,
    ExplanationPromptBuilder,
)
from learning_content.providers.base import AbstractTextGenerationProvider
from learning_content.providers.provider_info import GeneratorInfo


class ExplanationGenerator(BaseLearningGenerator):
    """
    Concrete implementation for generating in-depth educational explanations.
    Delegates all orchestration to BaseLearningGenerator.
    """

    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        super().__init__(provider)
        self._prompt_builder = ExplanationPromptBuilder()
        self._parser = ExplanationParser()

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
        return GeneratorInfo(
            generator_id="explanation-generator-v1",
            generator_name="Explanation Generator",
            generator_version="1.0",
            provider_name=self._provider.info.provider_id,
            supported_content_types=(ContentType.EXPLANATION,),
            maximum_chunks=150,
            maximum_tokens=8000,
            supports_batch_generation=False,
        )

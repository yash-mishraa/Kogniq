from learning_content.enums import ContentType
from learning_content.generators.base import (
    AbstractContentParser,
    AbstractPromptBuilder,
    BaseLearningGenerator,
)
from learning_content.generators.study_guide.parser import StudyGuideParser
from learning_content.generators.study_guide.prompt_builder import (
    PROMPT_VERSION,
    StudyGuidePromptBuilder,
)
from learning_content.providers.base import AbstractTextGenerationProvider
from learning_content.providers.provider_info import GeneratorInfo


class StudyGuideGenerator(BaseLearningGenerator):
    """
    Concrete implementation for generating a Study Guide.
    Delegates all orchestration to BaseLearningGenerator.
    """

    def __init__(self, provider: AbstractTextGenerationProvider) -> None:
        super().__init__(provider)
        self._prompt_builder = StudyGuidePromptBuilder()
        self._parser = StudyGuideParser()

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
            generator_id="study-guide-generator-v2",
            generator_name="Study Guide Generator",
            generator_version="2.0",
            provider_name=self._provider.info.provider_id,
            supported_content_types=(ContentType.STUDY_GUIDE,),
            maximum_chunks=150,
            maximum_tokens=16000,
            supports_batch_generation=False,
        )

from dataclasses import dataclass

from learning_content.enums import ContentType
from learning_content.exceptions import GenerationConfigurationError


@dataclass(frozen=True, kw_only=True)
class GeneratorInfo:
    """Immutable information about a learning content generator."""

    generator_id: str
    generator_name: str
    generator_version: str
    provider_name: str
    supported_content_types: tuple[ContentType, ...]
    maximum_chunks: int
    maximum_tokens: int
    supports_batch_generation: bool

    def __post_init__(self) -> None:
        if self.maximum_chunks <= 0:
            raise GenerationConfigurationError("Maximum chunks must be positive")
        if self.maximum_tokens <= 0:
            raise GenerationConfigurationError("Maximum tokens must be positive")
        if not self.supported_content_types:
            raise GenerationConfigurationError("Must support at least one content type")

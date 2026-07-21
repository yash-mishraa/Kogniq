from dataclasses import dataclass

from knowledge.extractors.exceptions import ExtractorConfigurationError


@dataclass(frozen=True, kw_only=True)
class KnowledgeExtractorInfo:
    """Immutable metadata describing a Knowledge Extractor's capabilities."""

    extractor_id: str
    extractor_name: str
    version: str
    provider: str
    supports_batch_processing: bool
    supports_streaming: bool
    maximum_chunks_per_request: int
    maximum_tokens: int
    supports_relationship_extraction: bool
    supports_alias_extraction: bool

    def __post_init__(self) -> None:
        if self.maximum_chunks_per_request <= 0:
            raise ExtractorConfigurationError(
                f"maximum_chunks_per_request must be > 0, got {self.maximum_chunks_per_request}"
            )
        if self.maximum_tokens <= 0:
            raise ExtractorConfigurationError(
                f"maximum_tokens must be > 0, got {self.maximum_tokens}"
            )

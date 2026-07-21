from dataclasses import dataclass

from .exceptions import ProviderConfigurationError


@dataclass(frozen=True, slots=True)
class ProviderInfo:
    """Immutable metadata describing the capabilities of an embedding provider."""

    provider_id: str
    provider_name: str
    model_name: str
    model_version: str
    embedding_version: str
    dimensions: int
    supports_batch_generation: bool
    supports_async_generation: bool
    maximum_batch_size: int
    maximum_tokens: int
    normalized_output: bool

    def __post_init__(self) -> None:
        if self.dimensions <= 0:
            raise ProviderConfigurationError(f"Dimensions must be > 0, got {self.dimensions}")
        if self.maximum_batch_size <= 0:
            raise ProviderConfigurationError(
                f"Maximum batch size must be > 0, got {self.maximum_batch_size}"
            )
        if self.maximum_tokens <= 0:
            raise ProviderConfigurationError(
                f"Maximum tokens must be > 0, got {self.maximum_tokens}"
            )

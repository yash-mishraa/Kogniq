from dataclasses import dataclass

from .exceptions import StoreConfigurationError


@dataclass(frozen=True, slots=True)
class StoreInfo:
    store_id: str
    store_name: str
    implementation_version: str
    supported_distance_metrics: tuple[str, ...]
    supports_metadata_filtering: bool
    supports_batch_insert: bool
    supports_batch_delete: bool
    maximum_batch_size: int

    def __post_init__(self) -> None:
        if self.maximum_batch_size <= 0:
            raise StoreConfigurationError(
                f"Maximum batch size must be > 0, got {self.maximum_batch_size}"
            )

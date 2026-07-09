from dataclasses import dataclass
from enum import Enum, auto

from .exceptions import InvalidChecksumError, validate_not_empty


class ChecksumAlgorithm(Enum):
    """Supported hashing algorithms."""

    SHA256 = auto()
    MD5 = auto()
    SHA1 = auto()


@dataclass(frozen=True, kw_only=True)
class Checksum:
    """Immutable representation of a content checksum."""

    algorithm: ChecksumAlgorithm
    value: str

    def __post_init__(self) -> None:
        validate_not_empty(self.value, "checksum value", InvalidChecksumError)

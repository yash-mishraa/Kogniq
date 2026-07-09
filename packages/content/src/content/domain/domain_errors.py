class ContentDomainError(Exception):
    """Base exception for all content domain errors."""


class InvalidResourceError(ContentDomainError):
    """Raised when a resource entity fails validation (e.g. empty title)."""


class InvalidSectionError(ContentDomainError):
    """Raised when a resource section is invalid (e.g. negative order)."""


class InvalidChunkError(ContentDomainError):
    """Raised when a resource chunk is invalid (e.g. empty text)."""


class InvalidStatisticsError(ContentDomainError):
    """Raised when statistics contain negative values."""


class InvalidMetadataError(ContentDomainError):
    """Raised when metadata is internally inconsistent."""

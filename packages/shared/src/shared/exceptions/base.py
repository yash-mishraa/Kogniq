"""Provider- and domain-neutral exceptions."""


class KogniqError(Exception):
    """Base class for expected errors raised by reusable Kogniq code."""


class InvalidConfigurationError(KogniqError, ValueError):
    """Raised when configuration cannot be validated safely."""


class UnsupportedOperationError(KogniqError):
    """Raised when a requested capability is intentionally unsupported."""

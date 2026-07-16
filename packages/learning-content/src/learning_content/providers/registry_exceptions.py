class GeneratorRegistrationError(Exception):
    """Raised when a generator fails to register (e.g., duplicate ID)."""

class GeneratorNotFoundError(Exception):
    """Raised when requesting a generator that is not registered."""

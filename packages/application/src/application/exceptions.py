class ApplicationError(Exception):
    """Base class for all application layer exceptions."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

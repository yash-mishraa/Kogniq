from enum import Enum, auto


class LifecycleState(Enum):
    """The current processing state of a learning resource."""

    CREATED = auto()
    REGISTERED = auto()
    VALIDATED = auto()
    PROCESSING = auto()
    PROCESSED = auto()
    FAILED = auto()
    ARCHIVED = auto()

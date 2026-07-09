from enum import Enum, auto


class ContentSource(Enum):
    """Origin of a learning resource."""

    LOCAL = auto()
    REMOTE_URL = auto()
    UPLOAD = auto()
    YOUTUBE = auto()
    GOOGLE_DRIVE = auto()
    GITHUB = auto()
    S3 = auto()
    MINIO = auto()
    GENERATED = auto()
    UNKNOWN = auto()

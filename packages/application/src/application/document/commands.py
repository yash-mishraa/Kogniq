from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessDocumentCommand:
    user_id: str
    filename: str
    content_type: str
    size_bytes: int
    content: bytes

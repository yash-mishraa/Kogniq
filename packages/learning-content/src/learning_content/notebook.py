import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NotebookEntry:
    """An immutable notebook entry."""

    id: str
    user_id: str
    document_id: str
    title: str
    thoughts_json: str
    created_at: datetime.datetime
    idempotency_key: Optional[str] = None

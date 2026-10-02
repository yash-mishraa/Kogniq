import dataclasses
from datetime import datetime

@dataclasses.dataclass(frozen=True, kw_only=True)
class DocumentSemantics:
    id: str
    document_id: str
    semantic_version: str
    status: str
    is_active: bool
    semantics_json: str
    created_at: datetime
    completed_at: datetime | None = None

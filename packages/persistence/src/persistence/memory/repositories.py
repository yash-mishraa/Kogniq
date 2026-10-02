from collections.abc import Sequence
from datetime import datetime
from content.normalized.semantics import DocumentSemantics
from persistence.models import SaveResult
from persistence.repositories.base import AbstractSemanticRepository

class MemorySemanticRepository(AbstractSemanticRepository):
    def __init__(self) -> None:
        self._store: dict[str, DocumentSemantics] = {}

    async def save(self, semantics: DocumentSemantics) -> SaveResult:
        self._store[semantics.id] = semantics
        return SaveResult(id=semantics.id, is_new=True)

    async def get_active(self, document_id: str) -> DocumentSemantics | None:
        for s in self._store.values():
            if s.document_id == document_id and s.is_active:
                return s
        return None

    async def list_by_document(self, document_id: str) -> Sequence[DocumentSemantics]:
        return sorted([s for s in self._store.values() if s.document_id == document_id], key=lambda x: x.created_at, reverse=True)

    async def activate_version(self, document_id: str, semantic_id: str) -> bool:
        target = self._store.get(semantic_id)
        if not target:
            return False
            
        current_active = await self.get_active(document_id)
        current_v = 0
        if current_active:
            try:
                current_v = int(current_active.semantic_version)
            except ValueError:
                pass
        try:
            new_v = int(target.semantic_version)
        except ValueError:
            new_v = 0

        if new_v >= current_v:
            for k, s in self._store.items():
                if s.document_id == document_id:
                    import dataclasses
                    if s.id == semantic_id:
                        self._store[k] = dataclasses.replace(s, is_active=True, status='completed')
                    else:
                        self._store[k] = dataclasses.replace(s, is_active=False)
            return True
        return False

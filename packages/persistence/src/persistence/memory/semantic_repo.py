from persistence.repositories.base import AbstractSemanticRepository
from content.normalized.semantics import DocumentSemantics
import copy

class MemorySemanticRepository(AbstractSemanticRepository):
    def __init__(self):
        self._data = {}
        
    async def save(self, semantics: DocumentSemantics) -> None:
        self._data[semantics.document_id] = copy.deepcopy(semantics)
        
    async def get_active(self, document_id: str) -> DocumentSemantics | None:
        return self._data.get(document_id)
        
    async def get_version(self, document_id: str, version: int) -> DocumentSemantics | None:
        if document_id in self._data and self._data[document_id].semantic_version == version:
            return self._data[document_id]
        return None
        
    async def list_versions(self, document_id: str) -> list[int]:
        if document_id in self._data:
            return [self._data[document_id].semantic_version]
        return []
        
    async def delete_all(self, document_id: str) -> bool:
        if document_id in self._data:
            del self._data[document_id]
            return True
        return False

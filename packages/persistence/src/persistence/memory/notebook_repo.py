from typing import Sequence
from learning_content.notebook import NotebookEntry
from persistence.repositories.notebook import AbstractNotebookRepository


class MemoryNotebookRepository(AbstractNotebookRepository):
    def __init__(self) -> None:
        self._entries: dict[str, NotebookEntry] = {}

    async def create(self, entry: NotebookEntry) -> None:
        if entry.id in self._entries:
            return  # Or raise depending on exactly how sqlite behaves, but SQLite has ON CONFLICT or IntegrityError.
        self._entries[entry.id] = entry

    async def list_by_document(self, document_id: str) -> Sequence[NotebookEntry]:
        return [
            entry
            for entry in self._entries.values()
            if entry.document_id == document_id
        ]

import abc
from typing import Sequence
from learning_content.notebook import NotebookEntry

class AbstractNotebookRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, entry: NotebookEntry) -> None:
        pass

    @abc.abstractmethod
    async def list_by_document(self, document_id: str) -> Sequence[NotebookEntry]:
        pass

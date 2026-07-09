from abc import ABC, abstractmethod

from ..entities import Concept, Subject, Topic
from ..value_objects import ConceptId, SubjectId, TopicId


class SubjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, subject_id: SubjectId) -> Subject | None:
        pass

    @abstractmethod
    async def save(self, subject: Subject) -> None:
        pass


class TopicRepository(ABC):
    @abstractmethod
    async def get_by_id(self, topic_id: TopicId) -> Topic | None:
        pass

    @abstractmethod
    async def get_by_subject(self, subject_id: SubjectId) -> list[Topic]:
        pass

    @abstractmethod
    async def save(self, topic: Topic) -> None:
        pass


class ConceptRepository(ABC):
    @abstractmethod
    async def get_by_id(self, concept_id: ConceptId) -> Concept | None:
        pass

    @abstractmethod
    async def get_by_topic(self, topic_id: TopicId) -> list[Concept]:
        pass

    @abstractmethod
    async def get_all_in_graph(self, starting_concept_ids: list[ConceptId]) -> list[Concept]:
        """Useful for prerequisite validation and graph traversal."""

    @abstractmethod
    async def save(self, concept: Concept) -> None:
        pass

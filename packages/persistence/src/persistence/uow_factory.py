import abc

from persistence.uow import AbstractUnitOfWork


class AbstractUnitOfWorkFactory(abc.ABC):
    @abc.abstractmethod
    def create(self) -> AbstractUnitOfWork:
        pass

from abc import ABC, abstractmethod

from retrieval.models import RetrievalQuery, RetrievalResult


class AbstractRetriever(ABC):
    """
    The canonical contract for all semantic retrieval operations.
    Consumers depend entirely on this interface, avoiding direct interaction
    with embedding providers or vector stores.
    """

    @abstractmethod
    def retrieve(self, query: RetrievalQuery) -> tuple[RetrievalResult, ...]:
        """
        Execute a retrieval query and return results.

        Args:
            query: The domain query to execute.

        Returns:
            A tuple of RetrievalResult objects matching the query.
        """
        ...

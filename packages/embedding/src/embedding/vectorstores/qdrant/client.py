import logging
from typing import Any

from qdrant_client import QdrantClient, models

from .exceptions import QdrantConnectionError, QdrantOperationError

logger = logging.getLogger(__name__)


class QdrantClientManager:
    """
    Manages the lifecycle, connection, and collection initialization for Qdrant.
    """

    def __init__(self, location: str | None = None, url: str | None = None) -> None:
        self.location = location
        self.url = url
        self._client: QdrantClient | None = None

    def connect(self) -> QdrantClient:
        """Establishes or returns an active connection to Qdrant."""
        if self._client is None:
            try:
                self._client = QdrantClient(location=self.location, url=self.url)
                logger.info(f"Connected to Qdrant at location={self.location}, url={self.url}")
            except Exception as e:
                raise QdrantConnectionError(
                    f"Failed to connect to Qdrant at location={self.location}, url={self.url}: {e}"
                ) from e
        return self._client

    def ensure_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: models.Distance = models.Distance.COSINE,
    ) -> None:
        """
        Idempotently ensures that the collection exists with the specified dimension size.
        Never recreate or delete an existing collection automatically.
        """
        client = self.connect()
        try:
            if not client.collection_exists(collection_name=collection_name):
                logger.info(
                    f"Creating Qdrant collection '{collection_name}' with size {vector_size}"
                )
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=distance,
                    ),
                )
        except Exception as e:
            raise QdrantOperationError(
                f"Failed to ensure collection '{collection_name}': {e}"
            ) from e

    def health_check(self) -> dict[str, Any]:
        """
        Performs a lightweight health check to verify connectivity.
        Useful for backend health endpoints.
        """
        if self._client is None:
            return {"status": "uninitialized"}
        try:
            # We can check collections as a ping
            collections = self._client.get_collections()
            return {"status": "healthy", "collections": len(collections.collections)}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def close(self) -> None:
        """Gracefully shuts down the connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("Closed Qdrant connection")

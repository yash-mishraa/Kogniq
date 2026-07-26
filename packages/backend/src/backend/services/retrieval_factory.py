from typing import Any

from backend.core.settings import BackendConfig
from embedding.providers.local.provider import LocalEmbeddingProvider
from embedding.vectorstores.chroma.store import ChromaVectorStore
from embedding.vectorstores.qdrant.client import QdrantClientManager
from embedding.vectorstores.qdrant.store import QdrantVectorStore
from retrieval.config import RetrieverConfig
from retrieval.interfaces import AbstractRetriever
from retrieval.semantic_retriever import SemanticRetriever


class RetrievalFactory:
    """
    Bootstraps the retrieval domain implementations.
    Returns interfaces, ensuring backend logic never touches concrete classes.
    """

    def __init__(self, settings: BackendConfig) -> None:
        self.settings = settings
        self._retriever: AbstractRetriever | None = None
        from embedding.providers.interfaces import AbstractEmbeddingProvider
        from embedding.vectorstores.interfaces import AbstractVectorStore

        self._provider: AbstractEmbeddingProvider | None = None
        self._vector_store: AbstractVectorStore | None = None

    def get_provider(self) -> "Any | None":
        self._initialize()
        return self._provider

    def get_vector_store(self) -> "Any | None":
        self._initialize()
        return self._vector_store

    def get_retriever(self) -> AbstractRetriever:
        """Constructs and returns the canonical SemanticRetriever."""
        self._initialize()
        assert self._retriever is not None
        return self._retriever

    def _initialize(self) -> None:
        if self._retriever is None:
            # We initialize a persistent ChromaDB store using the configured path.
            # LocalEmbeddingProvider uses sentence-transformers inside.
            provider = LocalEmbeddingProvider()

            from embedding.vectorstores.interfaces import AbstractVectorStore

            vector_store: AbstractVectorStore
            if self.settings.vector_store_provider == "qdrant":
                manager = QdrantClientManager(url=self.settings.qdrant_url)
                vector_store = QdrantVectorStore(
                    manager=manager,
                    collection_name=self.settings.qdrant_collection,
                )
            elif self.settings.vector_store_provider == "chroma":
                # Using persistence directory from settings to avoid ephemeral loss of embeddings
                vector_store = ChromaVectorStore(
                    collection_name="kogniq",
                    persist_directory=self.settings.chroma_db_path,
                )
            else:
                # Fallback for memory testing without persistence
                vector_store = ChromaVectorStore(collection_name="kogniq")

            self._provider = provider
            self._vector_store = vector_store

            config = RetrieverConfig(similarity_threshold=self.settings.similarity_threshold)

            self._retriever = SemanticRetriever(
                embedding_provider=provider,
                vector_store=vector_store,
                config=config,
            )

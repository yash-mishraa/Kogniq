from .interfaces import AbstractVectorStore
from .registry_exceptions import (
    DuplicateStoreError,
    InvalidStoreDefinitionError,
    StoreNotFoundError,
)


class VectorStoreRegistry:
    def __init__(self) -> None:
        self._stores: dict[str, AbstractVectorStore] = {}

    def register(self, store: AbstractVectorStore) -> None:
        if not isinstance(store, AbstractVectorStore):
            raise InvalidStoreDefinitionError("Store must implement AbstractVectorStore.")

        store_id = store.info.store_id
        if store_id in self._stores:
            raise DuplicateStoreError(f"Vector Store with ID '{store_id}' is already registered.")

        self._stores[store_id] = store

    def store(self, store_id: str) -> AbstractVectorStore:
        if store_id not in self._stores:
            raise StoreNotFoundError(f"Vector Store with ID '{store_id}' not found.")
        return self._stores[store_id]

    def available_stores(self) -> tuple[AbstractVectorStore, ...]:
        return tuple(self._stores.values())

    def store_count(self) -> int:
        return len(self._stores)

    def has_store(self, store_id: str) -> bool:
        return store_id in self._stores

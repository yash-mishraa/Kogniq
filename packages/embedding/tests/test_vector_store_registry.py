import pytest
from embedding.vectorstores import (
    DuplicateStoreError,
    InvalidStoreDefinitionError,
    StoreNotFoundError,
    VectorStoreRegistry,
)

from .test_vector_store_interface import FakeVectorStore


def test_registry_registration_and_lookup() -> None:
    registry = VectorStoreRegistry()
    store = FakeVectorStore()
    
    registry.register(store)
    
    assert registry.has_store("fake_store")
    assert registry.store_count() == 1
    
    retrieved = registry.store("fake_store")
    assert retrieved is store

def test_registry_duplicate_registration() -> None:
    registry = VectorStoreRegistry()
    store = FakeVectorStore()
    registry.register(store)
    
    with pytest.raises(DuplicateStoreError):
        registry.register(store)

def test_registry_store_not_found() -> None:
    registry = VectorStoreRegistry()
    with pytest.raises(StoreNotFoundError):
        registry.store("missing_store")

def test_registry_invalid_store_definition() -> None:
    registry = VectorStoreRegistry()
    with pytest.raises(InvalidStoreDefinitionError):
        registry.register("not_a_store")  # type: ignore

def test_registry_available_stores_is_immutable() -> None:
    registry = VectorStoreRegistry()
    registry.register(FakeVectorStore())
    
    stores = registry.available_stores()
    assert isinstance(stores, tuple)
    assert len(stores) == 1

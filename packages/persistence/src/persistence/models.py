from dataclasses import dataclass


@dataclass(frozen=True)
class SaveResult:
    """Result of a save operation."""

    id: str
    is_new: bool
    version: int | None = None


@dataclass(frozen=True)
class DeleteResult:
    """Result of a delete operation."""

    id: str
    was_deleted: bool


@dataclass(frozen=True)
class RepositoryStatistics:
    """Statistics about a repository's contents."""

    total_items: int
    storage_size_bytes: int | None = None

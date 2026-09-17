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


from datetime import datetime


@dataclass(frozen=True)
class DocumentJob:
    id: str
    user_id: str
    filename: str
    status: str
    created_at: datetime
    error_message: str | None = None

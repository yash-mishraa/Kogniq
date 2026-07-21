from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class Permission:
    permission_id: str
    name: str
    description: str


@dataclass(frozen=True)
class Role:
    role_id: str
    name: str
    description: str
    permissions: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class UserRole:
    user_id: str
    role_id: str
    assigned_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class AuthorizationResult:
    allowed: bool
    reason: str
    evaluated_permission: str | None = None
    evaluated_role: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

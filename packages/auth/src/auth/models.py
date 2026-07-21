from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class AuthProvider(StrEnum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"


@dataclass(frozen=True)
class User:
    user_id: str
    email: str
    display_name: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class Identity:
    identity_id: str
    user_id: str
    provider: AuthProvider
    provider_user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class Session:
    session_id: str
    user_id: str
    expires_at: datetime
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class UserProfile:
    user_id: str
    avatar_url: str | None = None
    timezone: str | None = None
    preferred_language: str | None = None


@dataclass(frozen=True)
class AuthenticationRequest:
    provider: AuthProvider
    payload: dict[str, Any]


@dataclass(frozen=True)
class AuthenticationResult:
    user: User
    identity: Identity
    provider: AuthProvider
    authenticated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    session: Session | None = None

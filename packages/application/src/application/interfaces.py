from typing import Any, Protocol


class IdentityProtocol(Protocol):
    provider: str
    provider_user_id: str


class SessionProtocol(Protocol):
    session_id: str


class AuthenticationResultProtocol(Protocol):
    identity: IdentityProtocol
    session: SessionProtocol | None


class UserProtocol(Protocol):
    user_id: str


class AuthenticationServiceProtocol(Protocol):
    async def get_current_user(self, session_id: str) -> UserProtocol | None: ...


class AuthorizationResultProtocol(Protocol):
    allowed: bool
    reason: str


class AuthorizationServiceProtocol(Protocol):
    async def require_permission(
        self, user_id: str, permission_id: str
    ) -> AuthorizationResultProtocol: ...


class DocumentServiceProtocol(Protocol):
    async def process_document(self, document_input: Any) -> Any: ...


class LearningServiceProtocol(Protocol):
    async def generate_artifact(self, request: Any) -> Any: ...


class RetrievalServiceProtocol(Protocol):
    async def search(self, request: Any) -> Any: ...


class JobServiceProtocol(Protocol):
    async def process_document_background(self, document_input: Any) -> Any: ...

    async def get_job_status(self, job_id: str) -> Any: ...

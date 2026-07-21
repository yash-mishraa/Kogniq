import abc

from auth.authorization import AuthorizationResult, Permission

# Reusable Permission Definitions
DOCUMENTS_READ = Permission("documents:read", "Read Documents", "Can read documents")
DOCUMENTS_WRITE = Permission("documents:write", "Write Documents", "Create or modify documents")
DOCUMENTS_DELETE = Permission("documents:delete", "Delete Documents", "Can delete documents")
LEARNING_GENERATE = Permission("learning:generate", "Generate Learning", "Generate learning")
RETRIEVAL_SEARCH = Permission("retrieval:search", "Search", "Can run semantic search")
JOBS_VIEW = Permission("jobs:view", "View Jobs", "Can view background jobs")
ADMIN_USERS = Permission("admin:users", "Admin Users", "Can manage users")

# Common roles
ROLE_ADMIN_ID = "ADMIN"
ROLE_USER_ID = "USER"
ROLE_GUEST_ID = "GUEST"


class ResourceOwner(abc.ABC):
    """Protocol for any domain entity that is owned by a user."""
    
    @property
    @abc.abstractmethod
    def owner_id(self) -> str | None:
        """Return the ID of the user who owns this resource, or None if unowned/public."""
        ...


class OwnershipPolicy:
    """Evaluates generic resource ownership rules."""
    
    @staticmethod
    def evaluate(
        user_id: str, resource_owner_id: str | None, is_admin: bool = False
    ) -> AuthorizationResult:
        if is_admin:
            return AuthorizationResult(
                allowed=True,
                reason="Admin override granted access to resource.",
            )
        
        if resource_owner_id is None:
            return AuthorizationResult(
                allowed=True,
                reason="Resource has no owner restriction.",
            )
            
        if user_id == resource_owner_id:
            return AuthorizationResult(
                allowed=True,
                reason="User is the owner of the resource.",
            )
            
        return AuthorizationResult(
            allowed=False,
            reason="User is not the owner of the resource.",
        )

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from persistence.factory import RepositoryFactory

from auth.authorization_interfaces import (
    AbstractAuthorizationProvider,
    AbstractPermissionRepository,
    AbstractRoleRepository,
)
from auth.authorization_memory import (
    MemoryAuthorizationProvider,
    MemoryPermissionRepository,
    MemoryRoleRepository,
)
from auth.interfaces import AbstractAuthenticationProvider, AbstractUserRepository
from auth.memory import MemoryAuthenticationProvider, MemoryUserRepository
from backend.core.settings import settings
from backend.services.auth_service import AuthenticationService
from backend.services.authorization_service import AuthorizationService
from backend.services.context_provider import LearningContextProvider
from backend.services.document_service import DocumentService
from backend.services.generator_factory import GeneratorFactory
from backend.services.job_service import JobService
from backend.services.learning_service import LearningService
from backend.services.retrieval_factory import RetrievalFactory
from backend.services.retrieval_service import RetrievalService
from backend.services.stubs import (
    PipelineService,
    StubPipelineService,
)
from jobs.interfaces import AbstractJobManager
from jobs.memory import MemoryJobManager


# --- Singletons for In-Memory Adapters ---
class _AuthSingletons:
    _user_repo: AbstractUserRepository | None = None
    _auth_provider: AbstractAuthenticationProvider | None = None

    @classmethod
    def get_user_repo(cls) -> AbstractUserRepository:
        if cls._user_repo is None:
            cls._user_repo = MemoryUserRepository()
        return cls._user_repo

    @classmethod
    def get_auth_provider(cls) -> AbstractAuthenticationProvider:
        if cls._auth_provider is None:
            cls._auth_provider = MemoryAuthenticationProvider(cls.get_user_repo())
        return cls._auth_provider


class _AuthorizationSingletons:
    _permission_repo: AbstractPermissionRepository | None = None
    _role_repo: AbstractRoleRepository | None = None
    _auth_provider: AbstractAuthorizationProvider | None = None

    @classmethod
    def get_permission_repo(cls) -> AbstractPermissionRepository:
        if cls._permission_repo is None:
            cls._permission_repo = MemoryPermissionRepository()
        return cls._permission_repo

    @classmethod
    def get_role_repo(cls) -> AbstractRoleRepository:
        if cls._role_repo is None:
            cls._role_repo = MemoryRoleRepository()
        return cls._role_repo

    @classmethod
    def get_auth_provider(cls) -> AbstractAuthorizationProvider:
        if cls._auth_provider is None:
            cls._auth_provider = MemoryAuthorizationProvider(
                role_repo=cls.get_role_repo(),
                permission_repo=cls.get_permission_repo(),
            )
        return cls._auth_provider


class _JobManagerSingleton:
    _instance: AbstractJobManager | None = None

    @classmethod
    def get(cls) -> AbstractJobManager:
        if cls._instance is None:
            cls._instance = MemoryJobManager()
        return cls._instance


_repository_factory_instance: RepositoryFactory | None = None


def get_repository_factory() -> RepositoryFactory:
    global _repository_factory_instance
    # Use a singleton for now to share the in-memory state across requests.
    if _repository_factory_instance is None:
        _repository_factory_instance = RepositoryFactory()
    return _repository_factory_instance


_retrieval_factory_instance: RetrievalFactory | None = None


def get_retrieval_factory() -> RetrievalFactory:
    global _retrieval_factory_instance
    if _retrieval_factory_instance is None:
        _retrieval_factory_instance = RetrievalFactory(settings)
    return _retrieval_factory_instance


async def get_pipeline_service() -> PipelineService:
    return StubPipelineService()


async def get_learning_service() -> LearningService:
    repo_factory = get_repository_factory()
    context_provider = LearningContextProvider(repository_factory=repo_factory)
    factory = GeneratorFactory()

    return LearningService(
        context_provider=context_provider,
        generator_factory=factory,
        repository_factory=repo_factory,
    )


async def get_retrieval_service() -> RetrievalService:
    retrieval_factory = get_retrieval_factory()
    repo_factory = get_repository_factory()

    return RetrievalService(
        retriever=retrieval_factory.get_retriever(),
        chunk_repository=repo_factory.get_chunk_repository(),
    )


# -----------------
# Core Services
# -----------------


async def get_document_service() -> DocumentService:
    from backend.services.document_service import DocumentService
    from backend.services.pipeline_factory import PipelineFactory

    pipeline = PipelineFactory.create()
    repo_factory = get_repository_factory()
    return DocumentService(pipeline=pipeline, repository_factory=repo_factory)


def get_job_manager() -> AbstractJobManager:
    return _JobManagerSingleton.get()


async def get_job_service() -> JobService:
    job_manager = get_job_manager()
    document_service = await get_document_service()
    return JobService(job_manager=job_manager, document_service=document_service)


def get_user_repository() -> AbstractUserRepository:
    return _AuthSingletons.get_user_repo()


def get_auth_provider() -> AbstractAuthenticationProvider:
    return _AuthSingletons.get_auth_provider()


async def get_authentication_service() -> AuthenticationService:
    return AuthenticationService(
        auth_provider=get_auth_provider(),
        user_repository=get_user_repository(),
    )


def get_permission_repository() -> AbstractPermissionRepository:
    return _AuthorizationSingletons.get_permission_repo()


def get_role_repository() -> AbstractRoleRepository:
    return _AuthorizationSingletons.get_role_repo()


def get_authorization_provider() -> AbstractAuthorizationProvider:
    return _AuthorizationSingletons.get_auth_provider()


async def get_authorization_service() -> AuthorizationService:
    return AuthorizationService(
        auth_provider=get_authorization_provider(),
        role_repo=get_role_repository(),
        permission_repo=get_permission_repository(),
    )





# Typed dependencies for clean injection in route handlers
PipelineDependency = Annotated[PipelineService, Depends(get_pipeline_service)]
LearningDependency = Annotated[LearningService, Depends(get_learning_service)]
RetrievalDependency = Annotated[RetrievalService, Depends(get_retrieval_service)]
JobDependency = Annotated[JobService, Depends(get_job_service)]
AuthorizationDependency = Annotated[AuthorizationService, Depends(get_authorization_service)]

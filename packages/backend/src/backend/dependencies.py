from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends
from persistence.factory import (
    AbstractRepositoryFactory,
    MemoryRepositoryFactory,
    SQLiteRepositoryFactory,
)
from persistence.memory_uow import MemoryUnitOfWork
from persistence.sqlite.connection import SQLiteConnectionManager
from persistence.sqlite.schema import init_db
from persistence.uow import AbstractUnitOfWork, SQLiteUnitOfWork
from persistence.uow_factory import AbstractUnitOfWorkFactory

if TYPE_CHECKING:
    from knowledge.extractors.interfaces import AbstractKnowledgeExtractor

    from application.analytics.get_analytics import GetAnalyticsUseCase
    from application.knowledge.get_knowledge import GetKnowledgeUseCase
    from application.learning.explain_mistake import ExplainMistakeUseCase
    from application.learning.get_learning_materials import GetLearningMaterialsUseCase
    from application.learning.get_next_action import GetNextActionUseCase
    from backend.services.knowledge_service import KnowledgeService

from application.auth.register_user import RegisterUserUseCase
from application.document.process_document import ProcessDocumentUseCase
from application.jobs.get_job_status import GetJobStatusUseCase
from application.jobs.submit_job import SubmitJobUseCase
from application.learning.generate_learning import GenerateLearningUseCase
from application.retrieval.retrieve import RetrieveUseCase
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


_uow_factory_instance: AbstractUnitOfWorkFactory | None = None


class DefaultUnitOfWorkFactory(AbstractUnitOfWorkFactory):
    def __init__(self, provider: str, sqlite_path: str) -> None:
        self.provider = provider
        self.sqlite_path = sqlite_path
        self.factory: AbstractRepositoryFactory

        if self.provider == "sqlite":
            from pathlib import Path

            Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
            self.manager = SQLiteConnectionManager(self.sqlite_path)
            self.factory = SQLiteRepositoryFactory()
            # Initialize schema once
            with self.manager.get_connection() as conn:
                init_db(conn)
        else:
            self.factory = MemoryRepositoryFactory()

    def create(self) -> AbstractUnitOfWork:
        if self.provider == "sqlite":
            return SQLiteUnitOfWork(self.manager.get_connection(), self.factory)
        return MemoryUnitOfWork(self.factory)  # type: ignore


def get_uow_factory() -> AbstractUnitOfWorkFactory:
    global _uow_factory_instance
    if _uow_factory_instance is None:
        _uow_factory_instance = DefaultUnitOfWorkFactory(
            provider=settings.persistence_provider,
            sqlite_path=settings.sqlite_database_path,
        )
    return _uow_factory_instance


_retrieval_factory_instance: RetrievalFactory | None = None


def get_retrieval_factory() -> RetrievalFactory:
    global _retrieval_factory_instance
    if _retrieval_factory_instance is None:
        _retrieval_factory_instance = RetrievalFactory(settings)
    return _retrieval_factory_instance


_knowledge_extractor_instance: AbstractKnowledgeExtractor | None = None


def get_knowledge_extractor() -> AbstractKnowledgeExtractor:
    global _knowledge_extractor_instance
    if _knowledge_extractor_instance is None:
        from knowledge.extractors.fake import FakeKnowledgeExtractor

        _knowledge_extractor_instance = FakeKnowledgeExtractor()
    return _knowledge_extractor_instance


async def get_pipeline_service() -> PipelineService:
    return StubPipelineService()


_generator_factory_instance: GeneratorFactory | None = None


def get_generator_factory() -> GeneratorFactory:
    global _generator_factory_instance
    if _generator_factory_instance is None:
        from backend.services.generator_factory import GeneratorFactory
        from learning_content.providers.mock.provider import MockTextGenerationProvider

        provider = MockTextGenerationProvider()
        _generator_factory_instance = GeneratorFactory(provider)
    return _generator_factory_instance


async def get_learning_service() -> LearningService:
    uow_factory = get_uow_factory()
    context_provider = LearningContextProvider(uow_factory=uow_factory)
    factory = get_generator_factory()

    return LearningService(
        context_provider=context_provider,
        generator_factory=factory,
        uow_factory=uow_factory,
    )


async def get_retrieval_service() -> RetrievalService:
    retrieval_factory = get_retrieval_factory()
    uow_factory = get_uow_factory()

    return RetrievalService(
        retriever=retrieval_factory.get_retriever(),
        uow_factory=uow_factory,
    )


# -----------------
# Core Services
# -----------------


async def get_document_service() -> DocumentService:
    from backend.services.document_service import DocumentService
    from backend.services.pipeline_factory import PipelineFactory

    job_manager = get_job_manager()
    uow_factory = get_uow_factory()
    retrieval_factory = get_retrieval_factory()
    knowledge_extractor = get_knowledge_extractor()
    generator_factory = get_generator_factory()

    pipeline = PipelineFactory.create(
        job_manager=job_manager,
        uow_factory=uow_factory,
        embedding_provider=retrieval_factory.get_provider(),
        vector_store=retrieval_factory.get_vector_store(),
        knowledge_extractor=knowledge_extractor,
        generator_factory=generator_factory,
    )
    return DocumentService(pipeline=pipeline, uow_factory=uow_factory)


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


async def get_process_document_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    document_service: DocumentService = Depends(get_document_service),  # noqa: B008
) -> ProcessDocumentUseCase:
    return ProcessDocumentUseCase(
        auth_service=auth_service,  # type: ignore
        authorization_service=authorization_service,  # type: ignore
        document_service=document_service,
    )


async def get_knowledge_service() -> KnowledgeService:
    from backend.services.knowledge_service import KnowledgeService

    uow_factory = get_uow_factory()
    return KnowledgeService(uow_factory=uow_factory)


async def get_knowledge_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),  # noqa: B008
) -> GetKnowledgeUseCase:
    from application.knowledge.get_knowledge import GetKnowledgeUseCase

    return GetKnowledgeUseCase(
        auth_service=auth_service,
        authorization_service=authorization_service,
        knowledge_service=knowledge_service,
    )


async def get_generate_learning_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    learning_service: LearningService = Depends(get_learning_service),  # noqa: B008
) -> GenerateLearningUseCase:
    return GenerateLearningUseCase(
        auth_service=auth_service,  # type: ignore
        authorization_service=authorization_service,  # type: ignore
        learning_service=learning_service,
    )


async def get_get_learning_materials_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> GetLearningMaterialsUseCase:
    from application.learning.get_learning_materials import GetLearningMaterialsUseCase

    return GetLearningMaterialsUseCase(
        auth_service=auth_service,
        authorization_service=authorization_service,
        uow_factory=uow_factory,
    )


async def get_retrieve_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    retrieval_service: RetrievalService = Depends(get_retrieval_service),  # noqa: B008
) -> RetrieveUseCase:
    return RetrieveUseCase(
        auth_service=auth_service,  # type: ignore
        authorization_service=authorization_service,  # type: ignore
        retrieval_service=retrieval_service,
    )


async def get_submit_job_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    job_service: JobService = Depends(get_job_service),  # noqa: B008
) -> SubmitJobUseCase:
    return SubmitJobUseCase(
        auth_service=auth_service,  # type: ignore
        authorization_service=authorization_service,  # type: ignore
        job_service=job_service,
    )


async def get_job_status_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
    job_service: JobService = Depends(get_job_service),  # noqa: B008
) -> GetJobStatusUseCase:
    return GetJobStatusUseCase(
        auth_service=auth_service,  # type: ignore
        authorization_service=authorization_service,  # type: ignore
        job_service=job_service,
    )


async def get_register_user_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    authorization_service: AuthorizationService = Depends(get_authorization_service),  # noqa: B008
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        auth_service=auth_service,  # type: ignore
        authorization_service=authorization_service,  # type: ignore
    )


async def get_analytics_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> GetAnalyticsUseCase:
    from application.analytics.get_analytics import GetAnalyticsUseCase

    return GetAnalyticsUseCase(
        auth_service=auth_service,
        uow_factory=uow_factory,
    )

async def get_resource_progress_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> Any:
    from application.analytics.get_resource_progress import GetResourceProgressUseCase

    return GetResourceProgressUseCase(
        auth_service=auth_service,
        uow_factory=uow_factory,
    )

async def get_record_events_batch_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> Any:
    from application.analytics.record_events_batch import RecordEventsBatchUseCase

    return RecordEventsBatchUseCase(
        auth_service=auth_service,
        uow_factory=uow_factory,
    )


async def get_next_action_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> GetNextActionUseCase:
    from application.learning.get_next_action import GetNextActionUseCase

    return GetNextActionUseCase(
        auth_service=auth_service,
        uow_factory=uow_factory,
    )


async def get_explain_mistake_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> ExplainMistakeUseCase:
    from application.learning.explain_mistake import ExplainMistakeUseCase

    provider = get_generator_factory().get_provider()

    return ExplainMistakeUseCase(
        auth_service=auth_service,
        uow_factory=uow_factory,
        provider=provider,
    )


# Typed dependencies for clean injection in route handlers
PipelineDependency = Annotated[PipelineService, Depends(get_pipeline_service)]
LearningDependency = Annotated[LearningService, Depends(get_learning_service)]
RetrievalDependency = Annotated[RetrievalService, Depends(get_retrieval_service)]
JobDependency = Annotated[JobService, Depends(get_job_service)]
AuthorizationDependency = Annotated[AuthorizationService, Depends(get_authorization_service)]


async def get_get_learning_resource_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> Any:
    from application.resources.use_cases import GetLearningResourceUseCase
    return GetLearningResourceUseCase(auth_service=auth_service, uow_factory=uow_factory) # type: ignore

async def get_list_learning_resources_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> Any:
    from application.resources.use_cases import ListLearningResourcesUseCase
    return ListLearningResourcesUseCase(auth_service=auth_service, uow_factory=uow_factory) # type: ignore

async def get_resource_sections_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> Any:
    from application.resources.use_cases import GetResourceSectionsUseCase
    return GetResourceSectionsUseCase(auth_service=auth_service, uow_factory=uow_factory) # type: ignore

async def get_resource_chunks_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> Any:
    from application.resources.use_cases import GetResourceChunksUseCase
    return GetResourceChunksUseCase(auth_service=auth_service, uow_factory=uow_factory) # type: ignore

async def get_resource_statistics_use_case(
    auth_service: AuthenticationService = Depends(get_authentication_service),  # noqa: B008
    uow_factory: AbstractUnitOfWorkFactory = Depends(get_uow_factory),  # noqa: B008
) -> Any:
    from application.resources.use_cases import GetResourceStatisticsUseCase
    return GetResourceStatisticsUseCase(auth_service=auth_service, uow_factory=uow_factory) # type: ignore

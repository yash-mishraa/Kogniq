from application.exceptions import ApplicationError
from application.interfaces import (
    AuthenticationServiceProtocol,
    AuthorizationServiceProtocol,
    JobServiceProtocol,
)
from application.jobs.commands import GetJobStatusCommand
from application.jobs.responses import JobStatusResult

JOBS_VIEW = "jobs:view"


class GetJobStatusUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        authorization_service: AuthorizationServiceProtocol,
        job_service: JobServiceProtocol,
    ) -> None:
        self._auth_service = auth_service
        self._authorization_service = authorization_service
        self._job_service = job_service

    async def execute(self, command: GetJobStatusCommand) -> JobStatusResult:
        auth_result = await self._authorization_service.require_permission(
            command.user_id, JOBS_VIEW
        )
        if not auth_result.allowed:
            raise ApplicationError(f"Permission denied: {auth_result.reason}")

        result = await self._job_service.get_job_status(command.job_id)
        if not result:
            raise ApplicationError(f"Job not found: {command.job_id}")

        return JobStatusResult(
            job_id=getattr(result, "id", getattr(result, "job_id", "")),
            job_type=getattr(result, "job_type", ""),
            status=getattr(result, "status", ""),
            current_stage=result.progress.current_stage if hasattr(result, "progress") else None,
            completed_stages=result.progress.completed_stages if hasattr(result, "progress") else 0,
            total_stages=result.progress.total_stages if hasattr(result, "progress") else 0,
            stage_status=result.progress.status.value if hasattr(result, "progress") else "queued",
            message=getattr(result, "message", None)
            or (result.progress.message if hasattr(result, "progress") else None),
            error_message=getattr(result, "error_message", None),
        )

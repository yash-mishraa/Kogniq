from application.exceptions import ApplicationError
from application.interfaces import (
    AuthenticationServiceProtocol,
    AuthorizationServiceProtocol,
    JobServiceProtocol,
)
from application.jobs.commands import JobCommand
from application.jobs.responses import JobSubmissionResult

JOBS_VIEW = "jobs:view"  # Or create jobs:create


class SubmitJobUseCase:
    def __init__(
        self,
        auth_service: AuthenticationServiceProtocol,
        authorization_service: AuthorizationServiceProtocol,
        job_service: JobServiceProtocol,
    ) -> None:
        self._auth_service = auth_service
        self._authorization_service = authorization_service
        self._job_service = job_service

    async def execute(self, command: JobCommand) -> JobSubmissionResult:
        auth_result = await self._authorization_service.require_permission(
            command.user_id, JOBS_VIEW
        )
        if not auth_result.allowed:
            raise ApplicationError(f"Permission denied: {auth_result.reason}")

        # We currently only support processing documents in background
        if command.job_type == "PROCESS_DOCUMENT":
            # Expecting payload to have document_input fields mapped correctly
            # In a real scenario, this would use a robust dispatcher.
            result = await self._job_service.process_document_background(command.payload)
            return JobSubmissionResult(
                job_id=getattr(result, "id", getattr(result, "job_id", "")),
                status=getattr(result, "status", "UNKNOWN"),
                message=getattr(result, "message", ""),
            )
        raise ApplicationError(f"Unsupported job type: {command.job_type}")

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class JobCommand:
    user_id: str
    job_type: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class GetJobStatusCommand:
    user_id: str
    job_id: str

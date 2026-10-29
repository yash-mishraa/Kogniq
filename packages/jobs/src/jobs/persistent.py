import asyncio
import json
import logging
import sqlite3
import uuid
from collections.abc import Callable, Coroutine
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from .interfaces import AbstractJobManager
from .models import Job, JobProgress, JobResult, JobStatistics, JobStatus, StageStatus

logger = logging.getLogger(__name__)


class PersistentJobManager(AbstractJobManager):
    """
    Durable, database-backed job manager supporting bounded retries,
    stuck-job recovery on startup, and graceful asynchronous execution.
    """

    def __init__(
        self,
        db_path: str = "./data/kogniq.db",
        concurrency: int = 3,
    ) -> None:
        self.db_path = db_path
        self.concurrency = concurrency
        self._queue: asyncio.Queue[tuple[str, Callable[[], Coroutine[Any, Any, Any]]]] = asyncio.Queue()
        self._workers: list[asyncio.Task] = []
        self._running = False
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_durable_jobs (
                        id TEXT PRIMARY KEY,
                        job_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        user_id TEXT,
                        current_stage TEXT,
                        completed_stages INTEGER DEFAULT 0,
                        total_stages INTEGER DEFAULT 0,
                        stage_status TEXT,
                        progress_message TEXT,
                        result_data TEXT,
                        error_message TEXT,
                        retry_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP NOT NULL,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_durable_jobs_status ON system_durable_jobs(status)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_durable_jobs_user ON system_durable_jobs(user_id)"
                )
        except Exception as e:
            logger.warning(f"Could not initialize durable jobs schema: {e}")

    def recover_stuck_jobs(self) -> int:
        """
        Detect jobs that were left in RUNNING state due to process termination/restart.
        Marks them as FAILED or PENDING for retry.
        """
        recovered_count = 0
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    "SELECT id, retry_count FROM system_durable_jobs WHERE status = 'RUNNING'"
                ).fetchall()
                now = datetime.now(UTC).isoformat()
                for row in rows:
                    job_id = row["id"]
                    retries = row["retry_count"] or 0
                    if retries < 3:
                        conn.execute(
                            """
                            UPDATE system_durable_jobs 
                            SET status = 'PENDING', retry_count = retry_count + 1, progress_message = 'Recovered after restart, queued for retry'
                            WHERE id = ?
                            """,
                            (job_id,),
                        )
                    else:
                        conn.execute(
                            """
                            UPDATE system_durable_jobs 
                            SET status = 'FAILED', completed_at = ?, error_message = 'Job terminated due to process restart and exceeded retry limit'
                            WHERE id = ?
                            """,
                            (now, job_id),
                        )
                    recovered_count += 1
            if recovered_count > 0:
                logger.info(f"Recovered {recovered_count} interrupted jobs from database.")
        except Exception as e:
            logger.warning(f"Failed to recover stuck jobs: {e}")
        return recovered_count

    async def submit(self, job_type: str, user_id: str | None = None) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, job_type=job_type)
        now = datetime.now(UTC).isoformat()

        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO system_durable_jobs (
                        id, job_type, status, user_id, current_stage, completed_stages,
                        total_stages, stage_status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job.id,
                        job.job_type,
                        job.status.value,
                        user_id,
                        job.progress.current_stage,
                        job.progress.completed_stages,
                        job.progress.total_stages,
                        job.progress.stage_status.value,
                        now,
                    ),
                )
        except Exception as e:
            logger.error(f"Failed to persist job submission: {e}")

        return job

    async def enqueue(
        self,
        job_type: str,
        task_func: Callable[[], Coroutine[Any, Any, Any]],
        user_id: str | None = None,
    ) -> Job:
        """Submit job and enqueue it for bounded asynchronous execution."""
        job = await self.submit(job_type, user_id=user_id)
        await self._queue.put((job.id, task_func))
        return job

    async def get(self, job_id: str) -> Job | None:
        try:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM system_durable_jobs WHERE id = ?", (job_id,)
                ).fetchone()
                if not row:
                    return None

                status = JobStatus(row["status"])
                progress = JobProgress(
                    current_stage=row["current_stage"],
                    completed_stages=row["completed_stages"] or 0,
                    total_stages=row["total_stages"] or 0,
                    stage_status=StageStatus(row["stage_status"]) if row["stage_status"] else StageStatus.NOT_STARTED,
                    message=row["progress_message"],
                )
                stats = JobStatistics(
                    created_at=datetime.fromisoformat(row["created_at"]),
                    started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
                    completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                )
                result = None
                if row["result_data"]:
                    try:
                        result = JobResult(success=True, data=json.loads(row["result_data"]))
                    except Exception:
                        pass

                return Job(
                    id=row["id"],
                    job_type=row["job_type"],
                    status=status,
                    progress=progress,
                    statistics=stats,
                    result=result,
                    error=row["error_message"],
                )
        except Exception as e:
            logger.error(f"Failed to fetch job {job_id}: {e}")
            return None

    async def update_progress(
        self,
        job_id: str,
        current_stage: str | None = None,
        completed_stages: int | None = None,
        total_stages: int | None = None,
        stage_status: str | None = None,
        message: str | None = None,
    ) -> Job:
        now = datetime.now(UTC).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE system_durable_jobs SET
                        status = 'RUNNING',
                        started_at = COALESCE(started_at, ?),
                        current_stage = COALESCE(?, current_stage),
                        completed_stages = COALESCE(?, completed_stages),
                        total_stages = COALESCE(?, total_stages),
                        stage_status = COALESCE(?, stage_status),
                        progress_message = COALESCE(?, progress_message)
                    WHERE id = ?
                    """,
                    (
                        now,
                        current_stage,
                        completed_stages,
                        total_stages,
                        stage_status,
                        message,
                        job_id,
                    ),
                )
        except Exception as e:
            logger.error(f"Failed to update progress for job {job_id}: {e}")

        job = await self.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job

    async def complete(self, job_id: str, result: JobResult) -> Job:
        now = datetime.now(UTC).isoformat()
        data_json = json.dumps(result.data) if result.data else None
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE system_durable_jobs SET
                        status = 'COMPLETED',
                        completed_at = ?,
                        result_data = ?
                    WHERE id = ?
                    """,
                    (now, data_json, job_id),
                )
        except Exception as e:
            logger.error(f"Failed to mark job completed {job_id}: {e}")

        job = await self.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job

    async def fail(self, job_id: str, error_message: str) -> Job:
        now = datetime.now(UTC).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    UPDATE system_durable_jobs SET
                        status = 'FAILED',
                        completed_at = ?,
                        error_message = ?
                    WHERE id = ?
                    """,
                    (now, error_message, job_id),
                )
        except Exception as e:
            logger.error(f"Failed to mark job failed {job_id}: {e}")

        job = await self.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job

    async def cancel(self, job_id: str) -> Job:
        now = datetime.now(UTC).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE system_durable_jobs SET status = 'CANCELLED', completed_at = ? WHERE id = ?",
                    (now, job_id),
                )
        except Exception as e:
            logger.error(f"Failed to mark job cancelled {job_id}: {e}")

        job = await self.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job

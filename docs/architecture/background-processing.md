# Background Processing & Job Queue

Kogniq leverages an asynchronous background processing mechanism to handle long-running workflows without blocking the HTTP response.

## Architecture

The orchestration separates the API layer from the domain execution layer via a formal Job domain.

```mermaid
graph TD
    A[Client] -->|POST /api/v1/jobs/process-document| B[FastAPI Router]
    B -->|Submit Document| C[JobService]
    C -->|submit| D[AbstractJobManager]
    D -->|save| E[MemoryJobManager]
    C -->|BackgroundTasks.add_task| F[FastAPI BackgroundTasks]
    B -->|Returns job_id instantly| A
    
    F -->|Run async| G[Document Processing]
    G -->|update_progress| D
    G -->|complete/fail| D
    
    A -->|GET /api/v1/jobs/{job_id}| B
```

## Lifecycle

A Job follows strict immutable state transitions:
1. `PENDING` - Job is registered and waiting for processing
2. `RUNNING` - Processing started (along with `started_at` timestamp)
3. `COMPLETED` - Processing successful, output ready in `JobResult`
4. `FAILED` - Exception raised, error details in `error_message`
5. `CANCELLED` - User manually halted execution

## Future Proofing

The architecture uses an `AbstractJobManager`. Currently, this is backed by an in-memory dictionary `MemoryJobManager`. When deployment requirements dictate multi-node scale, this interface can cleanly support a Redis/Celery-based implementation.

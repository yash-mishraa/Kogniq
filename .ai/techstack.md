# Technology Stack Register

No library or vendor is finalized during Stage 0. A choice becomes **Chosen** only after requirements, alternatives, evaluation evidence, and an ADR exist.

## Python Workspace

- **Chosen:** Python 3.12–3.13; uv for project/workspace and dependency lifecycle; Ruff for linting and formatting; MyPy for strict static typing; pytest and coverage.py for testing and coverage measurement.
- **Alternatives:** pip with virtualenv; Poetry; PDM; Hatch; separate formatter/linter/import-sorter tools; Pyright; unittest.
- **Reason:** The selected toolchain provides one fast workspace workflow, centralized standards, strict typing, and low configuration duplication while keeping runtime dependencies empty.
- **Current Status:** Foundation configured in `pyproject.toml` and resolved in `uv.lock`; development dependencies were not installed in this session.

## Backend

- **Chosen:** FastAPI for the application boundary, Pydantic Settings for environment configuration, and Uvicorn as the ASGI server.
- **Alternatives:** Other Python ASGI frameworks; TypeScript frameworks; other evidence-backed server platforms.
- **Reason:** The selected stack supports typed contracts, dependency injection, OpenAPI, ASGI middleware, lifespan management, and composition through an application factory while remaining independent of persistence and business logic.
- **Current Status:** Foundational application factory, system endpoints, configurable middleware, standardized errors, lifecycle logging, and initial tests implemented. Authentication, persistence, and business APIs remain deferred.

## Frontend

- **Chosen:** Not selected.
- **Alternatives:** React-based frameworks; other accessible web frameworks.
- **Reason:** Rendering, accessibility, offline, and interaction requirements require discovery.
- **Current Status:** Deferred.

## ML

- **Chosen:** Not selected.
- **Alternatives:** Major Python ML ecosystems; managed or self-hosted inference.
- **Reason:** Tasks, baselines, data scale, and deployment constraints remain unknown.
- **Current Status:** Deferred.

## Vector DB

- **Chosen:** Not selected.
- **Alternatives:** Database extensions; dedicated vector stores; managed search services.
- **Reason:** Corpus scale, filtering, recall, latency, operations, and cost must be benchmarked.
- **Current Status:** Deferred.

## Knowledge Graph

- **Chosen:** Not selected.
- **Alternatives:** Graph databases; relational graph modeling; RDF stores.
- **Reason:** Query patterns, ontology standards, scale, and interoperability need definition.
- **Current Status:** Deferred.

## Experiment Tracking

- **Chosen:** Not selected.
- **Alternatives:** Open-source tracking platforms; managed platforms; lightweight metadata standards.
- **Reason:** Reproducibility, artifact, governance, and hosting needs are not established.
- **Current Status:** Deferred.

## Deployment

- **Chosen:** Not selected.
- **Alternatives:** Managed platform services; containers; orchestrated containers; serverless workloads.
- **Reason:** Traffic, reliability, compliance, skills, and budget targets are unknown.
- **Current Status:** Deferred.

## Testing

- **Chosen:** pytest for Python test execution and pytest-cov/coverage.py for future Python coverage.
- **Alternatives:** unittest and other language-specific test frameworks for non-Python workspaces.
- **Reason:** pytest supports modular discovery and future unit, integration, and contract suites without coupling product architecture to the runner.
- **Current Status:** Discovery and coverage policy configured; no tests exist yet.

## CI/CD

- **Chosen:** Not selected.
- **Alternatives:** GitHub-hosted workflows; other managed or self-hosted automation.
- **Reason:** Repository hosting, security, release, and deployment requirements need confirmation.
- **Current Status:** Deferred.

## Observability

- **Chosen:** Not selected.
- **Alternatives:** Open standards with self-hosted or managed telemetry backends.
- **Reason:** SLOs, data sensitivity, retention, and cost requirements are not defined.
- **Current Status:** Deferred.

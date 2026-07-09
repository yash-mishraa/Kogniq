# Development Guide

Welcome to the Kogniq development environment. This guide outlines the ergonomic workflow designed to ensure consistency across the repository.

## Environment Setup

Kogniq relies heavily on `uv` to maintain a robust Python workspace spanning multiple sub-packages.

1. Install [uv](https://github.com/astral-sh/uv).
2. Install [Docker](https://docs.docker.com/get-docker/) for local dependency hosting (PostgreSQL, Redis).
3. Setup the local `.env`:
   ```bash
   cp .env.example .env
   ```
   *Review the "HUMAN ACTION ITEMS" block within `.env` and adjust the PostgreSQL password if necessary.*
4. Initialize the project:
   ```bash
   make setup
   ```

## Repository Layout

- `apps/`: Executable boundaries (e.g. `apps/api` for the FastAPI backend).
- `packages/`: Agnostic, shared business and domain rules. Packages under here are typically pure Python and not tied to frameworks.
- `infrastructure/`: Global infrastructure provisioning (e.g. Terraform).
- `tests/`: Global E2E or workspace integration testing.

## How to Start

Kogniq ships with a comprehensive `Makefile` acting as the sole entrypoint.

Start the necessary local infrastructure (PostgreSQL & Redis):
```bash
make docker-up
```

Verify services are running successfully:
```bash
make docker-status
```

## How to Run the Backend

To start the FastAPI application (`apps/api`), run:
```bash
make dev
```
The API is now running locally at `http://127.0.0.1:8000`.

## How Migrations Work

Kogniq uses **Alembic** integrated heavily at the repository root. Migrations live in `apps/api/src/apps/api/app/db/migrations`.

Check migration status:
```bash
make db-current
```

Apply pending migrations:
```bash
make db-upgrade
```

Generate a new migration (after modifying `Base` models in Python):
```bash
make db-revision MSG="add_users_table"
```

## How Quality Checks Work

Code quality is enforced strictly by **Ruff**, **MyPy**, and **Pytest**. We expect `0` errors or warnings on any commit.

Run everything:
```bash
make quality
```

Or run individual checks:
- `make format` (Formats code with Ruff)
- `make lint` (Checks for logical flaws with Ruff)
- `make typecheck` (Executes strict MyPy typing passes)
- `make test` (Executes Pytest tests)

## Common Troubleshooting

- **`uv run` fails to find a module**: Ensure you've ran `make setup` to properly link the `uv.workspace`.
- **Database Connection Refused**: Run `make docker-status` to ensure your containers are alive. If `pgAdmin` or `postgres` failed, check the logs via `make docker-logs`.
- **"Table does not exist" Error**: Run `make db-upgrade` to initialize Alembic migrations on a fresh container.
- **Ruff `I001` or `E402` Errors**: Imports must be correctly sorted and placed at the top of the file. Run `make format` to automatically fix import orders.

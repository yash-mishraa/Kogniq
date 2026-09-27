# Kogniq Developer Setup Guide

This guide details exactly how to configure, start, and test the Kogniq stack locally.

## 1. Prerequisites
- **OS**: Windows (tested natively), macOS, or Linux.
- **Python**: 3.13.x
- **Node.js**: v20+ (for frontend)
- **Package Manager (Backend)**: [uv](https://github.com/astral-sh/uv) (required for workspace management)
- **Package Manager (Frontend)**: npm
- **Docker**: (Optional) For running external vector stores if Qdrant/Chroma network implementations are used instead of local persistence.

## 2. Repository Setup

Clone the repository and install the backend workspace using `uv`:

```bash
git clone <repository_url>
cd Kogniq
uv sync
```
This single command resolves and installs the entire `apps/api` application and all `packages/*` dependencies in a virtual environment.

Install the frontend dependencies:
```bash
cd apps/web
npm install
```

## 3. Environment Variables

Create a `.env` file in the root directory (this file is `.gitignore`d).

**Required for Local LLM/Generation:**
- `GEMINI_API_KEY`: Your Google Gemini API key. Required for generating learning content (Flashcards, Quizzes, Study Guides) and Tutor chat responses.

**Backend Configuration (Safe Defaults):**
```ini
KOGNIQ_API_ENVIRONMENT=development
KOGNIQ_LOG_LEVEL=INFO

# Persistence
PERSISTENCE_PROVIDER=sqlite
SQLITE_DATABASE_PATH=kogniq_dev.sqlite

# Auth
# Optional Clerk keys if integrating cloud auth. 
# In 'development' mode, local memory auth is used automatically if these are omitted.
# CLERK_SECRET_KEY=
# CLERK_PUBLISHABLE_KEY=
```

> **WARNING:** Never commit `.env` containing real API keys or Clerk secrets. 

## 4. Database Setup

Kogniq defaults to SQLite in local development. 
The backend automatically executes necessary schema migrations upon startup. 
In `development` mode, the system automatically seeds a demo user account:
- **Email**: `admin@kogniq.ai`
- **Password**: `password`

## 5. Backend Startup

To start the FastAPI backend:

```bash
uv run uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Health Check**: `GET http://127.0.0.1:8000/api/v1/system/health`
- **API Docs**: `GET http://127.0.0.1:8000/docs`

## 6. Frontend Startup

To start the Next.js frontend:

```bash
cd apps/web
npm run dev
```
The frontend will be available at `http://localhost:3000`.

## 7. Testing & Verification

Kogniq uses `pytest` for authoritative backend testing and evaluation.

**Run the full backend regression suite:**
```bash
uv run pytest
```
*Current verified baseline: 461 tests collected and passed.*

**Run evaluation and benchmarking gates:**
```bash
uv run pytest packages/evaluation/tests/test_load_gates.py
```

**Run Static Analysis:**
```bash
uv run ruff check apps/ packages/
uv run mypy apps/ packages/
```

## 8. Benchmark/Evaluation Configuration

Kogniq ships with deterministic evaluation fakes to prevent LLM non-determinism and network latency from breaking CI tests.

To run the application in benchmark mode:
```ini
KOGNIQ_API_ENVIRONMENT=benchmark
LEARNING_GENERATION_PROVIDER=deterministic-fake
LEARNING_GENERATION_PROVIDER_DELAY_MS=1000.0
```
This replaces real Gemini API calls with deterministic HTTP 1000ms latency sleeps, allowing you to isolate and profile backend CPU orchestration overhead accurately.

> **WARNING:** The `deterministic-fake` provider and synthetic delays are strictly for local/CI evaluation tests. They must NEVER be copied into production or `development` configurations, as they will completely disable the LLM integration.

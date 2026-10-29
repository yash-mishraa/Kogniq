# Kogniq Testing Taxonomy & Test Suite

This directory and the module-level test directories govern the automated verification suite for Kogniq.

---

## Test Architecture

Kogniq enforces strict testing across three separate tiers:

```
                            ┌───────────────────────────────────────────────┐
                            │           Playwright E2E Tests                │
                            │  apps/web/tests/ (Browser User Journeys)       │
                            └───────────────────────┬───────────────────────┘
                                                    │
                                                    ▼
                            ┌───────────────────────────────────────────────┐
                            │      FastAPI Integration & Contract Tests     │
                            │  apps/api/tests/ (138 Pytest Tests)           │
                            └───────────────────────┬───────────────────────┘
                                                    │
                                                    ▼
                            ┌───────────────────────────────────────────────┐
                            │        Vitest Frontend Unit Component Tests   │
                            │  apps/web/src/**/*.test.tsx (106 Tests)       │
                            └───────────────────────┬───────────────────────┘
                                                    │
                                                    ▼
                            ┌───────────────────────────────────────────────┐
                            │       Package-Level Pure Domain Unit Tests    │
                            │  packages/*/tests/ (360+ Isolated Unit Tests) │
                            └───────────────────────────────────────────────┘
```

---

## Running the Verification Suite

### 1. Backend Integration & Route Tests
Runs all 138 API tests covering user isolation, document upload, chunking, hybrid retrieval, and authentication:
```bash
uv run pytest apps/api/tests/ -v
```

### 2. Frontend Component & Workspace Engine Tests
Runs all 22 test files (106 unit tests) using Vitest:
```bash
cd apps/web && npm test
```

### 3. All Domain & Package Unit Tests
Runs the full suite across all 15 packages:
```bash
uv run pytest packages/ -v
```

### 4. Production Build Validation
Verifies that the Next.js static asset and server bundle compile with zero type errors:
```bash
cd apps/web && npm run build
```

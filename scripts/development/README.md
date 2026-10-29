# Local Development & Engineering Utilities

Utilities for setting up, inspecting, and developing the Kogniq stack locally.

---

## Quickstart Commands

1. **Start Backend in Hot-Reload Mode**:
   ```bash
   uv run uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Start Frontend Dev Server**:
   ```bash
   cd apps/web && npm run dev
   ```

3. **Reset Local Database with Seed Accounts**:
   ```bash
   rm -f kogniq_dev.sqlite
   uv run uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000
   ```
   *(The backend automatically recreates schemas and seeds demo accounts `admin@kogniq.ai` and `yashmishra1408@gmail.com` with password `password`).*

4. **Run Full Test Suite**:
   ```bash
   uv run pytest apps/api/tests/ -q
   cd apps/web && npm test
   ```

# Deployment Guide

This guide details how to deploy Kogniq in a production-like environment based on its current architecture.

## Deployment Topology
Kogniq is designed as a **single-instance** deployment. Due to its use of SQLite (WAL mode) and local SentenceTransformers embeddings, horizontally scaling the backend across multiple machines is not supported without migrating to external databases (e.g., PostgreSQL, Qdrant).

### 1. Environment Configuration
On your deployment server, configure the environment variables carefully:

```ini
KOGNIQ_API_ENVIRONMENT=production
KOGNIQ_LOG_LEVEL=WARNING

# Persistence
PERSISTENCE_PROVIDER=sqlite
SQLITE_DATABASE_PATH=/var/lib/kogniq/data.sqlite

# Security
KOGNIQ_API_CORS_ORIGINS=["https://app.yourdomain.com"]
KOGNIQ_API_ALLOWED_HOSTS=["api.yourdomain.com"]

# AI Providers
GEMINI_API_KEY=<your_production_key>
```

> **WARNING:** Ensure `LEARNING_GENERATION_PROVIDER=deterministic-fake` is **NOT** set in production. Ensure no benchmark environments or delays are configured.

### 2. Backend Deployment (Single Worker)
Due to SQLite multiprocess read-staleness limitations, the backend must be deployed using a **single-worker** event loop. The single worker utilizes an internal thread-pool (default 50 threads) to handle high-concurrency requests safely.

Start the FastAPI application:
```bash
uv run uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

*(Note: The database schema is initialized automatically upon startup.)*

### 3. Frontend Deployment
The Next.js application can be built and served via Node.js, or exported.

```bash
cd apps/web
npm install
npm run build
npm run start -p 3000
```
Ensure the frontend environment variables point to your production API URL (e.g., `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`).

### 4. Health and Readiness Checks
Your load balancer or reverse proxy should monitor the application health at:
`GET /api/v1/system/health`

### 4b. Keep-alive (Preventing Free-tier Cold Starts)
On Render's free tier the backend service pauses after ~15 minutes without
inbound traffic, and the next visitor waits 50-60 seconds for a cold start.
Two mechanisms keep the public demo always warm:

1. **Automated pinging (in-repo):** `.github/workflows/keepalive.yml` sends an
   unauthenticated `GET /api/v1/system/health` request every 5 minutes via
   GitHub Actions (free for public repositories). It targets the public
   frontend origin, which proxies `/api/*` to the backend; override the URL
   with a `KEEPALIVE_PING_URL` repository secret if the origin changes.
   The workflow always exits successfully so the Actions history stays green.
   Note: GitHub disables scheduled workflows after 60 days of no repository
   activity — any commit resets the timer.
2. **External monitor (recommended backup):** create a free UptimeRobot
   (https://uptimerobot.com) HTTP monitor on the same health URL with a
   5-minute interval. External monitors keep running even if the repository is
   inactive.

Frontend resilience (independent of keep-alive): every API request carries a
deadline (`SESSION_TIMEOUT_MS = 10s`, default `45s`, LLM generation `180s`),
the session probe retries transient failures, and the boot splash reports
"warming up" rather than appearing frozen. A paused backend therefore degrades
into a clear retry state instead of an indefinite hang.

### 5. Security Considerations
- The API should be deployed behind a reverse proxy (Nginx/Caddy) with TLS (HTTPS) termination.
- Ensure the SQLite `.sqlite` file is mounted in a secure volume restricted to the application user.
- Kogniq strictly isolates users based on Authorization headers. Ensure your frontend handles authentication securely.

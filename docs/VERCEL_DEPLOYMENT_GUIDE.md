# Kogniq — Complete Vercel & Production Deployment Guide

This guide provides an end-to-end walkthrough for deploying Kogniq to production using **Vercel** for the Next.js frontend and a container host (Render, Railway, Fly.io, or VPS) for the FastAPI Python backend.

---

## 1. Architecture Overview

```
                        ┌───────────────────────────────────────────────┐
                        │                 Vercel Edge                   │
                        │       Next.js 15 Frontend (apps/web)          │
                        │                                               │
                        │  - Global CDN, SSR & Static Page Optimization │
                        │  - Route Rewrites: /api/:path* ───────────────┼───┐
                        └───────────────────────────────────────────────┘   │
                                                                            │ Proxied
                                                                            │ (Zero CORS)
                                                                            ▼
                        ┌───────────────────────────────────────────────┐
                        │      Backend Container (Render/Railway/VPS)   │
                        │             FastAPI (apps/api)                │
                        │                                               │
                        │  - PyTorch & Local SentenceTransformers       │
                        │  - Hybrid Search (ChromaDB + SQLite FTS5)     │
                        │  - Gemini / Local LLM Inference               │
                        │  - Durable Background Job Queue               │
                        └───────────────────────────────────────────────┘
```

### Why This Architecture?
- **Vercel** is the optimal platform for Next.js, providing automatic caching, worldwide CDN distribution, zero-downtime deploys, and instant rollbacks.
- The **Python Backend** relies on native C++ libraries (`sentence-transformers`, `torch`, `chromadb`) and persistent storage (`sqlite3` / `chroma_data`), which exceed Vercel's 250 MB serverless uncompressed bundle limits.
- Next.js rewrites route all client-side calls to `/api/v1/...` directly to the backend URL (`BACKEND_URL`), ensuring **zero CORS issues** and unified session cookies.

---

## 2. Step 1: Deploy Backend to Container Host (Render / Railway)

Before pointing Vercel to your backend, deploy the FastAPI container:

### Option A: Render.com (Recommended Free/Low-Cost)
1. Fork or push this repository to GitHub.
2. Sign in to [Render.com](https://render.com) and click **New +** $\to$ **Web Service**.
3. Connect your GitHub repository.
4. Configure the service:
   - **Name**: `kogniq-api`
   - **Language**: `Docker` (Render will detect the root `Dockerfile`)
   - **Region**: Closest to your users (e.g., Oregon or Frankfurt)
   - **Branch**: `main` (or your active branch)
   - **Instance Type**: Starter or Standard (1 GB+ RAM recommended for PyTorch embeddings)
5. Add **Environment Variables**:
   ```ini
   PORT=8000
   KOGNIQ_API_ENVIRONMENT=production
   KOGNIQ_API_LOG_LEVEL=info
   LEARNING_GENERATION_PROVIDER=gemini
   GEMINI_API_KEY=your_google_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash-lite
   PERSISTENCE_PROVIDER=sqlite
   SQLITE_DATABASE_PATH=./data/kogniq.db
   ```
6. Click **Create Web Service**.
7. Once deployed, copy your backend URL (e.g., `https://kogniq-api.onrender.com`).

### Option B: Railway.app
1. Go to [Railway.app](https://railway.app) $\to$ **New Project** $\to$ **Deploy from GitHub repo**.
2. Select the Kogniq repository.
3. In **Settings**, ensure the builder is set to `Dockerfile`.
4. In **Variables**, add the same environment variables listed above.
5. In **Networking**, click **Generate Domain** and copy the resulting HTTPS URL.

---

## 3. Step 2: Deploy Frontend to Vercel

The repository is pre-configured with:
- Root [`vercel.json`](file:///Users/yashmishra14/Personal%20projects/Kogniq/vercel.json) and [`apps/web/vercel.json`](file:///Users/yashmishra14/Personal%20projects/Kogniq/apps/web/vercel.json)
- Dynamic proxy rewrites in [`apps/web/next.config.ts`](file:///Users/yashmishra14/Personal%20projects/Kogniq/apps/web/next.config.ts)

### Option A: Via Vercel Web Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and click **Add New...** $\to$ **Project**.
2. Import your Kogniq GitHub repository.
3. Configure Project Settings:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click *Edit* and select **`apps/web`** (or leave as root, both work).
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`
4. Expand **Environment Variables** and add:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `NEXT_PUBLIC_PROVIDER_MODE` | `live` | Enables real backend API communication |
   | `BACKEND_URL` | `https://your-backend-api.onrender.com` | Deployed backend URL from Step 1 |
5. Click **Deploy**.

Vercel will build and deploy your application in under 60 seconds.

---

### Option B: Via Vercel CLI

If you prefer deploying directly from your terminal:

1. Install the Vercel CLI globally:
   ```bash
   npm install -g vercel
   ```
2. Navigate to the frontend directory:
   ```bash
   cd apps/web
   ```
3. Link and deploy:
   ```bash
   vercel
   ```
4. Set the backend URL environment variable:
   ```bash
   vercel env add BACKEND_URL production
   # Enter your deployed backend URL: https://your-backend-api.onrender.com
   ```
5. Deploy to production:
   ```bash
   vercel --prod
   ```

---

## 4. Environment Variables Reference

### Frontend (`apps/web`) on Vercel
| Variable | Required | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `BACKEND_URL` | **Yes** | `http://127.0.0.1:8000` | URL of the deployed FastAPI backend. Rewrites `/api/:path*` to this host. |
| `NEXT_PUBLIC_PROVIDER_MODE` | **Yes** | `live` | Instructs UI services to connect to live API endpoints rather than in-memory mocks. |

### Backend (`apps/api`) on Container Host
| Variable | Required | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `PORT` | No | `8000` | Port for the Uvicorn ASGI server to bind. |
| `GEMINI_API_KEY` | Yes (for hosted) | None | Google Gemini API key for question answering, quizzes, and flashcards. |
| `GEMINI_MODEL` | No | `gemini-3.5-flash-lite` | Gemini model identifier. |
| `LEARNING_GENERATION_PROVIDER` | No | `auto` | Provider mode: `auto` (Gemini with local fallback), `gemini`, or `local`. |
| `PERSISTENCE_PROVIDER` | No | `sqlite` | Primary storage engine (`sqlite` or `memory`). |
| `SQLITE_DATABASE_PATH` | No | `./data/kogniq.db` | Path to persistent SQLite database file. |

---

## 5. Post-Deployment Verification Checklist

Once deployed, verify your live Vercel URL (e.g., `https://kogniq.vercel.app`):

1. **Health Check**:
   Visit `https://your-vercel-domain.vercel.app/api/v1/system/overview` $\to$ should return HTTP 200 with system readiness statistics.
2. **Authentication**:
   Navigate to `/` $\to$ Login with demo credentials or register a new user.
3. **Document Ingestion**:
   Go to **My Documents** $\to$ Upload a PDF document $\to$ Confirm chunking and indexing completes.
4. **Ask Questions**:
   Go to **Ask Questions** $\to$ Submit a query against the uploaded document $\to$ Confirm grounded answers and citations appear.
5. **Flashcards & Quizzes**:
   Go to **Flashcards** and **Quizzes** $\to$ Verify cards flip, answers score accurately, and explanations render.
6. **Knowledge Graph**:
   Go to **Knowledge Graph** $\to$ Click *Extract Knowledge* $\to$ Inspect generated concepts and relationships.

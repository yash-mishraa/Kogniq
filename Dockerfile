FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependencies definitions
COPY pyproject.toml uv.lock* ./
COPY packages ./packages
COPY apps/api ./apps/api

# Sync Python packages
RUN uv sync --frozen || uv sync

# Pre-cache SentenceTransformers model at build time so runtime uploads don't stall or download from HuggingFace
ENV HF_HOME="/app/.cache/huggingface" \
    TORCH_NUM_THREADS=1 \
    OMP_NUM_THREADS=1
RUN uv run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Expose backend port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

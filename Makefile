.DEFAULT_GOAL := help

.PHONY: setup format lint typecheck test clean help

setup: ## Create/update the uv environment and install development tools.
	uv sync --group dev

format: ## Format Python source with Ruff.
	uv run --group dev ruff format .

lint: ## Run Ruff lint checks.
	uv run --group dev ruff check .

typecheck: ## Run strict MyPy checks.
	uv run --group dev mypy

test: ## Run the test suite.
	uv run --group dev pytest

clean: ## Remove repository-local Python caches and coverage output.
	uv run --no-sync python -c "from pathlib import Path; import shutil; names={'__pycache__','.mypy_cache','.pytest_cache','.ruff_cache','htmlcov'}; [shutil.rmtree(path, ignore_errors=True) for path in Path('.').rglob('*') if path.is_dir() and path.name in names]; [path.unlink(missing_ok=True) for path in Path('.').glob('.coverage*')]"

help: ## Show available commands.
	@echo "Kogniq development commands:"
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z_-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

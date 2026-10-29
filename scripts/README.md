# Kogniq Engineering & Operations Scripts

This directory houses operational tools, load testing runners, automated evaluation drivers, and maintenance utilities for the Kogniq platform.

---

## Script Inventory

| Script | Purpose | Usage |
| :--- | :--- | :--- |
| **`benchmark_runner.py`** | Evaluates end-to-end RAG latency, retrieval precision, and ground-truth hit rates across realistic workloads. | `uv run python scripts/benchmark_runner.py` |
| **`100_vu_runner.py`** | High-concurrency simulation simulating 100 simultaneous virtual users querying the hybrid search pipeline. | `uv run python scripts/100_vu_runner.py` |
| **`verify_forward_compatibility.sh`** | Bash script ensuring forward compatibility across database schemas, API schemas, and package interfaces. | `bash scripts/verify_forward_compatibility.sh` |
| **`run_m5_gates.ps1`** | Windows/Cross-platform PowerShell script running strict static analysis, linting, and quality verification gates. | `pwsh scripts/run_m5_gates.ps1` |
| **`take_screenshots.js`** | Puppeteer automation capturing responsive UI states for documentation and visual regression checks. | `node scripts/take_screenshots.js` |

---

## Directory Organization

- **[`deployment/`](deployment/)**: Operational checklists, container pre-flight diagnostics, and production verification procedures.
- **[`development/`](development/)**: Local engineering workflows, database seed resets, and mock service runners.
- **[`evaluation/`](evaluation/)**: Benchmark dataset runners and precision-recall metric exporters.
- **[`maintenance/`](maintenance/)**: Database VACUUM routines, orphaned document cleanup, and Chroma index rebuilding.

# Research Experiments & Benchmark Reports

This directory records experimental investigations, architectural comparisons, and empirical evaluations across the Kogniq retrieval pipeline.

---

## Key Experimental Results

### 1. Hybrid Retrieval vs. Single-Method Search
- **Experiment**: Comparison of standalone Dense Vector Search (Chroma), Lexical BM25 Search (SQLite FTS5), and Hybrid Fused Search with Reciprocal Rank Fusion (RRF).
- **Outcome**: Hybrid RRF achieved a **+14.2% higher Mean Reciprocal Rank (MRR)** and eliminated failure modes caused by exact acronyms and specialized numerical tokens that dense embeddings frequently fail to differentiate.

### 2. Chunking Parameter Optimization
- **Parameters Tested**:
  - Small: 600 characters / 100 character overlap
  - Medium (Selected): 1,200 characters / 200 character overlap (`KOGNIQ_CHUNK_SIZE=1200`, `KOGNIQ_CHUNK_OVERLAP=200`)
  - Large: 2,400 characters / 400 character overlap
- **Outcome**: The 1,200/200 configuration demonstrated the optimal trade-off between retaining complete semantic propositions (e.g. mathematical definitions and scientific conclusions) while preventing irrelevant noise from degrading LLM generation focus.

---

## Running Benchmark Experiments

```bash
uv run python scripts/benchmark_runner.py
```
Output results and evaluation runs are persisted automatically in the `evaluation_runs` SQLite table and displayed visually in the **Engineering Console $\to$ Evaluation** tab.

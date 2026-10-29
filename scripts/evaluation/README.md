# RAG Evaluation & Benchmark Utilities

Entrypoints and measurement drivers for empirical evaluation of the Kogniq retrieval and generation pipelines.

---

## Evaluation Drivers

1. **End-to-End Latency & Retrieval Quality**:
   ```bash
   uv run python scripts/benchmark_runner.py
   ```
   Measures:
   - **Hit Rate @ K**: Proportion of queries where at least one ground-truth passage was retrieved.
   - **MRR (Mean Reciprocal Rank)**: Quality of result ranking across fused vector and BM25 candidate lists.
   - **End-to-end Latency**: Time to retrieve, assemble context, generate answer, and validate citations.

2. **Concurrent Load Testing**:
   ```bash
   uv run python scripts/100_vu_runner.py
   ```
   Simulates 100 concurrent virtual users querying the system under heavy load to measure thread-pool latency under contention.

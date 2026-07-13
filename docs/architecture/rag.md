# Retrieval-Augmented Generation (RAG)

**Status:** Planned (Not Yet Implemented)

## Purpose
To dynamically retrieve relevant context from the knowledge base to ground the AI Agent's responses in factual curriculum material.

## Expected Responsibilities
- Vector database integration (e.g., Pinecone, Qdrant, PGVector).
- Hybrid search (Dense vector search + BM25 keyword search).
- Graph-based retrieval (traversing prerequisite nodes).
- Re-ranking and context window optimization.

## Relationship to Existing Packages
RAG bridges the output of the Machine Learning (Embeddings) layer with the Agent layer. It relies heavily on the quality of the `ChunkCollection` (from `packages/content`) and the `Concept` graph (from `packages/learning`).

---
*Return to [Architecture Index](README.md).*

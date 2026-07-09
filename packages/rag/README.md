# RAG Package

## Purpose

Reserve the reusable boundary for retrieval, grounding, generation, and citation capabilities.

## Responsibilities

Future ownership includes ingestion contracts, chunking, embedding, indexing, retrieval, reranking, context assembly, generation adapters, and citation validation.

## Public Interface

Planned ingestion, retrieval, grounded-generation, and citation contracts described in [the package catalog](../../.ai/package_contracts.md#packagesrag). No interface is implemented.

## Dependencies

May depend on `packages/shared` and approved public knowledge-graph contracts. Provider integrations must remain behind adapters.

## Future Expansion

Hybrid retrieval, graph-assisted search, model routing, multimodal grounding, and quality instrumentation may be added after evaluation criteria exist.

## Ownership

Retrieval and AI engineering team — `<OWNER_NAME>`.

## What Does NOT Belong Here

Application authorization, learner workflow ownership, UI, agent planning, domain hardcoding, ungoverned content, credentials, or direct access to other packages' storage.


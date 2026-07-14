# Knowledge Graph Domain Foundation

**Last Updated:** 2026-07-14
**Status:** Implemented

## Context

The Knowledge Graph Domain introduces immutable domain models representing educational knowledge independently of any extraction algorithm, LLM, parser, graph database, or AI provider. 

This domain forms the bridge between Retrieval and future educational reasoning systems, establishing the "truth" representation of concepts and their interconnectivity.

## Why Knowledge is its own bounded context

Knowledge requires a distinct lifecycle from raw content and search indices. While content focuses on text chunks and structure, and retrieval focuses on vector similarity, the Knowledge domain is concerned exclusively with semantics, entity definitions, and relationships (the ontology). Separating this allows Kogniq to evolve its ontology independently of the underlying text parser or the vector database.

## Difference between Knowledge and Content

- **Content Domain:** Transforms raw PDFs/HTML into structurally meaningful `Chunk` objects. It is concerned with formatting, headings, and character lengths.
- **Knowledge Domain:** Transforms structurally meaningful `Chunk` objects into semantically meaningful `KnowledgeConcept` objects. It is concerned with definitions, synonyms, and logical relationships (e.g., `DEPENDS_ON`, `DEFINES`).

## Difference between Knowledge and Retrieval

- **Retrieval Domain:** Orchestrates the semantic search over vectors representing text. It finds the most similar `Chunk` based on a mathematical embedding.
- **Knowledge Domain:** Navigates the actual structured relationships. It can answer logical questions like "What are the prerequisites for this concept?" independent of vector similarity.

## Deferred Extraction

Extraction algorithms (LLMs, NLP heuristics, Spacy/NLTK pipelines) are intentionally deferred. By establishing the pure domain models first, we guarantee that the rest of Kogniq (agents, UI, learning tracking) depends on the *shape* of the knowledge, not the *method* used to extract it. This ensures that when we eventually plug in an extraction provider, the core system boundaries remain perfectly intact.

## Architecture Flow

```mermaid
flowchart TD
    subgraph Content Domain
    A[Content / Source Document] -->|Parsing| B[Chunk]
    end
    
    subgraph Knowledge Extraction (Deferred)
    B -->|LLM / NLP Extraction| C[Knowledge Concept]
    C -->|Relationship Building| D[Knowledge Graph]
    end
    
    subgraph Knowledge Domain
    C
    D
    end
```

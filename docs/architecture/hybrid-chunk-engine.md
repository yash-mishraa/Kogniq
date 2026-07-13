# Hybrid Chunk Engine

## Overview
The `HybridChunkEngine` is the single public entry point for chunk generation in Kogniq. Instead of containing chunking logic itself, it acts as a lightweight orchestrator that selects the optimal chunking strategy based on the structure of the incoming `NormalizedDocument`.

## Purpose
Different documents require different chunking approaches. A well-formatted Markdown file with distinct headings should be chunked semantically by those boundaries (`StructuralChunkStrategy`). Conversely, a 50-page raw text transcript lacks semantic boundaries and must be chunked arbitrarily to fit into embedding context windows (`FixedSizeChunkStrategy`). 

By orchestrating strategies behind a unified engine facade, calling applications do not need to inspect documents or guess which algorithm to run.

```mermaid
flowchart TD
    A[Calling Application] -->|chunk(doc)| B[HybridChunkEngine]
    
    B --> C{_has_headings(doc)?}
    C -->|Yes| D[StructuralChunkStrategy]
    C -->|No| E[FixedSizeChunkStrategy]
    
    D --> F[ChunkCollection]
    E --> F
```

## Strategy Composition vs Inheritance
Kogniq prefers *Composition* over *Inheritance* for chunking logic. 
We explicitly did **not** create a `HybridFixedSizeStructuralStrategy` class that inherits from both strategies. Inheritance tightly couples implementations, makes independent testing difficult, and leads to brittle monolithic classes. 

Instead, `HybridChunkEngine` injects the independent strategies via its constructor:
```python
engine = HybridChunkEngine(
    structural_strategy=StructuralChunkStrategy(),
    fixed_strategy=FixedSizeChunkStrategy(max_characters=1000)
)
```
This isolates testing and enables dynamic swapping of behaviors without modifying the core algorithms.

## Observability
The engine exposes a `last_selected_strategy` property containing the class name of the delegated strategy. This provides transparency for debugging, telemetry, and testing, without polluting the immutable `NormalizedDocument` or `ChunkCollection` domain models with execution metadata.

## Future Compatibility
The engine is currently binary (Headings -> Structural, else -> Fixed Size). In the future, it is fully extensible to incorporate:
- **Sliding Window Chunking**: To add overlap between chunks.
- **Semantic Chunking**: Using LLMs or embeddings to find topic shifts.
- **Adaptive Chunking**: Adjusting limits dynamically based on token densities.

These future strategies can simply be added as new independent strategy classes and injected into the engine orchestration flow, preserving backward compatibility and avoiding regression risks in existing logic.

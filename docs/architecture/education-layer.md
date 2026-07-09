# Educational Knowledge Layer Architecture

## Purpose
The `education` bounded context is the semantic bridge between the raw parsed structure of a document (e.g., Normalized Document Model) and the actual pedagogical concepts meant to be taught.

It models the purely educational semantics—definitions, examples, exercises, and conceptual relationships—independent of any specific extraction algorithm (like a LLM or heuristic parser) or storage mechanism (like a graph database).

## Architecture

```mermaid
graph TD
    subgraph Content Domain
    ND[NormalizedDocument]
    NB[NormalizedBlock]
    end

    subgraph Education Domain
    EC[EducationalConcept]
    ED[EducationalDefinition]
    EE[EducationalExample]
    EX[EducationalExercise]
    ER[EducationalRelationship]
    end

    subgraph Learning Domain
    Course[Course]
    Learner[Learner]
    end

    NB -.->|Extracted into| ED
    NB -.->|Extracted into| EE
    NB -.->|Extracted into| EX
    
    ED -->|Belongs to| EC
    EE -->|Belongs to| EC
    EX -->|References| EC
    ER -->|Connects| EC
    
    EC -.->|Belongs to| Course
    Learner -.->|Masters| EC
```

## Core Principles
1. **Extraction Agnostic:** This layer defines what an educational concept *is*, not *how* an AI finds it in a PDF.
2. **Persistence Agnostic:** This layer defines relationship edges (e.g., Prerequisite), not graph database query structures.
3. **Immutability:** Educational entities and value objects are immutable once constructed to ensure predictable behavior during the eventual knowledge graph ingestion process.

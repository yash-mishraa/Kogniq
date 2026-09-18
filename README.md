# Kogniq

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![uv](https://img.shields.io/badge/uv-fast-magenta.svg)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![MyPy](https://img.shields.io/badge/mypy-strict-success.svg)
![Pytest](https://img.shields.io/badge/pytest-passing-success.svg)
![License](https://img.shields.io/badge/license-MIT-green)

## Project Vision

Kogniq is an open-source, agentic AI educational platform designed to transform raw learning materials—such as textbooks, documentation, and research papers—into interactive, personalized tutoring experiences. 

## Why Kogniq exists

Most AI tutors are merely wrappers around chat models. They lack a deep understanding of the *structure* of learning materials and the *pedagogy* required to teach them. Kogniq solves this by building a rigorous, Domain-Driven Design (DDD) foundation that processes content semantically, builds prerequisite knowledge graphs, and utilizes multi-agent systems to tutor students effectively.

## What Kogniq Is NOT

To understand our scope, it helps to understand what we are not building today:
- **Not an LMS**: We don't manage class rosters or gradebooks.
- **Not a note-taking application**: We aren't replacing Notion or Obsidian.
- **Not a generic chatbot**: We are strictly focused on pedagogical tutoring.
- **Not tied to any LLM vendor**: The architecture is provider-agnostic.
- **Not tied to any vector database**: The architecture is storage-agnostic.

## Current Repository Status

| Metric | Status |
|--------|--------|
| Workspace Packages | Multiple isolated domains (`shared`, `content`, `embedding`, etc.) |
| Developer Demos | 19 unique runnable demos demonstrating implemented components |
| Architecture Documents | Deep dives for every completed pipeline stage |
| Unit Tests | Hundreds of passing tests enforcing immutable invariants |
| Bounded Contexts | 8 distinct implemented contexts |
| Implemented AI Providers | SentenceTransformers, Gemini |

## Current Capabilities

Kogniq currently provides a complete, end-to-end foundation for AI educational content generation.
- **Robust Content Pipeline**: Ingests Markdown, PDF, DOCX, HTML, and TXT files.
- **Deterministic Normalization**: Converts diverse formats into a unified `NormalizedDocument` structure.
- **Hybrid Chunk Engine**: Dynamically orchestrates structural and fixed-size strategies.
- **Local Embeddings**: Provider-agnostic generation using local transformers.
- **Vector Storage**: Provider-agnostic indexing using ChromaDB and Qdrant.
- **Knowledge Extraction**: Transforms chunks into a synthesized `KnowledgeGraph`.
- **Learning Content Generation**: Produces AI-generated artifacts (Summaries, Notes, Flashcards, Quizzes, Study Guides).
- **Intelligent Learning Loop**: AI Tutor integrations ("Explain my mistake"), deterministic next-action recommendations, and analytics.
- **Modern React Frontend**: Immersive Workspace Engine handling Notebooks, Flashcards, Studio, and Document parsing.
- **100% Type Coverage**: Enforced by MyPy strict mode across all packages.

## Implemented Architecture

The following bounded contexts and concrete implementations are fully complete and tested in Kogniq today.

**Bounded Contexts**
- ✔ Shared
- ✔ Content
- ✔ Chunking
- ✔ Embedding
- ✔ Retrieval
- ✔ Knowledge
- ✔ Pipeline
- ✔ Learning Content
- ✔ API & Authentication
- ✔ Frontend Workspaces
- ✔ Content Intelligence

**Current Concrete Implementations**

*Processors*
- ✔ PDF
- ✔ DOCX
- ✔ Markdown
- ✔ TXT
- ✔ HTML

*Chunk Strategies*
- ✔ Structural
- ✔ Fixed Size
- ✔ Hybrid

*Embedding Providers*
- ✔ Local (SentenceTransformers)

*Vector Stores*
- ✔ ChromaDB

*Knowledge Extraction*
- ✔ Gemini


*Learning Generators*
- ✔ Summary Generator
- ✔ Notes Generator
- ✔ Flashcards Generator
- ✔ Quiz Generator
- ✔ Study Guide Generator
- ✔ Explanation Generator

## Current AI Pipeline

```mermaid
flowchart TD
    R[Resource]
    
    subgraph Content Processing
        PR[ProcessorRegistry]
        ND[NormalizedDocument]
        HC[HybridChunkEngine]
        CC[ChunkCollection]
    end
    
    subgraph Knowledge & Embeddings
        KE[Knowledge Extraction]
        KG[KnowledgeGraph]
        EP[Embedding Provider]
        EC[EmbeddingCollection]
        VS[(Vector Store)]
    end
    
    subgraph Learning Generation
        SG[SummaryGenerator]
        LC[LearningContent]
    end

    R --> PR
    PR --> ND
    ND --> HC
    HC --> CC
    
    CC --> KE
    KE --> KG
    
    CC --> EP
    EP --> EC
    EC --> VS
    
    CC -.-> SG
    KG -.-> SG
    SG --> LC
```

## Monorepo Structure

We use `uv` workspaces to manage multiple independent Python packages in a single repository.

### Workspace Packages
- `packages/shared/`: Core abstractions and domain primitives.
- `packages/content/`: File processing, normalization, intelligence, and chunking.
- `packages/embedding/`: Provider-agnostic vector generation.
- `packages/retrieval/`: Semantic search and ranking.
- `packages/knowledge/`: Extraction of concepts and prerequisite graphs.
- `packages/pipeline/`: Orchestration of the intelligence pipeline.
- `packages/learning-content/`: Generation of educational artifacts (Summaries, Flashcards, etc.).
- `packages/auth/`: Security and user isolation.
- `packages/application/`: Learning loop use cases and orchestrators.
- `apps/api/`: FastAPI endpoints.
- `apps/web/`: React frontend workspaces.

## Development Setup

1. Install `uv`:
   ```bash
   pip install uv
   ```
2. Sync the workspace:
   ```bash
   uv sync
   ```
3. Run the complete test suite:
   ```bash
   uv run python -m pytest
   ```

*See [docs/development.md](docs/development.md) for full instructions and developer demos.*

## Quality Gates

We enforce strict quality gates before any code is merged:
- All tests must pass (`uv run python -m pytest`).
- Code must be perfectly typed (`uv run python -m mypy .`).
- Code must be perfectly linted and formatted (`uv run ruff check .`).

## Current Implementation Status

| Component | Status |
|-----------|--------|
| Content Processing | ✅ Complete |
| Chunk Engine | ✅ Complete |
| Embedding | ✅ Complete |
| Vector Store | ✅ Complete |
| Retrieval | ✅ Complete |
| Knowledge Extraction | ✅ Complete |
| Learning Content | ✅ Complete |
| API | ✅ Complete |
| Frontend | ✅ Complete |
| Content Intelligence | ✅ Complete |

## Future Milestones

Please see [docs/ROADMAP.md](docs/ROADMAP.md) for a comprehensive view of upcoming features, including Notes, Flashcards, Quiz Generators, and the Frontend layer.

## Contributing

Contributions are welcome! Please read our [Development Guide](docs/development.md) to get started. Ensure all code passes the quality gates before submitting a pull request.

## License

MIT License. See `LICENSE` for details.

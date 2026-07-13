# Kogniq Roadmap

This document outlines the current state and future milestones for the Kogniq project.

## 🟢 Completed

### Stage 1 - 3: Domain Foundations
- ✅ `packages/shared`: Base entities, Identity, Timestamps, Domain Events.
- ✅ `packages/learning`: `Subject`, `Concept`, `LearningObjective`, and `PrerequisiteValidator` (DAG mapping).
- ✅ `packages/education`: `Student`, `ProgressRecord`, `TutorSession`, `Interaction`, and `Assessment`.

### Stage 4 - 6: Content Processors & Normalization
- ✅ `ProcessorRegistry`: Immutable plugin management.
- ✅ `NormalizedDocument`: The canonical representation for all ingested text.
- ✅ **Processors**: `PDFProcessor`, `MarkdownProcessor`, `TXTProcessor`, `HTMLProcessor`, `DOCXProcessor`.

### Stage 7: Universal Chunk Engine
- ✅ `ChunkModel`: Pure, immutable `Chunk` and `ChunkCollection` structures.
- ✅ `StructuralChunkStrategy`: Chunking based on semantic `HEADING` blocks.
- ✅ `FixedSizeChunkStrategy`: Deterministic fallback chunking by character limits.
- ✅ `HybridChunkEngine`: Dynamic orchestration based on document structure.

## 🟡 In Progress

### Stage 8: Repository Stabilization
- 🔄 Documentation rewrite and repository cleanup.
- 🔄 Architecture Indexing and Roadmap generation.

## 🔴 Upcoming

### Phase 3: AI & Embeddings
- Introduce Vector Database abstraction.
- Implement OpenAI / HuggingFace text-embedding connectors.
- Generate semantic vectors for `ChunkCollection` elements.

### Phase 4: Retrieval (RAG)
- Build hybrid search (dense + BM25).
- Enable Knowledge Graph traversal to rank chunks by prerequisite distance.
- Construct the `RAGService` in the Backend API.

### Phase 5: Agentic Tutors
- Build multi-agent orchestration for tutoring sessions.
- Implement the "Tutor" and "Grader" persona patterns.
- Connect Agents to the `TutorSession` entity in the `education` domain.

## 🌌 Long-Term Vision

- **React Frontend**: A web dashboard for uploading documents, viewing knowledge graphs, and interacting with the Agentic Tutors.
- **Voice Capabilities**: Real-time voice interaction with the Tutor.
- **Adaptive Curriculums**: Automatically generating missing concepts or lessons when a student repeatedly fails an assessment.

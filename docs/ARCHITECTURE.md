# Kogniq System Architecture

Kogniq is designed as an agentic AI education system. Its architecture emphasizes robust data modeling, strict boundaries, and determinism.

## 1. Frontend Architecture

The frontend (`apps/web`) is built with React/Next.js and follows a rich **Workspace Engine** paradigm.

- **Workspaces:** Distinct learning environments (Tutor, Learning Hub, Notebook, Flashcards, Quiz, Knowledge Graph, Analytics, Study Guide).
- **Workspace Memory:** A highly robust reducer-pattern architecture mapping intention to interaction. Data is persisted to `localStorage` deterministically.
- **Tutor Chat:** Acts as the primary agentic entry point.
- **Interactive Notebook:** Allows synchronous reading and AI generation, mapping directly to `NotebookEntry` models on the backend.

## 2. Backend Architecture

The backend (`apps/api`) is a FastAPI application implementing strict Clean Architecture.

- **Application Layer:** Contains pure Use Cases (e.g., `TutorChatUseCase`, `ProcessDocumentUseCase`).
- **Domain Layer:** Immutable entities, value objects, and business rules isolated from external concerns.
- **Infrastructure:** Repositories, Database sessions, and external API clients.
- **UnitOfWork (UoW):** Ensures transactional consistency for mutations. All database interactions route through a UoW factory.
- **Dependency Injection:** Repositories and Providers are injected into Use Cases.

## 3. AI / Agent Architecture

Kogniq utilizes a multi-agent structure focused around the `TutorChatUseCase`.

- **TutorChatUseCase:** The primary conversational loop. It maps user messages, executes `_provider.generate_chat`, handles tool calls, and bounds iterations (maximum 5 turns per request) to prevent infinite loops.
- **Global Tools vs. Document Tools:** Tools are authorized and injected dynamically. Examples include `QueryKnowledgeGraph` and `RetrieveSemanticContext`.
- **RAG & Semantic Search:** Content is chunked (Hybrid Chunk Engine), embedded using local transformers (SentenceTransformers), and queried semantically. 
- **Generators:** The `learning-content` package contains distinct deterministic pipelines (Flashcard, Quiz, Study Guide, Notes) using `GeminiTextGenerationProvider`.

## 4. Learning Intelligence

Kogniq moves beyond simple chatbots by building pedagogical graphs.

- **Knowledge State:** Tracks a user's mastery over extracted `Concept` entities.
- **Spaced Repetition (SRS):** Calculates decay and schedules review events for flashcards and quizzes.
- **Evidence Events:** Every interaction is persisted to calculate realtime analytics.

## 5. Persistence

- **SQLite (Development/Default):** Single-file persistence with WAL mode for high concurrency.
- **Schema & Migrations:** Explicit SQL schemas initialize the database idempotently.
- **Idempotency Keys:** Notebook entries and analytics events require client-provided idempotency keys to prevent duplicate creation on network retries.

## 6. Security

- **Server-Side Identity:** Endpoints extract user identity securely from `Authorization` headers. The backend completely distrusts client-provided user IDs.
- **Tenant Isolation:** Vector retrieval filters explicitly by the authenticated user's ID, guaranteeing 0 cross-tenant data leakage.
- **M4 Security:** The LLM is restricted from directly mutating the global knowledge graph or deleting documents. Mutations require explicit human confirmation via the UI.
- **Prompt Injection Boundaries:** Retrieved chunks are strictly wrapped in XML boundaries (`<retrieved_chunk>`) to prevent confusion.

# OpenRouter Text Generation Provider

**Bounded Context:** `packages/learning-content`
**Component:** `learning_content.providers.openrouter`

## Overview

The `OpenRouterTextGenerationProvider` is Kogniq's first concrete implementation of the `AbstractTextGenerationProvider`. It converts domain-agnostic prompts into generated text responses using OpenRouter's OpenAI-compatible API.

Its sole responsibility is orchestration of the underlying API client, prompt validation, and exception translation. It deliberately **does not** contain prompt templates, response parsing logic, business rules, or anything related to domain learning (like summaries or quizzes). Those responsibilities are strictly confined to the Learning Generators (e.g. `SummaryGenerator`).

## Architecture

The OpenRouter provider is cleanly isolated behind interfaces to prevent `openai` SDK leaking into the core application logic.

```mermaid
flowchart TD
    G[Learning Generator\n(e.g., SummaryGenerator)] -->|generate(prompt)| P(AbstractTextGenerationProvider)
    
    subgraph Provider Subsystem
        P --> O[OpenRouterTextGenerationProvider]
        O -->|prompt| C[LazyOpenRouterClient]
    end
    
    C -->|HTTP Request| OR[OpenRouter API]
    OR -->|JSON Response| C
    
    C -.->|Translate Exceptions| E[OpenRouterError]
    C -->|Extract Text| O
    
    O -->|string| G
```

## Key Design Decisions

### 1. Zero Business Logic
The provider's interface enforces `prompt: str -> text: str`. It is blind to whether it is generating a quiz or summarizing text. It only delegates text inference.

### 2. SDK Isolation & Lazy Loading
The `openai` SDK dependency is isolated entirely within `client.py`. It is loaded lazily on the first `generate()` call via `LazyOpenRouterClient` to avoid unnecessary initialization overhead on startup when generation is not required.

### 3. Capability Metadata (`TextGenerationProviderInfo`)
The provider exposes an immutable metadata object to downstream consumers, allowing them to adapt gracefully (e.g., fallback if streaming is unsupported or context window is exceeded).

### 4. Custom Exception Hierarchy
All errors originating from the `openai` SDK (e.g. `AuthenticationError`, `RateLimitError`) are mapped to internal domain exceptions (e.g. `OpenRouterAuthenticationError`, `OpenRouterRateLimitError`). This prevents upstream domain orchestrators from needing to handle SDK-specific exceptions, keeping our bounded contexts pure.

### 5. Future-Proof Generation Signature
The signature accepts optional keyword-only control overrides (`temperature`, `max_tokens`) so that different generators can exert granular control without needing provider-specific subclasses. It also provides a default sequential batch generation fallback `generate_batch`.

# Quiz Generator Architecture

The `QuizGenerator` is the fourth concrete learning generator for Kogniq, extending the structured JSON generation pattern established by the Flashcards generator. It natively produces deeply-validated, highly-structured multiple-choice questions (MCQs) while relying entirely on the `BaseLearningGenerator` for its orchestration.

## Architecture

```mermaid
graph TD
    A[GenerationContext] --> B[QuizPromptBuilder]
    B --> C[BaseLearningGenerator]
    C -->|Constructs Prompt| D[AbstractTextGenerationProvider]
    D -->|Returns Raw JSON| E[QuizParser]
    
    subgraph Validation Layer
        E --> V1[Defensive Markdown Stripping]
        V1 --> V2[JSON Parsing]
        V2 --> V3[Type & Schema Validation]
        V3 --> V4[Case-Insensitive Duplicate Checks]
        V4 --> V5[Correct Answer Strict Match]
        V5 --> V6[Enum Validations]
    end
    
    V6 --> F[QuizCollection]
    F -->|Serialized to| G[LearningContent.body]
```

## Features

1. **Immutable Options Model**: We utilize a `QuizOption` immutable object with UUIDs (or labels like A, B, C, D) to gracefully permit UI randomization later without losing answer correlation.
2. **Strict Validation**: The parser is highly defensive: checking exact bounds (4 unique options), non-empty fields, domain consistency (explanation != answer), and deduplication across questions.
3. **No Generator Logic Expansion**: Like previous generators, `LearningContent` handles all cross-cutting concerns (statistics, contexts, token budgets), proving the original `BaseLearningGenerator` framework is genuinely extensible.

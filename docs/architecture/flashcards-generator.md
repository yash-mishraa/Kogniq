# Flashcards Generator Architecture

The Flashcards Generator is the third concrete implementation of the `BaseLearningGenerator` orchestration framework, and the first to generate **structured JSON artifacts** rather than free-form Markdown.

It validates that the Base framework correctly supports rigorous JSON parsing, domain model validation, and structured output logic, all without introducing provider-specific orchestration logic.

## Separation of Concerns

The `FlashcardsGenerator` packages exactly two components:

1. **`FlashcardsPromptBuilder`**: Constructs deterministic prompts explicitly commanding the LLM to output a raw JSON array of question, answer, and difficulty fields.
2. **`FlashcardsParser`**:
   - Parses the JSON output and aggressively validates it against the schema.
   - Triggers domain validation through the `Flashcard` model (checking for empty fields, duplicated questions, etc.).
   - Serializes the valid `FlashcardCollection` into a canonical JSON string to populate the `body` of the resulting `LearningContent`.

## Inheritance Hierarchy

```mermaid
classDiagram
    class AbstractLearningGenerator {
        <<interface>>
    }

    class BaseLearningGenerator {
        <<abstract>>
    }

    class SummaryGenerator {
        +prompt_version "summary-v1"
    }

    class NotesGenerator {
        +prompt_version "notes-v1"
    }

    class FlashcardsGenerator {
        +prompt_version "flashcards-v1"
    }

    AbstractLearningGenerator <|-- BaseLearningGenerator
    BaseLearningGenerator <|-- SummaryGenerator
    BaseLearningGenerator <|-- NotesGenerator
    BaseLearningGenerator <|-- FlashcardsGenerator
```

## Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant BaseLearningGenerator
    participant FlashcardsPromptBuilder
    participant Provider
    participant FlashcardsParser
    participant FlashcardCollection
    
    Client->>BaseLearningGenerator: generate(chunks, graph)
    BaseLearningGenerator->>FlashcardsPromptBuilder: build(context)
    FlashcardsPromptBuilder-->>BaseLearningGenerator: prompt (str)
    
    BaseLearningGenerator->>Provider: generate(prompt)
    Provider-->>BaseLearningGenerator: raw_response (str/JSON)
    
    BaseLearningGenerator->>FlashcardsParser: parse(raw_response, context, metadata)
    FlashcardsParser->>FlashcardCollection: Validate and create
    FlashcardsParser-->>BaseLearningGenerator: LearningContent (JSON body)
    
    BaseLearningGenerator-->>Client: LearningContent
```

By storing the serialized `FlashcardCollection` string inside `LearningContent.body`, we avoid polluting the core domain boundary with generator-specific fields, allowing the artifact format to remain generic until a proper `LearningArtifact` abstraction is introduced.

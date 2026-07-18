# Learning Generation Framework

The Learning Generation Framework provides a robust, reusable orchestration layer for generating AI pedagogical artifacts (Summaries, Notes, Flashcards, Quizzes, Study Guides). By centralizing orchestration, it eliminates duplication and strictly enforces separation of concerns across all generation tasks.

## Architectural Separation of Concerns

Generation is split into four distinct, immutable responsibilities:

1. **Generator (`BaseLearningGenerator`)**: Owns the orchestration. It invokes the Prompt Builder, calls the Provider, handles timing, handles failures, and executes the Parser. It does not contain any artifact-specific logic.
2. **Prompt Builder (`AbstractPromptBuilder`)**: Owns deterministic prompt construction. It receives a `GenerationContext` (Chunks and Knowledge Graph) and formats it.
3. **Provider (`AbstractTextGenerationProvider`)**: Owns stateless LLM communication. It only knows about strings and tokens. It does not know about learning content.
4. **Parser (`AbstractContentParser`)**: Owns parsing and validating the raw LLM string into a structured `LearningContent` entity. It receives `GenerationMetadata` but never interacts directly with the provider.

## Inheritance Hierarchy

All future pedagogical generators in Kogniq inherit from this unified base structure.

```mermaid
classDiagram
    class AbstractLearningGenerator {
        <<interface>>
        +info() GeneratorInfo
        +generate(chunks, graph) LearningContent
        +generate_batch(collections, graphs) LearningContentCollection
    }

    class BaseLearningGenerator {
        <<abstract>>
        +prompt_builder AbstractPromptBuilder
        +parser AbstractContentParser
        +prompt_version str
        +before_generate(context)
        +after_generate(content)
        +generate(chunks, graph)
        +generate_batch(collections, graphs)
    }

    class SummaryGenerator {
        +prompt_builder SummaryPromptBuilder
        +parser SummaryParser
        +prompt_version "summary-v1"
        +info()
    }

    class NotesGenerator {
        +prompt_builder NotesPromptBuilder
        +parser NotesParser
        +prompt_version "notes-v1"
        +info()
    }

    class FlashcardGenerator {
        +prompt_builder FlashcardPromptBuilder
        +parser FlashcardParser
        +prompt_version "flashcards-v1"
        +info()
    }
    
    class QuizGenerator {
        +prompt_builder QuizPromptBuilder
        +parser QuizParser
        +prompt_version "quiz-v1"
        +info()
    }
    
    class StudyGuideGenerator {
        +prompt_builder StudyGuidePromptBuilder
        +parser StudyGuideParser
        +prompt_version "study-guide-v1"
        +info()
    }

    AbstractLearningGenerator <|-- BaseLearningGenerator
    BaseLearningGenerator <|-- SummaryGenerator
    BaseLearningGenerator <|-- NotesGenerator
    BaseLearningGenerator <|-- FlashcardGenerator
    BaseLearningGenerator <|-- QuizGenerator
    BaseLearningGenerator <|-- StudyGuideGenerator
```

## Data Flow Orchestration

The `BaseLearningGenerator` strictly manages the flow of data using immutable context models.

```mermaid
sequenceDiagram
    participant Client
    participant BaseLearningGenerator
    participant PromptBuilder
    participant Provider
    participant Parser

    Client->>BaseLearningGenerator: generate(chunks, graph)
    BaseLearningGenerator->>BaseLearningGenerator: before_generate(context)
    BaseLearningGenerator->>PromptBuilder: build(context)
    PromptBuilder-->>BaseLearningGenerator: prompt (str)
    
    BaseLearningGenerator->>Provider: generate(prompt)
    Note over BaseLearningGenerator,Provider: Execution timing captured
    Provider-->>BaseLearningGenerator: raw_response (str)
    
    BaseLearningGenerator->>BaseLearningGenerator: create GenerationMetadata
    
    BaseLearningGenerator->>Parser: parse(raw_response, context, metadata)
    Parser-->>BaseLearningGenerator: LearningContent
    
    BaseLearningGenerator->>BaseLearningGenerator: after_generate(content)
    BaseLearningGenerator-->>Client: LearningContent
```

By adhering to this framework, we ensure that adding a new generation feature requires *only* a new prompt string builder and a new parser. The overarching architecture handles the rest.

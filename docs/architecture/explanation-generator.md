# Explanation Generator Architecture

The `ExplanationGenerator` is the fifth concrete learning generator for Kogniq, extending the markdown generation pattern but with a distinct pedagogical objective: teaching rather than summarizing.

## Architecture

```mermaid
graph TD
    A[GenerationContext] --> B[ExplanationPromptBuilder]
    B -->|Instructs Analogies & Depth| C[BaseLearningGenerator]
    C -->|Constructs Prompt| D[AbstractTextGenerationProvider]
    D -->|Returns Pedagogical Markdown| E[ExplanationParser]
    
    subgraph Validation Layer
        E --> V1[Check for Empty/Placeholder]
        V1 --> V2[Verify Minimum Length]
        V2 --> V3[Ensure Required Headings]
        V3 --> V4[Extract Dynamic Title]
    end
    
    V4 --> F[Calculate Statistics including heading_count]
    F --> G[LearningContent.body]
```

## Features

1. **Pedagogical Focus**: Unlike `SummaryGenerator` which compresses information, `ExplanationGenerator` uses intuitive analogies, concrete examples, and common misconceptions to build understanding.
2. **Strict Heading Validation**: The parser is highly defensive, ensuring that the model output contains specific pedagogical structures (e.g., `## Intuition`, `## Common Mistakes`, `## Why It Matters`).
3. **Foundation for Study Guides**: This generator produces the "meat" of the educational content that will soon be composed together with quizzes and flashcards into a unified `StudyGuideGenerator`.

# Content Intelligence Foundation

## Purpose
The Content domain manages the lifecycle of raw learning resources (e.g., PDFs, Markdown, Videos) as they are validated, parsed, and semantically chunked into usable representations for AI processing. It operates as a pure Python orchestration layer, completely decoupled from specific AI models, OCR tools, or persistence layers.

## Entity Relationships
```mermaid
erDiagram
    LearningResource ||--o{ ResourceSection : "contains"
    ResourceSection ||--o{ ResourceChunk : "contains"
    LearningResource ||--|| ResourceMetadata : "has"
    LearningResource ||--|| ContentStatistics : "has"
```

## Processing Pipeline Flow
```mermaid
graph TD
    A[Raw Resource] --> B[Validator]
    B --> C[Parser]
    C --> D[Metadata Extractor]
    D --> E[Section Extractor]
    E --> F[Chunk Generator]
    F --> G[Statistics Extractor]
    G --> H[ProcessingResult]
```

## Domain Event Flow
```mermaid
stateDiagram-v2
    [*] --> UPLOADED : ResourceUploaded
    UPLOADED --> VALIDATING
    VALIDATING --> VALIDATED : ResourceValidated(True)
    VALIDATING --> FAILED : ResourceValidated(False)
    VALIDATED --> PROCESSING : ResourceProcessingStarted
    PROCESSING --> PROCESSED : ResourceProcessingCompleted
    PROCESSING --> FAILED : ResourceProcessingFailed
    PROCESSED --> [*]
    FAILED --> [*]
```

## Package Dependencies
```mermaid
graph TD
    kogniq-content --> kogniq-shared
    kogniq-learning --> kogniq-shared
    kogniq-api --> kogniq-content
    kogniq-api --> kogniq-learning
    kogniq-api --> kogniq-shared
```

# Knowledge Workspace

The Knowledge Workspace is the primary environment where users explore semantic relationships between concepts extracted from their documents.

## Architectural Philosophy

- **Separate from Graph**: The `knowledgeEnvironment` operates purely as the user-facing semantic layer. Graph databases or structures are implementation details that may have their own independent interfaces (e.g., `graphEnvironment`).
- **Typography-First Design**: Concept importance is expressed through hierarchy (font size and weight) rather than decorative UI elements like colored bubbles, badges, or bounding boxes.
- **Intentional Layouts**: We explicitly avoid force-directed graph libraries (like D3 or physics simulations). Concepts are mapped using an editorial logic where positioning represents meaning rather than dynamic physics. Nodes preserve their spatial anchors when selected, preserving orientation.
- **Semantic Understanding**: Edges convey subtle understanding via dashed, faded strokes instead of glowing, active particles.

## Core Components

- **KnowledgeSurface**: The main layout primitive that anchors the environment.
- **KnowledgeMap**: The canvas that renders the concept layout and relationships.
- **KnowledgeNode**: The typography-first primitive for individual concepts.
- **KnowledgeRelationship**: The visual edge connector between concepts.
- **KnowledgeInspector**: A side panel displaying a concept's explanation, related concepts, and text evidence snippets without acting like a traditional "properties panel".
- **KnowledgeTrail**: A vertical history tracker that reinforces exploration over strict directory navigation.

## State Management

The workspace is managed by `KnowledgeContext`, which tracks:
- `graph`: The currently loaded `KnowledgeGraph` data structure (mocked during Phase C).
- `activeConceptId`: The selected concept.
- `trail`: An array representing the history of concept selections. Selecting a new concept appends to the trail. Selecting an existing concept truncates the trail down to that point, enabling fluid backtracking.

## Locus Integration

Within the Knowledge Environment, the Locus transitions to:
```
│ Explore connections...
```
This anticipates future semantic search capabilities, setting the expectation that users are navigating ideas rather than files.

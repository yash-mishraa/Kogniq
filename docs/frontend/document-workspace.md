# Document Workspace Foundation

This document defines the interaction principles and architecture of the Kogniq Documents Workspace, serving as the canonical baseline for how knowledge enters Kogniq.

## Architecture

The Documents Workspace acts as a self-contained environment integrated into the broader `WorkspaceEngine`. 

- **DocumentsEnvironment**: The root component. Connects to `WorkspaceEngineBody`.
- **DocumentsContext / State**: Manages local environment state (document list, active selection, mock imports).
- **DocumentSurface**: Layout primitive managing the spatial relationship between the collection and the reading surface.

## Component Principles

- **ReadingSurface**: The reading interface unfolds when a document is selected. Designed to mimic academic papers, prioritizing typography, margins, and readability. It is completely decoupled from the data type, allowing future usage for summaries, flashcards, etc.
- **DocumentCollection**: An editorial list of documents. Selection reorganizes the layout without reducing the list to a conventional sidebar widget. Unselected items gracefully compress or fade.
- **DocumentLifecycle**: Displays textual progress of the processing pipeline: `Imported → Processing → Chunking → Embedding → Extraction → Ready`. Replaces spinners or progress bars with calm, textual transitions.
- **DocumentMetadata**: Communicates knowledge properties (e.g., page count, reading time, chunk count, extracted concepts) rather than storage primitives (e.g., file sizes).
- **DocumentEmptyState**: Prioritizes importing knowledge. Replaces traditional drag-and-drop hero sections with a single `Locus` prompt: `│ Import knowledge...` that natively triggers a file picker on submission.

## Emotional Journey

- **Importing**: Typing to import feels like starting a conversation or a task, rather than filling a form.
- **Processing**: The user witnesses knowledge extraction in progress, reinforcing that Kogniq is building an understanding, not just storing a file.
- **Reading**: Selecting a document expands the view naturally, emphasizing reading and deep thinking over dashboard metrics.

## Future Extensions

Because the `ReadingSurface` and other primitives are abstracted, they serve as the foundation for the upcoming Study and Extraction environments. Any UI for extracting concepts or taking notes should align spatially and aesthetically with this Document Workspace layout.

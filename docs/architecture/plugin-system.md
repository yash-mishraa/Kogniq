# Content Plugin Architecture

## Purpose
The Content Plugin Registry decouples the orchestration pipeline from specific parsing and extraction implementations. By utilizing a registry pattern, Kogniq can dynamically support arbitrary content types (PDF, DOCX, Markdown, YouTube transcripts, etc.) without requiring modifications to the core `ContentProcessingPipeline`.

## Design Principles
- **Dependency Inversion:** The pipeline depends on `AbstractContentProcessor`, not concrete parsers like PyMuPDF or BeautifulSoup.
- **Open/Closed Principle:** The system is open for extension (by registering new processors) but closed for modification (the core orchestration remains unchanged).
- **Framework Independence:** The registry purely leverages standard Python capabilities (O(1) dictionary lookups) and completely rejects infrastructure leakage (no LangChain, LlamaIndex, or persistence dependencies).

## Future Plugin Loading
When concrete parsing functionality is implemented (e.g., in `packages/plugins/pdf` or via standard package entry points), these external modules will instantiate classes inheriting from `AbstractContentProcessor`. During application startup, these instances will be passed to `ProcessorRegistry.register()`, gracefully binding the implementation to the domain.

## Architecture

```mermaid
graph TD
    Pipeline[ContentProcessingPipeline] --> Registry[ProcessorRegistry]
    Registry --> Abstract[AbstractContentProcessor]
    Abstract <.. PDF[PDFProcessor : Future]
    Abstract <.. MD[MarkdownProcessor : Future]
    Abstract <.. YT[YouTubeProcessor : Future]
```

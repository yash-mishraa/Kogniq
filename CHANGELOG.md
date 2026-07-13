# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Developer Experience**: A unified `uv` workspace structure supporting multiple pure Python packages (`content`, `learning`, `education`, `shared`).
- **Developer Experience**: Comprehensive developer scripts under `dev/` to simulate complex pipelines without a frontend.
- **Shared Domain**: Generic base entity classes (`Entity`, `ValueObject`, `DomainEvent`).
- **Learning Domain**: Core DAG validation (`PrerequisiteValidator`) ensuring circular concept prerequisites are strictly forbidden.
- **Learning Domain**: `Subject`, `Concept`, and `LearningObjective` models.
- **Education Domain**: `Student`, `ProgressRecord`, `TutorSession`, and `Assessment` tracking models.
- **Content Domain**: `ProcessorRegistry` enforcing MIME type and extension uniqueness.
- **Content Domain**: `NormalizedDocument` structure (`Page`, `Block`, `Span`) preserving reading order and block atomicity.
- **Processors**: `TXTProcessor`, `MarkdownProcessor`, `PDFProcessor`, `HTMLProcessor`, and `DOCXProcessor`.
- **Chunk Engine**: `StructuralChunkStrategy` for splitting documents cleanly at `HEADING` boundaries.
- **Chunk Engine**: `FixedSizeChunkStrategy` as a fallback character-limited strategy that respects block atomicity.
- **Hybrid Engine**: `HybridChunkEngine` to dynamically orchestrate between structural and fixed chunking strategies.

# Learning Content Package (`packages/learning-content`)

## Purpose
The `learning-content` package is responsible for generating concrete pedagogical artifacts—such as Summaries, Flashcards, and Quizzes—using AI LLM providers and the structural data provided by chunk collections and knowledge graphs.

## Responsibilities

### What belongs here
- Immutable representations of pedagogical material (`LearningContent`).
- AI orchestrators that synthesize data into artifacts (`AbstractLearningGenerator`).
- Robust prompt builders and parsers ensuring strict output compliance.
- Abstract Text Generation Providers (`AbstractTextGenerationProvider`).

### What does NOT belong here
- Extracting raw text from files (that belongs in `content`).
- Vector similarity search (that belongs in `retrieval`).
- Defining base relationships (that belongs in `knowledge`).

## Public API
- `learning_content.content.LearningContent`: The canonical entity for generated artifacts.
- `learning_content.generators.base.AbstractLearningGenerator`: Core generation interface.
- `learning_content.providers.base.AbstractTextGenerationProvider`: Pure LLM interaction boundary.
- `learning_content.generators.summary.SummaryGenerator`: Concrete implementation for generating study summaries.

## Architecture
Follows a rigorous separation of concerns:
- **PromptBuilder**: Handles exact instruction formulation.
- **Provider**: Handles stateless LLM communication.
- **Parser**: Enforces strict output validation and mapping.
- **Generator**: Orchestrates the above three without mixing logic.

## Dependencies
- `shared`
- `content`
- `knowledge`

## Relationships
- Depended upon by: `pipeline` (in the future).

## Current Features
- Fully integrated `SummaryGenerator`.
- Decoupled `OpenRouterTextGenerationProvider`.
- Active rejection of LLM placeholder responses and comprehensive token estimation utilities.

## Planned Features
- `FlashcardGenerator`
- `QuizGenerator`
- `NotesGenerator`
- `StudyGuideGenerator`

## Examples
- `uv run python dev/demo_learning_content.py`
- `uv run python dev/demo_openrouter_provider.py`
- `uv run python dev/demo_summary_generator.py`
- `uv run python dev/demo_summary_openrouter.py`

## Quality Gates
- **Tests**: `uv run python -m pytest packages/learning-content/tests/`
- **MyPy**: `uv run python -m mypy packages/learning-content/`
- **Ruff**: `uv run ruff check packages/learning-content/`

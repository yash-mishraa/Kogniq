# Frontend Architecture

**Status:** Implemented

## Purpose
To provide the interactive user interface through which users interact with Kogniq.

## Implemented Responsibilities
- **React Dashboard**: Modern web architecture hosted in `apps/web`.
- **Workspace Engine**: Contextual workspaces parsing and displaying `Notebook`, `Flashcards`, `Knowledge Graph`, `Analytics`, and `Studio` views.
- **Intelligent Learning Loop**: Interactive AI Tutor integrations offering "Explain my mistake" dialogs and deterministic next-action recommendations.
- **Content Upload**: Drag-and-drop document ingestion linked to async background jobs.

## Relationship to Existing Packages
The frontend communicates exclusively with the FastAPI layer in `apps/api`. It enforces type-safe API consumption and isolates UI state from backend domain logic.

---
*Return to [Architecture Index](README.md).*

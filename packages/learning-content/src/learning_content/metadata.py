from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class LearningContentMetadata:
    """Metadata about generated learning content and its source."""

    provider: str
    model: str
    model_version: str
    generation_version: str
    language: str
    educational_level: str
    subject: str
    syllabus: str
    prompt_version: str
    tags: tuple[str, ...]

    # Optional fields for future template versioning
    template_version: str | None = None
    generation_id: str | None = None

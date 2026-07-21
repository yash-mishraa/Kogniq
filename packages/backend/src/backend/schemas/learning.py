from typing import Any

from pydantic import BaseModel, Field


class LearningGenerationRequest(BaseModel):
    """
    API Request Schema for learning generation.
    """

    document_id: str = Field(..., description="Unique ID of the document to generate content for")
    generator: str = Field(
        ..., description="Type of generator to run (e.g. summary, notes, study_guide)"
    )
    options: dict[str, Any] = Field(
        default_factory=dict, description="Configuration options for generation"
    )


class LearningGenerationResponse(BaseModel):
    """
    API Response Schema for learning generation.
    """

    status: str = Field(..., description="Status of the generation")
    document_id: str = Field(..., description="Unique ID of the source document")
    generator: str = Field(..., description="The generator type used")
    title: str = Field(..., description="Title of the generated content")
    content_type: str = Field(..., description="MIME type or canonical content type string")
    generated_content: str = Field(
        ..., description="The generated educational content (usually Markdown or JSON string)"
    )
    metadata: dict[str, Any] = Field(..., description="Non-sensitive generation metadata")
    statistics: dict[str, Any] = Field(..., description="Generation statistics (word count, etc)")
    processing_time_ms: float = Field(
        ..., description="Time taken to generate the content in milliseconds"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Non-fatal warnings during generation"
    )

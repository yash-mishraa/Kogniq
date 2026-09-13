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


class LearningMaterialItem(BaseModel):
    """
    Individual generated learning material.
    """

    title: str = Field(..., description="Title of the material")
    body: Any = Field(..., description="Content of the material, can be string or parsed JSON")


class LearningMaterialsResponse(BaseModel):
    """
    API Response Schema for fetching all generated learning materials for a document.
    """

    status: str = Field(
        ..., description="Status of the generation pipeline ('processing' or 'completed')"
    )
    materials: dict[str, LearningMaterialItem] | None = Field(
        ..., description="Dictionary mapping generator types (e.g. 'notes') to the material content"
    )

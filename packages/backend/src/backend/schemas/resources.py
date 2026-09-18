from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResourceSectionResponse(BaseModel):
    id: str
    resource_id: str
    title: str
    order: int
    page_start: int | None = None
    page_end: int | None = None
    char_start: int | None = None
    char_end: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ResourceChunkResponse(BaseModel):
    id: str
    resource_id: str
    section_id: str | None = None
    text: str | None = None
    order: int
    checksum: str | None = None
    token_estimate: int | None = None
    metadata: dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class LearningResourceResponse(BaseModel):
    id: str
    title: str
    resource_type: str
    source: str
    checksum: str | None = None
    language: str = "en"
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceStatisticsResponse(BaseModel):
    section_count: int
    chunk_count: int
    total_tokens: int

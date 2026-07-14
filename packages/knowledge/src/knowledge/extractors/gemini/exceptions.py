from knowledge.extractors.exceptions import KnowledgeExtractionError


class GeminiExtractionError(KnowledgeExtractionError):
    """Base exception for Gemini extraction failures."""


class GeminiAPIError(GeminiExtractionError):
    """Raised when the Gemini API returns an error or fails to connect."""


class GeminiParsingError(GeminiExtractionError):
    """Raised when the Gemini response cannot be parsed as valid JSON."""

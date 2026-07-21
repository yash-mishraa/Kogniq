import time
from datetime import UTC, datetime

from content.chunking import ChunkCollection
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.extractors.gemini.exceptions import GeminiAPIError
from knowledge.extractors.gemini.parser import GeminiResponseParser
from knowledge.extractors.gemini.prompt_builder import GeminiPromptBuilder
from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from knowledge.extractors.provider_info import KnowledgeExtractorInfo

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None  # type: ignore


class GeminiKnowledgeExtractor(AbstractKnowledgeExtractor):
    """Concrete implementation of a Knowledge Extractor using Google Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.0,
        max_output_tokens: int = 8192,
    ) -> None:
        if genai is None:
            raise ImportError("google-genai is not installed. Please install it to use Gemini.")

        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self._client: genai.Client | None = None

        self._info = KnowledgeExtractorInfo(
            extractor_id=f"gemini_{model_name.replace('-', '_')}",
            extractor_name="Google Gemini Extractor",
            version="1.0",
            provider="Google",
            supports_batch_processing=True,
            supports_streaming=True,
            maximum_chunks_per_request=100,
            maximum_tokens=2_000_000,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )

        self._prompt_builder = GeminiPromptBuilder()
        self._parser = GeminiResponseParser()

    @property
    def client(self) -> "genai.Client":
        """Lazy initialization of the Gemini client."""
        if self._client is None:
            # If api_key is None, it reads from GEMINI_API_KEY env var automatically
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @property
    def info(self) -> KnowledgeExtractorInfo:
        return self._info

    def extract(self, chunks: ChunkCollection) -> KnowledgeExtractionResult:
        """Extract a KnowledgeGraph from chunks using Gemini."""
        start_time = time.perf_counter()

        prompt = self._prompt_builder.build(chunks)
        document_id = chunks.document_id if hasattr(chunks, "document_id") else "unknown"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
        except Exception as e:
            raise GeminiAPIError(f"Gemini API request failed: {e}") from e

        if not response.text:
            raise GeminiAPIError("Received empty response from Gemini")

        graph = self._parser.parse(response.text, document_id=document_id)

        end_time = time.perf_counter()

        return KnowledgeExtractionResult(
            graph=graph,
            extractor_id=self.info.extractor_id,
            extractor_name=self.info.extractor_name,
            version=self.info.version,
            processing_time_ms=(end_time - start_time) * 1000,
            processed_chunks=chunks.total_chunks,
            created_at=datetime.now(UTC),
        )

    def extract_batch(
        self, collections: tuple[ChunkCollection, ...]
    ) -> tuple[KnowledgeExtractionResult, ...]:
        """Extract sequentially. For a real production system, this would use asyncio."""
        return tuple(self.extract(c) for c in collections)

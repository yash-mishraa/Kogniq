import asyncio
import logging
import random
import time
from datetime import UTC, datetime
from typing import Any

from content.chunking import ChunkCollection
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.extractors.gemini.exceptions import GeminiAPIError
from knowledge.extractors.gemini.parser import GeminiResponseParser
from knowledge.extractors.gemini.prompt_builder import GeminiPromptBuilder
from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from knowledge.extractors.provider_info import KnowledgeExtractorInfo

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import errors, types
except ImportError:
    genai = None  # type: ignore
    errors = None  # type: ignore


class GeminiKnowledgeExtractor(AbstractKnowledgeExtractor):
    """Concrete implementation of a Knowledge Extractor using Google Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-3.1-flash-lite",
        temperature: float = 0.0,
        max_output_tokens: int = 8192,
        sleep_fn: Any = None,
    ) -> None:
        if genai is None:
            raise ImportError("google-genai is not installed. Please install it to use Gemini.")

        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self._sleep_fn = sleep_fn or asyncio.sleep
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

    def _is_transient(self, e: Exception) -> bool:
        if isinstance(e, (asyncio.TimeoutError, TimeoutError)):
            return True
        code = getattr(e, "code", getattr(e, "status_code", None))
        if code is not None:
            if code in (429, 500, 502, 503, 504):
                return True
            if code in (400, 401, 403, 404):
                return False
        if errors is not None and isinstance(e, errors.ServerError):
            return True
        if errors is not None and isinstance(e, errors.ClientError):
            return code == 429
        mro_names = {c.__name__ for c in e.__class__.__mro__}
        if "ServerError" in mro_names:
            return True
        err_msg = str(e).lower()
        if "timeout" in err_msg:
            return True
        if any(auth_kw in err_msg for auth_kw in ("api_key_invalid", "unauthorized", "forbidden", "permission denied")):
            return False
        if any(term in err_msg for term in ("503", "unavailable", "overloaded", "429", "rate limit", "quota")):
            return True
        return False

    async def extract(self, chunks: ChunkCollection) -> KnowledgeExtractionResult:
        """Extract a KnowledgeGraph from chunks using Gemini with transient error retries."""
        start_time = time.perf_counter()

        prompt = self._prompt_builder.build(chunks)
        document_id = chunks.document_id if hasattr(chunks, "document_id") else "unknown"

        max_attempts = 3
        response = None
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=self.temperature,
                        max_output_tokens=self.max_output_tokens,
                        response_mime_type="application/json",
                    ),
                )
                break
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if self._is_transient(e) and attempt < max_attempts:
                    delay = (0.5 * (2 ** (attempt - 1))) + random.uniform(0.1, 0.3)
                    logger.warning(
                        "Gemini knowledge extraction transient failure (attempt %d/%d): %s. Retrying in %.2fs",
                        attempt,
                        max_attempts,
                        e,
                        delay,
                    )
                    await self._sleep_fn(delay)
                    continue
                raise GeminiAPIError(f"Gemini API request failed: {e}") from e

        if not response or not response.text:
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

    async def extract_batch(
        self, collections: tuple[ChunkCollection, ...]
    ) -> tuple[KnowledgeExtractionResult, ...]:
        """Extract sequentially. For a real production system, this would use asyncio."""
        return tuple([await self.extract(c) for c in collections])

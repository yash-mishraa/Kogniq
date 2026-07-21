import os
import time
from datetime import UTC, datetime

from openai import OpenAI

from content.chunking import ChunkCollection
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from knowledge.extractors.openrouter.parser import GeminiResponseParser
from knowledge.extractors.openrouter.prompt_builder import GeminiPromptBuilder
from knowledge.extractors.provider_info import KnowledgeExtractorInfo


class OpenRouterKnowledgeExtractor(AbstractKnowledgeExtractor):
    """Concrete implementation of a Knowledge Extractor using OpenRouter."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "google/gemma-4-31b-it:free",
        temperature: float = 0.0,
        max_output_tokens: int = 8192,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

        self._info = KnowledgeExtractorInfo(
            extractor_id=f"openrouter_{model_name.replace('/', '_').replace(':', '_')}",
            extractor_name="OpenRouter Extractor",
            version="1.0",
            provider="OpenRouter",
            supports_batch_processing=True,
            supports_streaming=True,
            maximum_chunks_per_request=100,
            maximum_tokens=100_000,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )

        self._prompt_builder = GeminiPromptBuilder()
        self._parser = GeminiResponseParser()

    @property
    def info(self) -> KnowledgeExtractorInfo:
        return self._info

    def extract(self, chunks: ChunkCollection) -> KnowledgeExtractionResult:
        """Extract a KnowledgeGraph from chunks using OpenRouter."""
        start_time = time.perf_counter()

        prompt = self._prompt_builder.build(chunks)
        document_id = chunks.document_id if hasattr(chunks, "document_id") else "unknown"

        models_to_try = [
            self.model_name,
            "meta-llama/llama-3.3-70b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "google/gemma-4-31b-it:free",
            "google/gemma-4-26b-a4b-it:free",
        ]

        response_text = None
        last_error = None

        for model in models_to_try:
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_output_tokens,
                    response_format={"type": "json_object"},
                    extra_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Kogniq",
                    },
                )
                response_text = response.choices[0].message.content
                if response_text:
                    break
            except Exception as e:
                last_error = e
                continue

        if not response_text:
            raise RuntimeError(f"All OpenRouter free models failed. Last error: {last_error}")

        if not response_text:
            raise RuntimeError("Received empty response from OpenRouter")

        graph = self._parser.parse(response_text, document_id=document_id)

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

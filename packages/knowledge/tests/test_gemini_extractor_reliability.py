import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

from content.chunking import ChunkCollection
from knowledge.extractors.gemini.exceptions import GeminiAPIError
from knowledge.extractors.gemini.extractor import GeminiKnowledgeExtractor


def make_dummy_chunks() -> ChunkCollection:
    chunk1 = MagicMock(id="chk-1", text="Transformers use self-attention mechanism.")
    chunk_coll = ChunkCollection(chunks=(chunk1,))
    return chunk_coll


@pytest.mark.asyncio
async def test_gemini_extractor_transient_failure_then_success() -> None:
    """Verify that a transient 503 error is retried and succeeds on attempt 2."""
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    extractor = GeminiKnowledgeExtractor(api_key="fake-key", sleep_fn=fake_sleep)

    mock_client = MagicMock()
    success_resp = MagicMock()
    success_resp.text = '{"concepts": [{"id": "c1", "title": "Self-Attention"}], "relationships": []}'

    transient_error = Exception("503 Service Unavailable: overloaded")
    setattr(transient_error, "code", 503)

    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=[transient_error, success_resp]
    )
    extractor._client = mock_client

    result = await extractor.extract(make_dummy_chunks())

    assert len(result.graph.concepts) == 1
    assert result.graph.concepts[0].name == "Self-Attention"
    assert mock_client.aio.models.generate_content.call_count == 2
    assert len(sleep_calls) == 1


@pytest.mark.asyncio
async def test_gemini_extractor_retry_exhaustion() -> None:
    """Verify that after 3 consecutive transient errors, GeminiAPIError is raised."""
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    extractor = GeminiKnowledgeExtractor(api_key="fake-key", sleep_fn=fake_sleep)

    mock_client = MagicMock()
    transient_error = Exception("429 Resource Exhausted: rate limit exceeded")
    setattr(transient_error, "code", 429)

    mock_client.aio.models.generate_content = AsyncMock(side_effect=transient_error)
    extractor._client = mock_client

    with pytest.raises(GeminiAPIError) as exc_info:
        await extractor.extract(make_dummy_chunks())

    assert "rate limit exceeded" in str(exc_info.value)
    assert mock_client.aio.models.generate_content.call_count == 3
    assert len(sleep_calls) == 2


@pytest.mark.asyncio
async def test_gemini_extractor_permanent_auth_failure_no_retry() -> None:
    """Verify that permanent auth failures (401) fail immediately without retrying."""
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    extractor = GeminiKnowledgeExtractor(api_key="invalid-key", sleep_fn=fake_sleep)

    mock_client = MagicMock()
    auth_error = Exception("401 API_KEY_INVALID: User not authorized")
    setattr(auth_error, "code", 401)

    mock_client.aio.models.generate_content = AsyncMock(side_effect=auth_error)
    extractor._client = mock_client

    with pytest.raises(GeminiAPIError) as exc_info:
        await extractor.extract(make_dummy_chunks())

    assert "401" in str(exc_info.value)
    # Must fail on the very first attempt without burning retries
    assert mock_client.aio.models.generate_content.call_count == 1
    assert len(sleep_calls) == 0


@pytest.mark.asyncio
async def test_gemini_extractor_timeout_behavior() -> None:
    """Verify that TimeoutError is classified as transient and retried."""
    sleep_calls: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    extractor = GeminiKnowledgeExtractor(api_key="fake-key", sleep_fn=fake_sleep)

    mock_client = MagicMock()
    success_resp = MagicMock()
    success_resp.text = '{"concepts": [{"id": "c1", "title": "BERT"}], "relationships": []}'

    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=[asyncio.TimeoutError("Client request timed out"), success_resp]
    )
    extractor._client = mock_client

    result = await extractor.extract(make_dummy_chunks())

    assert len(result.graph.concepts) == 1
    assert result.graph.concepts[0].name == "BERT"
    assert mock_client.aio.models.generate_content.call_count == 2
    assert len(sleep_calls) == 1


@pytest.mark.asyncio
async def test_gemini_extractor_cancellation_propagation() -> None:
    """Verify that asyncio.CancelledError is directly propagated without being masked."""
    extractor = GeminiKnowledgeExtractor(api_key="fake-key")

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=asyncio.CancelledError("Task was cancelled")
    )
    extractor._client = mock_client

    with pytest.raises(asyncio.CancelledError):
        await extractor.extract(make_dummy_chunks())

    assert mock_client.aio.models.generate_content.call_count == 1

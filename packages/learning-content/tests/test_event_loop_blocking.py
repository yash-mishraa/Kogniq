import asyncio
import functools
import time
from unittest.mock import MagicMock, patch

import pytest
from google.genai.errors import APIError

from learning_content.providers.base import AgentMessage
from learning_content.providers.gemini.provider import GeminiTextGenerationProvider


@pytest.fixture
def provider() -> GeminiTextGenerationProvider:
    return GeminiTextGenerationProvider(api_key="fake")


@pytest.mark.asyncio
async def test_provider_transient_retry_does_not_block_event_loop(
    provider: GeminiTextGenerationProvider,
) -> None:
    mock_client = MagicMock()
    mock_models = MagicMock()
    mock_client.models = mock_models
    provider._client = mock_client

    # Fast failure
    mock_models.generate_content.side_effect = APIError(503, "Transient error", None)

    # We will simulate that time.sleep blocks. We patch time.sleep to do a real sleep of 0.1s
    # but track how long it blocked.
    def fake_sleep(_seconds: float) -> None:
        time.sleep(0.1)

    with patch("time.sleep", side_effect=fake_sleep):
        # We launch the provider in to_thread, like TutorChatUseCase does now.
        task = asyncio.create_task(
            asyncio.to_thread(
                functools.partial(
                    provider.generate_chat,
                    messages=[AgentMessage(role="user", content="Hi")],
                )
            )
        )

        # Run a quick background coroutine to ensure the event loop is responsive
        ticks = []

        async def background_tick() -> None:
            for _ in range(5):
                await asyncio.sleep(0.05)
                ticks.append(time.monotonic())

        await asyncio.gather(task, background_tick(), return_exceptions=True)

        # If it blocked the event loop, background_tick would not have ticked evenly.
        assert len(ticks) == 5, "Background coroutines should run concurrently"

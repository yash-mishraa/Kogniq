import logging
from typing import Any

from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    AgentMessage,
    TextGenerationProviderInfo,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


class MultiProviderRouter(AbstractTextGenerationProvider):
    """
    Intelligent provider router implementing bounded fallback between primary and secondary providers.
    Prevents single-provider outage from incapacitating generation.
    """

    def __init__(
        self,
        primary: AbstractTextGenerationProvider,
        fallback: AbstractTextGenerationProvider | None = None,
        *,
        fallback_enabled: bool = True,
    ) -> None:
        self.primary = primary
        self.fallback = fallback
        self.fallback_enabled = fallback_enabled
        self._last_used_provider = primary.info.provider_id

    @property
    def info(self) -> TextGenerationProviderInfo:
        return self.primary.info

    @property
    def last_used_provider_id(self) -> str:
        return self._last_used_provider

    def health(self) -> dict[str, Any]:
        """Aggregate health across configured providers."""
        primary_health = self.primary.health() if hasattr(self.primary, "health") else {"status": "unknown"}
        fallback_health = (
            self.fallback.health() if self.fallback and hasattr(self.fallback, "health") else None
        )
        return {
            "active_provider": self.primary.info.provider_id,
            "fallback_enabled": self.fallback_enabled and self.fallback is not None,
            "primary": primary_health,
            "fallback": fallback_health,
        }

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        try:
            self._last_used_provider = self.primary.info.provider_id
            return self.primary.generate(prompt, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            if not self.fallback_enabled or self.fallback is None:
                raise
            logger.warning(
                f"Primary provider '{self.primary.info.provider_id}' failed: {e}. "
                f"Attempting fallback to '{self.fallback.info.provider_id}'."
            )
            self._last_used_provider = self.fallback.info.provider_id
            return self.fallback.generate(prompt, temperature=temperature, max_tokens=max_tokens)

    def generate_chat(
        self,
        messages: list[AgentMessage],
        tools: list[ToolDefinition] | None = None,
        system_instruction: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AgentMessage:
        try:
            self._last_used_provider = self.primary.info.provider_id
            return self.primary.generate_chat(
                messages,
                tools=tools,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            if not self.fallback_enabled or self.fallback is None:
                raise
            logger.warning(
                f"Primary provider '{self.primary.info.provider_id}' chat failed: {e}. "
                f"Attempting fallback to '{self.fallback.info.provider_id}'."
            )
            self._last_used_provider = self.fallback.info.provider_id
            return self.fallback.generate_chat(
                messages,
                tools=tools,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    def generate_json(
        self,
        prompt: str,
        *,
        schema: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        try:
            self._last_used_provider = self.primary.info.provider_id
            return self.primary.generate_json(
                prompt,
                schema=schema,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            if not self.fallback_enabled or self.fallback is None:
                raise
            logger.warning(
                f"Primary provider '{self.primary.info.provider_id}' json failed: {e}. "
                f"Attempting fallback to '{self.fallback.info.provider_id}'."
            )
            self._last_used_provider = self.fallback.info.provider_id
            return self.fallback.generate_json(
                prompt,
                schema=schema,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )

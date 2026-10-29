import json
import logging
import os
from typing import Any

import httpx

from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    AgentMessage,
    ProviderUsage,
    TextGenerationProviderInfo,
    ToolCall,
    ToolDefinition,
)

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_URL = "http://localhost:11434"
DEFAULT_LOCAL_MODEL = "llama3.2:3b"


class LocalTextGenerationProvider(AbstractTextGenerationProvider):
    """
    Provider-neutral local inference adapter supporting Ollama and OpenAI-compatible runtimes.
    Does not require any cloud credentials or API keys.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (base_url or os.environ.get("LOCAL_LLM_URL") or DEFAULT_LOCAL_URL).rstrip("/")
        self.model_name = model_name or os.environ.get("LOCAL_LLM_MODEL") or DEFAULT_LOCAL_MODEL
        self.timeout = timeout
        self._info = TextGenerationProviderInfo(
            provider_id="local",
            provider_name="Local Open-Source (Ollama / LocalAI)",
            default_model=self.model_name,
            model_version="local-1.0",
            context_window=128_000,
            supports_streaming=True,
            supports_json=True,
            supports_images=False,
            supports_tools=True,
        )

    @property
    def info(self) -> TextGenerationProviderInfo:
        return self._info

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=self.timeout)

    def _unreachable_message(self, err: Exception) -> str:
        return (
            f"Local inference server is not reachable at {self.base_url}. "
            "To use free local generation without a cloud API key:\n"
            "  1. Install Ollama: https://ollama.ai\n"
            f"  2. Pull the model: ollama run {self.model_name}\n"
            f"Original error: {err}"
        )

    def health(self) -> dict[str, Any]:
        """Check if local inference server is up and whether target model exists."""
        try:
            with self._client() as client:
                # Try Ollama native tags endpoint
                resp = client.get(f"{self.base_url}/api/tags", timeout=3.0)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    model_found = any(self.model_name in m or m in self.model_name for m in models)
                    return {
                        "provider_id": "local",
                        "provider_name": "Local Open-Source",
                        "status": "healthy" if model_found else "model_missing",
                        "url": self.base_url,
                        "model": self.model_name,
                        "model_installed": model_found,
                        "installed_models": models,
                        "instructions": None if model_found else f"Run: ollama pull {self.model_name}",
                    }
        except Exception:
            pass

        try:
            # Try OpenAI-compatible /v1/models endpoint
            with self._client() as client:
                resp = client.get(f"{self.base_url}/v1/models", timeout=3.0)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id", "") for m in data.get("data", [])]
                    return {
                        "provider_id": "local",
                        "provider_name": "Local OpenAI-Compatible",
                        "status": "healthy",
                        "url": self.base_url,
                        "model": self.model_name,
                        "installed_models": models,
                    }
        except Exception as e:
            return {
                "provider_id": "local",
                "provider_name": "Local Open-Source",
                "status": "unreachable",
                "url": self.base_url,
                "model": self.model_name,
                "error": str(e),
                "setup_instructions": (
                    f"Start Ollama at {self.base_url} and run: ollama run {self.model_name}"
                ),
            }

        return {
            "provider_id": "local",
            "provider_name": "Local Open-Source",
            "status": "unreachable",
            "url": self.base_url,
            "model": self.model_name,
        }

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate text via Ollama /api/generate or /v1/completions."""
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if options:
            payload["options"] = options

        try:
            with self._client() as client:
                # 1. Try Ollama native endpoint
                resp = client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    return resp.json().get("response", "").strip()

                # 2. Try OpenAI compatible chat fallback
                resp_openai = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": temperature or 0.7,
                        "max_tokens": max_tokens or 1000,
                    },
                )
                if resp_openai.status_code == 200:
                    choices = resp_openai.json().get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()

                raise RuntimeError(
                    f"Local provider returned HTTP {resp.status_code}: {resp.text}"
                )
        except httpx.ConnectError as e:
            raise RuntimeError(self._unreachable_message(e)) from e
        except Exception as e:
            raise RuntimeError(f"Local generation failed: {e}") from e

    def generate_chat(
        self,
        messages: list[AgentMessage],
        tools: list[ToolDefinition] | None = None,
        system_instruction: str | None = None,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AgentMessage:
        """Generate chat response via Ollama /api/chat or OpenAI-compatible endpoint."""
        formatted_messages: list[dict[str, Any]] = []
        if system_instruction:
            formatted_messages.append({"role": "system", "content": system_instruction})

        for m in messages:
            formatted_messages.append({"role": m.role, "content": m.content})

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": False,
        }
        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if options:
            payload["options"] = options

        try:
            with self._client() as client:
                # 1. Try Ollama /api/chat
                resp = client.post(f"{self.base_url}/api/chat", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    msg = data.get("message", {})
                    content = msg.get("content", "").strip()

                    usage = None
                    if "prompt_eval_count" in data or "eval_count" in data:
                        prompt_tokens = data.get("prompt_eval_count", 0)
                        completion_tokens = data.get("eval_count", 0)
                        usage = ProviderUsage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=prompt_tokens + completion_tokens,
                        )

                    return AgentMessage(role="assistant", content=content, usage=usage)

                # 2. Try OpenAI-compatible /v1/chat/completions
                openai_payload = {
                    "model": self.model_name,
                    "messages": formatted_messages,
                    "temperature": temperature or 0.7,
                }
                if max_tokens:
                    openai_payload["max_tokens"] = max_tokens
                resp_openai = client.post(f"{self.base_url}/v1/chat/completions", json=openai_payload)
                if resp_openai.status_code == 200:
                    data = resp_openai.json()
                    choices = data.get("choices", [])
                    content = choices[0].get("message", {}).get("content", "").strip() if choices else ""
                    return AgentMessage(role="assistant", content=content)

                raise RuntimeError(f"Local provider error HTTP {resp.status_code}: {resp.text}")
        except httpx.ConnectError as e:
            raise RuntimeError(self._unreachable_message(e)) from e
        except Exception as e:
            raise RuntimeError(f"Local generation failed: {e}") from e

    def generate_json(
        self,
        prompt: str,
        *,
        schema: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON via Ollama format='json' or prompt coercion."""
        formatted_messages: list[dict[str, Any]] = []
        sys = (system_instruction or "") + "\nYou MUST respond with valid JSON only. Do not include markdown code fences or conversational text."
        formatted_messages.append({"role": "system", "content": sys.strip()})
        formatted_messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": formatted_messages,
            "format": "json",
            "stream": False,
        }
        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        try:
            with self._client() as client:
                resp = client.post(f"{self.base_url}/api/chat", json=payload)
                if resp.status_code == 200:
                    content = resp.json().get("message", {}).get("content", "")
                    return json.loads(content)
        except httpx.ConnectError as e:
            raise RuntimeError(self._unreachable_message(e)) from e
        except Exception:
            pass

        # Fallback to standard generate
        text = self.generate(f"{prompt}\nReturn strictly valid JSON.", temperature=temperature, max_tokens=max_tokens)
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())

import json
import logging
from typing import AsyncGenerator, List, Optional
import httpx
from backend.app.config import get_settings
from backend.app.core.exceptions import (
    AuthenticationException,
    LLMTimeoutException,
    ModelNotFoundException,
    NetworkFailureException,
    ProviderUnavailableException,
    RateLimitException,
)
from backend.app.schemas.llm import ChatMessage, ModelInfo
from backend.app.services.llm.base import LLMProvider

logger = logging.getLogger("app.llm.openai")

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.openai_api_key
        self.base_url = self.settings.openai_base_url.rstrip("/")
        self._default_model = self.settings.openai_default_model
        self.timeout = self.settings.llm_timeout_seconds

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self._default_model

    def _get_headers(self) -> dict:
        if not self.api_key:
            raise AuthenticationException(
                "OpenAI API key is not configured. Set OPENAI_API_KEY in your environment or .env file."
            )
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                self._handle_http_errors(response, target_model)
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            raise LLMTimeoutException(f"OpenAI request timed out after {self.timeout}s.")
        except httpx.NetworkError as exc:
            raise NetworkFailureException(f"Network failure connecting to OpenAI: {exc}")

    async def generate_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": [{"role": m.role.value, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }

        headers = self._get_headers()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:
                    self._handle_http_errors(response, target_model)
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            continue
                        if line.startswith("data: "):
                            raw_data = line[6:].strip()
                            if raw_data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(raw_data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except httpx.TimeoutException:
            raise LLMTimeoutException("OpenAI streaming request timed out.")
        except httpx.NetworkError as exc:
            raise NetworkFailureException(f"Network error during OpenAI streaming: {exc}")

    async def list_models(self) -> List[ModelInfo]:
        if not self.api_key:
            # Return standard fallback OpenAI model listings when key is not set
            return [
                ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai", description="Flagship omni model"),
                ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", description="Fast, lightweight model", is_default=True),
                ModelInfo(id="o1-preview", name="o1-preview", provider="openai", description="Reasoning model"),
            ]

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/models", headers=self._get_headers())
                if response.status_code == 200:
                    data = response.json()
                    gpt_models = [m for m in data.get("data", []) if "gpt" in m.get("id", "").lower()]
                    return [
                        ModelInfo(
                            id=m["id"],
                            name=m["id"],
                            provider="openai",
                            is_default=(m["id"] == self.default_model)
                        )
                        for m in gpt_models[:10]
                    ]
        except Exception:
            pass

        return [
            ModelInfo(id=self.default_model, name=self.default_model, provider="openai", is_default=True)
        ]

    async def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._get_headers())
                return resp.status_code == 200
        except Exception:
            return False

    def _handle_http_errors(self, response: httpx.Response, model: str) -> None:
        if response.status_code == 401:
            raise AuthenticationException("Invalid OpenAI API key provided.")
        elif response.status_code == 404:
            raise ModelNotFoundException(f"OpenAI model '{model}' was not found.")
        elif response.status_code == 429:
            raise RateLimitException("OpenAI rate limit or quota exceeded.")
        elif response.status_code >= 500:
            raise ProviderUnavailableException(f"OpenAI service returned server error {response.status_code}.")

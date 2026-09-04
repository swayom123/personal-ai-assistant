import json
import logging
from typing import AsyncGenerator, List, Optional
import httpx
from backend.app.config import get_settings
from backend.app.core.exceptions import (
    LLMTimeoutException,
    ModelNotFoundException,
    NetworkFailureException,
    ProviderUnavailableException,
)
from backend.app.schemas.llm import ChatMessage, ModelInfo
from backend.app.services.llm.base import LLMProvider

logger = logging.getLogger("app.llm.ollama")

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.ollama_base_url.rstrip("/")
        self._default_model = self.settings.ollama_default_model
        self.timeout = self.settings.llm_timeout_seconds

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return self._default_model

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
            "options": {"temperature": temperature},
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                self._handle_http_errors(response, target_model)
                data = response.json()
                return data.get("message", {}).get("content", "")
        except httpx.ConnectError:
            raise ProviderUnavailableException(
                f"Ollama server is not running at {self.base_url}. Start it with 'ollama serve'."
            )
        except httpx.TimeoutException:
            raise LLMTimeoutException(f"Ollama request timed out after {self.timeout}s.")
        except httpx.NetworkError as exc:
            raise NetworkFailureException(f"Network error connecting to Ollama: {exc}")

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
            "options": {"temperature": temperature},
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    self._handle_http_errors(response, target_model)
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            raise ProviderUnavailableException(
                f"Ollama server is not running at {self.base_url}. Start it with 'ollama serve'."
            )
        except httpx.TimeoutException:
            raise LLMTimeoutException("Ollama streaming request timed out.")
        except httpx.NetworkError as exc:
            raise NetworkFailureException(f"Network error during Ollama stream: {exc}")

    async def list_models(self) -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    for item in data.get("models", []):
                        m_name = item.get("name", "")
                        models.append(
                            ModelInfo(
                                id=m_name,
                                name=m_name,
                                provider="ollama",
                                description=f"Local Ollama model ({item.get('details', {}).get('parameter_size', 'standard')})",
                                is_default=(m_name == self.default_model),
                            )
                        )
                    if models:
                        return models
        except Exception:
            pass

        # Fallback catalog if Ollama tags are offline or not yet pulled
        return [
            ModelInfo(id="llama3.2", name="Llama 3.2 (3B)", provider="ollama", description="Fast lightweight local model", is_default=True),
            ModelInfo(id="llama3.1:8b", name="Llama 3.1 (8B)", provider="ollama", description="Local instruction tuned model"),
            ModelInfo(id="mistral", name="Mistral 7B", provider="ollama", description="Local code and reasoning model"),
            ModelInfo(id="deepseek-r1:8b", name="DeepSeek-R1 (8B)", provider="ollama", description="Local reasoning model"),
        ]

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    def _handle_http_errors(self, response: httpx.Response, model: str) -> None:
        if response.status_code == 404:
            raise ModelNotFoundException(f"Model '{model}' is not installed in Ollama. Run 'ollama pull {model}'.")
        elif response.status_code >= 500:
            raise ProviderUnavailableException(f"Ollama server returned error: HTTP {response.status_code}")

import logging
from typing import Dict, Optional
from backend.app.config import get_settings
from backend.app.core.exceptions import ValidationException
from backend.app.schemas.llm import ModelsResponse
from backend.app.services.llm.base import LLMProvider
from backend.app.services.llm.openai_provider import OpenAIProvider
from backend.app.services.llm.ollama_provider import OllamaProvider
from backend.app.services.llm.mock_provider import MockProvider

logger = logging.getLogger("app.llm.factory")

class LLMProviderFactory:
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {
            "openai": OpenAIProvider(),
            "ollama": OllamaProvider(),
            "mock": MockProvider(),
        }

    def register_provider(self, name: str, provider: LLMProvider) -> None:
        self._providers[name.lower()] = provider

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        settings = get_settings()
        target = (name or settings.default_llm_provider).lower().strip()

        if target == "auto":
            # 1. Prefer OpenAI if key is set
            if settings.openai_api_key and settings.openai_api_key.strip():
                logger.info("Auto-selecting OpenAI provider (API key detected)")
                return self._providers["openai"]
            # 2. Fallback to Mock provider for local reliable execution
            logger.info("Auto-selecting Mock fallback provider (No OpenAI API key supplied)")
            return self._providers["mock"]

        if target not in self._providers:
            available = ", ".join(self._providers.keys())
            raise ValidationException(
                f"Unsupported LLM provider: '{target}'. Available providers: {available}, auto"
            )

        return self._providers[target]

    async def list_all_models(self) -> ModelsResponse:
        settings = get_settings()
        active_provider = self.get_provider()
        
        all_models = []
        for provider_name, provider in self._providers.items():
            try:
                models = await provider.list_models()
                all_models.extend(models)
            except Exception as e:
                logger.warning(f"Could not retrieve models from provider {provider_name}: {e}")

        return ModelsResponse(
            active_provider=active_provider.provider_name,
            models=all_models
        )

# Global singleton
llm_factory = LLMProviderFactory()

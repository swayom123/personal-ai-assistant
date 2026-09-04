from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional
from backend.app.schemas.llm import ChatMessage, ModelInfo

class LLMProvider(ABC):
    """Abstract Base Class for Large Language Model Providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique identifier for this provider."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Returns the default model identifier."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generates a complete response for the given messages."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens as an asynchronous generator."""
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """Lists all available models for this provider."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Checks if the provider endpoint is healthy and accessible."""
        pass

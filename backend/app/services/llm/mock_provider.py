import asyncio
from typing import AsyncGenerator, List, Optional
from backend.app.schemas.llm import ChatMessage, ModelInfo
from backend.app.services.llm.base import LLMProvider

class MockProvider(LLMProvider):
    """
    Built-in intelligent fallback provider.
    Ensures the assistant can run, chat, and stream seamlessly offline
    without requiring active cloud credentials or a local daemon.
    """
    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "aether-local-engine"

    async def generate(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        last_msg = messages[-1].content if messages else ""
        return self._formulate_response(last_msg)

    async def generate_stream(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        last_msg = messages[-1].content if messages else ""
        full_text = self._formulate_response(last_msg)
        
        # Stream chunks with micro-delays to simulate natural generation
        words = full_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            await asyncio.sleep(0.02)

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                id="aether-local-engine",
                name="Aether Local Engine (Built-in)",
                provider="mock",
                description="Fast offline test and development engine",
                is_default=True
            )
        ]

    async def is_available(self) -> bool:
        return True

    def _formulate_response(self, user_prompt: str) -> str:
        p = user_prompt.lower()
        if "hello" in p or "hi" in p or "hey" in p:
            return "Greetings! I am Aether, your personal AI assistant. How may I assist your engineering workflow or technical tasks today?"
        elif "status" in p or "health" in p:
            return "All AI subsystems are operational. Provider routing is active, context builder is ready, and conversation persistence is synchronized."
        elif "code" in p or "python" in p or "react" in p:
            return (
                "Here is an architectural pattern tailored to your request:\n\n"
                "```python\n"
                "async def execute_task(prompt: str) -> dict:\n"
                "    # Multi-phase AI Engine Pipeline\n"
                "    context = await context_builder.build(prompt)\n"
                "    response = await llm_engine.generate(context)\n"
                "    return {'status': 'success', 'result': response}\n"
                "```\n\n"
                "Let me know if you would like me to extend this implementation or add unit test coverage."
            )
        else:
            return (
                f"I have received and analyzed your prompt: **\"{user_prompt}\"**.\n\n"
                f"The AI core successfully processed this through the Context Builder, System Instructions, "
                f"and active session history. Everything is configured and operating within expected parameters."
            )

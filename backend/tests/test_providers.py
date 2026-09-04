import pytest
from backend.app.schemas.llm import ChatMessage, Role
from backend.app.services.llm.factory import LLMProviderFactory
from backend.app.services.llm.mock_provider import MockProvider
from backend.app.services.llm.openai_provider import OpenAIProvider
from backend.app.services.llm.ollama_provider import OllamaProvider
from backend.app.core.exceptions import AuthenticationException, ValidationException

@pytest.mark.asyncio
async def test_provider_registration_and_selection():
    factory = LLMProviderFactory()
    
    mock_p = factory.get_provider("mock")
    assert isinstance(mock_p, MockProvider)
    assert mock_p.provider_name == "mock"

    openai_p = factory.get_provider("openai")
    assert isinstance(openai_p, OpenAIProvider)
    assert openai_p.provider_name == "openai"

    ollama_p = factory.get_provider("ollama")
    assert isinstance(ollama_p, OllamaProvider)
    assert ollama_p.provider_name == "ollama"

def test_invalid_provider_selection():
    factory = LLMProviderFactory()
    with pytest.raises(ValidationException):
        factory.get_provider("nonexistent-provider")

@pytest.mark.asyncio
async def test_mock_provider_generation_and_stream():
    provider = MockProvider()
    messages = [ChatMessage(role=Role.USER, content="Hello Aether")]
    
    response = await provider.generate(messages)
    assert isinstance(response, str)
    assert len(response) > 0

    # Test stream
    stream_chunks = []
    async for chunk in provider.generate_stream(messages):
        stream_chunks.append(chunk)
    
    streamed_text = "".join(stream_chunks)
    assert len(streamed_text) > 0

@pytest.mark.asyncio
async def test_openai_missing_key_raises_auth_error():
    provider = OpenAIProvider()
    provider.api_key = None
    messages = [ChatMessage(role=Role.USER, content="Test")]
    with pytest.raises(AuthenticationException):
        await provider.generate(messages)

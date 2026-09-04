import json
import logging
import uuid
from typing import AsyncGenerator
from backend.app.schemas.llm import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    Role,
)
from backend.app.services.llm.context_builder import ContextBuilder
from backend.app.services.llm.factory import llm_factory
from backend.app.services.conversation_service import conversation_service

logger = logging.getLogger("app.assistant_engine")

class AssistantEngine:
    def __init__(self):
        self.context_builder = ContextBuilder()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        # 1. Resolve or create conversation
        conv_id = request.conversation_id
        if not conv_id or not conversation_service.get_conversation(conv_id):
            conv = conversation_service.create_conversation(title=request.message[:35])
            conv_id = conv.id

        # 2. Build full contextual prompt
        prompt_messages = self.context_builder.build_prompt_context(
            user_input=request.message,
            conversation_id=conv_id,
        )

        # 3. Resolve LLM provider
        provider = llm_factory.get_provider(request.provider)
        target_model = request.model or provider.default_model

        logger.info(
            f"Dispatching chat request to provider '{provider.provider_name}' "
            f"with model '{target_model}' (conv_id: {conv_id})"
        )

        # 4. Generate response
        response_text = await provider.generate(
            messages=prompt_messages,
            model=target_model,
            temperature=request.temperature or 0.7,
        )

        # 5. Persist user and assistant messages
        conversation_service.add_message(conv_id, Role.USER, request.message)
        assistant_msg = conversation_service.add_message(conv_id, Role.ASSISTANT, response_text)

        # 6. Return response payload
        return ChatResponse(
            id=str(uuid.uuid4()),
            conversation_id=conv_id,
            message=assistant_msg,
            model=target_model,
            provider=provider.provider_name,
        )

    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        # 1. Resolve or create conversation
        conv_id = request.conversation_id
        if not conv_id or not conversation_service.get_conversation(conv_id):
            conv = conversation_service.create_conversation(title=request.message[:35])
            conv_id = conv.id

        # 2. Build prompt context
        prompt_messages = self.context_builder.build_prompt_context(
            user_input=request.message,
            conversation_id=conv_id,
        )

        # 3. Resolve provider
        provider = llm_factory.get_provider(request.provider)
        target_model = request.model or provider.default_model

        # Record user input immediately
        conversation_service.add_message(conv_id, Role.USER, request.message)

        # Emit conversation metadata as first SSE event
        meta_event = {
            "type": "meta",
            "conversation_id": conv_id,
            "model": target_model,
            "provider": provider.provider_name,
        }
        yield f"data: {json.dumps(meta_event)}\n\n"

        # 4. Stream response tokens
        accumulated_chunks = []
        async for chunk in provider.generate_stream(
            messages=prompt_messages,
            model=target_model,
            temperature=request.temperature or 0.7,
        ):
            accumulated_chunks.append(chunk)
            chunk_event = {"type": "content", "content": chunk}
            yield f"data: {json.dumps(chunk_event)}\n\n"

        full_reply = "".join(accumulated_chunks)
        # 5. Persist completed assistant response
        conversation_service.add_message(conv_id, Role.ASSISTANT, full_reply)

        # Emit done event
        done_event = {"type": "done", "full_content": full_reply}
        yield f"data: {json.dumps(done_event)}\n\n"

# Global singleton
assistant_engine = AssistantEngine()

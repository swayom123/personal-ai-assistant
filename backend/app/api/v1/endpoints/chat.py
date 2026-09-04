from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.app.schemas.llm import ChatRequest, ChatResponse
from backend.app.services.assistant_engine import assistant_engine

router = APIRouter()

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Generate Chat Response",
    description="Processes user input through context builder and generates an LLM response."
)
async def chat_completion(request: ChatRequest) -> ChatResponse:
    return await assistant_engine.chat(request)

@router.post(
    "/chat/stream",
    summary="Generate Streaming Chat Response",
    description="Streams LLM tokens in real-time using Server-Sent Events (SSE)."
)
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        assistant_engine.chat_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

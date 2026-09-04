from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    role: Role
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt or input message")
    conversation_id: Optional[str] = Field(default=None, description="Active conversation identifier")
    model: Optional[str] = Field(default=None, description="Optional override model name")
    provider: Optional[str] = Field(default=None, description="Optional override provider (e.g. openai, ollama)")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stream: bool = Field(default=False, description="Whether to stream response")

class ChatResponse(BaseModel):
    id: str
    conversation_id: str
    message: ChatMessage
    model: str
    provider: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    description: Optional[str] = None
    is_default: bool = False

class ModelsResponse(BaseModel):
    active_provider: str
    models: List[ModelInfo]

from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.llm import ChatMessage

class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100, description="Title of the new conversation")

class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="New title for the conversation")

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int

class ConversationDetailResponse(ConversationResponse):
    messages: List[ChatMessage] = []

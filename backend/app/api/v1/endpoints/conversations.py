from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
    ConversationUpdate,
)
from backend.app.services.conversation_service import conversation_service

router = APIRouter()

@router.get(
    "/conversations",
    response_model=List[ConversationResponse],
    summary="List Conversations",
    description="Returns all conversation sessions sorted by most recently updated."
)
async def list_conversations() -> List[ConversationResponse]:
    return conversation_service.list_conversations()

@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation",
    description="Creates a new conversation session."
)
async def create_conversation(data: ConversationCreate) -> ConversationResponse:
    return conversation_service.create_conversation(title=data.title)

@router.get(
    "/conversations/search",
    response_model=List[ConversationResponse],
    summary="Search Conversations",
    description="Searches conversations by matching title or message content."
)
async def search_conversations(
    q: str = Query(..., min_length=1, description="Search term")
) -> List[ConversationResponse]:
    return conversation_service.search_conversations(q)

@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Get Conversation Messages",
    description="Retrieves a conversation along with its full message history."
)
async def get_conversation(conversation_id: str) -> ConversationDetailResponse:
    conv = conversation_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found."
        )
    return conv

@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    summary="Rename Conversation",
    description="Updates the title of a conversation."
)
async def rename_conversation(
    conversation_id: str,
    data: ConversationUpdate
) -> ConversationResponse:
    updated = conversation_service.rename_conversation(conversation_id, data.title)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found."
        )
    return updated

@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Conversation",
    description="Permanently deletes a conversation and its messages."
)
async def delete_conversation(conversation_id: str) -> None:
    deleted = conversation_service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found."
        )

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from backend.app.schemas.llm import ChatMessage, Role
from backend.app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
)

logger = logging.getLogger("app.conversations")

class Conversation:
    def __init__(self, id: str, title: str, created_at: str, updated_at: str, messages: Optional[List[ChatMessage]] = None):
        self.id = id
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.messages = messages or []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [m.model_dump() for m in self.messages],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        messages = [ChatMessage(**m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages,
        )

class ConversationService:
    def __init__(self, storage_dir: str = "backend/data/conversations"):
        self.storage_path = Path(storage_dir)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._conversations: Dict[str, Conversation] = {}
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        for file in self.storage_path.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conv = Conversation.from_dict(data)
                    self._conversations[conv.id] = conv
            except Exception as e:
                logger.error(f"Error loading conversation file {file}: {e}")

    def _persist(self, conversation: Conversation) -> None:
        file_path = self.storage_path / f"{conversation.id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(conversation.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist conversation {conversation.id}: {e}")

    def create_conversation(self, title: Optional[str] = None) -> ConversationResponse:
        now = datetime.now(timezone.utc).isoformat()
        conv_id = str(uuid.uuid4())
        conv_title = title or f"Conversation {datetime.now(timezone.utc).strftime('%b %d, %H:%M')}"
        
        conv = Conversation(
            id=conv_id,
            title=conv_title,
            created_at=now,
            updated_at=now,
            messages=[],
        )
        self._conversations[conv.id] = conv
        self._persist(conv)
        logger.info(f"Created conversation: {conv.id} ('{conv.title}')")
        return self._to_response(conv)

    def get_conversation(self, conv_id: str) -> Optional[ConversationDetailResponse]:
        conv = self._conversations.get(conv_id)
        if not conv:
            return None
        return ConversationDetailResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages),
            messages=conv.messages,
        )

    def list_conversations(self) -> List[ConversationResponse]:
        sorted_convs = sorted(
            self._conversations.values(),
            key=lambda c: c.updated_at,
            reverse=True,
        )
        return [self._to_response(c) for c in sorted_convs]

    def rename_conversation(self, conv_id: str, new_title: str) -> Optional[ConversationResponse]:
        conv = self._conversations.get(conv_id)
        if not conv:
            return None
        conv.title = new_title
        conv.updated_at = datetime.now(timezone.utc).isoformat()
        self._persist(conv)
        return self._to_response(conv)

    def delete_conversation(self, conv_id: str) -> bool:
        if conv_id in self._conversations:
            del self._conversations[conv_id]
            file_path = self.storage_path / f"{conv_id}.json"
            if file_path.exists():
                file_path.unlink()
            logger.info(f"Deleted conversation: {conv_id}")
            return True
        return False

    def add_message(self, conv_id: str, role: Role, content: str) -> ChatMessage:
        if conv_id not in self._conversations:
            self.create_conversation(title=content[:35] + ("..." if len(content) > 35 else ""))

        conv = self._conversations[conv_id]
        msg = ChatMessage(role=role, content=content)
        conv.messages.append(msg)
        conv.updated_at = datetime.now(timezone.utc).isoformat()
        self._persist(conv)
        return msg

    def search_conversations(self, query: str) -> List[ConversationResponse]:
        q = query.lower().strip()
        matches = []
        for conv in self._conversations.values():
            if q in conv.title.lower():
                matches.append(conv)
                continue
            for msg in conv.messages:
                if q in msg.content.lower():
                    matches.append(conv)
                    break
        matches.sort(key=lambda c: c.updated_at, reverse=True)
        return [self._to_response(c) for c in matches]

    def _to_response(self, conv: Conversation) -> ConversationResponse:
        return ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages),
        )

conversation_service = ConversationService()

import pytest
from backend.app.schemas.llm import Role
from backend.app.services.conversation_service import conversation_service

def test_conversation_lifecycle():
    # 1. Create
    conv = conversation_service.create_conversation(title="Architecture Discussion")
    assert conv.id is not None
    assert conv.title == "Architecture Discussion"
    assert conv.message_count == 0

    # 2. Add Messages
    msg1 = conversation_service.add_message(conv.id, Role.USER, "Discuss Microservices vs Monolith")
    msg2 = conversation_service.add_message(conv.id, Role.ASSISTANT, "A modular monolith is often best.")
    assert msg1.content == "Discuss Microservices vs Monolith"
    assert msg2.content == "A modular monolith is often best."

    # 3. Retrieve
    detail = conversation_service.get_conversation(conv.id)
    assert detail is not None
    assert detail.message_count == 2
    assert len(detail.messages) == 2

    # 4. Rename
    renamed = conversation_service.rename_conversation(conv.id, "Modular Monoliths")
    assert renamed is not None
    assert renamed.title == "Modular Monoliths"

    # 5. Search
    search_results = conversation_service.search_conversations("Monolith")
    assert any(c.id == conv.id for c in search_results)

    # 6. Delete
    deleted = conversation_service.delete_conversation(conv.id)
    assert deleted is True
    assert conversation_service.get_conversation(conv.id) is None

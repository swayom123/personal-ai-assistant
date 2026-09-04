import pytest
from backend.app.schemas.llm import Role
from backend.app.services.llm.context_builder import ContextBuilder
from backend.app.services.conversation_service import conversation_service

def test_prompt_context_construction():
    builder = ContextBuilder(max_history_messages=5)
    
    # Create conversation with history
    conv = conversation_service.create_conversation("Test Context Conv")
    conversation_service.add_message(conv.id, Role.USER, "What is Python?")
    conversation_service.add_message(conv.id, Role.ASSISTANT, "Python is a programming language.")
    
    messages = builder.build_prompt_context(
        user_input="How do I use FastAPI in it?",
        conversation_id=conv.id,
        custom_memory={"project_language": "Python 3.14"}
    )

    # 1. First message must be SYSTEM with Assistant personality
    assert messages[0].role == Role.SYSTEM
    assert "You are Aether" in messages[0].content

    # 2. Second message must be memory context anchor
    assert messages[1].role == Role.SYSTEM
    assert "Context & User Memory Anchor" in messages[1].content
    assert "Python 3.14" in messages[1].content

    # 3. History should be included
    history_contents = [m.content for m in messages]
    assert "What is Python?" in history_contents
    assert "Python is a programming language." in history_contents

    # 4. Final message must be user input
    assert messages[-1].role == Role.USER
    assert messages[-1].content == "How do I use FastAPI in it?"

import logging
from typing import Dict, List, Optional
from backend.app.schemas.llm import ChatMessage, Role
from backend.app.schemas.profile import AssistantProfile
from backend.app.services.profile_service import ProfileService
from backend.app.services.conversation_service import conversation_service

logger = logging.getLogger("app.context_builder")

class ContextBuilder:
    """
    Constructs the contextual prompt sequence for the LLM:
    System Instructions -> Memory Context -> Conversation History -> User Input
    """
    def __init__(self, max_history_messages: int = 15):
        self.max_history = max_history_messages

    def build_prompt_context(
        self,
        user_input: str,
        conversation_id: Optional[str] = None,
        custom_memory: Optional[Dict[str, str]] = None,
    ) -> List[ChatMessage]:
        profile = ProfileService.get_profile()
        messages: List[ChatMessage] = []

        # 1. System Instructions & Personality
        system_prompt = self._compile_system_instruction(profile)
        messages.append(ChatMessage(role=Role.SYSTEM, content=system_prompt))

        # 2. Memory Context (User Preferences & Active Environment)
        memory_content = self._compile_memory_context(profile, custom_memory)
        if memory_content:
            messages.append(
                ChatMessage(
                    role=Role.SYSTEM,
                    content=f"### Context & User Memory Anchor\n{memory_content}"
                )
            )

        # 3. Conversation History
        if conversation_id:
            conv = conversation_service.get_conversation(conversation_id)
            if conv and conv.messages:
                # Include up to max_history prior messages
                history = conv.messages[-self.max_history:]
                messages.extend(history)

        # 4. Current User Input
        messages.append(ChatMessage(role=Role.USER, content=user_input))

        logger.debug(f"Compiled prompt context: {len(messages)} messages for conversation {conversation_id}")
        return messages

    def _compile_system_instruction(self, profile: AssistantProfile) -> str:
        return (
            f"You are {profile.name}.\n\n"
            f"Personality: {profile.personality}\n"
            f"Response Style: {profile.response_style}\n\n"
            f"Directives:\n{profile.system_instructions}"
        )

    def _compile_memory_context(
        self,
        profile: AssistantProfile,
        custom_memory: Optional[Dict[str, str]] = None
    ) -> str:
        lines = []
        if profile.user_preferences:
            for k, v in profile.user_preferences.items():
                lines.append(f"- {k.replace('_', ' ').capitalize()}: {v}")

        if custom_memory:
            for k, v in custom_memory.items():
                lines.append(f"- {k.capitalize()}: {v}")

        return "\n".join(lines)

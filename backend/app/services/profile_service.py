import json
import logging
from pathlib import Path
from typing import Optional
from backend.app.config import get_settings
from backend.app.schemas.profile import AssistantProfile

logger = logging.getLogger("app.profile")

class ProfileService:
    _cached_profile: Optional[AssistantProfile] = None

    @classmethod
    def get_profile(cls) -> AssistantProfile:
        if cls._cached_profile is not None:
            return cls._cached_profile

        settings = get_settings()
        config_path = Path(settings.profile_config_path)

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls._cached_profile = AssistantProfile(**data)
                    logger.info(f"Loaded assistant profile: {cls._cached_profile.name}")
                    return cls._cached_profile
            except Exception as e:
                logger.error(f"Failed to load profile config from {config_path}: {e}")

        # Fallback profile if file is unreadable
        cls._cached_profile = AssistantProfile(
            name="Aether",
            personality="Helpful, calm, and technically precise.",
            response_style="Structured markdown with code blocks.",
            system_instructions="You are a personal AI assistant on this laptop.",
            user_preferences={"theme": "dark"}
        )
        return cls._cached_profile

    @classmethod
    def reload_profile(cls) -> AssistantProfile:
        cls._cached_profile = None
        return cls.get_profile()

import logging
from typing import Dict, List, Optional
from backend.app.config import get_settings
from backend.app.core.exceptions import ValidationException
from backend.app.schemas.voice import VoiceInfo
from backend.app.services.voice.tts.base import TTSProvider
from backend.app.services.voice.tts.piper_provider import PiperProvider
from backend.app.services.voice.tts.coqui_provider import CoquiProvider
from backend.app.services.voice.tts.mock_provider import MockTTSProvider

logger = logging.getLogger("app.voice.tts.factory")

class TTSProviderFactory:
    def __init__(self):
        self._providers: Dict[str, TTSProvider] = {
            "piper": PiperProvider(),
            "coqui": CoquiProvider(),
            "mock": MockTTSProvider(),
        }

    def register_provider(self, name: str, provider: TTSProvider) -> None:
        self._providers[name.lower()] = provider

    def get_provider(self, name: Optional[str] = None) -> TTSProvider:
        settings = get_settings()
        target = (name or settings.voice_tts_provider).lower().strip()

        if target not in self._providers:
            # Fallback to piper or mock
            if "piper" in self._providers:
                return self._providers["piper"]
            return self._providers["mock"]

        return self._providers[target]

    def list_all_voices(self) -> List[VoiceInfo]:
        all_voices: List[VoiceInfo] = []
        for provider in self._providers.values():
            try:
                all_voices.extend(provider.list_voices())
            except Exception as e:
                logger.warning(f"Failed to list voices from {provider.provider_name}: {e}")
        return all_voices

tts_factory = TTSProviderFactory()

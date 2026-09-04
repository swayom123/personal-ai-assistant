import json
import logging
import threading
from pathlib import Path
from backend.app.config import get_settings
from backend.app.schemas.voice import VoiceSettings

logger = logging.getLogger("app.voice.settings")

class VoiceSettingsService:
    def __init__(self):
        self._lock = threading.Lock()
        self._settings_cache: VoiceSettings = self._load()

    def _get_path(self) -> Path:
        settings = get_settings()
        return Path(settings.voice_settings_path)

    def _load(self) -> VoiceSettings:
        path = self._get_path()
        settings = get_settings()
        default_settings = VoiceSettings(
            microphone=settings.voice_input_device or "default",
            speaker=settings.voice_output_device or "default",
            voice=settings.voice_tts_voice,
            speed=settings.voice_speech_speed,
            volume=settings.voice_volume,
            wake_word=settings.voice_wake_word,
            assistant_name=settings.voice_assistant_name,
            language=settings.voice_stt_language,
            tts_provider=settings.voice_tts_provider,
            stt_model=settings.voice_stt_model,
            vad_filter=settings.voice_vad_filter,
        )

        if not path.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default_settings.model_dump(), f, indent=2)
            except Exception as e:
                logger.warning(f"Could not persist default voice settings: {e}")
            return default_settings

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return VoiceSettings(**data)
        except Exception as e:
            logger.error(f"Failed to load voice settings from {path}: {e}")
            return default_settings

    def get_settings(self) -> VoiceSettings:
        with self._lock:
            return self._settings_cache

    def update_settings(self, updates: VoiceSettings) -> VoiceSettings:
        with self._lock:
            self._settings_cache = updates
            path = self._get_path()
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(updates.model_dump(), f, indent=2)
                logger.info("Updated persistent voice settings successfully")
            except Exception as e:
                logger.error(f"Failed to save voice settings to {path}: {e}")
            return self._settings_cache

voice_settings_service = VoiceSettingsService()

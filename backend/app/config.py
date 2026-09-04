from functools import lru_cache
from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = Field(default="personal-ai-assistant", description="Name of the service")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=True, description="Debug mode")
    port: int = Field(default=8000, description="Port to bind server")
    host: str = Field(default="0.0.0.0", description="Host to bind server")
    
    # CORS
    cors_origins: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.strip().startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="Prefix for API v1 routes")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Path to log file")

    # AI Engine & LLM Providers
    default_llm_provider: str = Field(
        default="auto",
        description="Default LLM provider: 'openai', 'ollama', or 'auto' (detects available or fallback)"
    )
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key (never exposed to frontend)")
    openai_base_url: str = Field(default="https://api.openai.com/v1", description="OpenAI API Base URL")
    openai_default_model: str = Field(default="gpt-4o-mini", description="Default OpenAI model")

    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    ollama_default_model: str = Field(default="llama3.2", description="Default Ollama model")

    llm_timeout_seconds: float = Field(default=30.0, description="LLM provider HTTP timeout in seconds")
    profile_config_path: str = Field(default="backend/config/profile.json", description="Path to assistant profile JSON")

    # Phase 4 — Voice Assistant Configuration
    voice_input_device: Optional[str] = Field(default=None, description="Audio input device ID / name")
    voice_output_device: Optional[str] = Field(default=None, description="Audio output device ID / name")
    voice_wake_word: str = Field(default="Hey Max", description="Configurable wake word")
    voice_wake_word_detector: str = Field(
        default="openwakeword",
        description="Wake word engine: 'openwakeword', 'porcupine', or 'builtin'"
    )
    porcupine_access_key: Optional[str] = Field(default=None, description="Picovoice Porcupine AccessKey if using porcupine")
    voice_assistant_name: str = Field(default="Max", description="Configurable assistant name")
    voice_stt_model: str = Field(default="base", description="Faster-Whisper model size: tiny, base, small, medium")
    voice_stt_language: str = Field(default="en", description="Default language code or 'auto'")
    voice_tts_provider: str = Field(default="piper", description="TTS Provider: 'piper', 'coqui', or 'mock'")
    voice_tts_voice: str = Field(default="en_US-lessac-medium", description="TTS voice name/model")
    voice_speech_speed: float = Field(default=1.0, description="Voice playback speed multiplier (0.5 to 2.0)")
    voice_volume: float = Field(default=1.0, description="Voice playback volume multiplier (0.0 to 1.0)")
    voice_vad_filter: bool = Field(default=True, description="Enable Silero VAD noise handling in Faster-Whisper")
    voice_settings_path: str = Field(default="backend/config/voice_settings.json", description="Persistent voice settings file")

@lru_cache
def get_settings() -> Settings:
    return Settings()

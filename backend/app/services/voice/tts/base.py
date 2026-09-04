from abc import ABC, abstractmethod
from typing import List, Optional
from backend.app.schemas.voice import VoiceInfo

class TTSProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the TTS provider."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider and necessary voice models or dependencies are available."""
        pass

    @abstractmethod
    def list_voices(self) -> List[VoiceInfo]:
        """List available voices for this provider."""
        pass

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        volume: float = 1.0
    ) -> bytes:
        """
        Synthesize text to audio bytes (WAV format).
        Must be asynchronous or run in threadpool to prevent blocking the event loop.
        """
        pass

import logging
from typing import Optional
from backend.app.config import get_settings
from backend.app.services.voice.wake_word.base import WakeWordDetector

logger = logging.getLogger("app.voice.wake_word.porcupine")

class PorcupineDetector(WakeWordDetector):
    def __init__(self, wake_word: str = "computer", access_key: Optional[str] = None):
        self._wake_word = wake_word.lower()
        self._access_key = access_key or get_settings().porcupine_access_key
        self._porcupine = None
        self._is_available = False
        self._init_porcupine()

    def _init_porcupine(self):
        if not self._access_key:
            logger.info("Porcupine access key not configured; detector marked unavailable")
            self._is_available = False
            return

        try:
            import pvporcupine
            # Normalize keyword if in built-ins
            valid_keywords = pvporcupine.KEYWORDS
            kw = self._wake_word if self._wake_word in valid_keywords else "computer"
            self._porcupine = pvporcupine.create(
                access_key=self._access_key,
                keywords=[kw]
            )
            self._is_available = True
            logger.info(f"Porcupine detector initialized for keyword: {kw}")
        except Exception as e:
            logger.warning(f"Porcupine initialization failed: {e}")
            self._is_available = False
            self._porcupine = None

    @property
    def detector_name(self) -> str:
        return "porcupine"

    def is_available(self) -> bool:
        return self._is_available

    def get_wake_word(self) -> str:
        return self._wake_word

    def set_wake_word(self, word: str) -> None:
        self._wake_word = word.lower()
        self._init_porcupine()

    def detect(self, audio_chunk: bytes) -> bool:
        if not self._is_available or self._porcupine is None:
            return False

        try:
            import numpy as np
            pcm = np.frombuffer(audio_chunk, dtype=np.int16)
            if len(pcm) != self._porcupine.frame_length:
                return False
            result = self._porcupine.process(pcm)
            return result >= 0
        except Exception as e:
            logger.debug(f"Porcupine detection error: {e}")
            return False

    def close(self):
        if self._porcupine is not None:
            try:
                self._porcupine.delete()
            except Exception:
                pass
            self._porcupine = None

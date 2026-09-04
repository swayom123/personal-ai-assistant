import logging
from backend.app.services.voice.wake_word.base import WakeWordDetector

logger = logging.getLogger("app.voice.wake_word.mock")

class MockWakeWordDetector(WakeWordDetector):
    def __init__(self, wake_word: str = "Hey Max"):
        self._wake_word = wake_word
        self._simulated_trigger = False

    @property
    def detector_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def get_wake_word(self) -> str:
        return self._wake_word

    def set_wake_word(self, word: str) -> None:
        self._wake_word = word

    def trigger_next(self):
        """Helper for automated tests to simulate wake word trigger."""
        self._simulated_trigger = True

    def detect(self, audio_chunk: bytes) -> bool:
        if self._simulated_trigger:
            self._simulated_trigger = False
            return True
        return False

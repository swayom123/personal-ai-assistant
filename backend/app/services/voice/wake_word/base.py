from abc import ABC, abstractmethod

class WakeWordDetector(ABC):
    @property
    @abstractmethod
    def detector_name(self) -> str:
        """Name of the wake word detector."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if detector is ready to process audio."""
        pass

    @abstractmethod
    def detect(self, audio_chunk: bytes) -> bool:
        """
        Process a 16-bit PCM 16kHz audio chunk and return True if wake word is detected.
        """
        pass

    @abstractmethod
    def get_wake_word(self) -> str:
        """Return currently configured wake word."""
        pass

    @abstractmethod
    def set_wake_word(self, word: str) -> None:
        """Update configured wake word."""
        pass

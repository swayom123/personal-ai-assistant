import logging
from typing import Dict, Optional
from backend.app.config import get_settings
from backend.app.services.voice.wake_word.base import WakeWordDetector
from backend.app.services.voice.wake_word.openwakeword_detector import OpenWakeWordDetector
from backend.app.services.voice.wake_word.porcupine_detector import PorcupineDetector
from backend.app.services.voice.wake_word.mock_detector import MockWakeWordDetector

logger = logging.getLogger("app.voice.wake_word.factory")

class WakeWordDetectorFactory:
    def __init__(self):
        settings = get_settings()
        self._detectors: Dict[str, WakeWordDetector] = {
            "openwakeword": OpenWakeWordDetector(wake_word=settings.voice_wake_word),
            "porcupine": PorcupineDetector(wake_word=settings.voice_wake_word),
            "mock": MockWakeWordDetector(wake_word=settings.voice_wake_word),
        }

    def register_detector(self, name: str, detector: WakeWordDetector) -> None:
        self._detectors[name.lower()] = detector

    def get_detector(self, name: Optional[str] = None) -> WakeWordDetector:
        settings = get_settings()
        target = (name or settings.voice_wake_word_detector).lower().strip()

        if target not in self._detectors:
            # Default to openwakeword or mock
            if "openwakeword" in self._detectors and self._detectors["openwakeword"].is_available():
                return self._detectors["openwakeword"]
            return self._detectors["mock"]

        return self._detectors[target]

wake_word_factory = WakeWordDetectorFactory()

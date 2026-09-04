import logging
import numpy as np
from typing import Optional
from backend.app.services.voice.wake_word.base import WakeWordDetector

logger = logging.getLogger("app.voice.wake_word.openwakeword")

class OpenWakeWordDetector(WakeWordDetector):
    def __init__(self, wake_word: str = "Hey Max", threshold: float = 0.5):
        self._wake_word = wake_word
        self._threshold = threshold
        self._model = None
        self._is_available = False
        self._init_model()

    def _init_model(self):
        try:
            import openwakeword
            # Load default pretrained openwakeword models
            self._model = openwakeword.Model()
            self._is_available = True
            logger.info("OpenWakeWord engine initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize OpenWakeWord model: {e}")
            self._model = None
            self._is_available = False

    @property
    def detector_name(self) -> str:
        return "openwakeword"

    def is_available(self) -> bool:
        return self._is_available

    def get_wake_word(self) -> str:
        return self._wake_word

    def set_wake_word(self, word: str) -> None:
        self._wake_word = word
        logger.info(f"Updated wake word to: {word}")

    def detect(self, audio_chunk: bytes) -> bool:
        if not self._is_available or self._model is None:
            return False

        try:
            # Convert 16-bit PCM to int16 numpy array
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            if len(audio_data) == 0:
                return False

            prediction = self._model.predict(audio_data)
            # Check model predictions
            for model_name, score in prediction.items():
                if score >= self._threshold:
                    logger.info(f"Wake word detected by model '{model_name}' with score {score:.2f}")
                    return True
            return False
        except Exception as e:
            logger.debug(f"OpenWakeWord inference error: {e}")
            return False

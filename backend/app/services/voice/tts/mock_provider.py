import asyncio
import io
import math
import struct
import wave
import logging
from typing import List, Optional
from backend.app.schemas.voice import VoiceInfo
from backend.app.services.voice.tts.base import TTSProvider

logger = logging.getLogger("app.voice.tts.mock")

class MockTTSProvider(TTSProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def list_voices(self) -> List[VoiceInfo]:
        return [
            VoiceInfo(id="mock-aether-en", name="Aether Standard (Simulated)", provider="mock", language="en", gender="neutral"),
            VoiceInfo(id="mock-max-en", name="Max Direct (Simulated)", provider="mock", language="en", gender="male"),
        ]

    def _generate_wav_sync(self, text: str, speed: float = 1.0, volume: float = 1.0) -> bytes:
        sample_rate = 22050
        # Calculate duration based on text length and speed
        word_count = max(1, len(text.split()))
        duration = max(0.4, min(10.0, (word_count * 0.25) / max(0.2, speed)))
        num_samples = int(sample_rate * duration)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)       # Mono
            wav_file.setsampwidth(2)      # 16-bit
            wav_file.setframerate(sample_rate)

            # Generate pleasant modulated harmonic tone reflecting speech syllables
            base_freq = 280.0
            vol = max(0.0, min(1.0, volume)) * 12000.0

            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                # Envelope: smooth attack and decay
                envelope = math.sin(math.pi * (i / num_samples))
                # Formant-like harmonic modulation
                f = base_freq + 40.0 * math.sin(2 * math.pi * 3.5 * t)
                sample_val = int(vol * envelope * (
                    0.7 * math.sin(2 * math.pi * f * t) +
                    0.3 * math.sin(4 * math.pi * f * t)
                ))
                sample_val = max(-32768, min(32767, sample_val))
                frames.extend(struct.pack("<h", sample_val))

            wav_file.writeframes(frames)

        return buffer.getvalue()

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        volume: float = 1.0
    ) -> bytes:
        # Run audio synthesis in worker thread
        return await asyncio.to_thread(self._generate_wav_sync, text, speed, volume)

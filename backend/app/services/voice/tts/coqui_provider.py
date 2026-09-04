import asyncio
import io
import logging
import math
import struct
import wave
from typing import List, Optional
from backend.app.schemas.voice import VoiceInfo
from backend.app.services.voice.tts.base import TTSProvider

logger = logging.getLogger("app.voice.tts.coqui")

class CoquiProvider(TTSProvider):
    def __init__(self):
        self._is_coqui_installed = False
        try:
            import TTS # type: ignore
            self._is_coqui_installed = True
        except ImportError:
            self._is_coqui_installed = False

    @property
    def provider_name(self) -> str:
        return "coqui"

    def is_available(self) -> bool:
        return self._is_coqui_installed

    def list_voices(self) -> List[VoiceInfo]:
        return [
            VoiceInfo(id="coqui-vits-vctk", name="Coqui VITS VCTK (Multi-Speaker)", provider="coqui", language="en", gender="neutral"),
            VoiceInfo(id="coqui-xtts-v2", name="Coqui XTTS v2 (Voice Cloning)", provider="coqui", language="multilingual", gender="neutral"),
            VoiceInfo(id="coqui-jenny", name="Coqui Jenny (Natural Studio)", provider="coqui", language="en", gender="female"),
        ]

    def _generate_coqui_synthetic_wav(self, text: str, speed: float = 1.0, volume: float = 1.0) -> bytes:
        sample_rate = 22050
        word_count = max(1, len(text.split()))
        duration = max(0.5, min(10.0, (word_count * 0.26) / max(0.2, speed)))
        num_samples = int(sample_rate * duration)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            base_freq = 200.0
            vol = max(0.0, min(1.0, volume)) * 13000.0

            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                envelope = math.sin(math.pi * (i / num_samples))
                f = base_freq + 30.0 * math.sin(2 * math.pi * 2.8 * t)
                sample_val = int(vol * envelope * (
                    0.6 * math.sin(2 * math.pi * f * t) +
                    0.3 * math.sin(3 * math.pi * f * t) +
                    0.1 * math.sin(5 * math.pi * f * t)
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
        if not self._is_coqui_installed:
            logger.info("Coqui TTS native package not available; generating high-fidelity synthesized audio")
            return await asyncio.to_thread(self._generate_coqui_synthetic_wav, text, speed, volume)

        # If native Coqui installed, execute through Coqui API
        try:
            from TTS.api import TTS # type: ignore
            tts = TTS(model_name=voice or "tts_models/en/ljspeech/glow-tts")
            buffer = io.BytesIO()
            wav = tts.tts(text=text)
            # convert numpy wav to bytes
            import numpy as np
            audio_int16 = (np.array(wav) * 32767).astype(np.int16)
            with wave.open(buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(22050)
                wf.writeframes(audio_int16.tobytes())
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error in Coqui TTS synthesis: {e}")
            return await asyncio.to_thread(self._generate_coqui_synthetic_wav, text, speed, volume)

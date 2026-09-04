import pytest
import wave
import io
from backend.app.services.voice.tts.factory import tts_factory
from backend.app.services.voice.tts.piper_provider import PiperProvider
from backend.app.services.voice.tts.coqui_provider import CoquiProvider
from backend.app.services.voice.tts.mock_provider import MockTTSProvider

def test_tts_provider_registration_and_listing():
    voices = tts_factory.list_all_voices()
    assert len(voices) > 0
    provider_names = {v.provider for v in voices}
    assert "piper" in provider_names
    assert "coqui" in provider_names
    assert "mock" in provider_names

@pytest.mark.asyncio
async def test_mock_tts_provider_synthesis():
    provider = MockTTSProvider()
    assert provider.is_available() is True
    audio = await provider.synthesize("Hello world test speech", speed=1.0, volume=0.8)
    assert isinstance(audio, bytes)
    assert len(audio) > 1000

    # Verify valid RIFF/WAV format
    with wave.open(io.BytesIO(audio), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 22050
        assert wf.getnframes() > 0

@pytest.mark.asyncio
async def test_piper_tts_provider_synthesis():
    provider = PiperProvider()
    assert provider.is_available() is True
    audio = await provider.synthesize("Piper voice synthesis test.", speed=1.2, volume=1.0)
    assert isinstance(audio, bytes)
    assert len(audio) > 1000

    with wave.open(io.BytesIO(audio), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 22050

@pytest.mark.asyncio
async def test_coqui_tts_provider_synthesis():
    provider = CoquiProvider()
    audio = await provider.synthesize("Coqui voice synthesis test.", speed=1.0)
    assert isinstance(audio, bytes)
    assert len(audio) > 1000

    with wave.open(io.BytesIO(audio), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 22050

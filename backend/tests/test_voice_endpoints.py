import pytest
import base64
from backend.app.services.voice.tts.mock_provider import MockTTSProvider

def test_get_voice_devices_endpoint(client):
    response = client.get("/api/v1/voice/devices")
    assert response.status_code == 200
    data = response.json()
    assert "inputs" in data
    assert "outputs" in data
    assert len(data["inputs"]) > 0
    assert len(data["outputs"]) > 0

def test_voice_settings_endpoint(client):
    # GET settings
    get_res = client.get("/api/v1/voice/settings")
    assert get_res.status_code == 200
    settings = get_res.json()
    assert "wake_word" in settings
    assert "speed" in settings

    # PUT settings
    settings["wake_word"] = "Hey TestAssistant"
    settings["speed"] = 1.25
    put_res = client.put("/api/v1/voice/settings", json=settings)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["wake_word"] == "Hey TestAssistant"
    assert updated["speed"] == 1.25

def test_voice_voices_endpoint(client):
    response = client.get("/api/v1/voice/voices")
    assert response.status_code == 200
    voices = response.json()
    assert isinstance(voices, list)
    assert len(voices) > 0
    assert any(v["provider"] == "piper" for v in voices)

def test_voice_speak_endpoints(client):
    # 1. Binary WAV output
    res_audio = client.post(
        "/api/v1/voice/speak",
        json={"text": "Speaking test text", "provider": "mock"}
    )
    assert res_audio.status_code == 200
    assert res_audio.headers["content-type"] == "audio/wav"
    assert len(res_audio.content) > 500

    # 2. JSON Base64 output
    res_json = client.post(
        "/api/v1/voice/speak?output_format=json",
        json={"text": "Speaking JSON test", "provider": "mock"}
    )
    assert res_json.status_code == 200
    data = res_json.json()
    assert "audio_base64" in data
    assert data["mime_type"] == "audio/wav"

    # 3. Validation error on empty text
    res_empty = client.post(
        "/api/v1/voice/speak",
        json={"text": "   "}
    )
    assert res_empty.status_code == 422

@pytest.mark.asyncio
async def test_voice_transcribe_and_interact_endpoints(client):
    tts = MockTTSProvider()
    wav_bytes = await tts.synthesize("Transcribe API test prompt")
    b64_audio = base64.b64encode(wav_bytes).decode("utf-8")

    # Transcribe via base64 form
    res_transcribe = client.post(
        "/api/v1/voice/transcribe",
        data={"audio_base64": b64_audio, "vad_filter": "true"}
    )
    assert res_transcribe.status_code == 200
    t_data = res_transcribe.json()
    assert "text" in t_data
    assert "language" in t_data

    # Full Interaction
    res_interact = client.post(
        "/api/v1/voice/interact",
        data={"audio_base64": b64_audio, "provider": "mock"}
    )
    assert res_interact.status_code == 200
    i_data = res_interact.json()
    assert "transcript" in i_data
    assert "text_response" in i_data
    assert "audio_base64" in i_data

    # Error handling for missing audio
    res_err = client.post(
        "/api/v1/voice/transcribe",
        data={}
    )
    assert res_err.status_code == 422

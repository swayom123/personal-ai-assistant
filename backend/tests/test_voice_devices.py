import pytest
from backend.app.services.voice.devices_service import devices_service

def test_devices_service_discovery():
    res = devices_service.get_audio_devices()
    assert res is not None
    assert len(res.inputs) > 0, "Should detect at least one input microphone device"
    assert len(res.outputs) > 0, "Should detect at least one output speaker device"
    assert res.default_input is not None
    assert res.default_output is not None

    # Verify input device schema
    mic = res.inputs[0]
    assert mic.type == "input"
    assert len(mic.id) > 0
    assert len(mic.name) > 0

    # Verify output device schema
    speaker = res.outputs[0]
    assert speaker.type == "output"
    assert len(speaker.id) > 0
    assert len(speaker.name) > 0

import pytest
from backend.app.schemas.voice import VoiceState
from backend.app.services.voice.pipeline import VoicePipeline
from backend.app.services.voice.tts.mock_provider import MockTTSProvider

@pytest.mark.asyncio
async def test_voice_pipeline_state_transitions():
    pipeline = VoicePipeline()
    recorded_states = []

    def on_state(st: VoiceState):
        recorded_states.append(st)

    pipeline.subscribe_state(on_state)
    assert pipeline.current_state == VoiceState.IDLE

    pipeline.set_state(VoiceState.LISTENING)
    pipeline.set_state(VoiceState.PROCESSING)
    pipeline.set_state(VoiceState.SPEAKING)
    pipeline.set_state(VoiceState.IDLE)

    assert recorded_states == [
        VoiceState.LISTENING,
        VoiceState.PROCESSING,
        VoiceState.SPEAKING,
        VoiceState.IDLE
    ]

@pytest.mark.asyncio
async def test_voice_pipeline_execution():
    pipeline = VoicePipeline()
    tts = MockTTSProvider()
    audio_input = await tts.synthesize("Pipeline test prompt", speed=1.0)

    res = await pipeline.execute_interaction(
        audio_bytes=audio_input,
        llm_provider="mock",
        llm_model="aether-local-engine"
    )

    assert res is not None
    assert res.transcript is not None
    assert res.text_response is not None
    assert len(res.text_response) > 0
    assert res.voice_state == VoiceState.IDLE
    assert res.processing_time_ms >= 0

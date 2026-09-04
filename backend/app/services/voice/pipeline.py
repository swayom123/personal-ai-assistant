import asyncio
import base64
import logging
import time
from typing import Callable, List, Optional
from backend.app.schemas.voice import VoiceState, VoiceInteractionResponse
from backend.app.services.assistant_engine import assistant_engine
from backend.app.services.voice.stt_service import stt_service
from backend.app.services.voice.tts.factory import tts_factory
from backend.app.services.voice.wake_word.factory import wake_word_factory
from backend.app.services.voice.settings_service import voice_settings_service

logger = logging.getLogger("app.voice.pipeline")

class VoicePipeline:
    def __init__(self):
        self._current_state = VoiceState.IDLE
        self._state_subscribers: List[Callable[[VoiceState], None]] = []
        self._lock = asyncio.Lock()

    @property
    def current_state(self) -> VoiceState:
        return self._current_state

    def set_state(self, state: VoiceState):
        if self._current_state != state:
            logger.info(f"Voice state transition: {self._current_state} -> {state}")
            self._current_state = state
            for sub in self._state_subscribers:
                try:
                    sub(state)
                except Exception as e:
                    logger.warning(f"Error notifying state subscriber: {e}")

    def subscribe_state(self, callback: Callable[[VoiceState], None]):
        if callback not in self._state_subscribers:
            self._state_subscribers.append(callback)

    def unsubscribe_state(self, callback: Callable[[VoiceState], None]):
        if callback in self._state_subscribers:
            self._state_subscribers.remove(callback)

    def check_wake_word(self, audio_chunk: bytes) -> bool:
        detector = wake_word_factory.get_detector()
        return detector.detect(audio_chunk)

    async def execute_interaction(
        self,
        audio_bytes: bytes,
        conversation_id: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
    ) -> VoiceInteractionResponse:
        """
        Full Pipeline:
        Audio -> Whisper (STT) -> AI Engine (LLM) -> TTS -> Audio
        """
        start_time = time.time()
        settings = voice_settings_service.get_settings()

        async with self._lock:
            try:
                # 1. State -> LISTENING / PROCESSING
                self.set_state(VoiceState.LISTENING)
                await asyncio.sleep(0.05)
                self.set_state(VoiceState.PROCESSING)

                # 2. Whisper Speech-to-text
                stt_res = await stt_service.transcribe(
                    audio_bytes=audio_bytes,
                    language=settings.language if settings.language != "auto" else None,
                    vad_filter=settings.vad_filter
                )

                transcript = stt_res.text.strip()
                if not transcript or transcript == "(No audible speech detected)":
                    self.set_state(VoiceState.IDLE)
                    return VoiceInteractionResponse(
                        transcript=transcript or "No speech detected",
                        text_response="I didn't catch that. Could you please speak again?",
                        conversation_id=conversation_id or "",
                        audio_base64=None,
                        voice_state=VoiceState.IDLE,
                        processing_time_ms=round((time.time() - start_time) * 1000, 2)
                    )

                # 3. AI Core Engine (LLM reasoning & context)
                from backend.app.schemas.llm import ChatRequest
                chat_req = ChatRequest(
                    message=transcript,
                    conversation_id=conversation_id,
                    provider=llm_provider,
                    model=llm_model
                )
                ai_response = await assistant_engine.chat(chat_req)
                ai_text = ai_response.message.content

                # 4. Text-To-Speech
                self.set_state(VoiceState.SPEAKING)
                tts_provider = tts_factory.get_provider(settings.tts_provider)
                audio_out_bytes = await tts_provider.synthesize(
                    text=ai_text,
                    voice=settings.voice,
                    speed=settings.speed,
                    volume=settings.volume
                )

                audio_b64 = base64.b64encode(audio_out_bytes).decode("utf-8")

                elapsed_ms = round((time.time() - start_time) * 1000, 2)
                self.set_state(VoiceState.IDLE)

                return VoiceInteractionResponse(
                    transcript=transcript,
                    text_response=ai_text,
                    conversation_id=ai_response.conversation_id,
                    audio_base64=audio_b64,
                    voice_state=VoiceState.IDLE,
                    processing_time_ms=elapsed_ms
                )

            except Exception as e:
                logger.error(f"Voice interaction failed: {e}", exc_info=True)
                self.set_state(VoiceState.ERROR)
                await asyncio.sleep(0.5)
                self.set_state(VoiceState.IDLE)
                raise e

voice_pipeline = VoicePipeline()

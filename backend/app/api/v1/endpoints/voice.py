import asyncio
import base64
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect, status
from fastapi.responses import Response

from backend.app.schemas.voice import (
    AudioDevicesResponse,
    TranscriptionResponse,
    TTSRequest,
    TTSResponse,
    VoiceInfo,
    VoiceInteractionRequest,
    VoiceInteractionResponse,
    VoiceSettings,
    VoiceState,
)
from backend.app.services.voice.devices_service import devices_service
from backend.app.services.voice.pipeline import voice_pipeline
from backend.app.services.voice.settings_service import voice_settings_service
from backend.app.services.voice.stt_service import stt_service
from backend.app.services.voice.tts.factory import tts_factory
from backend.app.services.voice.wake_word.factory import wake_word_factory

logger = logging.getLogger("app.api.voice")
router = APIRouter()

@router.get("/devices", response_model=AudioDevicesResponse, summary="List audio input and output devices")
async def get_audio_devices():
    """Retrieve available microphone and speaker devices on the system."""
    return devices_service.get_audio_devices()

@router.get("/settings", response_model=VoiceSettings, summary="Get voice subsystem configuration")
async def get_voice_settings():
    """Get current voice settings including microphone, speaker, speed, volume, and wake word."""
    return voice_settings_service.get_settings()

@router.put("/settings", response_model=VoiceSettings, summary="Update voice configuration")
async def update_voice_settings(settings: VoiceSettings):
    """Update persistent voice settings."""
    updated = voice_settings_service.update_settings(settings)
    # Also synchronize active wake word
    detector = wake_word_factory.get_detector()
    detector.set_wake_word(updated.wake_word)
    return updated

@router.get("/voices", response_model=List[VoiceInfo], summary="List available TTS voices")
async def list_voices():
    """List voices supported across Piper, Coqui, and fallback TTS providers."""
    return tts_factory.list_all_voices()

@router.post("/transcribe", response_model=TranscriptionResponse, summary="Transcribe audio to text")
async def transcribe_audio(
    file: Optional[UploadFile] = File(None),
    audio_base64: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    vad_filter: bool = Form(True)
):
    """
    Transcribe speech using Faster-Whisper.
    Accepts either an uploaded audio file (WAV, MP3, WebM, OGG) or base64-encoded audio.
    Supports language detection and VAD noise reduction.
    """
    audio_bytes: Optional[bytes] = None

    if file is not None:
        audio_bytes = await file.read()
    elif audio_base64 is not None:
        try:
            # Strip data URL prefix if provided
            raw_b64 = audio_base64.split(",")[-1]
            audio_bytes = base64.b64decode(raw_b64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid base64 audio data: {e}"
            )

    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Audio data is required (via file upload or audio_base64 field)"
        )

    try:
        res = await stt_service.transcribe(
            audio_bytes=audio_bytes,
            language=language,
            vad_filter=vad_filter
        )
        return res
    except Exception as e:
        logger.error(f"Transcription failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription failed: {str(e)}"
        )

@router.post("/speak", summary="Synthesize speech from text")
async def speak_text(
    request: TTSRequest,
    output_format: str = Query("audio", description="'audio' for WAV binary stream, or 'json' for base64 response")
):
    """
    Synthesize text to speech using configured TTS provider (Piper / Coqui / Fallback).
    Returns WAV binary stream by default, or JSON with base64 payload.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Text cannot be empty"
        )

    try:
        settings = voice_settings_service.get_settings()
        provider_name = request.provider or settings.tts_provider
        provider = tts_factory.get_provider(provider_name)

        audio_bytes = await provider.synthesize(
            text=request.text,
            voice=request.voice or settings.voice,
            speed=request.speed or settings.speed,
            volume=request.volume or settings.volume
        )

        if output_format == "json":
            b64 = base64.b64encode(audio_bytes).decode("utf-8")
            return TTSResponse(audio_base64=b64, mime_type="audio/wav")

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "Cache-Control": "no-cache"
            }
        )
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )

@router.post("/interact", response_model=VoiceInteractionResponse, summary="Full duplex voice interaction")
async def voice_interaction(
    file: Optional[UploadFile] = File(None),
    audio_base64: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    model: Optional[str] = Form(None)
):
    """
    Execute end-to-end voice pipeline:
    Microphone Audio -> Whisper STT -> AI Core Context -> TTS -> Audio Speech Response
    """
    audio_bytes: Optional[bytes] = None

    if file is not None:
        audio_bytes = await file.read()
    elif audio_base64 is not None:
        try:
            raw_b64 = audio_base64.split(",")[-1]
            audio_bytes = base64.b64decode(raw_b64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid base64 audio: {e}"
            )

    if not audio_bytes or len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Audio recording data is required"
        )

    try:
        response = await voice_pipeline.execute_interaction(
            audio_bytes=audio_bytes,
            conversation_id=conversation_id,
            llm_provider=provider,
            llm_model=model
        )
        return response
    except Exception as e:
        logger.error(f"Voice interaction pipeline error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice interaction failed: {str(e)}"
        )

@router.websocket("/stream")
async def voice_websocket_stream(websocket: WebSocket):
    """
    Real-time duplex WebSocket for streaming voice interactions:
    - Audio chunk streaming
    - Wake word detection
    - Live state transitions: IDLE, LISTENING, PROCESSING, SPEAKING, ERROR
    - Partial transcription updates
    """
    await websocket.accept()
    logger.info("Voice WebSocket client connected")

    loop = asyncio.get_running_loop()

    # Hook into state transitions
    def send_state_update(st: VoiceState):
        try:
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({
                    "type": "state_change",
                    "state": st.value
                }),
                loop
            )
        except Exception:
            pass

    voice_pipeline.subscribe_state(send_state_update)

    try:
        # Send initial state
        await websocket.send_json({
            "type": "state_change",
            "state": voice_pipeline.current_state.value
        })

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "wake_word_check":
                    audio_b64 = msg.get("audio_chunk", "")
                    chunk_bytes = base64.b64decode(audio_b64.split(",")[-1])
                    detected = voice_pipeline.check_wake_word(chunk_bytes)
                    if detected:
                        settings = voice_settings_service.get_settings()
                        await websocket.send_json({
                            "type": "wake_word_detected",
                            "wake_word": settings.wake_word,
                            "assistant_name": settings.assistant_name
                        })

                elif msg_type == "interact":
                    audio_b64 = msg.get("audio_base64", "")
                    conv_id = msg.get("conversation_id")
                    prov = msg.get("provider")
                    mod = msg.get("model")

                    audio_bytes = base64.b64decode(audio_b64.split(",")[-1])
                    result = await voice_pipeline.execute_interaction(
                        audio_bytes=audio_bytes,
                        conversation_id=conv_id,
                        llm_provider=prov,
                        llm_model=mod
                    )
                    await websocket.send_json({
                        "type": "interaction_result",
                        "transcript": result.transcript,
                        "text_response": result.text_response,
                        "conversation_id": result.conversation_id,
                        "audio_base64": result.audio_base64,
                        "processing_time_ms": result.processing_time_ms
                    })

                elif msg_type == "set_state":
                    requested_state = msg.get("state")
                    if requested_state in VoiceState._value2member_map_:
                        voice_pipeline.set_state(VoiceState(requested_state))

            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

    except WebSocketDisconnect:
        logger.info("Voice WebSocket client disconnected")
    finally:
        voice_pipeline.unsubscribe_state(send_state_update)

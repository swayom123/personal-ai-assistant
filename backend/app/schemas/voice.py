from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class VoiceState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"

class AudioDevice(BaseModel):
    id: str
    name: str
    is_default: bool = False
    type: str = Field(description="'input' or 'output'")
    channels: int = 2
    sample_rate: int = 44100

class AudioDevicesResponse(BaseModel):
    inputs: List[AudioDevice] = Field(default_factory=list)
    outputs: List[AudioDevice] = Field(default_factory=list)
    default_input: Optional[str] = None
    default_output: Optional[str] = None

class TranscriptionSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str

class TranscriptionResponse(BaseModel):
    text: str
    language: str = "en"
    language_probability: float = 1.0
    duration: float = 0.0
    segments: List[TranscriptionSegment] = Field(default_factory=list)

class VoiceInfo(BaseModel):
    id: str
    name: str
    provider: str
    language: str = "en"
    gender: Optional[str] = "neutral"

class TTSRequest(BaseModel):
    text: str
    provider: Optional[str] = None
    voice: Optional[str] = None
    speed: Optional[float] = 1.0
    volume: Optional[float] = 1.0

class TTSResponse(BaseModel):
    audio_base64: str
    mime_type: str = "audio/wav"
    duration: Optional[float] = None
    sample_rate: int = 22050

class VoiceSettings(BaseModel):
    microphone: Optional[str] = "default"
    speaker: Optional[str] = "default"
    voice: str = "en_US-lessac-medium"
    speed: float = 1.0
    volume: float = 1.0
    wake_word: str = "Hey Max"
    assistant_name: str = "Max"
    language: str = "en"
    tts_provider: str = "piper"
    stt_model: str = "base"
    vad_filter: bool = True

class VoiceInteractionRequest(BaseModel):
    audio_base64: Optional[str] = None
    conversation_id: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None

class VoiceInteractionResponse(BaseModel):
    transcript: str
    text_response: str
    conversation_id: str
    audio_base64: Optional[str] = None
    voice_state: VoiceState = VoiceState.IDLE
    processing_time_ms: float = 0.0

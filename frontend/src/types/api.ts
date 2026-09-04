export type Role = 'system' | 'user' | 'assistant';

export interface ChatMessage {
  role: Role;
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  model?: string;
  provider?: string;
  temperature?: number;
  stream?: boolean;
}

export interface ChatResponse {
  id: string;
  conversation_id: string;
  message: ChatMessage;
  model: string;
  provider: string;
  created_at: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  description?: string;
  is_default?: boolean;
}

export interface ModelsResponse {
  active_provider: string;
  models: ModelInfo[];
}

export interface ConversationItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail extends ConversationItem {
  messages: ChatMessage[];
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  timestamp?: string;
}

export interface ApiError {
  message: string;
  statusCode?: number;
  details?: Record<string, unknown>;
  requestId?: string;
}

export interface SystemInfo {
  version: string;
  uptime: number;
  environment: string;
}

// Phase 4 — Voice Assistant Types
export type VoiceState = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'SPEAKING' | 'ERROR';

export interface AudioDevice {
  id: string;
  name: string;
  is_default: boolean;
  type: 'input' | 'output';
  channels: number;
  sample_rate: number;
}

export interface AudioDevicesResponse {
  inputs: AudioDevice[];
  outputs: AudioDevice[];
  default_input?: string;
  default_output?: string;
}

export interface VoiceSettings {
  microphone?: string;
  speaker?: string;
  voice: string;
  speed: number;
  volume: number;
  wake_word: string;
  assistant_name: string;
  language: string;
  tts_provider: string;
  stt_model: string;
  vad_filter: boolean;
}

export interface VoiceInfo {
  id: string;
  name: string;
  provider: string;
  language: string;
  gender?: string;
}

export interface TranscriptionSegment {
  id: number;
  start: number;
  end: number;
  text: string;
}

export interface TranscriptionResponse {
  text: string;
  language: string;
  language_probability: number;
  duration: number;
  segments: TranscriptionSegment[];
}

export interface VoiceInteractionResponse {
  transcript: string;
  text_response: string;
  conversation_id: string;
  audio_base64?: string;
  voice_state: VoiceState;
  processing_time_ms: number;
}

import {
  HealthResponse,
  ChatRequest,
  ChatResponse,
  ModelsResponse,
  ConversationItem,
  ConversationDetail,
  AudioDevicesResponse,
  VoiceSettings,
  VoiceInfo,
  TranscriptionResponse,
  VoiceInteractionResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  // Health Endpoints
  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`Health check failed with HTTP ${response.status}`);
    return response.json();
  }

  async checkApiV1Health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`API v1 health check failed with HTTP ${response.status}`);
    return response.json();
  }

  // Models Endpoint
  async getModels(): Promise<ModelsResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/models`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`Failed to load models: HTTP ${response.status}`);
    return response.json();
  }

  // Chat Completion (Non-Streaming)
  async sendChatMessage(req: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(req),
    });
    if (!response.ok) {
      const errBody = await response.json().catch(() => ({}));
      throw new Error(errBody.error?.message || `Chat request failed with HTTP ${response.status}`);
    }
    return response.json();
  }

  // Chat Completion (Server-Sent Events Streaming)
  async streamChatMessage(
    req: ChatRequest,
    callbacks: {
      onMeta?: (meta: { conversation_id: string; model: string; provider: string }) => void;
      onChunk: (chunk: string) => void;
      onDone: (fullContent: string) => void;
      onError: (err: Error) => void;
    }
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({ ...req, stream: true }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error?.message || `Stream request failed: HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is empty or streaming unsupported.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const jsonStr = trimmed.slice(6);
            try {
              const parsed = JSON.parse(jsonStr);
              if (parsed.type === 'meta' && callbacks.onMeta) {
                callbacks.onMeta(parsed);
              } else if (parsed.type === 'content') {
                accumulatedContent += parsed.content;
                callbacks.onChunk(parsed.content);
              } else if (parsed.type === 'done') {
                callbacks.onDone(parsed.full_content || accumulatedContent);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE event:', e);
            }
          }
        }
      }

      callbacks.onDone(accumulatedContent);
    } catch (err: unknown) {
      callbacks.onError(err instanceof Error ? err : new Error(String(err)));
    }
  }

  // Conversation Management
  async listConversations(): Promise<ConversationItem[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`Failed to list conversations: HTTP ${response.status}`);
    return response.json();
  }

  async createConversation(title?: string): Promise<ConversationItem> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error(`Failed to create conversation: HTTP ${response.status}`);
    return response.json();
  }

  async getConversation(id: string): Promise<ConversationDetail> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${id}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`Failed to get conversation: HTTP ${response.status}`);
    return response.json();
  }

  async renameConversation(id: string, title: string): Promise<ConversationItem> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error(`Failed to rename conversation: HTTP ${response.status}`);
    return response.json();
  }

  async deleteConversation(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/conversations/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error(`Failed to delete conversation: HTTP ${response.status}`);
  }

  // Phase 4 — Voice Assistant Methods
  async getVoiceDevices(): Promise<AudioDevicesResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/voice/devices`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`Failed to get voice devices: HTTP ${response.status}`);
    return response.json();
  }

  async getVoiceSettings(): Promise<VoiceSettings> {
    const response = await fetch(`${this.baseUrl}/api/v1/voice/settings`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`Failed to get voice settings: HTTP ${response.status}`);
    return response.json();
  }

  async updateVoiceSettings(settings: VoiceSettings): Promise<VoiceSettings> {
    const response = await fetch(`${this.baseUrl}/api/v1/voice/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(settings),
    });
    if (!response.ok) throw new Error(`Failed to update voice settings: HTTP ${response.status}`);
    return response.json();
  }

  async getVoiceVoices(): Promise<VoiceInfo[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/voice/voices`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`Failed to get voices: HTTP ${response.status}`);
    return response.json();
  }

  async transcribeAudio(
    audio: Blob | string,
    language?: string,
    vadFilter = true
  ): Promise<TranscriptionResponse> {
    const formData = new FormData();
    if (typeof audio === 'string') {
      formData.append('audio_base64', audio);
    } else {
      formData.append('file', audio, 'recording.webm');
    }
    if (language) formData.append('language', language);
    formData.append('vad_filter', vadFilter ? 'true' : 'false');

    const response = await fetch(`${this.baseUrl}/api/v1/voice/transcribe`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error(`Transcription failed: HTTP ${response.status}`);
    return response.json();
  }

  async speakText(
    text: string,
    options: { provider?: string; voice?: string; speed?: number; volume?: number } = {}
  ): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/voice/speak?output_format=audio`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        provider: options.provider,
        voice: options.voice,
        speed: options.speed,
        volume: options.volume,
      }),
    });
    if (!response.ok) throw new Error(`Speech synthesis failed: HTTP ${response.status}`);
    return response.blob();
  }

  async voiceInteract(
    audio: Blob | string,
    options: { conversationId?: string; provider?: string; model?: string } = {}
  ): Promise<VoiceInteractionResponse> {
    const formData = new FormData();
    if (typeof audio === 'string') {
      formData.append('audio_base64', audio);
    } else {
      formData.append('file', audio, 'user_prompt.webm');
    }
    if (options.conversationId) formData.append('conversation_id', options.conversationId);
    if (options.provider) formData.append('provider', options.provider);
    if (options.model) formData.append('model', options.model);

    const response = await fetch(`${this.baseUrl}/api/v1/voice/interact`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error(`Voice interaction failed: HTTP ${response.status}`);
    return response.json();
  }

  getVoiceWsUrl(): string {
    const wsBase = this.baseUrl.replace(/^http:\/\//, 'ws://').replace(/^https:\/\//, 'wss://');
    return `${wsBase}/api/v1/voice/stream`;
  }
}

export const apiService = new ApiService(API_BASE_URL);

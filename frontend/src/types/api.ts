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
  environment: string;
  architecture: string;
  isElectron: boolean;
}

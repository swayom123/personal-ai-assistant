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

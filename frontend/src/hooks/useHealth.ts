import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { useAppStore } from '../stores/appStore';
import { HealthResponse } from '../types/api';

export function useHealth(autoPoll: boolean = false, pollIntervalMs: number = 10000) {
  const { health, setHealth, healthLoading, setHealthLoading, healthError, setHealthError } = useAppStore();
  const [latency, setLatency] = useState<number | null>(null);

  const fetchHealth = useCallback(async (): Promise<HealthResponse | null> => {
    setHealthLoading(true);
    const start = performance.now();
    try {
      const data = await apiService.checkHealth();
      const elapsed = Math.round(performance.now() - start);
      setLatency(elapsed);
      setHealth(data);
      return data;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to connect to backend';
      setHealthError(message);
      setLatency(null);
      return null;
    } finally {
      setHealthLoading(false);
    }
  }, [setHealth, setHealthLoading, setHealthError]);

  useEffect(() => {
    fetchHealth();

    if (!autoPoll) return;
    const interval = setInterval(fetchHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [fetchHealth, autoPoll, pollIntervalMs]);

  return {
    health,
    latency,
    isLoading: healthLoading,
    error: healthError,
    refetch: fetchHealth,
  };
}

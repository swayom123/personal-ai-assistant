import React from 'react';
import { useHealth } from '../hooks/useHealth';
import { StatusBadge } from './StatusBadge';
import { Activity, RefreshCw } from 'lucide-react';

export const HealthIndicator: React.FC = () => {
  const { health, latency, isLoading, error, refetch } = useHealth(true, 15000);

  const status = isLoading && !health ? 'loading' : health?.status === 'ok' ? 'ok' : 'error';

  return (
    <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-surface border border-border text-xs font-mono">
      <Activity className="w-3.5 h-3.5 text-primary" />
      <StatusBadge status={status} size="sm" />
      {latency !== null && (
        <span className="text-text-secondary hidden sm:inline">{latency}ms</span>
      )}
      <button
        onClick={() => refetch()}
        disabled={isLoading}
        className="p-1 hover:bg-surface-elevated rounded text-text-secondary hover:text-text-primary transition-colors disabled:opacity-50"
        title={error || 'Refresh Health Status'}
      >
        <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
      </button>
    </div>
  );
};

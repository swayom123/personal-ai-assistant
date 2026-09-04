import React from 'react';
import { cn } from '../utils/cn';

interface StatusBadgeProps {
  status: 'ok' | 'degraded' | 'error' | 'loading';
  label?: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, size = 'md' }) => {
  const statusStyles = {
    ok: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    degraded: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    error: 'bg-red-500/15 text-red-400 border-red-500/30',
    loading: 'bg-zinc-500/15 text-zinc-400 border-zinc-500/30',
  };

  const dotStyles = {
    ok: 'bg-emerald-400 animate-pulse',
    degraded: 'bg-amber-400',
    error: 'bg-red-400',
    loading: 'bg-zinc-400 animate-spin',
  };

  const defaultLabels = {
    ok: 'Operational',
    degraded: 'Degraded',
    error: 'Offline',
    loading: 'Connecting...',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-mono font-medium rounded-full border',
        size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs',
        statusStyles[status]
      )}
    >
      <span className={cn('rounded-full', size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2', dotStyles[status])} />
      {label || defaultLabels[status]}
    </span>
  );
};

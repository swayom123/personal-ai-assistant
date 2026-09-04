import React from 'react';
import { HealthIndicator } from './HealthIndicator';
import { Laptop, Moon, Layers } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { useElectron } from '../hooks/useElectron';
import { cn } from '../utils/cn';

export const TopBar: React.FC = () => {
  const { sidebarOpen } = useAppStore();
  const { isElectron, platform } = useElectron();

  return (
    <header
      className={cn(
        'h-16 fixed top-0 right-0 border-b border-border bg-background/80 backdrop-blur-md z-30 transition-all duration-300 px-6 flex items-center justify-between',
        sidebarOpen ? 'left-64' : 'left-20'
      )}
    >
      {/* Left Title / Breadcrumbs */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-mono text-text-muted">
          <Layers className="w-4 h-4 text-primary" />
          <span>PHASE 1</span>
          <span>/</span>
          <span className="text-text-primary font-medium">FOUNDATION & ARCHITECTURE</span>
        </div>
      </div>

      {/* Right Tools & Indicators */}
      <div className="flex items-center gap-4">
        {/* Environment Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface border border-border text-xs font-mono text-text-secondary">
          <Laptop className="w-3.5 h-3.5 text-accent-cyan" />
          <span>{isElectron ? 'Electron Host' : `Web Client (${platform})`}</span>
        </div>

        {/* Live Backend Health Checker */}
        <HealthIndicator />

        {/* Dark Theme Indicator */}
        <div className="p-2 rounded-lg bg-surface border border-border text-text-secondary" title="Dark Theme Enforced">
          <Moon className="w-4 h-4 text-accent-violet" />
        </div>
      </div>
    </header>
  );
};

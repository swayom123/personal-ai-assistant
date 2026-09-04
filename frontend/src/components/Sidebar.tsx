import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  Mic,
  Brain,
  FolderTree,
  Workflow,
  Settings,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Terminal,
} from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { cn } from '../utils/cn';

export const Sidebar: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useAppStore();

  const navItems = [
    { title: 'Overview', path: '/', icon: LayoutDashboard, phase: 1 },
    { title: 'AI Chat', path: '/chat', icon: MessageSquare, phase: 2, disabled: true },
    { title: 'Voice & Audio', path: '/voice', icon: Mic, phase: 3, disabled: true },
    { title: 'Semantic Memory', path: '/memory', icon: Brain, phase: 4, disabled: true },
    { title: 'Workspace Files', path: '/files', icon: FolderTree, phase: 5, disabled: true },
    { title: 'Automations', path: '/automations', icon: Workflow, phase: 6, disabled: true },
    { title: 'Diagnostics & Logs', path: '/diagnostics', icon: Terminal, phase: 1 },
    { title: 'Settings', path: '/settings', icon: Settings, phase: 1 },
  ];

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-surface border-r border-border z-40 transition-all duration-300 flex flex-col justify-between select-none',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-border">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent-violet p-0.5 flex items-center justify-center shrink-0 shadow-lg shadow-primary/20">
              <div className="w-full h-full bg-background rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-primary" />
              </div>
            </div>
            {sidebarOpen && (
              <div className="truncate">
                <h1 className="font-semibold text-sm text-text-primary tracking-tight">AI Assistant</h1>
                <p className="text-[11px] font-mono text-text-muted">Phase 1 Foundation</p>
              </div>
            )}
          </div>
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-lg hover:bg-surface-elevated text-text-secondary hover:text-text-primary transition-colors"
            title={sidebarOpen ? 'Collapse Sidebar' : 'Expand Sidebar'}
          >
            {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.title}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors relative group',
                    isActive
                      ? 'bg-primary/10 text-primary border-l-2 border-primary font-semibold'
                      : 'text-text-secondary hover:text-text-primary hover:bg-surface-elevated',
                    item.disabled && 'opacity-40 cursor-not-allowed hover:bg-transparent'
                  )
                }
                onClick={(e) => {
                  if (item.disabled) e.preventDefault();
                }}
              >
                <Icon className="w-5 h-5 shrink-0" />
                {sidebarOpen && (
                  <div className="flex-1 flex items-center justify-between truncate">
                    <span className="truncate">{item.title}</span>
                    {item.disabled ? (
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-surface-elevated text-text-muted border border-border">
                        P{item.phase}
                      </span>
                    ) : (
                      item.phase === 1 && (
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-primary/20 text-primary border border-primary/30">
                          Active
                        </span>
                      )
                    )}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-border">
        {sidebarOpen ? (
          <div className="p-2.5 rounded-lg bg-background border border-border text-xs space-y-1">
            <div className="flex justify-between text-text-muted font-mono text-[11px]">
              <span>Architecture</span>
              <span className="text-emerald-400">Modular</span>
            </div>
            <div className="flex justify-between text-text-muted font-mono text-[11px]">
              <span>Target</span>
              <span className="text-text-primary">Laptop / Desktop</span>
            </div>
          </div>
        ) : (
          <div className="w-2 h-2 rounded-full bg-emerald-400 mx-auto" title="Phase 1 Active" />
        )}
      </div>
    </aside>
  );
};

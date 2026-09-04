import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Server,
  Layers,
  Cpu,
  Terminal,
  RefreshCw,
  FolderTree,
  Globe,
  Mic,
  ArrowRight,
} from 'lucide-react';
import { useHealth } from '../hooks/useHealth';
import { apiService } from '../services/api';
import { HealthResponse } from '../types/api';

export const HomePage: React.FC = () => {
  const { health, latency, isLoading, error } = useHealth(false);
  const [manualHealthResponse, setManualHealthResponse] = useState<HealthResponse | null>(null);
  const [manualLoading, setManualLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'status' | 'architecture' | 'phases'>('status');

  const testEndpoint = async (type: 'root' | 'v1') => {
    setManualLoading(true);
    try {
      const res = type === 'root' ? await apiService.checkHealth() : await apiService.checkApiV1Health();
      setManualHealthResponse(res);
    } catch (err) {
      console.error(err);
    } finally {
      setManualLoading(false);
    }
  };

  const foundationPillars = [
    {
      title: 'FastAPI 0.115+ Backend',
      desc: 'Modular ASGI architecture with lifespan lifecycle, global exception handling, and Pydantic validation.',
      status: 'Verified',
      icon: Server,
    },
    {
      title: 'Request ID & Structured Logging',
      desc: 'Middleware attaching X-Request-ID and latency timers to every request, logged to console and file.',
      status: 'Active',
      icon: Terminal,
    },
    {
      title: 'React 18 + Vite + Tailwind',
      desc: 'Component architecture with dark theme, Lucide icons, Zustand state management, and React Router.',
      status: 'Running',
      icon: Globe,
    },
    {
      title: 'Electron Desktop Architecture',
      desc: 'Pre-configured contextBridge preload and IPC architecture prepared for packaging as a native laptop application.',
      status: 'Prepped',
      icon: Cpu,
    },
  ];

  const phaseRoadmap = [
    { phase: 1, title: 'Foundation & Core Architecture', desc: 'FastAPI, React frontend shell, logging, health check, Electron bridge.', current: false, status: 'Completed' },
    { phase: 3, title: 'AI Core and LLM Engine', desc: 'OpenAI/Ollama/Mock providers, context builder, SSE streaming chat, conversations.', current: false, status: 'Completed' },
    { phase: 4, title: 'Voice Assistant & Audio Pipeline', desc: 'Faster-Whisper STT, Piper/Coqui TTS, OpenWakeWord/Porcupine, duplex voice studio.', current: true, status: 'Completed' },
    { phase: 5, title: 'Semantic Memory & Knowledge Graph', desc: 'Vector embeddings, user facts, episodic context recall.', current: false, status: 'Upcoming' },
    { phase: 6, title: 'Desktop Workspace & Automations', desc: 'Local file indexing, window controls, scheduled routines, MCP tools.', current: false, status: 'Upcoming' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Hero Welcome Banner */}
      <section className="p-6 md:p-8 rounded-2xl bg-gradient-to-r from-surface to-surface-subtle border border-border relative overflow-hidden shadow-xl">
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-muted border border-primary/30 text-primary text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            Phase 1, 3 & 4 Active • Voice Assistant & AI Core
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-text-primary">
            Duplex Voice & Central AI Engine
          </h1>
          <p className="text-text-secondary text-sm md:text-base leading-relaxed">
            Production-grade personal laptop AI assistant. Central LLM reasoning engine, Faster-Whisper
            speech-to-text, Piper text-to-speech, configurable wake-word detection, and real-time audio interaction.
          </p>
        </div>
      </section>

      {/* Tabs */}
      <div className="flex border-b border-border space-x-6 text-sm font-medium">
        <button
          onClick={() => setActiveTab('status')}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === 'status'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          System Verification
        </button>
        <button
          onClick={() => setActiveTab('architecture')}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === 'architecture'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          Project Architecture
        </button>
        <button
          onClick={() => setActiveTab('phases')}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === 'phases'
              ? 'border-primary text-primary font-semibold'
              : 'border-transparent text-text-secondary hover:text-text-primary'
          }`}
        >
          Phase Roadmap
        </button>
      </div>

      {activeTab === 'status' && (
        <div className="space-y-6">
          {/* Health Verification Playground Card */}
          <div className="glass-card p-6 rounded-2xl border border-border space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
              <div>
                <h3 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                  <Server className="w-5 h-5 text-primary" />
                  Backend Health Verification
                </h3>
                <p className="text-xs text-text-secondary font-mono mt-0.5">
                  Verified endpoint: <code className="text-primary">GET /health</code> and <code className="text-primary">GET /api/v1/health</code>
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => testEndpoint('root')}
                  disabled={manualLoading}
                  className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-mono flex items-center gap-1.5 transition-all shadow-md shadow-primary/20 disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${manualLoading ? 'animate-spin' : ''}`} />
                  Test GET /health
                </button>
                <button
                  onClick={() => testEndpoint('v1')}
                  disabled={manualLoading}
                  className="px-3 py-1.5 rounded-lg bg-surface-elevated hover:bg-border text-text-primary text-xs font-mono flex items-center gap-1.5 transition-all border border-border"
                >
                  Test GET /api/v1/health
                </button>
              </div>
            </div>

            {/* Response Box */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-background border border-border space-y-2 font-mono text-xs">
                <div className="text-text-muted flex justify-between">
                  <span>Current Hook State:</span>
                  <span className={health?.status === 'ok' ? 'text-emerald-400 font-bold' : 'text-red-400'}>
                    {isLoading ? 'Polling...' : health?.status === 'ok' ? 'ONLINE (200 OK)' : 'OFFLINE'}
                  </span>
                </div>
                <div className="text-text-secondary">
                  Service Name: <span className="text-text-primary">{health?.service || 'personal-ai-assistant'}</span>
                </div>
                <div className="text-text-secondary">
                  Ping Latency: <span className="text-accent-cyan">{latency !== null ? `${latency}ms` : 'N/A'}</span>
                </div>
                {error && <div className="text-red-400 font-mono text-[11px] pt-1">Error: {error}</div>}
              </div>

              <div className="p-4 rounded-xl bg-background border border-border space-y-1 font-mono text-xs">
                <div className="text-text-muted">Live JSON Payload:</div>
                <pre className="text-emerald-400 overflow-x-auto p-2 rounded bg-surface/50 border border-border/50 text-[11px]">
                  {JSON.stringify(manualHealthResponse || health || { status: 'ok', service: 'personal-ai-assistant' }, null, 2)}
                </pre>
              </div>
            </div>
          </div>

          {/* Phase 4 Voice Assistant Subsystem Quick Card */}
          <div className="glass-card p-6 rounded-2xl border border-border bg-gradient-to-r from-surface to-surface-subtle space-y-4 shadow-md">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-primary/10 text-primary border border-primary/20">
                  <Mic className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-text-primary">
                    Voice Assistant Subsystem (Phase 4)
                  </h3>
                  <p className="text-xs text-text-secondary">
                    Faster-Whisper STT • Piper TTS • OpenWakeWord & Porcupine Ready
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Link
                  to="/voice"
                  className="px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-xs font-medium flex items-center gap-2 transition-all shadow-md shadow-primary/20"
                >
                  Open Voice Studio
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-background border border-border">
                <span className="text-text-muted text-[11px] block">Wake Word</span>
                <span className="text-primary font-bold">"Hey Max"</span>
              </div>
              <div className="p-3 rounded-xl bg-background border border-border">
                <span className="text-text-muted text-[11px] block">Speech-to-Text</span>
                <span className="text-text-primary">Faster-Whisper (base)</span>
              </div>
              <div className="p-3 rounded-xl bg-background border border-border">
                <span className="text-text-muted text-[11px] block">Text-to-Speech</span>
                <span className="text-text-primary">Piper ONNX</span>
              </div>
              <div className="p-3 rounded-xl bg-background border border-border">
                <span className="text-text-muted text-[11px] block">States</span>
                <span className="text-emerald-400">IDLE • DUPLEX</span>
              </div>
            </div>
          </div>

          {/* Pillars Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {foundationPillars.map((pillar) => {
              const Icon = pillar.icon;
              return (
                <div key={pillar.title} className="glass-card p-5 rounded-xl border border-border space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/20">
                        <Icon className="w-4 h-4" />
                      </div>
                      <h4 className="font-semibold text-sm text-text-primary">{pillar.title}</h4>
                    </div>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {pillar.status}
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed">{pillar.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {activeTab === 'architecture' && (
        <div className="glass-card p-6 rounded-2xl border border-border space-y-4 font-mono text-xs">
          <div className="flex items-center gap-2 text-primary font-semibold text-sm">
            <FolderTree className="w-4 h-4" />
            <span>AI_Assistant / Workspace Tree Structure</span>
          </div>
          <pre className="p-4 rounded-xl bg-background border border-border text-text-secondary overflow-x-auto text-[11px] leading-relaxed">
{`AI_Assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI factory, lifespan, CORS, middleware, /health
│   │   ├── config.py            # Pydantic BaseSettings environment config
│   │   ├── logging_config.py    # Structured console and file logging
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py       # API router aggregating v1 routes
│   │   │       └── endpoints/
│   │   │           └── health.py # Health check endpoint
│   │   ├── core/
│   │   │   ├── middleware.py    # X-Request-ID & latency tracker
│   │   │   └── exceptions.py    # Global exception handlers
│   │   ├── services/            # Business logic (Phase 2+)
│   │   ├── models/              # DB / ORM models (Phase 4+)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── utils/               # Helpers and formatters
│   │   └── plugins/             # Extensible plugin system
│   ├── tests/
│   │   ├── conftest.py          # Pytest TestClient fixture
│   │   └── test_health.py       # 5 automated tests for health & middleware
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Sidebar, TopBar, StatusBadge, HealthIndicator
│   │   ├── pages/               # HomePage, NotFoundPage
│   │   ├── layouts/             # AppLayout shell
│   │   ├── hooks/               # useHealth, useElectron
│   │   ├── stores/              # Zustand appStore, themeStore
│   │   ├── services/            # apiService, electronBridge
│   │   ├── types/               # TypeScript interfaces
│   │   └── utils/               # cn tailwind merge helper
│   ├── electron/
│   │   ├── main.ts              # Electron main process blueprint
│   │   └── preload.ts           # contextBridge IPC bridge
│   ├── package.json
│   └── .env.example
│
├── docs/                        # Architecture and phase specifications
├── tests/                       # End-to-end integration tests
├── scripts/                     # Launch and verification shell scripts
├── logs/                        # Persistent runtime execution logs
├── .gitignore
├── README.md
└── LICENSE`}
          </pre>
        </div>
      )}

      {activeTab === 'phases' && (
        <div className="glass-card p-6 rounded-2xl border border-border space-y-4">
          <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
            <Layers className="w-4 h-4 text-primary" />
            Multi-Phase Architecture Roadmap
          </h3>
          <div className="space-y-3">
            {phaseRoadmap.map((item) => (
              <div
                key={item.phase}
                className={`p-4 rounded-xl border transition-all ${
                  item.current
                    ? 'bg-primary/10 border-primary/40 shadow-sm'
                    : 'bg-surface border-border opacity-70'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-primary">PHASE {item.phase}</span>
                    <span className="text-xs font-semibold text-text-primary">• {item.title}</span>
                  </div>
                  {item.current ? (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Active (Phase 1 Target)
                    </span>
                  ) : (
                    <span className="text-[10px] font-mono text-text-muted">Pending Phase 1 Signoff</span>
                  )}
                </div>
                <p className="text-xs text-text-secondary">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

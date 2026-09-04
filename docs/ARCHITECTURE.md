# Personal AI Assistant — Phase 1 Architecture

## Overview
This project establishes the production-grade foundation for an offline-first, private Personal AI Assistant designed for personal laptops and workstations.

Phase 1 focuses strictly on core structural integrity, protocol versioning, structured observability, and a robust client interface shell.

---

## 1. Backend Architecture (`backend/`)

- **Framework**: FastAPI (ASGI) running on Python 3.12+.
- **Configuration**: `Settings` derived from `pydantic_settings.BaseSettings`, reading from `.env` with strict type validation.
- **Observability**:
  - `logging_config.py`: Structured timestamps, log levels, logger namespaces, and file persistence (`logs/app.log`).
  - `RequestIDMiddleware`: Generates or propagates `X-Request-ID` across every HTTP request and measures latency in milliseconds (`X-Process-Time`).
- **Error Handling**:
  - Global hierarchy based on `AppException` with consistent JSON error envelope (`message`, `status_code`, `request_id`).
- **Versioning**:
  - Root health route: `GET /health` -> `{"status": "ok", "service": "personal-ai-assistant"}`
  - Versioned API router: `/api/v1` (`/api/v1/health`, extensible for Phase 2+).

---

## 2. Frontend Architecture (`frontend/`)

- **Runtime & Tooling**: Vite 6, React 18, TypeScript (strict mode enabled).
- **Styling**: Tailwind CSS with dark-mode foundation (#0B0F17 background, elevated glassmorphic panels).
- **State Management**: Zustand lightweight store (`appStore.ts`, `themeStore.ts`).
- **Routing**: React Router v6 with layouts, navigation guards, and phase status indicators.
- **Desktop Architecture**:
  - Electron main process blueprint in `frontend/electron/main.ts`.
  - Context-isolated preload script in `frontend/electron/preload.ts` providing secure IPC wrappers.

---

## 3. Directory Specification

```text
AI_Assistant/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           └── health.py
│   │   ├── core/
│   │   │   ├── middleware.py
│   │   │   └── exceptions.py
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   │   └── health.py
│   │   ├── utils/
│   │   └── plugins/
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_health.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   └── HealthIndicator.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   ├── layouts/
│   │   │   └── AppLayout.tsx
│   │   ├── hooks/
│   │   │   ├── useHealth.ts
│   │   │   └── useElectron.ts
│   │   ├── stores/
│   │   │   ├── appStore.ts
│   │   │   └── themeStore.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── electronBridge.ts
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   ├── navigation.ts
│   │   │   └── electron.d.ts
│   │   └── utils/
│   │       └── cn.ts
│   ├── electron/
│   │   ├── main.ts
│   │   └── preload.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── .env.example
│
├── docs/
│   └── ARCHITECTURE.md
├── tests/
│   └── test_integration.py
├── scripts/
│   ├── run_backend.sh
│   ├── run_frontend.sh
│   └── test_all.sh
├── logs/
│   └── .gitkeep
├── .gitignore
├── README.md
└── LICENSE
```

---

## 4. Multi-Phase Roadmap
- **Phase 1 (Current)**: Personal AI Assistant Foundation (Backend, Frontend Shell, Health Checks, Structured Logs, Electron Preparation).
- **Phase 2**: Agentic AI Core & LLM Orchestration.
- **Phase 3**: Duplex Voice & Audio Engine.
- **Phase 4**: Long-Term Semantic Memory & Vector Knowledge Graph.
- **Phase 5**: Desktop Workspace & Local File Indexer.
- **Phase 6**: Autonomous Workflows & Extensible MCP Plugins.

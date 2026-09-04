# Personal AI Assistant — Phase 1 Foundation

A production-grade, modular Personal AI Assistant designed for personal laptops and workstations.

This repository represents **Phase 1** of a multi-phase engineering roadmap, delivering a robust, offline-capable foundation with a FastAPI backend, a React + TypeScript frontend shell, structured observability, and pre-configured Electron desktop architecture.

---

## 🏗️ Project Architecture

```text
AI_Assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory, lifespan lifecycle, CORS, middleware, /health
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
│   │   ├── services/            # Business logic placeholder (Phase 2+)
│   │   ├── models/              # Data models placeholder (Phase 4+)
│   │   ├── schemas/
│   │   │   └── health.py        # Pydantic request/response schemas
│   │   ├── utils/               # Common utilities and helpers
│   │   └── plugins/             # Extensible plugin system
│   ├── tests/
│   │   ├── conftest.py          # Starlette TestClient fixture
│   │   └── test_health.py       # 5 automated tests for health & middleware
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Backend environment template
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
│   ├── package.json             # Frontend dependencies
│   ├── vite.config.ts           # Vite configuration
│   ├── tsconfig.json            # TypeScript configuration (strict mode)
│   ├── tailwind.config.js       # Tailwind dark theme configuration
│   ├── postcss.config.js        # PostCSS configuration
│   ├── index.html               # Web entrypoint
│   └── .env.example             # Frontend environment template
│
├── docs/
│   └── ARCHITECTURE.md          # Architectural blueprints and roadmap
├── tests/
│   └── test_integration.py     # Root-level integration verification
├── scripts/
│   ├── run_backend.sh           # Backend launch script
│   ├── run_frontend.sh          # Frontend launch script
│   └── test_all.sh              # Unified test runner
├── logs/
│   ├── .gitkeep
│   └── app.log                  # Persistent structured log file
├── .gitignore
├── README.md
└── LICENSE                      # MIT License
```

---

## ⚙️ Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI**: Modern ASGI framework with automatic OpenAPI documentation.
- **Uvicorn**: High-performance ASGI server.
- **Pydantic & pydantic-settings**: Strictly typed settings and data schemas.
- **python-dotenv**: Environment variable management.
- **pytest & httpx**: Automated test execution.

### Frontend
- **React 18** + **TypeScript** (Strict mode)
- **Vite 6**: Fast HMR development and optimized production bundling.
- **Tailwind CSS**: Dark-first palette (`#0B0F17` background, elevated surfaces).
- **Zustand**: Lightweight global state management.
- **React Router v6**: Client-side routing with layout shells.
- **Lucide React**: Clean, modern iconography.
- **Framer Motion**: Smooth interface transitions.

### Desktop
- **Electron Architecture Ready**: Context-isolated `preload.ts` and `main.ts` blueprint.

---

## 🚀 Getting Started

### 1. Installation

#### Backend
```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install --upgrade pip
backend/.venv/bin/pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

#### Frontend
```bash
npm --prefix frontend install
cp frontend/.env.example frontend/.env
```

---

## 🏃 Running the Application

### Option A: Using Helper Scripts
```bash
# Terminal 1: Run Backend
./scripts/run_backend.sh

# Terminal 2: Run Frontend
./scripts/run_frontend.sh
```

### Option B: Manual Commands
```bash
# Backend (http://localhost:8000)
PYTHONPATH=. backend/.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (http://localhost:5173)
npm --prefix frontend run dev
```

---

## 🧪 Testing and Verification

Run the unified test suite:
```bash
./scripts/test_all.sh
```

Or run test suites individually:
```bash
# Backend unit & endpoint tests
PYTHONPATH=. backend/.venv/bin/pytest backend/tests/ -v

# Root integration tests
PYTHONPATH=. backend/.venv/bin/pytest tests/ -v

# Frontend TypeScript check & build
npm --prefix frontend run build
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Sample Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Root health status | `{"status": "ok", "service": "personal-ai-assistant"}` |
| `GET` | `/api/v1/health` | Versioned API v1 health status | `{"status": "ok", "service": "personal-ai-assistant"}` |
| `GET` | `/docs` | Interactive Swagger / OpenAPI docs | Interactive UI |

---

## 🔒 Engineering Standards Met
- **Strict Typing**: Python type hints across all endpoints, schemas, and middlewares; TypeScript strict mode across frontend.
- **Zero Hardcoded Secrets**: All configuration loaded via typed environment variables.
- **Traceability**: Unique `X-Request-ID` attached to all request states and response headers.
- **Structured Logs**: Persisted to `logs/app.log` with timestamp, log level, latency, and request ID.
- **Global Error Handling**: Standardized error envelopes with request IDs.

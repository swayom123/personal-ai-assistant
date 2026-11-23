# Personal AI Assistant — Production Release (v1.0.0)

A private, autonomous, extensible Personal AI Assistant engineered for laptops and workstations.

[![CI Tests](https://img.shields.io/badge/tests-297%20passed-success)](scripts/test_all.sh)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](RELEASE_NOTES.md)
[![Security](https://img.shields.io/badge/security-hardened-blueviolet.svg)](docs/security.md)

---

## 📖 Table of Contents

- [1. Features](#1-features)
- [2. Architecture](#2-architecture)
- [3. Requirements](#3-requirements)
- [4. Installation](#4-installation)
- [5. Configuration](#5-configuration)
- [6. Development](#6-development)
- [7. Testing & Quality Assurance](#7-testing--quality-assurance)
- [8. Building & Desktop Packaging](#8-building--desktop-packaging)
- [9. Troubleshooting](#9-troubleshooting)
- [10. Security & Permissions](#10-security--permissions)
- [11. Plugin Development](#11-plugin-development)
- [12. Documentation Index](#12-documentation-index)

---

## 1. Features

- 🧠 **Autonomous Task Planner**: Natural language instruction decomposition into executable, verified step plans with dependency resolution, observation feedback loops, and intelligent replanning.
- 🗣️ **Local Voice Pipeline**: Continuous on-device wake word detection (`openwakeword`), speech-to-text (`whisper`), and ultra-fast neural speech synthesis (`piper`) with real-time waveform animations.
- 💾 **Multi-Tier Memory & Personalization**: Ephemeral working memory, short-term conversational context, structured facts in SQLite, and dense semantic vector embeddings in ChromaDB with hybrid relevance ranking.
- 💻 **Computer Control Engine**: Secure desktop task execution via `ToolRegistry`, controlling applications, processes, and operating system configuration.
- 🌐 **Web Research & Browser Automation**: Headless Playwright Chromium navigation, DOM text extraction, and automated multi-step research synthesis.
- 📁 **AI File Management**: Watchdog real-time directory indexing, SHA-256 duplicate content detection, rule-based organization, and safe recycling via OS trash (`send2trash`).
- ⚡ **Background Automation & Workflows**: Multi-trigger scheduling engine supporting cron intervals, file creation triggers, system events, and conditional action graphs with automatic retries.
- 🧩 **Extensible Plugin Ecosystem**: Dynamic plugin discovery and sandboxed execution with dynamic Pydantic parameter models and runtime permission revocation.
- 📊 **System Telemetry & Intelligence**: Real-time CPU, RAM, Disk, and Battery monitoring with automated threshold alerts and process management.
- 👁️ **Screen Understanding & Computer Vision**: Screenshot capture with window crop, morphological OCR text extraction, UI element grounding, and document layout parsing.
- ⏰ **Productivity & Reminders**: Natural language reminder scheduling (one-time and recurring), todo list with priorities, and desktop/audio notification center.
- 🖥️ **Native Desktop Integration**: Electron 34 desktop runner with Context Isolation, system tray quick controls, global shortcut activation (`Ctrl+Shift+Space`), and automatic FastAPI subprocess lifecycle management.
- 🛡️ **Defense-in-Depth Security**: Strict backend validation (the LLM is never the security boundary), 5 permission tiers, configurable confirmation policies, protected filesystem areas, SSRF egress firewall, secrets vault, and tamper-evident SHA-256 audit chaining.

---

## 2. Architecture

The system operates across three decoupled tiers connected via secure IPC, RESTful HTTP/2 APIs, and low-latency WebSockets:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Operating System Desktop                        │
│                   (Linux / Windows / macOS Desktop)                    │
└────────────┬──────────────────────────────────────────────┬────────────┘
             │                                              │
             ▼                                              ▼
┌───────────────────────────┐                  ┌─────────────────────────┐
│     Live System Tray      │                  │  Global Hotkey Summon   │
│ (Quick Toggles & Status)  │                  │   (Ctrl+Shift+Space)    │
└────────────┬──────────────┘                  └────────────┬────────────┘
             │                                              │
             └──────────────────────┬───────────────────────┘
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                Electron Desktop Shell                   │
       │  - Node 20+ Main Process (Lifecycle, Windows, Tray)     │
       │  - Context Isolation = true, Node Integration = false   │
       │  - Backend Process Supervisor (Spawns & Monitors Core)  │
       └────────────────────────────┬────────────────────────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
       ┌───────────────────────────┐ ┌───────────────────────────┐
       │   Secure Preload Bridge   │ │  FastAPI Core AI Backend  │
       │   (window.electronAPI)    │ │  (Python 3.10+ / ASGI)    │
       │   - Whitelisted IPC       │ │  - SQLite WAL Databases   │
       │   - Zero Native Node APIs │ │  - ChromaDB Vector Store  │
       └─────────────┬─────────────┘ └─────────────┬─────────────┘
                     ▼                             │
       ┌───────────────────────────┐               │
       │    React 18 + Vite UI     │◄──────────────┘
       │  (Tailwind, Lucide, WS)   │  HTTP/REST & WebSockets
       └───────────────────────────┘
```

Detailed technical specifications are documented in [docs/architecture.md](docs/architecture.md).

---

## 3. Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, Fedora 38+, Arch), Windows 10/11, macOS 12+
- **Memory (RAM)**: 4 GB minimum (8 GB+ recommended for local Whisper and Ollama weights)
- **Disk Space**: 2 GB free disk space
- **Python**: 3.10, 3.11, or 3.12+
- **Node.js**: 18.x or 20.x LTS

---

## 4. Installation

### 1. Clone & Set Up Python Virtual Environment

```bash
git clone https://github.com/swayom123/personal-ai-assistant.git
cd personal-ai-assistant

# Create virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate  # On Windows: backend\.venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 2. Set Up Frontend & Electron Dependencies

```bash
cd frontend
npm install
cd ..
```

For platform-specific system packages (audio codecs, tesseract), see [docs/installation.md](docs/installation.md).

---

## 5. Configuration

Copy the example configuration file:

```bash
cp backend/.env.example .env
```

Key environment variables in `.env`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DEFAULT_LLM_PROVIDER` | `auto` | Preferred provider: `auto`, `mock`, `ollama`, `openai` |
| `OPENAI_API_KEY` | `""` | Optional OpenAI key |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434`| Local Ollama service URL |
| `VOICE_WAKE_WORD` | `hey_assistant` | Keyword to trigger voice listener |
| `VOICE_TTS_PROVIDER` | `piper` | Local neural TTS provider (`piper`, `coqui`, `mock`) |
| `SECURITY_DEFAULT_CONFIRMATION_POLICY` | `ASK_FOR_RISKY` | Policy: `ALWAYS_ASK`, `ASK_FOR_RISKY`, `TRUST_TOOL`, `NEVER_ALLOW` |

Full configuration reference is documented in [docs/configuration.md](docs/configuration.md).

---

## 6. Development

Run the full stack with hot module replacement and auto-reloading:

```bash
# Terminal 1: Backend API (port 8000)
source backend/.venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend & Electron (port 5173 + Desktop window)
npm --prefix frontend run electron:dev
```

- Web UI: `http://127.0.0.1:5173`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

See [docs/development.md](docs/development.md) for contribution guidelines.

---

## 7. Testing & Quality Assurance

The codebase includes an exhaustive test suite covering all subsystems:

```bash
# Run all backend unit & API tests (283 tests)
PYTHONPATH=. backend/.venv/bin/pytest backend/tests/ -v

# Run root multi-phase integration contracts (14 tests)
PYTHONPATH=. backend/.venv/bin/pytest tests/ -v

# Run frontend component tests (Vitest + Testing Library)
npm --prefix frontend run test

# Run performance and resource benchmarks
PYTHONPATH=. backend/.venv/bin/python3 scripts/benchmark_performance.py

# Execute full unified verification pipeline
./scripts/test_all.sh
```

### Performance Benchmarks

| Metric | Measured | Production Budget |
| :--- | :--- | :--- |
| **Cold Boot Startup Latency** | **1,212 ms** | < 2,000 ms |
| **Idle Process Memory (RSS)** | **169 MB** | < 350 MB |
| **API Throughput** | **435.5 req/s** | > 100 req/s |
| **Concurrency Latency (p95)** | **41.07 ms** | < 100 ms |
| **Task Planner Decomposition** | **2.27 ms** | < 1,000 ms |
| **Production UI Bundle** | **171.35 KB gzipped** | < 500 KB |

---

## 8. Building & Desktop Packaging

Build standalone installers and binaries for desktop distribution:

```bash
# 1. Package Python core distribution
./scripts/package_backend.sh

# 2. Package Electron desktop installer
./scripts/package_desktop.sh
```

Artifacts generated in `frontend/dist-electron-package/`:
- **Linux**: `Personal AI Assistant-1.0.0.AppImage` & `.deb`
- **Windows**: `Personal AI Assistant Setup 1.0.0.exe`
- **macOS**: `Personal AI Assistant-1.0.0.dmg`

See [docs/DESKTOP_PACKAGING.md](docs/DESKTOP_PACKAGING.md) for signing and packaging configurations.

---

## 9. Troubleshooting

- **Port 8000 in use**: Terminate conflicting processes with `kill -9 $(lsof -t -i :8000)` or update `PORT=8080` in `.env`.
- **Microphone not detected**: Ensure user is added to `audio` group (`sudo usermod -aG audio $USER`) and check device index via `GET /api/v1/voice/devices`.
- **Playwright launch errors**: Run `playwright install chromium && playwright install-deps chromium`.
- **Ollama offline**: The assistant automatically falls back to the built-in offline mock provider.
- **Database reset**: Remove runtime stores with `rm -rf data/*.db data/chroma logs/*.log`.

Complete troubleshooting matrix is in [docs/troubleshooting.md](docs/troubleshooting.md).

---

## 10. Security & Permissions

Security is built on defense-in-depth:
- **Permission Levels**: `READ`, `WRITE`, `EXECUTE`, `NETWORK`, `SYSTEM`.
- **Confirmation Policies**: Configurable per tool (`ALWAYS_ASK`, `ASK_FOR_RISKY`, `TRUST_TOOL`, `NEVER_ALLOW`).
- **Protected Areas**: Sensitive directories (`/etc`, `/root`, `~/.ssh`, `~/.aws`) are restricted to `NO_ACCESS` or `CONFIRMATION_REQUIRED`.
- **SSRF Egress Firewall**: Outbound requests block loopback, broadcast, and metadata IPs (`169.254.169.254`).
- **Automated Secrets Redaction**: Regex-based automated scrubbing for OpenAI, Anthropic, AWS, GitHub, Slack, and Bearer tokens in logs and context.
- **Tamper-Evident Audit Logging**: Cryptographic SHA-256 blockchain-style chaining for all security actions.

Full security manual is in [docs/security.md](docs/security.md).

---

## 11. Plugin Development

Create a new directory in `plugins/<plugin_name>/` with `manifest.json` and `main.py`:

```json
{
  "name": "custom_utility",
  "version": "1.0.0",
  "required_permissions": ["filesystem.read"],
  "entrypoint": "main.py:CustomUtilityPlugin",
  "tools": [
    {
      "name": "AnalyzeData",
      "description": "Custom data analysis tool",
      "required_permissions": ["filesystem.read"],
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": { "type": "string" }
        },
        "required": ["file_path"]
      }
    }
  ]
}
```

Implement your logic by extending `BasePlugin`:

```python
from backend.app.services.plugins.base import BasePlugin

class CustomUtilityPlugin(BasePlugin):
    async def execute_tool(self, tool_name: str, arguments: dict):
        if tool_name == "AnalyzeData":
            return {"summary": "Analysis complete"}
        raise NotImplementedError
```

Step-by-step tutorial is available in [docs/plugins.md](docs/plugins.md).

---

## 12. Documentation Index

| Guide | Description |
| :--- | :--- |
| [docs/architecture.md](docs/architecture.md) | Complete multi-tier system architecture and data flows |
| [docs/installation.md](docs/installation.md) | OS-specific setup, dependencies, and environment setup |
| [docs/configuration.md](docs/configuration.md) | Comprehensive `.env` configuration guide and defaults |
| [docs/api.md](docs/api.md) | REST API reference, WebSockets, SSE streams, schemas |
| [docs/voice.md](docs/voice.md) | Wake word detection, Whisper STT, Piper TTS, devices |
| [docs/memory.md](docs/memory.md) | Working memory, SQLite facts, Chroma vector store, ranking |
| [docs/automation.md](docs/automation.md) | Workflow engine, triggers, actions, conditions, retries |
| [docs/plugins.md](docs/plugins.md) | Plugin architecture, manifest specs, security sandbox |
| [docs/security.md](docs/security.md) | Permissions, confirmation policies, SSRF, audit chains |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Diagnostic resolutions for audio, AI, and runtime errors |
| [docs/development.md](docs/development.md) | Contribution standards, testing commands, code style |
| [CHANGELOG.md](CHANGELOG.md) | Complete version history across all 18 phases |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | Official v1.0.0 production release notes |

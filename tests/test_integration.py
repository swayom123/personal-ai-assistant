"""System-level integration test checking project contract."""
import os
import sys

def test_project_structure():
    required_paths = [
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/logging_config.py",
        "backend/app/api/v1/api.py",
        "backend/app/api/v1/endpoints/health.py",
        "backend/app/core/middleware.py",
        "backend/app/core/exceptions.py",
        "backend/tests/test_health.py",
        "frontend/src/App.tsx",
        "frontend/src/main.tsx",
        "frontend/src/components/Sidebar.tsx",
        "frontend/src/components/TopBar.tsx",
        "frontend/src/pages/HomePage.tsx",
        "frontend/electron/main.ts",
        "frontend/electron/preload.ts",
        "frontend/package.json",
        "backend/requirements.txt",
        "docs/ARCHITECTURE.md",
        "README.md",
        "LICENSE"
    ]
    for path in required_paths:
        assert os.path.exists(path), f"Missing required file: {path}"

def test_backend_import():
    from backend.app.main import app
    from backend.app.config import get_settings
    settings = get_settings()
    assert settings.app_name == "personal-ai-assistant"
    assert app.title == "personal-ai-assistant"

#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

if [ ! -d "backend/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/.venv
    backend/.venv/bin/pip install -r backend/requirements.txt
fi

echo "Starting Backend on http://localhost:8000..."
export PYTHONPATH=.
backend/.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

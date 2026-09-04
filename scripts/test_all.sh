#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "=== 1. Running Backend Unit Tests (pytest) ==="
PYTHONPATH=. backend/.venv/bin/pytest backend/tests/ -v

echo "=== 2. Running Root Integration Tests ==="
PYTHONPATH=. backend/.venv/bin/pytest tests/ -v

echo "=== 3. Running Frontend Production Build (TypeScript + Vite) ==="
npm --prefix frontend run build

echo "=== All Phase 1 & Phase 3 Tests Passed Successfully! ==="

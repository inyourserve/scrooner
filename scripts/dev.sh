#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
backend_dir="$repo_root/apps/backend"
frontend_dir="$repo_root/apps/app"

if [[ ! -x "$backend_dir/.venv/bin/uvicorn" ]]; then
  echo "Backend environment is missing. Run: cd apps/backend && uv sync"
  exit 1
fi

cleanup() {
  if [[ -n "${backend_pid:-}" ]]; then
    kill "$backend_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

(
  cd "$backend_dir"
  exec .venv/bin/uvicorn main:app --env-file .env --host 127.0.0.1 --port 8000
) &
backend_pid=$!

cd "$frontend_dir"
npm run dev -- --webpack

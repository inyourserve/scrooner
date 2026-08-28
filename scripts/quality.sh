#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

pipeline/.venv/bin/pytest pipeline/tests
(cd apps/backend && .venv/bin/pytest tests)
pipeline/.venv/bin/python -m compileall -q pipeline/src apps/backend
python3 scripts/check_migrations.py
python3 scripts/check_docs.py
python3 scripts/check_secrets.py
python3 scripts/check_design_system.py
(cd apps/site && npm test)
(cd apps/site && npm run check)
(cd apps/site && npm run build)
(cd apps/app && npm run lint)
(cd apps/app && npm test)
(cd apps/app && npm run build)

if command -v ruff >/dev/null 2>&1; then
  ruff check --select E9,F63,F7,F82 pipeline/src apps/backend
else
  echo "ruff not installed locally; CI runs the required correctness lint"
fi

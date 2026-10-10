#!/bin/bash
# Population-wide conflict-latest-filed (normalizer/conflict_latest_filed.py).
# Idempotent; each batch of 25 companies is its own small transaction.
# Usage (cwd pipeline/): scripts/run_conflict_latest_filed.sh
set -uo pipefail
CIKS=$(uv run python3 - <<'PY'
import psycopg
from scrooner_pipeline.common.config import settings
with psycopg.connect(settings.database_url) as c:
    print(",".join(r[0] for r in c.execute("select cik from core.company where status='active' order by cik").fetchall()))
PY
)
echo "conflict-latest-filed: $(echo "$CIKS" | tr ',' '\n' | wc -l | tr -d ' ') active companies"
uv run scrooner-normalize conflict-latest-filed --ciks "$CIKS"

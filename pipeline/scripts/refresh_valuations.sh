#!/usr/bin/env bash
# Daily: recompute price-dependent metrics for every priced active company,
# then rebuild the screener snapshot.
#
# Added 2026-09-27. The daily cron refreshed core.market_price_alpaca but
# nothing recomputed Market Cap / P/E / P/S / P/B / Dividend Yield / FCF
# Yield from it (every stored market_cap was from 2026-09-08 prices), and
# nothing rebuilt analytics.company_screening_snapshot (last built
# 2026-09-19), so the Screener served data from whenever someone last ran
# it by hand. reprocess_recent_filers.sh only covers companies that filed.
#
# Scope: active companies with a bar in the last 14 days. Everyone else
# gets no new price, so recomputing them would only rewrite the same rows
# (price_metrics.py nulls a price older than 14 days as stale:real_price;
# those companies are still picked up whenever they refile).
set -euo pipefail
cd "$(dirname "$0")/.."

CIKS=$(uv run python3 - <<'PY'
import psycopg
from scrooner_pipeline.common.config import settings

with psycopg.connect(settings.database_url) as conn:
    rows = conn.execute(
        """
        select distinct c.cik
        from core.company c
        join core.market_price_alpaca p on p.company_id = c.id
        where c.status = 'active'
          and p.price_date >= current_date - 14
        order by c.cik
        """
    ).fetchall()
print(",".join(r[0] for r in rows))
PY
)

if [ -z "$CIKS" ]; then
  echo "refresh_valuations: no recently priced companies -- check update-market-price" >&2
  exit 1
fi

N=$(echo "$CIKS" | tr ',' '\n' | wc -l | tr -d ' ')
echo "refresh_valuations: ${N} recently priced companies"

uv run scrooner-map calculate-price-metrics --ciks "$CIKS"
uv run scrooner-screen build-snapshot

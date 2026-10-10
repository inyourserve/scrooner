#!/bin/bash
# One-off (2026-10-03): re-label and reprocess companies whose fiscal-year-end
# falls on Jan 1-10 (52/53-week calendars). normalizer/periods.py used to label
# those years with the next calendar year, colliding with the year ending the
# following Dec, which blocked derive-q4. periods.py is fixed; this re-runs the
# stages that depend on fiscal_year labels for just the affected companies.
# Idempotent: every stage is a scoped upsert or delete-then-reinsert.
#
# Usage: scripts/reprocess_fiscal_year_relabel.sh   (cwd: pipeline/)
set -uo pipefail

CIKS=$(uv run python3 - <<'PY'
import psycopg
from scrooner_pipeline.common.config import settings
with psycopg.connect(settings.database_url) as c:
    rows = c.execute("""
        select distinct co.cik from core.period p
        join core.company co on co.id = p.company_id and co.status = 'active'
        where p.period_type = 'duration' and p.fiscal_period = 'FY'
          and (p.end_date - p.start_date) between 340 and 380
          and extract(month from p.end_date) = 1 and extract(day from p.end_date) <= 10
        order by 1""").fetchall()
print(",".join(r[0] for r in rows))
PY
)
if [ -z "$CIKS" ]; then echo "no affected companies"; exit 0; fi
echo "relabel: $(echo "$CIKS" | tr ',' '\n' | wc -l | tr -d ' ') companies"

STAGES="periods conflict-latest-filed derive-interim-quarters derive-q4"
# SKIP_PERIODS=1 resumes after a partial run (periods is already relabelled).
[ "${SKIP_PERIODS:-0}" = 1 ] && STAGES="conflict-latest-filed derive-interim-quarters derive-q4"
for stage in $STAGES; do
  echo "--- normalize $stage ---"
  uv run scrooner-normalize "$stage" --ciks "$CIKS" || echo "STAGE FAILED: normalize $stage"
done
for stage in resolve-facts resolve-concept-fallbacks calculate growth ttm-returns ttm-margins calculate-expanded-metrics calculate-piotroski calculate-quality-flags calculate-reconciliation calculate-tax-reconciliation calculate-fcf-growth calculate-dividend-streak; do
  echo "--- map $stage ---"
  uv run scrooner-map "$stage" --ciks "$CIKS" || echo "STAGE FAILED: map $stage"
done
echo "relabel: done"

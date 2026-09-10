#!/bin/zsh
# Incremental Normalizer + Mapper reprocessing for recently-filed companies
# (added 2026-09-09). Closes a real, confirmed gap: `scrooner-incremental`
# only ever wrote NEW filing metadata + companyfacts/submissions into `raw`
# -- nothing downstream ever reran the Normalizer's derive-interim-quarters/
# derive-q4 or the Mapper's resolve/calculate chain for those companies, so
# a company's `core`/`analytics` data could silently go stale forever after
# its first full-population pass. Found live investigating a real user
# report (Etsy showing blank quarterly revenue) -- the last full-population
# derive/resolve/calculate run was 2026-08-25; every quarter filed since
# then for any company was invisible past `raw` until this script existed.
#
# Scope: companies with a core.filing row filed in the last N days
# (default 10, matching jobs/incremental.py's own _most_recent_published_
# day lookback convention) -- cheap (usually a few hundred CIKs/day, not
# the full ~5,200-company population) and safe to run daily. Every stage
# below is idempotent (delete-then-reinsert per company, per this
# project's own documented discipline) so a company with nothing new is
# harmless work, not a correctness risk.
#
# Order matters and mirrors jobs/normalize.py's `golden` command plus the
# Mapper stages each module's own docstring says must follow resolve-facts:
# identity -> periods -> units -> facts -> dedupe -> restatements ->
# derive-interim-quarters -> derive-q4 -> resolve-facts ->
# resolve-concept-fallbacks -> calculate -> growth -> ttm-returns ->
# calculate-expanded-metrics -> calculate-piotroski -> calculate-quality-flags
# -> calculate-reconciliation -> calculate-tax-reconciliation ->
# calculate-fcf-growth -> calculate-dividend-streak.
# resolve-statement-fallbacks is deliberately excluded -- it's always
# population-wide, set-based SQL (see its own CLI docstring), too heavy to
# run daily for a handful of companies; that one stays on its existing
# manual/periodic cadence.
set -e
export PATH="/opt/homebrew/opt/libxslt/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
cd "$(dirname "$0")/.."

LOOKBACK_DAYS="${1:-10}"

CIKS=$(uv run python3 -c "
import psycopg
from scrooner_pipeline.common.config import settings
conn = psycopg.connect(settings.database_url)
cur = conn.cursor()
# Sourced from raw.sec_filing_documents, NOT core.filing -- core.filing only
# exists once the Normalizer's identity stage has already run for a CIK, so
# scoping off of it would silently exclude exactly the companies this
# script exists to catch up (confirmed live 2026-09-09: core.filing's own
# max filing_date lagged raw's by ~1 week, and 2,660 active CIKs had a raw
# filing in the last 10 days with zero core.filing awareness of it yet).
cur.execute('''
    select distinct d.cik
    from raw.sec_filing_documents d
    join core.company c on c.cik = d.cik
    where d.filing_date >= current_date - interval '${LOOKBACK_DAYS} days'
      and c.status = 'active'
''')
print(','.join(r[0] for r in cur.fetchall()))
")

if [ -z "$CIKS" ]; then
  echo "reprocess_recent_filers: no companies filed in the last ${LOOKBACK_DAYS} days -- nothing to do"
  exit 0
fi

N=$(echo "$CIKS" | tr ',' '\n' | wc -l | tr -d ' ')
echo "reprocess_recent_filers: ${N} companies with a filing in the last ${LOOKBACK_DAYS} days"

for stage in identity periods units facts dedupe restatements derive-interim-quarters derive-q4; do
  echo "--- normalize $stage ---"
  uv run scrooner-normalize "$stage" --ciks "$CIKS"
done

for stage in resolve-facts resolve-concept-fallbacks calculate growth ttm-returns calculate-expanded-metrics calculate-piotroski calculate-quality-flags calculate-reconciliation calculate-tax-reconciliation calculate-fcf-growth calculate-dividend-streak; do
  echo "--- map $stage ---"
  uv run scrooner-map "$stage" --ciks "$CIKS"
done

echo "reprocess_recent_filers: done"

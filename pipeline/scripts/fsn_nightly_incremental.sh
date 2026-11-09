#!/usr/bin/env bash
# Nightly hybrid incremental (data-team/strategy/team/FSN-NIGHTLY-INCREMENTAL-DESIGN-2026-11-09.md).
#
# Runs inside pipeline-refresh.yml after `scrooner-incremental` (core.filing is fresh) and before
# reprocess_recent_filers.sh (the old normalizer and mapper). FSN_NIGHTLY_STAGE:
#   off   (default) nothing
#   build fetch + convert the day's new 10-K/10-Q filings of the cohort; local files only
#   load  + `scrooner-fsn load --increment` and `pilot` (map, checks, select): writes fsn.* only
#   write + before-image, done gate, protected cell write to analytics.canonical_fact
# load and write are production writes: they need the founder's typed words before the variable
# is set (CLAUDE.md). This script never fails the night: every failure is a ::warning and exit 0,
# and a filing that did not make it is picked up by the next night's lookback (it is still not in
# fsn.filing).
set -uo pipefail

STAGE="${FSN_NIGHTLY_STAGE:-off}"
OUT="${FSN_NIGHTLY_OUT:-out-fsn-nightly}"
MAX_BACKENDS="${MAX_BACKENDS:-60}"
DATA_POINTS="${FSN_NIGHTLY_DATA_POINTS:-revenue_sanity_resolved,net_income_resolved,operating_income_resolved,gross_profit_resolved,cost_of_revenue_resolved,income_before_tax_resolved,income_tax_expense_resolved,interest_expense_resolved,cfo_resolved,share_buybacks_resolved,dividends_paid_resolved,basic_eps_resolved,diluted_eps_resolved,dividends_per_share_resolved,shares_outstanding_resolved}"
FSN="uv run --project pipeline scrooner-fsn"

case "$STAGE" in
  off) echo "fsn nightly: FSN_NIGHTLY_STAGE=off, skipped"; exit 0 ;;
  build|load|write) ;;
  *) echo "::warning::fsn nightly: unknown FSN_NIGHTLY_STAGE '$STAGE', skipped"; exit 0 ;;
esac

warn() { echo "::warning::fsn nightly: $*"; }
mkdir -p "$OUT"

# the window reaches back to the day after the latest SEC FSN set in the store (the backfill), or
# FSN_NIGHTLY_SINCE; FSN_NIGHTLY_MAX_MINUTES caps fetching and defers the rest to the next night
MAX_MIN="${FSN_NIGHTLY_MAX_MINUTES:-25}"
SINCE_ARGS=()
[ -n "${FSN_NIGHTLY_SINCE:-}" ] && SINCE_ARGS=(--since "$FSN_NIGHTLY_SINCE")
if ! timeout $((MAX_MIN + 5))m $FSN nightly --out "$OUT/companies" --report "$OUT/nightly.json" --max-minutes "$MAX_MIN" "${SINCE_ARGS[@]}"; then
  warn "build failed (see the step log); the old mapper runs as before"
  exit 0
fi
CIKS="$(cat "$OUT/companies/ciks.txt" 2>/dev/null || true)"
if [ -z "$CIKS" ]; then
  echo "fsn nightly: no new filing built"
  exit 0
fi
[ "$STAGE" = build ] && exit 0

used=$(psql "$DATABASE_URL" -tAc "select count(*) from pg_stat_activity where backend_type = 'client backend'" 2>/dev/null || echo 999)
if [ "$used" -gt $((MAX_BACKENDS - 2)) ]; then
  warn "$used client backends, no headroom under $MAX_BACKENDS; load skipped (next night catches up)"
  exit 0
fi

if ! timeout 15m $FSN load --companies "$OUT/companies" --increment --report "$OUT/load.json"; then
  warn "increment load failed"
  exit 0
fi
if ! timeout 30m $FSN pilot --ciks "$CIKS" --out "$OUT/pilot"; then
  warn "map/checks/select failed for some companies (see $OUT/pilot/failed.json)"
fi
[ "$STAGE" = load ] && exit 0

if ! [ -f "$OUT/pilot/report.json" ]; then
  warn "no pilot report; nothing written"
  exit 0
fi
timeout 10m $FSN pilot-prod --pilot-out "$OUT/pilot" || { warn "before-image failed; nothing written"; exit 0; }
timeout 5m $FSN done-gate --pilot-out "$OUT/pilot" --data-points "$DATA_POINTS" || { warn "done gate failed; nothing written"; exit 0; }
for d in "$OUT"/pilot/cells/*/; do
  [ -f "$d/cells.jsonl.gz" ] || continue
  fam=$(basename "$d")
  [ "$fam" = unowned ] && continue
  mkdir -p "$OUT/write/$fam"
  python3 pipeline/scripts/fsn_filter_done_cells.py "$d/cells.jsonl.gz" "$OUT/write/$fam/cells.jsonl.gz" "$DATA_POINTS" "$OUT/pilot/done_companies.txt" || continue
  [ "$(zcat "$OUT/write/$fam/cells.jsonl.gz" | wc -l)" -eq 0 ] && continue
  timeout 15m uv run --project pipeline scrooner-cells load "$OUT/write/$fam/cells.jsonl.gz" --family "$fam" --apply \
    --max-backends "$MAX_BACKENDS" --statement-timeout 10min --protect \
    --report "$OUT/write-$fam.json" || warn "cell write $fam failed"
done
exit 0

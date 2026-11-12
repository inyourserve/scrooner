#!/usr/bin/env bash
# Nightly hybrid incremental (data-team/strategy/team/FSN-NIGHTLY-INCREMENTAL-DESIGN-2026-11-09.md).
#
# Runs inside pipeline-refresh.yml after `scrooner-incremental` (core.filing is fresh) and before
# reprocess_recent_filers.sh (the old normalizer and mapper). FSN_NIGHTLY_STAGE:
#   off   (default) nothing
#   build fetch + convert the day's new 10-K/10-Q filings of the cohort; local files only
#   load  + `scrooner-fsn load --increment` and `pilot` (map, checks, select): writes fsn.* only
#   write + the tag-map write (`scrooner-map tagmap-plan --apply`, rule company_tag_map.select@1) for the
#         night's companies that have a company_tag_map; values come from the SEC company facts
# load and write are production writes: they need the founder's typed words before the variable
# is set (CLAUDE.md). This script never fails the night: every failure is a ::warning and exit 0,
# and a filing that did not make it is picked up by the next night's lookback (it is still not in
# fsn.filing).
set -uo pipefail

STAGE="${FSN_NIGHTLY_STAGE:-off}"
OUT="${FSN_NIGHTLY_OUT:-out-fsn-nightly}"
MAX_BACKENDS="${MAX_BACKENDS:-60}"
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

# write: the tag-map write path (founder 2026-11-11 "FSN FOR LEARNING - which tag is what. SEC FOR MAPPING";
# Engineering 2026-11-12): rule company_tag_map.select@1 over the SEC company facts (core.fact) for the night's
# companies that have analytics.company_tag_map rows. It writes with scrooner.writer = 'company_tag_map' (0123),
# protects every written key and records ownership, all in one transaction per company, with a before-image.
# Companies without a tag map are not written (they stay on the old path until their map exists).
IDS=$(python3 - "$OUT/nightly.json" <<'PY'
import json, sys
print(",".join(sorted({str(f["company_id"]) for f in json.load(open(sys.argv[1]))["filings"]})))
PY
)
[ -n "$IDS" ] || { echo "fsn nightly: no company to write"; exit 0; }
MAPPED=$(psql "$DATABASE_URL" -tAc "set statement_timeout = '15s'; select string_agg(distinct company_id::text, ',') from analytics.company_tag_map where company_id = any('{${IDS}}'::bigint[])" 2>/dev/null | tail -1)
if [ -z "$MAPPED" ]; then
  echo "fsn nightly: none of tonight's companies has a tag map; nothing written"
  exit 0
fi
if ! SCROONER_RULES_ENABLED="${SCROONER_RULES_ENABLED:+$SCROONER_RULES_ENABLED,}company_tag_map.select@1" \
  timeout 30m uv run --project pipeline scrooner-map tagmap-plan --company-ids "$MAPPED" --apply \
  --before-image-dir "$OUT/before_image" > "$OUT/tagmap-plan.txt" 2>&1; then
  warn "tag-map write failed or reported NEITHER cells (see $OUT/tagmap-plan.txt); each company is its own transaction"
fi
cat "$OUT/tagmap-plan.txt"
exit 0

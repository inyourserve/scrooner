#!/bin/zsh
# One-off backfill (2026-08-29): calculate/growth's generic-engine metrics
# added since the last full-population Mapper run (payout_ratio,
# pretax_margin, net_cash, net_cash_per_share, dps_growth_yoy,
# dps_growth_3y_cagr) were verified against a single company and never
# scaled -- see doc/audit/2026-08-29_ownership_insider_data_audit.md's
# follow-on and doc/execution-plans/30_Data_Moat_Full_Population_Strengthening_Plan.md's
# Track 6/7. `calculate --ciks <full population>` and `growth --ciks <full
# population>` are idempotent (delete-then-insert per company, per
# pipeline/CLAUDE.md's documented discipline) and pick up every
# requires_price=false metric automatically -- no new pipeline code needed,
# same pattern doc 30 already established for this exact situation
# ("no new command, just needs to run again").
#
# Chunked (200 CIKs/chunk) rather than one giant call: this environment has
# real, documented history of intermittent connection stalls under
# concurrent load (pipeline/CLAUDE.md's Normalizer Day 7 retrospective) --
# chunking means a mid-run failure loses at most one chunk's progress, not
# the whole multi-hour job, and progress is visible in the log rather than
# opaque until the end.
set -e
cd /Users/vikash/scrooner/pipeline

CHUNK_DIR=/tmp/cik_chunk_backfill
rm -rf "$CHUNK_DIR"
mkdir -p "$CHUNK_DIR"
split -l 200 /tmp/all_active_ciks.txt "$CHUNK_DIR/chunk_"

LOG=/tmp/backfill_zero_fetch_metrics.log
echo "=== backfill started $(date) ===" >> "$LOG"

echo "=== STAGE: calculate ===" >> "$LOG"
for f in "$CHUNK_DIR"/chunk_*; do
  CHUNK=$(paste -sd, "$f")
  echo "--- calculate chunk $f ($(wc -l < "$f") ciks) started $(date) ---" >> "$LOG"
  uv run scrooner-map calculate --ciks "$CHUNK" >> "$LOG" 2>&1
  echo "--- calculate chunk $f done $(date) ---" >> "$LOG"
done

echo "=== STAGE: growth ===" >> "$LOG"
for f in "$CHUNK_DIR"/chunk_*; do
  CHUNK=$(paste -sd, "$f")
  echo "--- growth chunk $f ($(wc -l < "$f") ciks) started $(date) ---" >> "$LOG"
  uv run scrooner-map growth --ciks "$CHUNK" >> "$LOG" 2>&1
  echo "--- growth chunk $f done $(date) ---" >> "$LOG"
done

echo "=== backfill complete $(date) ===" >> "$LOG"

#!/bin/zsh
# One-off backfill (2026-09-05): 18 new metrics added this session per
# doc/Frontend/financials/scrooner-financials-display-spec-final.md's
# data-point gap analysis (book_value_per_share, working_capital,
# net_change_in_cash, ocf_to_net_income, cash_returned_to_shareholders,
# ebitda_margin, debt_to_ebitda, fcf_per_share, share_repurchases_pct_fcf,
# dividends_pct_fcf, net_income_growth_yoy/3y/5y/10y_cagr,
# diluted_shares_growth_yoy/3y/5y_cagr, fcf_growth_yoy) were verified
# against AAPL + JPM only and never scaled -- same "no new pipeline code
# needed, just needs to run again" situation
# scripts/backfill_zero_fetch_metrics.sh already established 2026-08-29.
#
# Spans 4 modules/commands (calculate, growth, calculate-fcf-growth,
# calculate-expanded-metrics), all idempotent (delete-then-insert per
# company). Chunked (200 CIKs/chunk), sequential (no parallel workers) --
# this environment has real documented history of connection stalls under
# concurrent load; a slower, single-stream run that reliably finishes beats
# a faster one that silently strands a chunk (pipeline/CLAUDE.md's
# 2026-09-03 hung-worker finding).
set -e
cd /Users/vikash/scrooner/pipeline

CHUNK_DIR=/tmp/cik_chunk_financials_spec
rm -rf "$CHUNK_DIR"
mkdir -p "$CHUNK_DIR"
split -l 200 /tmp/all_active_ciks.txt "$CHUNK_DIR/chunk_"

LOG=/tmp/backfill_financials_spec_metrics.log
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

echo "=== STAGE: calculate-fcf-growth ===" >> "$LOG"
for f in "$CHUNK_DIR"/chunk_*; do
  CHUNK=$(paste -sd, "$f")
  echo "--- calculate-fcf-growth chunk $f ($(wc -l < "$f") ciks) started $(date) ---" >> "$LOG"
  uv run scrooner-map calculate-fcf-growth --ciks "$CHUNK" >> "$LOG" 2>&1
  echo "--- calculate-fcf-growth chunk $f done $(date) ---" >> "$LOG"
done

echo "=== STAGE: calculate-expanded-metrics ===" >> "$LOG"
for f in "$CHUNK_DIR"/chunk_*; do
  CHUNK=$(paste -sd, "$f")
  echo "--- calculate-expanded-metrics chunk $f ($(wc -l < "$f") ciks) started $(date) ---" >> "$LOG"
  uv run scrooner-map calculate-expanded-metrics --ciks "$CHUNK" >> "$LOG" 2>&1
  echo "--- calculate-expanded-metrics chunk $f done $(date) ---" >> "$LOG"
done

echo "=== backfill complete $(date) ===" >> "$LOG"

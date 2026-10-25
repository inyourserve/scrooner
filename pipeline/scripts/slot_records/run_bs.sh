#!/usr/bin/env bash
# One command for a balance-sheet-totals run: detect -> assemble -> replay -> summary.
# usage: run_bs.sh <name> <cik,cik,...|@file> [anchors.json]
#   name    tag for the output files (results/bs_<name>_*.jsonl/json in the scratch dir)
#   ciks    comma list, or @file with one cik per line
# env: SCRATCH (default: this session's scratchpad), DATABASE_URL via pipeline/.env
# Prints ONLY the summary line, per-company states, and anchor results; the
# per-cell dump and withheld details go to the report file, not the terminal.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
SCRATCH="${SCRATCH:-/private/tmp/claude-501/-Users-vikash-scrooner/6f443880-97cf-4cf4-95d5-77b8189f3fb4/scratchpad}"
NAME="$1"; CIKS="$2"; ANCHORS="${3:-$SCRATCH/no_anchors.json}"
[[ "$CIKS" == @* ]] && CIKS="$(tr '\n' ',' < "${CIKS#@}" | sed 's/,$//')"
set -a; source "$REPO/.env"; set +a
PY="$REPO/.venv/bin/python"
[[ -f "$SCRATCH/no_anchors.json" ]] || echo '{"anchors": []}' > "$SCRATCH/no_anchors.json"
python3 -I "$HERE/bs_totals_detect.py" "$SCRATCH/fsds_cohort/cohort_pre_rows.jsonl.gz" "$CIKS" \
  "$SCRATCH/fsds_work/bs_eras_$NAME.json" "$SCRATCH/fsds_work/bs_boundaries_$NAME.txt" | head -1
python3 -I "$HERE/bs_assemble.py" "$SCRATCH/fsds_work/bs_eras_$NAME.json" "$SCRATCH/bs_cal" \
  "$SCRATCH/fsds_cohort/cohort_bs_dims.jsonl.gz" "$SCRATCH/bs_records_$NAME.jsonl" | tail -1
"$PY" -I "$HERE/bs_replay.py" "$SCRATCH/bs_records_$NAME.jsonl" "$ANCHORS" "$SCRATCH/bs_replay_${NAME}_report.json" \
  "$SCRATCH/instance_evidence/bs_custom_facts.jsonl" 2>&1 | grep -vE '^WITHHELD|^         members' | cut -c1-160
echo "report: $SCRATCH/bs_replay_${NAME}_report.json"

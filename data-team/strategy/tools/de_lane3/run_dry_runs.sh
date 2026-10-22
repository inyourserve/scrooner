#!/usr/bin/env bash
# Lane 3 per-family dry runs. READ-ONLY (every command is a dry run and writes nothing).
# Input : a file with one CIK per line or a comma list (at most 100 per call; chunk bigger lists).
# Needs : DATABASE_URL (read-only use), SEC_* env for the Settings object; run from the repo root.
# Output: one JSONL before-image per family under OUTDIR plus the stats line of each command.
# Rollback of a later live run: flag off + recompute of the ciks in the before-image
#   (common/rule_before_image.py: manifest(), restore_command(), verify_restored()).
set -euo pipefail
CIKS_ARG="${1:?usage: run_dry_runs.sh <ciks-file-or-comma-list> [outdir]}"
OUTDIR="${2:-./lane3_dry_run_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$OUTDIR"
OUTDIR="$(cd "$OUTDIR" && pwd)"
if [ -f "$CIKS_ARG" ]; then CIKS="$(paste -sd, "$CIKS_ARG")"; else CIKS="$CIKS_ARG"; fi
MAP="${MAP_CMD:-uv run scrooner-map}"   # disk-limited sessions: MAP_CMD="env PYTHONPATH=$PWD/pipeline/src /path/to/.venv/bin/python -c \"from scrooner_pipeline.jobs.map import app; app()\""
cd pipeline
$MAP resolve-employee-count-fallback --ciks "$CIKS" --dry-run --before-image "$OUTDIR/d4_employee_count.jsonl"
$MAP apply-revenue-total-guard --ciks "$CIKS" --dry-run --before-image "$OUTDIR/rf13_revenue_total.jsonl"
$MAP apply-operating-income-guard --ciks "$CIKS" --dry-run --before-image "$OUTDIR/rf14_operating_income.jsonl"
$MAP apply-scale-unit-guard --ciks "$CIKS" --dry-run --before-image "$OUTDIR/rf18_scale_unit.jsonl"
$MAP price-guards-dry-run --ciks "$CIKS" --before-image "$OUTDIR/rf15_rf19_price.jsonl"
# the total-debt family lives on the held branch (work/data-engineer/lane3-total-debt)
if $MAP --help 2>/dev/null | grep -q total-debt-dry-run; then
  $MAP total-debt-dry-run --ciks "$CIKS" --before-image "$OUTDIR/rf11_total_debt.jsonl"
else
  echo "total-debt-dry-run not available on this branch (held guards not merged)"
fi
echo "dry runs done: $OUTDIR (wc -l of each .jsonl = cells that would change)"

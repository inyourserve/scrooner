#!/usr/bin/env bash
# Regression gate for the balance-sheet port to the FSN store (BS-PORT-2026-11-01.md).
# Runs the lane code twice on identical inputs and compares:
#   A  cohort mode, OLD code (git rev $OLD) vs PORTED code, per-period FSN files      -> byte-identical
#   B  company mode (FSN store company directories) vs cohort mode, same filings       -> identical as sets
#   C  debt replay (company mode) vs the Verifier-passed report_v4.json (10 pilot cos) -> bs_port_compare.py
#   D  bs_assemble company mode vs the Verifier-passed bs_records_v3.jsonl (19 cos)    -> bs_port_compare.py
# Zero SEC requests, zero database reads.
# usage: bs_port_gate.sh <period_dir> <companies_dir> <cohort.csv> <work_dir> [old_rev]
#   period_dir    per-period FSN files in the bucket layout (<p>/<p>_{sub,pre,num,cal}.tsv.zst)
#   companies_dir fsn_store shard output (companies/<cik10>/)
#   cohort.csv    cik,ticker for the companies to gate
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
PER="$1"; COMP="$2"; COHORT="$3"; WORK="$4"; OLD="${5:-c0925d1}"
PY="${PY:-python3}"
mkdir -p "$WORK/old" "$WORK/new" "$WORK/company"
# the old code: the lane files at $OLD, beside the unchanged shared helpers
for f in bs_totals_detect.py era_detect.py assemble_fsn.py replay_debt_fsn.py debt_fsn_inputs.py fsn_company_instants.py fsds_debt_pre.py; do
  git -C "$REPO" show "$OLD:pipeline/scripts/slot_records/$f" > "$WORK/old/$f"
done
for f in common.py build_debt_slots.py face_admission.py taxonomy_attrs.py; do cp "$HERE/$f" "$WORK/old/$f"; done
ln -sfn "$HERE/results" "$WORK/old/results"
CIKS="$(tail -n +2 "$COHORT" | cut -d, -f1 | paste -sd, -)"
CIK10="$(tail -n +2 "$COHORT" | cut -d, -f1 | awk '{printf "%010d\n", $1}' | paste -sd, -)"
printf '' | gzip > "$WORK/no_prod.jsonl.gz"

echo "== inputs (cohort mode): instants extract and FSDS-shaped BS pre rows from the period files"
$PY -I "$WORK/old/fsn_company_instants.py" "$PER" "$CIKS" "$WORK/instants.jsonl.gz" debt | tail -1
rm -f "$WORK/cohort_pre_rows.jsonl"
for p in "$PER"/*/; do
  n="$(basename "$p")"
  [[ -f "$p/${n}_sub.tsv.zst" ]] || continue
  tmp="$WORK/zip_$n"; mkdir -p "$tmp"
  zstd -q -dc "$p/${n}_sub.tsv.zst" > "$tmp/sub.txt"; zstd -q -dc "$p/${n}_pre.tsv.zst" > "$tmp/pre.txt"
  $PY -I -c 'import sys, zipfile; z = zipfile.ZipFile(sys.argv[1], "w"); [z.write(f"{sys.argv[2]}/{m}", m) for m in ("sub.txt", "pre.txt")]; z.close()' "$WORK/$n.zip" "$tmp"
  $PY -I "$WORK/old/fsds_debt_pre.py" "$WORK/$n.zip" "$WORK/cohort_pre_rows.jsonl" "$CIK10" >/dev/null
  rm -rf "$tmp" "$WORK/$n.zip"
done
gzip -f "$WORK/cohort_pre_rows.jsonl"

for side in old new; do
  S="$HERE"; [[ $side == old ]] && S="$WORK/old"
  O="$WORK/$side"
  $PY -I "$S/bs_totals_detect.py" "$WORK/cohort_pre_rows.jsonl.gz" "$CIK10" "$O/bs_eras.json" "$O/bs_boundaries.txt" | head -1
  $PY -I "$S/debt_fsn_inputs.py" "$WORK/instants.jsonl.gz" "$COHORT" "$O/debt" | tail -1
  $PY -I "$S/era_detect.py" "$O/debt/bs_pre_rows.jsonl" "$O/debt_eras.json" "$O/debt_boundaries.txt" | head -1
  $PY -I "$S/assemble_fsn.py" "$O/debt_eras.json" "$PER" "$O/debt/lease_facts.csv" "$O/debt_records.jsonl" \
    "$O/debt/bs_pre_rows.jsonl" "$COHORT" "$O/debt/adsh_period.json" | tail -1
  $PY -I "$S/replay_debt_fsn.py" "$O/debt_records.jsonl" "$WORK/instants.jsonl.gz" "$WORK/no_prod.jsonl.gz" "$O/debt_replay.json" > /dev/null
done
echo "== A: old vs ported code, cohort mode (byte-identical)"
for f in bs_eras.json bs_boundaries.txt debt/bs_pre_rows.jsonl debt/adsh_period.json debt/lease_facts.csv debt_eras.json debt_boundaries.txt debt_records.jsonl debt_replay.json; do
  if cmp -s "$WORK/old/$f" "$WORK/new/$f"; then echo "  identical  $f"; else echo "  DIFFERENT  $f"; fi
done

echo "== company mode on $COMP"
C="$WORK/company"
ls -d "$COMP"/*/ | sed 's:/$::' > "$C/dirs.txt"
$PY -I "$HERE/bs_totals_detect.py" --company "@$C/dirs.txt" "$C/bs_eras.json" "$C/bs_boundaries.txt" | head -1
$PY -I "$HERE/era_detect.py" --company "@$C/dirs.txt" "$C/debt_eras.json" "$C/debt_boundaries.txt" | head -1
$PY -I "$HERE/assemble_fsn.py" --company "@$C/dirs.txt" "$C/debt_eras.json" "$COHORT" "$C/debt_records.jsonl" | tail -1
$PY -I "$HERE/replay_debt_fsn.py" --company "@$C/dirs.txt" "$C/debt_records.jsonl" "$C/debt_replay.json" > /dev/null
$PY -I "$HERE/bs_assemble.py" --company "@$C/dirs.txt" "$C/bs_eras.json" "$C/bs_records.jsonl" | tail -1
$PY -I "$HERE/bs_port_compare.py" "$WORK" "$HERE/results/debt_fsn_pilot_v1/report_v4.json" "$HERE/results/bs_records_v3.jsonl"

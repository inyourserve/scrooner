#!/usr/bin/env bash
# Regression gate for the balance-sheet port to the FSN store (BS-PORT-2026-11-01.md).
# Runs the lane code twice on identical inputs and compares:
#   A  cohort mode, OLD code (git rev $OLD: lane scripts AND shared helpers) vs PORTED code, per-period FSN
#      files, incl. bs_assemble on the boundary filings' _cal.xml                       -> byte-identical
#   B  company mode (FSN store company directories) vs cohort mode, same filings       -> identical
#   C  debt replay (company mode) vs the Verifier-passed report_v4.json (10 pilot cos)
#   D  bs_assemble company mode vs the Verifier-passed bs_records_v3.jsonl (19 cos)
# FAILS CLOSED (review 2026-11-01): bs_port_compare.py exits 1 on ANY difference; with EXPECTED=<file> it
# passes only when the observed differences equal that pinned, explained set exactly. Any step that fails
# fails the gate (set -euo pipefail). Zero database reads; SEC requests only through fetch_boundary_cal.py
# for _cal.xml files missing from CAL_DIR.
# usage: [EXPECTED=<expected_diffs.json>] bs_port_gate.sh <period_dir> <companies_dir> <cohort.csv> <work_dir> <cal_dir> [old_rev]
#   cal_dir       <adsh>/*_cal.xml of the bs boundary filings (fetch_boundary_cal.py fills what is missing)
#   period_dir    per-period FSN files in the bucket layout (<p>/<p>_{sub,pre,num,cal}.tsv.zst)
#   companies_dir fsn_store shard output (companies/<cik10>/)
#   cohort.csv    cik,ticker for the companies to gate
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
PER="$1"; COMP="$2"; COHORT="$3"; WORK="$4"; CAL="$5"; OLD="${6:-c0925d1}"
PY="${PY:-python3}"
mkdir -p "$WORK/old" "$WORK/new" "$WORK/company"
# the old code: the lane files AND the shared helpers at $OLD (review 2026-11-01: helpers are in Gate A)
for f in bs_totals_detect.py bs_assemble.py era_detect.py assemble_fsn.py replay_debt_fsn.py debt_fsn_inputs.py \
         fsn_company_instants.py fsds_debt_pre.py common.py build_debt_slots.py face_admission.py taxonomy_attrs.py; do
  git -C "$REPO" show "$OLD:pipeline/scripts/slot_records/$f" > "$WORK/old/$f"
done
ln -sfn "$HERE/results" "$WORK/old/results"
CIKS="$(tail -n +2 "$COHORT" | cut -d, -f1 | paste -sd, -)"
CIK10="$(tail -n +2 "$COHORT" | cut -d, -f1 | awk '{printf "%010d\n", $1}' | paste -sd, -)"
printf '' | gzip > "$WORK/no_prod.jsonl.gz"

echo "== inputs (cohort mode): instants extract and FSDS-shaped BS pre rows from the period files"
$PY -I "$HERE/fsn_company_instants.py" "$PER" "$CIKS" "$WORK/instants.jsonl.gz" debt | sed -n '$p'
# BS dimensional rows (bs_assemble's mezzanine dims), one file for both sides
$PY -I -c 'import gzip, json, sys; sys.path.insert(0, sys.argv[1]); import fsn_company_bs as fc
with gzip.open(sys.argv[3], "wt") as o:
    for d in fc.company_dir_list(sys.argv[2]):
        for r in fc.bs_dim_rows(d): o.write(json.dumps(r) + "\n")' "$HERE" "$COMP" "$WORK/cohort_bs_dims.jsonl.gz"
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
  $PY -I "$S/bs_totals_detect.py" "$WORK/cohort_pre_rows.jsonl.gz" "$CIK10" "$O/bs_eras.json" "$O/bs_boundaries.txt" | sed -n 1p
  [[ $side == old ]] && $PY -I "$HERE/fetch_boundary_cal.py" "$O/bs_boundaries.txt" "$CAL" | sed -n '$p'
  $PY -I "$S/bs_assemble.py" "$O/bs_eras.json" "$CAL" "$WORK/cohort_bs_dims.jsonl.gz" "$O/bs_records.jsonl" | sed -n '$p'
  $PY -I "$S/debt_fsn_inputs.py" "$WORK/instants.jsonl.gz" "$COHORT" "$O/debt" | sed -n '$p'
  $PY -I "$S/era_detect.py" "$O/debt/bs_pre_rows.jsonl" "$O/debt_eras.json" "$O/debt_boundaries.txt" | sed -n 1p
  $PY -I "$S/assemble_fsn.py" "$O/debt_eras.json" "$PER" "$O/debt/lease_facts.csv" "$O/debt_records.jsonl" \
    "$O/debt/bs_pre_rows.jsonl" "$COHORT" "$O/debt/adsh_period.json" | sed -n '$p'
  $PY -I "$S/replay_debt_fsn.py" "$O/debt_records.jsonl" "$WORK/instants.jsonl.gz" "$WORK/no_prod.jsonl.gz" "$O/debt_replay.json" > /dev/null
done
# ablation: the ported replay with the pre-review (first-filed) selection, to separate the selection change
# from the other review fixes in Gate A
REPLAY_DEBT_ABLATE=first_filed $PY -I "$HERE/replay_debt_fsn.py" "$WORK/new/debt_records.jsonl" "$WORK/instants.jsonl.gz" \
  "$WORK/no_prod.jsonl.gz" "$WORK/new/debt_replay_first_filed.json" > /dev/null
echo "== company mode on $COMP"
C="$WORK/company"
ls -d "$COMP"/*/ | sed 's:/$::' > "$C/dirs.txt"
$PY -I "$HERE/bs_totals_detect.py" --company "@$C/dirs.txt" "$C/bs_eras.json" "$C/bs_boundaries.txt" | sed -n 1p
$PY -I "$HERE/era_detect.py" --company "@$C/dirs.txt" "$C/debt_eras.json" "$C/debt_boundaries.txt" | sed -n 1p
$PY -I "$HERE/assemble_fsn.py" --company "@$C/dirs.txt" "$C/debt_eras.json" "$COHORT" "$C/debt_records.jsonl" | sed -n '$p'
$PY -I "$HERE/replay_debt_fsn.py" --company "@$C/dirs.txt" "$C/debt_records.jsonl" "$C/debt_replay.json" > /dev/null
$PY -I "$HERE/bs_assemble.py" --company "@$C/dirs.txt" "$C/bs_eras.json" "$C/bs_records.jsonl" | sed -n '$p'
# the verdict: exit 1 on any difference (or on any difference outside the pinned EXPECTED set)
$PY -I "$HERE/bs_port_compare.py" "$WORK" "$HERE/results/debt_fsn_pilot_v1/report_v4.json" "$HERE/results/bs_records_v3.jsonl" \
  ${EXPECTED:+--expected "$EXPECTED"}

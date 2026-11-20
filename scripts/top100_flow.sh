#!/bin/zsh
# Top-110 per-company flow (founder approvals 2026-11-13/14: load, guarded new-system-only rewrite, proof --write,
# era guard). Runs one company (or a short id list) through the chain on a fresh worktree of origin/main, then appends
# its coverage line to .runs/top100_flow/flow_results.tsv. All run state lives under the repo's gitignored .runs/,
# never /tmp, so a restart costs only a relaunch. Usage: scripts/top100_flow.sh <company_id[,id...]> <tag>
# Parallel: xargs -P 8 -I{} scripts/top100_flow.sh {} c{} < ids.txt
export PATH=/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/usr/local/bin:$PATH
set -u; setopt pipefail
command -v zstd >/dev/null || { echo "zstd missing"; exit 90; }
# CI mode (GitHub Actions, TOP100_CI=1): the checkout of origin/main is the worktree, the venv is pipeline/.venv from
# `uv sync`, secrets come from the job env, and the Mac-only pieces (disk floor, worktree add/remove, .env) are skipped.
# The chain below is identical in both modes.
CI_MODE=${TOP100_CI:-}
IDS=${1:?ids}; TAG=${2:?tag}
REPO=$(cd "$(dirname "$0")/.." && pwd); S=$REPO/.runs/top100_flow; mkdir -p $S
W=$S/wt-$TAG; O=$S/run_$TAG; rm -rf $O; mkdir -p $O
cd $REPO
[ -z "$CI_MODE" ] && {
# disk floor (Dhairya 2026-11-14): a full disk hangs a process silently, so a run waits while free space on the
# volume is under FREE_FLOOR_GB (default 8) and never starts a worktree below it
FLOOR=${FREE_FLOOR_GB:-8}
while [ "$(df -g $S | awk 'NR==2{print $4}')" -lt "$FLOOR" ]; do echo "$(date -u +%H:%MZ) $TAG waiting: free < ${FLOOR}GB" >> $S/disk_wait.log; sleep 120; done
# every exit, clean or failed, removes this run's own worktree (and only it); a run never touches another run's tree
[ -z "$CI_MODE" ] && trap 'cd $REPO && git worktree remove --force $W 2>/dev/null; git worktree prune 2>/dev/null' EXIT
# parallel workers fetch at once; a ref-lock collision is retried, never fatal
for t in 1 2 3 4 5 6; do git fetch -q 2>/dev/null && break; sleep $((RANDOM % 7 + 2)); done
for t in 1 2 3; do rm -rf $W; git worktree prune 2>/dev/null; git worktree add -q --detach $W origin/main 2>/dev/null && break; sleep $((RANDOM % 5 + 2)); done
[ -d $W/pipeline ] || exit 2
ln -s $REPO/pipeline/.venv $W/pipeline/.venv; cd $W
set -a; source $REPO/pipeline/.env; set +a
}
[ -n "$CI_MODE" ] && { W=$REPO; cd $W; }
export SCROONER_RULES_ENABLED=company_tag_map.select@1 PYTHONPATH=pipeline/src
PY=$W/pipeline/.venv/bin/python
echo "code: $(git rev-parse --short HEAD)"
q() { $PY -c "
import os,psycopg,sys
with psycopg.connect(os.environ.get('SCROONER_DATABASE_URL') or os.environ['DATABASE_URL']) as c:
    c.execute(\"set statement_timeout='5min'\")
    print(c.execute(sys.argv[1]).fetchone()[0])" "$1"; }
while [ "$(q 'select count(*) from pg_stat_activity')" -gt 80 ]; do sleep 60; done
CIKS=$(q "select string_agg(cik, ',') from core.company where id in ($IDS)")
TK=$(q "select string_agg(primary_ticker, '|') from core.company where id in ($IDS)")
# companies with no 10-K of their own before the template window: data-driven (was a hard-coded CIK list, 2026-11-16);
# the rule and its cutoff are in pipeline/src/scrooner_pipeline/onboarding/no_filing.py. A failed check stops the run.
NOFILE=$($PY -m scrooner_pipeline.onboarding.no_filing --company-ids "$IDS" --explain 2> $O/no_filing_why.txt) || { tail -3 $O/no_filing_why.txt; exit 13; }
echo "no-filing ciks: ${NOFILE:-none}"
R=$O/reads; mkdir -p $R/fixes
for f in data-team/companies/reads/*-docmap-*; do t=${${f:t}%%-docmap-*}; echo $t | grep -Eqx "$TK" && cp $f $R/; done
for f in data-team/companies/reads/fixes/*-fixes-*.csv(N); do t=${${f:t}%%-fixes-*}; echo $t | grep -Eqx "$TK" && cp $f $R/fixes/; done
echo "docmaps $(ls $R/*.csv 2>/dev/null | wc -l) fix files $(ls $R/fixes | wc -l)"
PG="-c statement_timeout=900000"
PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map docmap-load $R --conflicts-out $O/conflicts.csv --rejects-out $O/rejects.csv --extend-eras --era-log $O/era_log.csv --predictor-eras data-team/tags/exam/eras --no-filing-ciks "$NOFILE" --apply > $O/1.txt 2>&1 || { tail -3 $O/1.txt; exit 11; }
head -1 $O/1.txt | cut -c1-220
RES=$(PYTHONPATH=pipeline/src $PY -c "from scrooner_pipeline.mapper import resolver_files as rf; print(rf.resolver_source() or '')")  # per-company dir, else the single file
if [ -n "$RES" ]; then
  PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map structural-load $RES --company-ids $IDS --conflicts-out $O/s_conflicts.csv --exceptions-out $O/s_exceptions.csv --rejects-out $O/s_rejects.csv --apply > $O/1s.txt 2>&1 || { tail -3 $O/1s.txt; exit 12; }
  grep -iE "structural-load|written|exceptions" $O/1s.txt | head -2 | cut -c1-220
fi
plan() { mkdir -p $O/bi_$1; PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map tagmap-plan --company-ids $IDS --apply --coverage-gate --coverage-gate-scope concept --docmap-reads $R --before-image-dir $O/bi_$1 > $O/plan_$1.txt 2> $O/plan_$1.err || { tail -3 $O/plan_$1.err; exit 21; }; }
# proof --write is rule-scoped by default (ONE-PATH step 1, proof/rules.py): it writes only cells with no current row or
# whose recorded rules changed, and stamps untouched legacy rows with their rule record. `--full` rewrites every cell.
proof() { for c in ${(s:,:)CIKS}; do PGOPTIONS=$PG $PY -c "import sys; from scrooner_pipeline.jobs.proof import app; sys.argv=['p','run','--ciks','$c','--report','$O/proof_$1_$c.jsonl','--write']; app()" > $O/proof_$1_$c.log 2>&1 || { tail -2 $O/proof_$1_$c.log; exit 31; }; grep "cell-proof:" $O/proof_$1_$c.log | cut -c1-200; done; }
plan a; proof a
PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map era-guard --company-ids $IDS --apply > $O/guard.txt 2>&1 || { tail -3 $O/guard.txt; exit 41; }
plan b; proof b
# The export reads inside `set transaction read only` (mapper/top100_coverage.py main), so the process is no longer forced
# read-only by PGOPTIONS: --write-display-state upserts analytics.cell_display_state (0130) on its own connection, one
# transaction per exported company. The held re-export below writes it again so the table matches the final state.
# --company-ids: this job exports ONLY its own company (scale plan 2026-11-17 section 6 item 1; the full export was ~5 of
# the 8 chain minutes and O(N^2) over a run). The publish job merges the rows into the committed files on main.
mkdir -p $O/coverage; PYTHONPATH=pipeline/src $PY pipeline/scripts/top100_coverage.py $O/coverage --write-display-state --company-ids $IDS > $O/coverage.txt 2>&1
# Certified-company regression guard: a certified company (approvals/<TICKER>-certificate-*.md on main) must keep every
# certified cell (PROVEN/REASON/DERIVED, same shown_value). On a regression its rows are restored from the first
# rewrite's before-image (bi_a), the proof is re-run so verdicts match, and the flow line says HELD_CERTIFIED.
typeset -A HELD
for c in ${(s:,:)IDS}; do
  tk=$(q "select primary_ticker from core.company where id = $c"); ck=$(q "select cik from core.company where id = $c")
  # (N) on an array glob: no certificate -> empty array -> skip (a bare `ls` of an empty glob lists the cwd instead)
  certs=(data-team/strategy/approvals/${tk}-certificate-*.md(N)); cert=${certs[-1]:-}
  [ -n "$cert" ] || continue
  ccsv=$(grep -oE "data-team/strategy/certification/$tk-coverage-[0-9-]+\.csv" $cert | head -1)
  [ -n "$ccsv" ] && [ -f "$ccsv" ] || { echo "certified $tk: certified csv not found in $cert"; HELD[$c]=NOCSV; continue; }
  mkdir -p $S/regressions; rp=$S/regressions/$tk-$(date -u +%Y%m%dT%H%M%SZ).csv
  $PY -m scrooner_pipeline.jobs.map certified-guard --company-id $c --certified-csv $ccsv --coverage-csv $O/coverage/top100-coverage.csv --report $rp > $O/guard_$c.txt 2>&1; g=$?
  head -3 $O/guard_$c.txt | cut -c1-220
  if [ $g -eq 1 ]; then
    PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map restore-before-image --company-id $c --dir $O/bi_a --apply > $O/restore_$c.txt 2>&1 || { tail -3 $O/restore_$c.txt; HELD[$c]=RESTORE_FAILED; continue; }
    cut -c1-220 $O/restore_$c.txt
    PGOPTIONS=$PG $PY -c "import sys; from scrooner_pipeline.jobs.proof import app; sys.argv=['p','run','--ciks','$ck','--report','$O/proof_held_$ck.jsonl','--write']; app()" > $O/proof_held_$ck.log 2>&1 || { tail -2 $O/proof_held_$ck.log; HELD[$c]=REPROOF_FAILED; continue; }
    mkdir -p $O/coverage_held; PYTHONPATH=pipeline/src $PY pipeline/scripts/top100_coverage.py $O/coverage_held --write-display-state --company-ids $IDS > $O/coverage_held.txt 2>&1
    HELD[$c]=HELD_CERTIFIED
  elif [ $g -ne 0 ]; then HELD[$c]=GUARD_ERROR; fi
done
CV=$O/coverage; [ -f $O/coverage_held/top100-coverage-summary.csv ] && CV=$O/coverage_held
for c in ${(s:,:)IDS}; do
  line=$(python3 -c "
import csv
for r in csv.DictReader(open('$CV/top100-coverage-summary.csv')):
    if r['company_id']=='$c':
        print(r['ticker'], 'shown %s/%s %s open=%s' % (r['shown_values'], r['shown_cells'], r['pct_shown_values'] or '-', r['open_shown']), 'FULL' if r['display_certified']=='yes' else 'NOT_CERTIFIED')" 2>&1)
  echo "$(date -u +%H:%MZ)\t$c\t$line${HELD[$c]:+ ${HELD[$c]}}" | tee -a $S/flow_results.tsv
done
[ -z "$CI_MODE" ] && { cd $REPO && git worktree remove --force $W 2>/dev/null; git worktree prune; }
echo DONE

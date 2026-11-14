#!/bin/zsh
# Top-110 per-company flow (founder approvals 2026-11-13/14: load, guarded new-system-only rewrite, proof --write,
# era guard). Runs one company (or a short id list) through the chain on a fresh worktree of origin/main, then appends
# its coverage line to .runs/top100_flow/flow_results.tsv. All run state lives under the repo's gitignored .runs/,
# never /tmp, so a restart costs only a relaunch. Usage: scripts/top100_flow.sh <company_id[,id...]> <tag>
# Parallel: xargs -P 8 -I{} scripts/top100_flow.sh {} c{} < ids.txt
export PATH=/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/usr/local/bin:$PATH
set -u; setopt pipefail
command -v zstd >/dev/null || { echo "zstd missing"; exit 90; }
IDS=${1:?ids}; TAG=${2:?tag}
REPO=$(cd "$(dirname "$0")/.." && pwd); S=$REPO/.runs/top100_flow; mkdir -p $S
W=$S/wt-$TAG; O=$S/run_$TAG; rm -rf $O; mkdir -p $O
NOFILE=2115436,1996810,1594805,2023554,2012383
cd $REPO && git fetch -q && rm -rf $W && git worktree prune && git worktree add -q --detach $W origin/main || exit 2
ln -s $REPO/pipeline/.venv $W/pipeline/.venv; cd $W
set -a; source $REPO/pipeline/.env; set +a
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
R=$O/reads; mkdir -p $R/fixes
for f in data-team/companies/reads/*-docmap-*; do t=${${f:t}%%-docmap-*}; echo $t | grep -Eqx "$TK" && cp $f $R/; done
for f in data-team/companies/reads/fixes/*-fixes-*.csv(N); do t=${${f:t}%%-fixes-*}; echo $t | grep -Eqx "$TK" && cp $f $R/fixes/; done
echo "docmaps $(ls $R/*.csv 2>/dev/null | wc -l) fix files $(ls $R/fixes | wc -l)"
PG="-c statement_timeout=900000"
PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map docmap-load $R --conflicts-out $O/conflicts.csv --rejects-out $O/rejects.csv --extend-eras --era-log $O/era_log.csv --predictor-eras data-team/tags/exam/eras --no-filing-ciks $NOFILE --apply > $O/1.txt 2>&1 || { tail -3 $O/1.txt; exit 11; }
head -1 $O/1.txt | cut -c1-220
RES=$(ls data-team/tags/line_map/resolver-all110-*.csv 2>/dev/null | sort | tail -1)
if [ -n "$RES" ]; then
  PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map structural-load $RES --company-ids $IDS --conflicts-out $O/s_conflicts.csv --exceptions-out $O/s_exceptions.csv --rejects-out $O/s_rejects.csv --apply > $O/1s.txt 2>&1 || { tail -3 $O/1s.txt; exit 12; }
  grep -iE "structural-load|written|exceptions" $O/1s.txt | head -2 | cut -c1-220
fi
plan() { mkdir -p $O/bi_$1; PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map tagmap-plan --company-ids $IDS --apply --coverage-gate --coverage-gate-scope concept --docmap-reads $R --before-image-dir $O/bi_$1 > $O/plan_$1.txt 2> $O/plan_$1.err || { tail -3 $O/plan_$1.err; exit 21; }; }
proof() { for c in ${(s:,:)CIKS}; do PGOPTIONS=$PG $PY -c "import sys; from scrooner_pipeline.jobs.proof import app; sys.argv=['p','run','--ciks','$c','--report','$O/proof_$1_$c.jsonl','--write']; app()" > $O/proof_$1_$c.log 2>&1 || { tail -2 $O/proof_$1_$c.log; exit 31; }; grep "cell-proof:" $O/proof_$1_$c.log | cut -c1-200; done; }
plan a; proof a
PGOPTIONS=$PG $PY -m scrooner_pipeline.jobs.map era-guard --company-ids $IDS --apply > $O/guard.txt 2>&1 || { tail -3 $O/guard.txt; exit 41; }
plan b; proof b
mkdir -p $O/coverage; PYTHONPATH=pipeline/src PGOPTIONS="-c default_transaction_read_only=on" $PY pipeline/scripts/top100_coverage.py $O/coverage > $O/coverage.txt 2>&1
for c in ${(s:,:)IDS}; do
  line=$(python3 -c "
import csv
for r in csv.DictReader(open('$O/coverage/top100-coverage-summary.csv')):
    if r['company_id']=='$c':
        oc=sum(int(r.get(k) or 0) for k in ('DISAGREE','UNCHECKED','BLANK','HELD'))
        print(r['ticker'], r['cells'], r['pct_proven_plus_reason'], 'FULL' if oc==0 and int(r['cells'] or 0)>0 else 'open=%d'%oc)" 2>&1)
  echo "$(date -u +%H:%MZ)\t$c\t$line" | tee -a $S/flow_results.tsv
done
cd $REPO && git worktree remove --force $W 2>/dev/null; git worktree prune
echo DONE

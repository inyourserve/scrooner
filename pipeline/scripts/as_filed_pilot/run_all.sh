#!/bin/bash
# One SEC process, sequential. Each quarter: download -> extract (python -I, stdlib) -> delete zip.
# usage: run_all.sh <workdir> <worktree-src> ; env SEC_UA must be set
W=$1; SRC=$2; D=$(dirname "$0")
CIKS=1045810,320193,1652044,1288776,789019,1018724,1326801,1730168,1441634,1318605,59478,723125
mkdir -p $W/dl $W/out
for y in $(seq 2015 2026); do for q in 1 2 3 4; do
  Q=${y}q${q}; [ $y = 2026 ] && [ $q = 4 ] && continue
  [ -s $W/out/$Q.jsonl.gz ] && [ $Q != 2018q4 ] && { echo "skip $Q"; continue; }
  FREE=$(df -k /private/tmp | tail -1 | awk '{print $4}'); [ $FREE -lt 3145728 ] && { echo "STOP low disk $FREE KB"; exit 3; }
  s=$(date +%s)
  /Users/vikash/scrooner/pipeline/.venv/bin/python $D/fetch_fsds.py $Q $W/dl $SRC || { echo "FETCH FAIL $Q"; continue; }
  python3 -I $D/extract_fsds.py $W/dl/$Q.zip $W/out/$Q.jsonl.gz $CIKS
  rm -f $W/dl/$Q.zip
  echo "$Q done $(( $(date +%s)-s ))s requests=1"
done; done
echo ALLDONE

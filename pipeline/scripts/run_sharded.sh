#!/usr/bin/env bash
# Generic N-way sharded runner for any scrooner-* CLI command that takes
# --ciks. Added 2026-10-04, by direct request ("keep provision of
# multiple workers in next phases"), generalizing a pattern that had
# already been hand-built three times in one session (derive-interim-
# quarters, derive-q4, resolve-facts) -- each time re-deriving the same
# "split the active CIK list into N files, launch N background workers,
# one log file each" shell logic from scratch.
#
# Always re-derives the active CIK list fresh from the live DB (never
# trusts a stale /tmp file from an earlier run -- this dev machine's
# /tmp has been wiped mid-session before, see pipeline/CLAUDE.md).
# Workers are launched with nohup + disown, so they survive independent
# of this script's own process and of this shell session -- the same
# "detached, not bound by any 30-minute background-task cap" pattern
# used for every long derive-interim-quarters/derive-q4/resolve-facts
# run today. The CLI command itself owns its own correctness (per-
# company commits, idempotent writes, safe_rollback reconnect) -- this
# script only owns splitting the company list and launching workers.
#
# Usage:
#   scripts/run_sharded.sh <num_shards> <log_prefix> <scrooner-command> [args...]
#
# Example (what today's derive-interim-quarters run looked like by hand):
#   scripts/run_sharded.sh 6 /tmp/derive_interim scrooner-normalize derive-interim-quarters
#
# This launches 6 background workers running:
#   uv run scrooner-normalize derive-interim-quarters --ciks <shard-N-ciks>
# logging to /tmp/derive_interim_shard_0.log .. _shard_5.log, and prints
# each shard's PID and log path so the caller can monitor/wait on them
# (poll `ps -p <pid>`, or tail the log files -- this script does not
# block waiting for completion, matching every prior run's own pattern
# of checking in periodically rather than blocking the whole session).
#
# A company that errors in one shard does not affect any other shard --
# each shard is a fully independent `uv run` process. If a shard reports
# errors, rerun just that shard's failed CIKs directly (see the
# "scrooner-normalize derive-q4 --ciks <failed-ciks>" retry pattern used
# today for 4 transient failures), rather than rerunning the whole thing.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <num_shards> <log_prefix> <scrooner-command> [args...]" >&2
  echo "Example: $0 6 /tmp/myjob scrooner-normalize derive-q4" >&2
  exit 1
fi

NUM_SHARDS="$1"
LOG_PREFIX="$2"
shift 2
# Remaining args ("$@") are the command itself, e.g. scrooner-normalize derive-q4

CIK_FILE=$(mktemp)
trap 'rm -f "$CIK_FILE"' EXIT

uv run python3 - "$CIK_FILE" <<'PY'
import sys
import psycopg
from scrooner_pipeline.common.config import settings

out_path = sys.argv[1]
with psycopg.connect(settings.database_url) as conn:
    with conn.cursor() as cur:
        cur.execute("select cik from core.company where status='active' order by cik")
        ciks = [r[0] for r in cur.fetchall()]

with open(out_path, "w") as f:
    f.write(",".join(ciks))

print(f"active companies: {len(ciks)}", file=sys.stderr)
PY

readarray -t ALL_CIKS < <(tr ',' '\n' < "$CIK_FILE")
TOTAL=${#ALL_CIKS[@]}
SHARD_SIZE=$(( (TOTAL + NUM_SHARDS - 1) / NUM_SHARDS ))

echo "Splitting $TOTAL active companies into $NUM_SHARDS shards (~$SHARD_SIZE each)"

for ((i = 0; i < NUM_SHARDS; i++)); do
  START=$(( i * SHARD_SIZE ))
  SHARD_CIKS=$(printf "%s," "${ALL_CIKS[@]:$START:$SHARD_SIZE}")
  SHARD_CIKS="${SHARD_CIKS%,}"  # drop trailing comma
  if [ -z "$SHARD_CIKS" ]; then
    continue
  fi
  LOG_FILE="${LOG_PREFIX}_shard_${i}.log"
  nohup uv run "$@" --ciks "$SHARD_CIKS" > "$LOG_FILE" 2>&1 &
  disown
  echo "shard $i: PID $! -> $LOG_FILE"
done

echo ""
echo "All shards launched, detached. Check progress with:"
echo "  ps -p <pid>   (per shard)"
echo "  tail -f ${LOG_PREFIX}_shard_0.log"
echo "Once all PIDs have exited, grep each log for its final summary line"
echo "(e.g. 'derive-q4: {...}') to check 'errored' counts before trusting completion."

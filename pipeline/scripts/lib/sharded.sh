#!/usr/bin/env bash
# Shared helper: run one pipeline stage across N parallel shards of a
# comma-separated CIK list, then wait for ALL of them (a barrier) before the
# caller moves to the next stage. Sourced by reprocess_recent_filers.sh.
#
# Why: the nightly reprocess ran every stage as ONE process over ~200 companies
# and hit its 180-minute job cap (Oct 10), so the whole refresh was cancelled.
# Stages are safe to run on disjoint company sets in parallel: every write is
# keyed by company, and the only shared tables (core.unit, core.concept) are
# written with ON CONFLICT DO NOTHING. The Normalizer makes no SEC fetches, so
# there is no rate-limit to multiply. The same sharding is what the manual
# population runs use (scripts/run_sharded.sh).
#
# Contract:
#   run_sharded <program> <stage>      uses $CIKS (comma-separated) and
#                                      $SHARDS (default 4, capped at the number
#                                      of companies)
#   Returns non-zero if ANY shard failed, after every shard has finished, so
#   a caller running under `set -e` aborts exactly as it did when the stage was
#   a single process. Output lines are prefixed "[sK] " so interleaved shard
#   logs stay attributable.

# Kill a process and all its descendants (a hung `uv run` leaves the python
# worker as a grandchild, which killing only the subshell would orphan).
_kill_tree() {
  local pid="$1" child
  for child in $(pgrep -P "$pid" 2>/dev/null); do _kill_tree "$child"; done
  kill -9 "$pid" 2>/dev/null || true
}

# Optional per-stage wall-clock cap, STAGE_TIMEOUT_SECS (default 0 = none). Added
# 2026-10-17: the nightly reprocess step selected only ~250 companies yet ran the
# whole 180-minute job cap four nights in a row and was cancelled, with no log
# kept, because one hung shard (a dead pooler socket, no query, no output) holds
# the barrier forever. On expiry the stage's shards are killed, the stage is
# reported by name and counts as failed; every stage is idempotent, so the caller
# moves on to the next stage instead of losing the whole night.
run_sharded() {
  local program="$1" stage="$2"
  local n shards k chunk pid rc=0
  local pids=()

  n=$(echo "$CIKS" | tr ',' '\n' | awk 'NF' | wc -l | tr -d ' ')
  shards="${SHARDS:-4}"
  if [ "$n" -lt "$shards" ]; then shards="$n"; fi
  if [ "$shards" -lt 1 ]; then shards=1; fi

  for ((k = 0; k < shards; k++)); do
    # Round-robin split: line i goes to shard (i-1) mod N, so shards stay
    # balanced and are disjoint by construction.
    chunk=$(echo "$CIKS" | tr ',' '\n' | awk 'NF' \
      | awk -v n="$shards" -v k="$k" '((NR - 1) % n) == k' | paste -sd, -)
    if [ -z "$chunk" ]; then continue; fi
    (
      set -o pipefail
      uv run "$program" "$stage" --ciks "$chunk" 2>&1 \
        | awk -v p="[s$k] " '{ print p $0; fflush() }'
    ) &
    pids+=("$!")
  done

  local cap="${STAGE_TIMEOUT_SECS:-0}" started=$SECONDS timed_out=0
  if [ "$cap" -gt 0 ]; then
    # Poll instead of `wait`, so a hung shard cannot hold the barrier forever.
    while :; do
      local alive=0
      for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then alive=1; fi
      done
      [ "$alive" -eq 0 ] && break
      if [ $((SECONDS - started)) -ge "$cap" ]; then
        echo "run_sharded: stage '$stage' exceeded ${cap}s -- killing its shards" >&2
        for pid in "${pids[@]}"; do _kill_tree "$pid"; done
        timed_out=1
        break
      fi
      sleep 2
    done
  fi
  for pid in "${pids[@]}"; do
    wait "$pid" 2>/dev/null || rc=1
  done
  [ "$timed_out" -eq 1 ] && rc=1
  echo "run_sharded: stage '$stage' took $((SECONDS - started))s (rc=$rc)"
  return "$rc"
}

# run_capped <secs> <cmd...>: run one command under a wall-clock cap with no
# dependency on GNU `timeout` (absent on macOS). Kills the whole process tree on
# expiry and returns 124 (as `timeout` does); otherwise returns the command's rc.
run_capped() {
  local cap="$1" pid started=$SECONDS rc=0
  shift
  "$@" &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$cap" -gt 0 ] && [ $((SECONDS - started)) -ge "$cap" ]; then
      echo "run_capped: '$*' exceeded ${cap}s -- killing it" >&2
      _kill_tree "$pid"
      wait "$pid" 2>/dev/null || true
      return 124
    fi
    sleep 1
  done
  wait "$pid" || rc=$?
  return "$rc"
}

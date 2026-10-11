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

  for pid in "${pids[@]}"; do
    wait "$pid" || rc=1
  done
  return "$rc"
}

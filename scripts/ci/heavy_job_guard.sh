#!/usr/bin/env bash
# Keep the FSN production write and the heavy nightly database jobs apart (2026-11-08).
#
# The write workflow used a fixed 18:00-21:30 UTC "nightly window", but GitHub starts the
# scheduled jobs hours late and at varying times (refresh scheduled 12:23 UTC; observed
# starts 17:47-21:49 UTC, ends up to 01:34 UTC, 2026-11-02..07), so a clock window cannot
# say whether a heavy job is running. This asks GitHub what is actually running.
#
#   heavy_job_guard.sh refuse-if-heavy
#       Exit 1 if any heavy-db-jobs workflow has a run in progress or waiting to start.
#       Used by pipeline-fsn-write.yml before it opens any connection.
#   heavy_job_guard.sh wait-for-write [max_minutes]
#       Wait while an FSN production write is in progress; exit 1 if it is still running
#       after max_minutes (default 330). Used as the first job of the scheduled heavy
#       workflows, so a late-starting nightly job never runs beside a write.
#
# Needs GH_TOKEN (the workflow's github.token with `actions: read`) and GITHUB_REPOSITORY.
set -euo pipefail

HEAVY_WORKFLOWS=(
  pipeline-refresh.yml
  pipeline-sanity.yml
  pipeline-tag-library.yml
  pipeline-recompute.yml
  pipeline-certify.yml
  pipeline-cells-load.yml
  pipeline-cells-proof.yml
  cells-load-stage.yml
)
WRITE_WORKFLOW=pipeline-fsn-write.yml
ACTIVE_STATUSES=(in_progress queued waiting pending requested)
POLL_SECONDS="${HEAVY_GUARD_POLL_SECONDS:-60}"

active_runs() {
  # Prints one line per active run of workflow $1: "<id> <status> <url>".
  # Exits non-zero if any gh call fails (set -e in a command substitution is not enough).
  local workflow=$1 status
  for status in "${ACTIVE_STATUSES[@]}"; do
    gh run list --repo "$GITHUB_REPOSITORY" --workflow "$workflow" --status "$status" \
      --limit 20 --json databaseId,status,url \
      --jq '.[] | "\(.databaseId) \(.status) \(.url)"' || return 1
  done
}

refuse_if_heavy() {
  local workflow found=0 runs
  for workflow in "${HEAVY_WORKFLOWS[@]}"; do
    if ! runs=$(active_runs "$workflow"); then
      echo "::error::could not list $workflow runs; refusing (a heavy job may be running)"
      exit 1
    fi
    if [ -n "$runs" ]; then
      found=1
      while read -r line; do
        echo "::error::$workflow is active: $line"
      done <<<"$runs"
    fi
  done
  if [ "$found" -eq 1 ]; then
    echo "::error::a heavy database job is running or queued; dispatch the write after it finishes"
    exit 1
  fi
  echo "no heavy database job is running or queued"
}

wait_for_write() {
  # Fails CLOSED: a GitHub API error is "unknown", never "no write" (it waits and asks again).
  # Bounded: after max_minutes of wall-clock time it exits 1, so a hung write fails the
  # nightly job instead of blocking it forever (the write's own jobs time out at 340 min).
  local max_minutes=${1:-330} start=$SECONDS listing runs waited state
  while :; do
    waited=$((SECONDS - start))
    if listing=$(active_runs "$WRITE_WORKFLOW"); then
      runs=$(grep -E ' in_progress ' <<<"$listing" || true)
      if [ -z "$runs" ]; then
        echo "no FSN production write in progress"
        return 0
      fi
      state="in progress: $runs"
    else
      state="unknown (the GitHub API call failed)"
      echo "::warning::could not list $WRITE_WORKFLOW runs; treating a write as possibly in progress"
    fi
    if [ "$waited" -ge $((max_minutes * 60)) ]; then
      echo "::error::after ${max_minutes} minutes an FSN production write is still $state"
      exit 1
    fi
    echo "waiting for the FSN production write (${waited}s so far); write $state"
    sleep "$POLL_SECONDS"
  done
}

case "${1:-}" in
  refuse-if-heavy) refuse_if_heavy ;;
  wait-for-write) shift; wait_for_write "$@" ;;
  *) echo "usage: $0 refuse-if-heavy | wait-for-write [max_minutes]" >&2; exit 2 ;;
esac

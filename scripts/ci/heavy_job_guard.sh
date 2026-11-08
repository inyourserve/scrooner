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
  local workflow=$1 status
  for status in "${ACTIVE_STATUSES[@]}"; do
    gh run list --repo "$GITHUB_REPOSITORY" --workflow "$workflow" --status "$status" \
      --limit 20 --json databaseId,status,url \
      --jq '.[] | "\(.databaseId) \(.status) \(.url)"'
  done
}

refuse_if_heavy() {
  local workflow found=0 runs
  for workflow in "${HEAVY_WORKFLOWS[@]}"; do
    runs=$(active_runs "$workflow")
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
  local max_minutes=${1:-330} waited=0 runs
  while :; do
    runs=$(active_runs "$WRITE_WORKFLOW" | grep -E ' in_progress ' || true)
    if [ -z "$runs" ]; then
      echo "no FSN production write in progress"
      return 0
    fi
    if [ $((waited / 60)) -ge "$max_minutes" ]; then
      echo "::error::an FSN production write is still in progress after ${max_minutes} minutes: $runs"
      exit 1
    fi
    echo "waiting for the FSN production write to finish (${waited}s so far): $runs"
    sleep "$POLL_SECONDS"
    waited=$((waited + POLL_SECONDS))
  done
}

case "${1:-}" in
  refuse-if-heavy) refuse_if_heavy ;;
  wait-for-write) shift; wait_for_write "$@" ;;
  *) echo "usage: $0 refuse-if-heavy | wait-for-write [max_minutes]" >&2; exit 2 ;;
esac

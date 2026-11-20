"""Company ids whose top100-flow job is running or queued right now (their database state is mid-reload).

usage: top100_inflight.py [--workflow top100-flow.yml] [--jobs-json FILE ...]
Prints the ids comma-separated on one line (empty line when none). Uses `gh` (GITHUB_TOKEN with actions: read) to
list in-progress/queued runs of the workflow and each run's jobs; a "company <id>" job that is not completed marks the
company in flight. --jobs-json replaces the gh calls with saved `gh run view --json jobs` outputs (tests).

FAILS CLOSED: any gh error exits 3 with a message on stderr, so the caller knows it could not tell and must not commit
an export as if nothing were in flight.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

JOB = re.compile(r"^company (\d+)$")


def inflight_from_jobs(jobs: list[dict]) -> set[str]:
    out: set[str] = set()
    for j in jobs:
        m = JOB.match(j.get("name") or "")
        if m and j.get("status") != "completed":
            out.add(m.group(1))
    return out


def gh(args: list[str]) -> str:
    try:
        return subprocess.run(
            ["gh", *args], check=True, capture_output=True, text=True, timeout=120
        ).stdout
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ) as e:
        err = getattr(e, "stderr", "") or str(e)
        raise SystemExit(
            f"gh {' '.join(args[:3])} failed: {err.strip()[:300]}"
        ) from None


def live_run_ids(workflow: str) -> list[str]:
    ids: list[str] = []
    for status in ("in_progress", "queued", "waiting"):
        raw = gh(
            [
                "run",
                "list",
                "--workflow",
                workflow,
                "--status",
                status,
                "--limit",
                "20",
                "--json",
                "databaseId",
            ]
        )
        ids.extend(str(r["databaseId"]) for r in json.loads(raw or "[]"))
    return sorted(set(ids))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", default="top100-flow.yml")
    ap.add_argument(
        "--jobs-json",
        nargs="*",
        help="saved `gh run view --json jobs` files (no gh calls)",
    )
    a = ap.parse_args(argv)
    found: set[str] = set()
    try:
        if a.jobs_json is not None:
            for f in a.jobs_json:
                with open(f) as fh:
                    found |= inflight_from_jobs(json.load(fh).get("jobs", []))
        else:
            for rid in live_run_ids(a.workflow):
                found |= inflight_from_jobs(
                    json.loads(gh(["run", "view", rid, "--json", "jobs"])).get(
                        "jobs", []
                    )
                )
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 3
    except (OSError, ValueError) as e:
        print(f"could not read jobs: {e}", file=sys.stderr)
        return 3
    print(",".join(sorted(found, key=int)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

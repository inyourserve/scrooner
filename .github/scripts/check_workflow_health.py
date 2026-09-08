"""Checks one workflow's recent SCHEDULED run history via `gh run list`
and exits non-zero if there's a real failure pattern. Extracted out of
workflow-health-check.yml's own `run:` block (2026-09-08) -- an earlier
version embedded this directly as a multi-line Python heredoc inside a
YAML `run: |` block, which silently broke the workflow at parse time:
YAML requires every line inside a block scalar to stay indented at or
past the block's own base indentation, and the embedded Python's
unindented lines (e.g. `import json, sys` at column 0) fell below that
base, so YAML terminated the block early and the rest parsed as
invalid top-level YAML. A real script file has no such conflict
between YAML's indentation rules and Python's own."""

import json
import subprocess
import sys


def main(workflow_file: str) -> int:
    result = subprocess.run(
        ["gh", "run", "list", "--workflow", workflow_file, "--limit", "5", "--json", "conclusion,createdAt,event"],
        capture_output=True, text=True,
    )
    runs = json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else []

    scheduled = [r for r in runs if r.get("event") == "schedule"]
    if not scheduled:
        print("  no scheduled runs found yet (new workflow, or not committed long enough to have run) -- not flagging")
        return 0

    for r in scheduled:
        print(f"  {r.get('createdAt')}: {r.get('conclusion')}")

    failures = [r for r in scheduled if r.get("conclusion") not in ("success", None)]
    if len(failures) == len(scheduled):
        print("  ALL recent scheduled runs failed")
        return 1
    if len(failures) >= 3:
        print(f"  {len(failures)}/{len(scheduled)} recent scheduled runs failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

"""Reject NEW files over 10 MB (founder-approved repo slimming, 2026-11-16; doc/infra/GITHUB.md).

Only files ADDED in this push or pull request are checked: existing large inputs the code reads (the resolver CSVs)
keep being rewritten. Run outputs belong in workflow artifacts or Supabase Storage. A deliberate exception is listed,
with its reason, in .github/large-files-allowlist.txt (one path per line, `#` comments).

usage (CI): EVENT=push|pull_request BEFORE=<sha> PR_BASE=<sha> python3 scripts/ci/check_large_files.py
"""

import os
import subprocess
import sys
from pathlib import Path

LIMIT = 10 * 1024 * 1024
ALLOWLIST = Path(".github/large-files-allowlist.txt")
ZERO = "0" * 40


def allowlisted() -> set[str]:
    if not ALLOWLIST.exists():
        return set()
    return {
        ln.split("#", 1)[0].strip()
        for ln in ALLOWLIST.read_text().splitlines()
        if ln.split("#", 1)[0].strip()
    }


def added_files(env: dict[str, str]) -> list[str]:
    pr = env.get("EVENT") == "pull_request"
    base = env.get("PR_BASE") if pr else env.get("BEFORE")
    if not base or base == ZERO:
        # new branch: compare with main's merge base
        base = subprocess.run(
            ["git", "merge-base", "origin/main", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        if not base:
            return []
    rng = f"{base}...HEAD" if pr else f"{base}..HEAD"
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", rng],
        capture_output=True,
        text=True,
    ).stdout
    return [p for p in out.splitlines() if p]


def too_large(paths: list[str], allow: set[str], limit: int = LIMIT) -> list[tuple[str, int]]:
    bad = []
    for p in paths:
        f = Path(p)
        if p in allow or not f.is_file():
            continue
        size = f.stat().st_size
        if size > limit:
            bad.append((p, size))
    return bad


def main() -> int:
    bad = too_large(added_files(dict(os.environ)), allowlisted())
    for p, size in bad:
        print(f"::error file={p}::new file is {size / 1e6:.1f} MB (limit 10 MB). Use a workflow artifact or "
              f"Supabase Storage, or list it with a reason in {ALLOWLIST}.")
    if not bad:
        print("no new file over 10 MB")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

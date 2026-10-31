#!/usr/bin/env python3
"""Check migration identity, ordering, and basic file completeness."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION_DIR = ROOT / "pipeline" / "db" / "migrations"
NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")
SKIPPED_FILE = "SKIPPED.txt"
SKIPPED_LINE_RE = re.compile(r"^(\d{4}) \S")


def load_skipped(migration_dir: Path) -> tuple[set[int], list[str]]:
    """Numbers permanently skipped, listed one per line as 'NNNN reason' in SKIPPED.txt."""
    path = migration_dir / SKIPPED_FILE
    skipped: set[int] = set()
    problems: list[str] = []
    if not path.exists():
        return skipped, problems
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = SKIPPED_LINE_RE.match(line)
        if not match:
            problems.append(f"{SKIPPED_FILE}: line must be 'NNNN reason': {line!r}")
            continue
        number = int(match.group(1))
        if number in skipped:
            problems.append(f"{SKIPPED_FILE}: duplicate number {number:04d}")
        skipped.add(number)
    return skipped, problems


def check(migration_dir: Path) -> tuple[list[str], list[int]]:
    """Return (failures, versions). Gaps are allowed only for numbers in SKIPPED.txt."""
    failures: list[str] = []
    migrations = sorted(migration_dir.glob("*.sql"))
    versions: list[int] = []

    for path in migrations:
        match = NAME_RE.match(path.name)
        if not match:
            failures.append(f"invalid migration filename: {path.name}")
            continue
        versions.append(int(match.group(1)))
        sql = path.read_text(encoding="utf-8").strip()
        if not sql:
            failures.append(f"empty migration: {path.name}")
        elif not sql.endswith(";"):
            failures.append(f"migration must end with semicolon: {path.name}")

    skipped, problems = load_skipped(migration_dir)
    failures.extend(problems)

    if len(versions) != len(set(versions)):
        failures.append("duplicate migration version detected")
    for number in sorted(skipped & set(versions)):
        failures.append(f"{number:04d} is listed in {SKIPPED_FILE} but a migration file uses it")
    if versions:
        expected = [n for n in range(min(versions), max(versions) + 1) if n not in skipped]
        if versions != expected:
            failures.append(
                f"migration sequence is not contiguous: found={versions}, expected={expected} "
                f"(permitted gaps are listed in {SKIPPED_FILE}: {sorted(skipped)})"
            )
    return failures, versions


def main() -> int:
    failures, versions = check(MIGRATION_DIR)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    skipped, _ = load_skipped(MIGRATION_DIR)
    print(
        f"migrations: {len(versions)} file(s), contiguous {versions[0]:04d}-{versions[-1]:04d} "
        f"({len(skipped)} permanently skipped)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

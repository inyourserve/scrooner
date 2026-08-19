#!/usr/bin/env python3
"""Check migration identity, ordering, and basic file completeness."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION_DIR = ROOT / "pipeline" / "db" / "migrations"
NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")


def main() -> int:
    failures: list[str] = []
    migrations = sorted(MIGRATION_DIR.glob("*.sql"))
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

    if len(versions) != len(set(versions)):
        failures.append("duplicate migration version detected")
    if versions:
        expected = list(range(min(versions), max(versions) + 1))
        if versions != expected:
            failures.append(f"migration sequence is not contiguous: found={versions}, expected={expected}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"migrations: {len(migrations)} file(s), contiguous {versions[0]:04d}-{versions[-1]:04d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

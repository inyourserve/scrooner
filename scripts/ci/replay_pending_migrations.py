"""Replay pipeline/db/pending/*.sql on a database that already has every committed migration, then smoke-test
every object they create or change. Used by .github/workflows/migrations-pending-replay.yml.

Pending files are migrations written ahead of their contiguous number (doc 53): they must apply cleanly, in numeric
order, on top of main's committed schema, long before anyone runs them on the live database.

Checks (exit 1 on any failure):
- names match NNNN_snake_case.sql, numbers are unique, none collides with a committed migration, each is above the
  highest committed number; gaps (numbers held on unmerged branches) are reported, not failed;
- each file applies with psql ON_ERROR_STOP in one transaction (--single-transaction);
- every `create table|view|materialized view` object answers `select * from <obj> limit 0`, and every
  `alter table <t> add column [if not exists] <c>` answers `select <c> from <t> limit 0`.

usage: python3 scripts/ci/replay_pending_migrations.py [pending_dir] [migrations_dir]   (PG* env vars select the DB)
"""

import re
import subprocess
import sys
from pathlib import Path

NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")
OBJ_RE = re.compile(
    r"\bcreate\s+(?:or\s+replace\s+)?(?:materialized\s+)?(?:table|view)\s+(?:if\s+not\s+exists\s+)?([a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*)",
    re.I,
)
ALTER_RE = re.compile(r"\balter\s+table\s+(?:if\s+exists\s+)?(?:only\s+)?([a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*)(.*?);", re.I | re.S)
ADD_COL_RE = re.compile(r"\badd\s+column\s+(?:if\s+not\s+exists\s+)?([a-z_][a-z0-9_]*)", re.I)


def strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def smoke_targets(sql: str) -> list[str]:
    """SELECT statements that prove each created object / added column exists."""
    sql = strip_comments(sql)
    out = [f"select * from {o} limit 0" for o in dict.fromkeys(m.lower() for m in OBJ_RE.findall(sql))]
    for table, body in ALTER_RE.findall(sql):
        for col in ADD_COL_RE.findall(body):
            out.append(f"select {col.lower()} from {table.lower()} limit 0")
    return out


def check_names(pending: list[Path], committed: list[Path]) -> tuple[list[str], list[str]]:
    errors, notes = [], []
    done = {int(m.group(1)) for p in committed if (m := NAME_RE.match(p.name))}
    top = max(done, default=0)
    seen: set[int] = set()
    for p in pending:
        m = NAME_RE.match(p.name)
        if not m:
            errors.append(f"{p.name}: name must be NNNN_snake_case.sql")
            continue
        n = int(m.group(1))
        if n in seen:
            errors.append(f"{p.name}: duplicate pending number {n:04d}")
        if n in done:
            errors.append(f"{p.name}: {n:04d} is already a committed migration")
        elif n <= top:
            errors.append(f"{p.name}: {n:04d} is not above the highest committed migration {top:04d}")
        seen.add(n)
    nums = sorted(seen | {top})
    gaps = [n for n in range(top + 1, max(nums) + 1) if n not in seen]
    if gaps:
        notes.append("held numbers not on main (expected while their branches are open): " + ", ".join(f"{g:04d}" for g in gaps))
    return errors, notes


def psql(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["psql", "-X", "--set", "ON_ERROR_STOP=1", "-q", *args], capture_output=True, text=True)


def main() -> int:
    pending_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "pipeline/db/pending")
    migrations_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "pipeline/db/migrations")
    pending = sorted(pending_dir.glob("*.sql"))
    if not pending:
        print("no pending migrations")
        return 0
    errors, notes = check_names(pending, sorted(migrations_dir.glob("*.sql")))
    for n in notes:
        print(f"note: {n}")
    for p in pending:
        r = psql("--single-transaction", "-f", str(p))
        if r.returncode:
            errors.append(f"{p.name}: does not apply on the committed schema:\n{r.stderr.strip()}")
            continue
        print(f"applied {p.name}")
        for q in smoke_targets(p.read_text(encoding="utf-8")):
            s = psql("-c", q)
            if s.returncode:
                errors.append(f"{p.name}: smoke `{q}` failed: {s.stderr.strip()}")
            else:
                print(f"  ok  {q}")
    for e in errors:
        print(f"::error::{e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

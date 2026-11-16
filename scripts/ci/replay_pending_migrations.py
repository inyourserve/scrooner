"""Replay pipeline/db/pending/*.sql on a database that already has every committed migration, then smoke-test
every object they create or change. Used by .github/workflows/migrations-pending-replay.yml.

Pending files are migrations written ahead of their contiguous number (doc 53): they must apply cleanly, in numeric
order, on top of main's committed schema, long before anyone runs them on the live database.

Checks (exit 1 on any failure):
- names match NNNN_snake_case.sql, numbers are unique, none collides with a committed migration, each is above the
  highest committed number; the pending set continues main's sequence with no hole (a gap must be listed in migrations/SKIPPED.txt);
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


def load_skipped(migrations_dir: Path) -> set[int]:
    path = migrations_dir / "SKIPPED.txt"
    if not path.exists():
        return set()
    return {int(m.group(1)) for line in path.read_text(encoding="utf-8").splitlines() if (m := re.match(r"^(\d{4}) \S", line))}


# Behaviour smokes beyond "the object exists": (file number, sql, text that must appear, expect_error). The text is
# searched in stderr when expect_error, else in stdout. Each proves a guard or constraint is live, not only the tables.
BEHAVIOUR_SMOKES: list[tuple[str, str, str, bool]] = [
    ("0124", "insert into analytics.verifier_check (company_id, data_point_name, period_grain, period_start, period_end, "
             "verdict, draw_id, draw_kind, verifier_session) values (1, 'x', 'FY', '2024-01-01', '2024-12-31', "
             "'blank_right', 'd', 'blanks', 's')", "written by the Verifier only", True),
    ("0125", "select conname from pg_constraint where conname = 'company_tag_map_dims_decision_check'",
     "company_tag_map_dims_decision_check", False),
    ("0125", "select proname from pg_proc where proname = 'company_tag_map_no_overlap'", "company_tag_map_no_overlap", False),
    ("0129", "select count(*) from pg_proc p join pg_namespace n on n.oid = p.pronamespace where (n.nspname, p.proname) in "
             "(('analytics','check_first_match_priority_unique'),('analytics','cell_evidence_append_only'),"
             "('core','company_identity_audit_guard'),('analytics','slot_protected_cell_guard'),"
             "('analytics','company_value_owner_guard'),('core','company_history_source_no_overlap'),"
             "('analytics','company_tag_map_no_overlap'),('analytics','verifier_check_writer_guard')) "
             "and p.proconfig::text ~ 'search_path=pg_catalog, (analytics|core)'", "8", False),
    ("0130", "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display) "
             "values (1, 'x', '2024-12-31', 'FY', 'HIDDEN_ROW')", "cell_display_state_hide_class_iff_hidden", True),
    ("0130", "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class) "
             "values (1, 'x', '2024-12-31', 'FY', 'OPEN', 'pre_filing')", "cell_display_state_hide_class_iff_hidden", True),
    ("0130", "insert into analytics.cell_display_state (company_id, data_point, period_end, grain, display, hide_class) "
             "values (1, 'x', '2024-12-31', 'FY', 'HIDDEN_YEAR', 'made_up')", "cell_display_state_hide_class_check", True),
]


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
    skipped = load_skipped(committed[0].parent) if committed else set()
    for n in sorted(seen & skipped):
        errors.append(f"{n:04d} is listed in SKIPPED.txt but a pending file uses it")
    # the pending set must continue main's sequence with no hole: committed top + pending + SKIPPED numbers
    gaps = [n for n in range(top + 1, max(nums) + 1) if n not in seen and n not in skipped]
    for g in gaps:
        errors.append(f"pending set is not contiguous: {g:04d} is neither a pending file nor listed in SKIPPED.txt")
    if seen:
        inside = ", ".join(f"{n:04d}" for n in sorted(skipped) if min(seen) < n < max(seen))
        notes.append(f"pending set {min(seen):04d}-{max(seen):04d}: " + ", ".join(f"{n:04d}" for n in sorted(seen))
                     + (f" (skipped inside the range: {inside})" if inside else ""))
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
    applied = {m.group(1) for p in pending if (m := NAME_RE.match(p.name))}
    for num, q, needle, expect_error in BEHAVIOUR_SMOKES:
        if num not in applied:
            continue
        r = psql("-At", "-c", q)
        out = (r.stderr if expect_error else r.stdout) or ""
        if bool(r.returncode) != expect_error or needle not in out:
            errors.append(f"{num}: behaviour smoke `{q[:70]}` expected {needle!r}, got rc={r.returncode} {out.strip()[:200]}")
        else:
            print(f"  ok  [{num}] {needle}")
    for e in errors:
        print(f"::error::{e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

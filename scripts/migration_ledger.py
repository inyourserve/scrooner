#!/usr/bin/env python3
"""Migration ledger tooling (review-response plan P1.2): ops.migration_ledger, migration 0131.

Subcommands
  row FILE --by WHO     print the INSERT to append to FILE's own transaction (the same-transaction rule)
  backfill [--emit-sql] probe the LIVE database read-only (one connection, statement_timeout set) and propose ledger
                        rows for migrations already applied; never writes. --emit-sql prints reviewable INSERTs.

Pure functions (parse_objects, sha256_file, compare, row_sql) are unit-tested; the DB parts take an open connection.
Nothing here ever writes to the database. `check_migrations.py --live` uses fetch_ledger and compare.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_DIR = ROOT / "pipeline" / "db" / "migrations"
PENDING_DIR = ROOT / "pipeline" / "db" / "pending"
NAME_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")
IDENT = r"[a-z_][a-z0-9_]*"
REL = rf"({IDENT})\.({IDENT})"
CREATE_REL_RE = re.compile(
    rf"\bcreate\s+(?:or\s+replace\s+)?(?:materialized\s+)?(?:unlogged\s+)?(table|view)\s+(?:if\s+not\s+exists\s+)?{REL}", re.I
)
CREATE_SCHEMA_RE = re.compile(rf"\bcreate\s+schema\s+(?:if\s+not\s+exists\s+)?({IDENT})", re.I)
CREATE_INDEX_RE = re.compile(
    rf"\bcreate\s+(?:unique\s+)?index\s+(?:concurrently\s+)?(?:if\s+not\s+exists\s+)?({IDENT})\s+on\s+(?:only\s+)?{REL}", re.I
)
CREATE_FUNC_RE = re.compile(rf"\bcreate\s+(?:or\s+replace\s+)?function\s+{REL}\s*\(", re.I)
ALTER_RE = re.compile(rf"\balter\s+table\s+(?:if\s+exists\s+)?(?:only\s+)?{REL}(.*?);", re.I | re.S)
ADD_COL_RE = re.compile(rf"\badd\s+column\s+(?:if\s+not\s+exists\s+)?({IDENT})", re.I)


def strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"--[^\n]*", " ", sql)
    # string literals can contain words like 'create table x.y'; blank them out
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


@dataclass
class Objects:
    schemas: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)  # schema.name, table/view/matview
    indexes: list[tuple[str, str]] = field(default_factory=list)  # (schema of table, index name)
    functions: list[str] = field(default_factory=list)  # schema.name
    columns: list[tuple[str, str, str]] = field(default_factory=list)  # schema, table, column

    def count(self) -> int:
        return len(self.schemas) + len(self.relations) + len(self.indexes) + len(self.functions) + len(self.columns)


def _uniq(xs):
    return list(dict.fromkeys(xs))


def parse_objects(sql: str) -> Objects:
    """Objects a migration creates, as far as a static scan can tell. Data-only statements are not probed."""
    s = strip_comments(sql)
    o = Objects()
    o.schemas = _uniq(m.group(1).lower() for m in CREATE_SCHEMA_RE.finditer(s))
    o.relations = _uniq(f"{m.group(2).lower()}.{m.group(3).lower()}" for m in CREATE_REL_RE.finditer(s))
    o.indexes = _uniq((m.group(2).lower(), m.group(1).lower()) for m in CREATE_INDEX_RE.finditer(s))
    o.functions = _uniq(f"{m.group(1).lower()}.{m.group(2).lower()}" for m in CREATE_FUNC_RE.finditer(s))
    cols = []
    for m in ALTER_RE.finditer(s):
        for c in ADD_COL_RE.findall(m.group(3)):
            cols.append((m.group(1).lower(), m.group(2).lower(), c.lower()))
    o.columns = _uniq(cols)
    return o


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sql_literal(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def row_sql(path: Path, applied_by: str, evidence: str = "transaction") -> str:
    m = NAME_RE.match(path.name)
    if not m:
        raise ValueError(f"not a migration filename: {path.name}")
    if not applied_by.strip():
        raise ValueError("applied_by is required")
    return (
        "insert into ops.migration_ledger (number, filename, sha256, applied_by, evidence) values "
        f"({int(m.group(1))}, {sql_literal(path.name)}, {sql_literal(sha256_file(path))}, "
        f"{sql_literal(applied_by)}, {sql_literal(evidence)});"
    )


def repo_files(migration_dir: Path = MIGRATION_DIR, pending_dir: Path = PENDING_DIR) -> dict[int, tuple[Path, str]]:
    """number -> (path, 'migrations'|'pending')."""
    out: dict[int, tuple[Path, str]] = {}
    for folder, kind in ((migration_dir, "migrations"), (pending_dir, "pending")):
        if not folder.exists():
            continue
        for p in sorted(folder.glob("*.sql")):
            m = NAME_RE.match(p.name)
            if m:
                out.setdefault(int(m.group(1)), (p, kind))
    return out


def compare(files: dict[int, tuple[Path, str]], ledger: dict[int, tuple[str, str]], skipped: set[int] | None = None) -> list[str]:
    """Failures when repo files and ledger rows disagree. ledger: number -> (filename, sha256).

    - a ledger row with no repo file, or a different name, or a different hash, fails;
    - a committed migrations/ file with no ledger row fails (pending/ files may be unapplied, so they may lack a row).
    """
    failures: list[str] = []
    for number in sorted(ledger):
        name, digest = ledger[number]
        if number not in files:
            failures.append(f"{number:04d}: ledger row {name} has no repo file")
            continue
        path, _kind = files[number]
        if path.name != name:
            failures.append(f"{number:04d}: name differs, repo {path.name} vs ledger {name}")
        elif sha256_file(path) != digest:
            failures.append(f"{number:04d}: hash differs for {name} (file edited after it was applied, or a different file ran)")
    for number in sorted(files):
        path, kind = files[number]
        if kind == "migrations" and number not in ledger:
            failures.append(f"{number:04d}: {path.name} is committed but has no ledger row")
    return failures


def fetch_ledger(conn) -> dict[int, tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("select to_regclass('ops.migration_ledger') is not null")
        if not cur.fetchone()[0]:
            raise RuntimeError("ops.migration_ledger does not exist (migration 0131 is not applied)")
        cur.execute("select number, filename, sha256 from ops.migration_ledger")
        return {n: (f, h) for n, f, h in cur.fetchall()}


def connect_readonly(url: str, timeout_ms: int = 60000):
    """One read-only connection with an explicit statement_timeout."""
    import psycopg  # lazy: check_migrations.py stays stdlib-only without --live

    conn = psycopg.connect(url, autocommit=False)
    conn.read_only = True
    with conn.cursor() as cur:
        cur.execute(f"set statement_timeout = {int(timeout_ms)}")
    return conn


def probe(conn, objs: Objects) -> tuple[list[str], list[str]]:
    """(present, missing) object descriptions for one migration. Read-only catalog lookups."""
    present: list[str] = []
    missing: list[str] = []
    with conn.cursor() as cur:
        for sch in objs.schemas:
            cur.execute("select exists (select 1 from pg_namespace where nspname = %s)", (sch,))
            (present if cur.fetchone()[0] else missing).append(f"schema {sch}")
        for rel in objs.relations:
            cur.execute("select to_regclass(%s) is not null", (rel,))
            (present if cur.fetchone()[0] else missing).append(f"relation {rel}")
        for sch, idx in objs.indexes:
            cur.execute("select exists (select 1 from pg_indexes where schemaname = %s and indexname = %s)", (sch, idx))
            (present if cur.fetchone()[0] else missing).append(f"index {sch}.{idx}")
        for fn in objs.functions:
            sch, name = fn.split(".")
            cur.execute(
                "select exists (select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace "
                "where n.nspname = %s and p.proname = %s)",
                (sch, name),
            )
            (present if cur.fetchone()[0] else missing).append(f"function {fn}")
        for sch, tbl, col in objs.columns:
            cur.execute(
                "select exists (select 1 from information_schema.columns "
                "where table_schema = %s and table_name = %s and column_name = %s)",
                (sch, tbl, col),
            )
            (present if cur.fetchone()[0] else missing).append(f"column {sch}.{tbl}.{col}")
    return present, missing


def verdict(objs: Objects, present: list[str], missing: list[str]) -> str:
    if objs.count() == 0:
        return "UNPROBEABLE"  # data-only or drop/alter-only: a human decides
    if not missing:
        return "APPLIED"
    return "PARTIAL" if present else "ABSENT"


def backfill_plan(conn, files: dict[int, tuple[Path, str]]) -> list[dict]:
    """One proposal per repo file (migrations/ and pending/), in number order. Reads the catalog only."""
    out = []
    for number in sorted(files):
        path, kind = files[number]
        objs = parse_objects(path.read_text(encoding="utf-8"))
        present, missing = probe(conn, objs)
        out.append(
            {
                "number": number,
                "filename": path.name,
                "folder": kind,
                "sha256": sha256_file(path),
                "verdict": verdict(objs, present, missing),
                "present": len(present),
                "missing": missing,
            }
        )
    return out


def render_plan(plan: list[dict], emit_sql: bool, applied_by: str) -> str:
    lines = []
    for p in plan:
        miss = f" missing: {'; '.join(p['missing'])}" if p["missing"] else ""
        lines.append(f"{p['number']:04d} {p['verdict']:<11} present={p['present']}{miss}  ({p['folder']}/{p['filename']})")
    if emit_sql:
        lines += [
            "",
            "-- Proposed rows: APPLIED only. PARTIAL / ABSENT / UNPROBEABLE need a human; applying needs the founder's typed words.",
            "begin;",
        ]
        for p in plan:
            if p["verdict"] == "APPLIED":
                lines.append(
                    "insert into ops.migration_ledger (number, filename, sha256, applied_by, evidence) values "
                    f"({p['number']}, {sql_literal(p['filename'])}, {sql_literal(p['sha256'])}, {sql_literal(applied_by)}, 'probe');"
                )
        lines.append("commit;")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("row")
    r.add_argument("file", type=Path)
    r.add_argument("--by", required=True)
    b = sub.add_parser("backfill")
    b.add_argument("--emit-sql", action="store_true")
    b.add_argument("--by", default="backfill-probe")
    b.add_argument("--timeout-ms", type=int, default=60000)
    b.add_argument("--db-url", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args(argv)
    if args.cmd == "row":
        print(row_sql(args.file, args.by))
        return 0
    if not args.db_url:
        print("DATABASE_URL (or --db-url) is required", file=sys.stderr)
        return 2
    conn = connect_readonly(args.db_url, args.timeout_ms)
    try:
        print(render_plan(backfill_plan(conn, repo_files()), args.emit_sql, args.by))
    finally:
        conn.rollback()
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

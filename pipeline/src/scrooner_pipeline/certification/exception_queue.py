"""The single exceptions queue (PIPELINE.md section 4, step M5): loader, close and report for ops.exception_queue (0135).

Builds queue rows from today's separate sources (files in the repo; nothing is read from the live DB):

  OPEN         data-team/strategy/top100-coverage.csv, display = OPEN and class <> DISAGREE (no proof, no evidenced hide);
               family "<class>:<reason_code>", owner resolver, one row per cell
  DISAGREE     the same file, class = DISAGREE; family = reason_code, owner proof
  SAMPLE_FAIL  approvals/registry.csv, the latest row per ticker when its verdict is FAIL (owner verifier);
               also approvals/reads/*.csv rows with verdict MISMATCH
  NEEDS_READ   approvals/reads/*.csv rows with verdict NEEDS_READ or REVIEW (owner approver, per the 2026-11-28 review)
  DRILL_MISS   data-team/tags/rules/inbox/drill-auto.csv rows whose STATUS.csv status is open (owner tag_expert);
               cells_affected from the note's cells=N
  DEAD_LETTER  data-team/tags/line_map/refresh-failures/*.md (a refused resolver refresh; owner data_engineer)
  CENSUS_FAIL  no persisted source exists yet (stage 5 prints census results only inside the certificate); rows arrive through
               --extra-csv (the Row column names) until stage 5 writes them directly. Orchestrator dead letters the same way.

The key of an OPEN/DISAGREE item is the cell (no sha: the coverage file is rebuilt hourly). The key of a stage 5 item is
ticker + coverage_sha256 + judge version (a new sha is a new item; the old one closes when the check passes on it).

Usage (from the repo root, PYTHONPATH=pipeline/src):
  python3 -m scrooner_pipeline.certification.exception_queue load --dry-run [--db-url URL]
  python3 -m scrooner_pipeline.certification.exception_queue load --apply --db-url "$DATABASE_URL"
  python3 -m scrooner_pipeline.certification.exception_queue report --db-url "$DATABASE_URL"
  python3 -m scrooner_pipeline.certification.exception_queue close KEY --by who --rule-id R --test-path P

--apply needs migration 0135 applied first (founder's typed words); one transaction, batched, statement_timeout set.
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
KINDS = ("OPEN", "DISAGREE", "CENSUS_FAIL", "SAMPLE_FAIL", "NEEDS_READ", "DRILL_MISS", "DEAD_LETTER")
LANES = ("resolver", "proof", "verifier", "tag_expert", "approver", "data_engineer")
CHUNK = 1000
STATEMENT_TIMEOUT_MS = 120_000
UNRECORDED_JUDGE = "unrecorded"  # registry.csv has no judge-version column yet
COVERAGE = "data-team/strategy/top100-coverage.csv"
REGISTRY = "data-team/strategy/approvals/registry.csv"
READS = "data-team/strategy/approvals/reads"
DRILL = "data-team/tags/rules/inbox/drill-auto.csv"
STATUS = "data-team/tags/rules/inbox/STATUS.csv"
FAILURES = "data-team/tags/line_map/refresh-failures"


@dataclass(frozen=True)
class Row:
    idempotency_key: str
    kind: str
    cell_key: str
    root_cause_family: str
    owner_lane: str
    ticker: str | None = None
    cik: str | None = None
    company_id: int | None = None
    data_point: str | None = None
    period_end: str | None = None
    cells_affected: int = 1
    detail: str | None = None
    source_sha: str | None = None
    source_path: str | None = None
    evidence_locator: str | None = None
    judge_version: str | None = None


COLUMNS = tuple(Row.__dataclass_fields__)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _blank(v) -> str | None:
    v = (v or "").strip()
    return v or None


def _dec(v) -> str | None:
    try:
        return format(Decimal(v), "f")
    except (InvalidOperation, TypeError):
        return None


def coverage_rows(root: Path = ROOT) -> list[Row]:
    path = root / COVERAGE
    sha = _sha(path)
    out: list[Row] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["display"] != "OPEN":
                continue
            disagree = r["class"] == "DISAGREE"
            kind = "DISAGREE" if disagree else "OPEN"
            code = r["reason_code"] or "no_reason_code"
            family = code if disagree else f"{r['class']}:{code}"
            cell = f"{r['data_point']}|{r['fiscal_year']}|{r['period_end']}"
            loc = " ".join(x for x in (r["accession"], r["r_page"]) if x) or None
            val = _dec(r["shown_value"])
            out.append(
                Row(
                    idempotency_key=f"{kind}|{r['company_id']}|{cell}",
                    kind=kind,
                    cell_key=cell,
                    root_cause_family=family,
                    owner_lane="proof" if disagree else "resolver",
                    ticker=r["ticker"],
                    company_id=int(r["company_id"]),
                    data_point=r["data_point"],
                    period_end=r["period_end"] or None,
                    detail=f"proof_verdict={r['proof_verdict']}" + (f" shown_value={val}" if val else ""),
                    source_sha=sha,
                    source_path=COVERAGE,
                    evidence_locator=loc,
                )
            )
    return out


def registry_rows(root: Path = ROOT) -> list[Row]:
    path = root / REGISTRY
    sha = _sha(path)
    latest: dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["ticker"] not in latest or r["date"] >= latest[r["ticker"]]["date"]:
                latest[r["ticker"]] = r
    out = []
    for t, r in sorted(latest.items()):
        if r["verdict"] != "FAIL":
            continue
        errors = int(r["errors"] or 0)
        out.append(
            Row(
                idempotency_key=f"SAMPLE_FAIL|{t}|{r['coverage_sha256']}|{UNRECORDED_JUDGE}",
                kind="SAMPLE_FAIL",
                cell_key=f"{t}:{r['coverage_sha256']}:{UNRECORDED_JUDGE}",
                root_cause_family="sampled_errors" if errors else "bound_above_1.5pct",
                owner_lane="verifier",
                ticker=t,
                detail=f"{r['date']} n={r['n']} errors={errors} upper_bound_95={_dec(r['upper_bound_95'])}",
                source_sha=r["coverage_sha256"],
                source_path=REGISTRY,
                evidence_locator=f"{REGISTRY}: {t} {r['date']} seed {r['seed']}",
                judge_version=UNRECORDED_JUDGE,
            )
        )
    return out


def read_rows(root: Path = ROOT) -> list[Row]:
    out = []
    for f in sorted(glob.glob(str(root / READS / "*.csv"))):
        name = Path(f).name
        m = re.match(r"([A-Z.]+)-([0-9a-f]{12})\.csv$", name)
        if not m:
            continue
        t, sha12 = m.groups()
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                v = (r.get("verdict") or "").upper()
                if v == "MATCH":
                    continue
                needs = v in ("NEEDS_READ", "REVIEW")
                kind = "NEEDS_READ" if needs else "SAMPLE_FAIL"
                cell = f"{r['data_point']}|{r['fiscal_year']}"
                out.append(
                    Row(
                        idempotency_key=f"{kind}|{t}|{sha12}|{UNRECORDED_JUDGE}|{cell}",
                        kind=kind,
                        cell_key=f"{t}:{sha12}:{UNRECORDED_JUDGE}:{cell}",
                        root_cause_family="read_" + (v.lower() or "unverdicted"),
                        owner_lane="approver" if needs else "verifier",
                        ticker=t,
                        data_point=r["data_point"],
                        detail=f"verdict={v}",
                        source_sha=sha12,  # the certificate's coverage-sha prefix, from the file name
                        source_path=f"{READS}/{name}",
                        evidence_locator=(r.get("evidence") or "")[:300] or f"{READS}/{name}",
                        judge_version=UNRECORDED_JUDGE,
                    )
                )
    return out


def drill_rows(root: Path = ROOT) -> list[Row]:
    status = {}
    with (root / STATUS).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            status[r["rule_id"]] = r["status"].strip().split(" ")[0].lower()
    path = root / DRILL
    sha = _sha(path)
    out = []
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if status.get(r["rule_id"]) != "open" or r["kind"] != "proposal_open":
                continue
            note = r["note"]
            n = re.search(r"cells=(\d+)", note)
            el = re.search(r"element=(\S+)", note)
            out.append(
                Row(
                    idempotency_key=f"DRILL_MISS|{r['rule_id']}",
                    kind="DRILL_MISS",
                    cell_key=r["rule_id"],
                    root_cause_family=f"{note.split(' ', 1)[0]}:{el.group(1) if el else r['data_point']}",
                    owner_lane="tag_expert",
                    data_point=r["data_point"],
                    cells_affected=max(int(n.group(1)) if n else 1, 1),
                    detail=note[:400],
                    source_sha=sha,
                    source_path=DRILL,
                    evidence_locator=r["evidence"] or None,
                )
            )
    return out


def failure_rows(root: Path = ROOT) -> list[Row]:
    out = []
    for f in sorted(glob.glob(str(root / FAILURES / "*.md"))):
        text = Path(f).read_text(encoding="utf-8")
        name = Path(f).name
        reasons = [ln[2:].strip() for ln in text.splitlines() if ln.startswith("- ")]
        n = re.search(r"values that would change: (\d+)", text)
        scope = re.search(r"^Scope: (.+)$", text, re.M)
        out.append(
            Row(
                idempotency_key=f"DEAD_LETTER|refresh|{name}",
                kind="DEAD_LETTER",
                cell_key=f"refresh:{name}",
                root_cause_family="refresh_refused:" + (reasons[0] if reasons else "no_reason_listed")[:80],
                owner_lane="data_engineer",
                ticker=(scope.group(1).split(",")[0].strip() if scope else None) or "resolver-refresh",
                cells_affected=max(int(n.group(1)) if n else 1, 1),
                detail="; ".join(reasons)[:400],
                source_sha=hashlib.sha256(text.encode()).hexdigest(),
                source_path=f"{FAILURES}/{name}",
                evidence_locator=f"{FAILURES}/{name}",
            )
        )
    return out


def extra_rows(path: Path) -> list[Row]:
    """Rows from a CSV with the Row column names (CENSUS_FAIL, orchestrator DEAD_LETTER). Strict: a bad row raises."""
    out = []
    with path.open(newline="", encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh), 2):
            kw = {k: _blank(r.get(k)) for k in COLUMNS}
            for k in ("idempotency_key", "kind", "cell_key", "root_cause_family", "owner_lane"):
                if not kw[k]:
                    raise ValueError(f"{path}:{i}: {k} is required")
            if kw["kind"] not in KINDS or kw["owner_lane"] not in LANES:
                raise ValueError(f"{path}:{i}: bad kind or owner_lane")
            kw["company_id"] = int(kw["company_id"]) if kw["company_id"] else None
            kw["cells_affected"] = int(kw["cells_affected"] or 1)
            out.append(Row(**kw))
    return out


def build(root: Path = ROOT, extra: list[Path] = ()) -> list[Row]:
    rows = coverage_rows(root) + registry_rows(root) + read_rows(root) + drill_rows(root) + failure_rows(root)
    for p in extra:
        rows += extra_rows(p)
    return list({r.idempotency_key: r for r in rows}.values())  # one row per key within a batch


def counts(rows) -> dict[tuple[str, str], tuple[int, int]]:
    """(kind, family) -> (items, cells affected)."""
    c: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        c[(r.kind, r.root_cause_family)][0] += 1
        c[(r.kind, r.root_cause_family)][1] += r.cells_affected
    return {k: (v[0], v[1]) for k, v in c.items()}


def format_counts(rows) -> str:
    by_kind = Counter(r.kind for r in rows)
    lines = [f"rows: {len(rows)}"] + [f"kind {k}: {by_kind[k]}" for k in KINDS if by_kind[k]]
    lines.append("kind | root_cause_family | items | cells_affected")
    for (k, f), (n, cells) in sorted(counts(rows).items(), key=lambda kv: (KINDS.index(kv[0][0]), -kv[1][1], kv[0][1])):
        lines.append(f"{k} | {f} | {n} | {cells}")
    return "\n".join(lines)


_CELL_KIND = "ops.exception_queue.kind in ('OPEN', 'DISAGREE')"
UPSERT = f"""
insert into ops.exception_queue (idempotency_key, kind, cell_key, root_cause_family, owner_lane, ticker, cik, company_id,
    data_point, period_end, cells_affected, detail, source_sha, source_path, evidence_locator, judge_version)
values (%(idempotency_key)s, %(kind)s, %(cell_key)s, %(root_cause_family)s, %(owner_lane)s, %(ticker)s, %(cik)s,
    %(company_id)s, %(data_point)s, %(period_end)s, %(cells_affected)s, %(detail)s, %(source_sha)s, %(source_path)s,
    %(evidence_locator)s, %(judge_version)s)
on conflict (idempotency_key) do update set
    root_cause_family = excluded.root_cause_family, cells_affected = excluded.cells_affected, detail = excluded.detail,
    source_sha = excluded.source_sha, source_path = excluded.source_path, evidence_locator = excluded.evidence_locator,
    last_seen_at = now(),
    -- a cell still OPEN/DISAGREE after a close means the close did not work: reopen. Other kinds stay closed.
    reopened_count = ops.exception_queue.reopened_count
        + case when ops.exception_queue.closed_at is not null and {_CELL_KIND} then 1 else 0 end,
    opened_at = case when ops.exception_queue.closed_at is not null and {_CELL_KIND}
                     then now() else ops.exception_queue.opened_at end,
    closed_at = case when {_CELL_KIND} then null else ops.exception_queue.closed_at end,
    close_rule_id = case when {_CELL_KIND} then null else ops.exception_queue.close_rule_id end,
    close_test_path = case when {_CELL_KIND} then null else ops.exception_queue.close_test_path end,
    close_hide_class = case when {_CELL_KIND} then null else ops.exception_queue.close_hide_class end,
    close_evidence = case when {_CELL_KIND} then null else ops.exception_queue.close_evidence end,
    closed_by = case when {_CELL_KIND} then null else ops.exception_queue.closed_by end
"""


def _params(r: Row) -> dict:
    return {k: getattr(r, k) for k in COLUMNS}


def load(conn, rows: list[Row], apply: bool) -> dict[str, int]:
    """Upsert rows in chunks inside one transaction. Dry run: count new vs existing, roll back, write nothing."""
    keys = [r.idempotency_key for r in rows]
    with conn.cursor() as cur:
        cur.execute(f"set local statement_timeout = {STATEMENT_TIMEOUT_MS}")
        cur.execute("select count(*) from ops.exception_queue where idempotency_key = any(%s)", (keys,))
        existing = cur.fetchone()[0]
        if apply:
            for i in range(0, len(rows), CHUNK):
                cur.executemany(UPSERT, [_params(r) for r in rows[i : i + CHUNK]])
    if apply:
        conn.commit()
    else:
        conn.rollback()
    return {"rows": len(rows), "new": len(rows) - existing, "existing": existing}


def close_item(conn, key: str, by: str, rule_id=None, test_path=None, hide_class=None, evidence=None) -> bool:
    """Close one open item. The table's CHECK refuses a close without (rule id + test path) or (hide class + evidence)."""
    with conn.cursor() as cur:
        cur.execute(f"set local statement_timeout = {STATEMENT_TIMEOUT_MS}")
        cur.execute(
            "update ops.exception_queue set closed_at = now(), closed_by = %s, close_rule_id = %s, close_test_path = %s, "
            "close_hide_class = %s, close_evidence = %s where idempotency_key = %s and closed_at is null",
            (by, _blank(rule_id), _blank(test_path), _blank(hide_class), _blank(evidence), key),
        )
        n = cur.rowcount
    conn.commit()
    return n == 1


REPORT_FLOW = """
select d::date as day,
       (select count(*) from ops.exception_queue where opened_at >= d and opened_at < d + interval '1 day') as inflow,
       (select count(*) from ops.exception_queue where closed_at >= d and closed_at < d + interval '1 day') as outflow
from generate_series(current_date - (%s - 1), current_date, interval '1 day') d order by day
"""
REPORT_FAMILY = """
select root_cause_family, kind, owner_lane, count(*) as items, sum(cells_affected) as cells_affected,
       count(distinct coalesce(ticker, company_id::text)) as companies
from ops.exception_queue where closed_at is null
group by root_cause_family, kind, owner_lane order by sum(cells_affected) desc, root_cause_family limit %s
"""


def report(conn, days: int = 14, top: int = 25) -> str:
    """PIPELINE.md section 6: queue size, inflow vs outflow per day, open families ranked by cells affected."""
    with conn.cursor() as cur:
        cur.execute(f"set local statement_timeout = {STATEMENT_TIMEOUT_MS}")
        cur.execute("select count(*) from ops.exception_queue where closed_at is null")
        open_n = cur.fetchone()[0]
        cur.execute(REPORT_FLOW, (days,))
        flow = cur.fetchall()
        cur.execute(REPORT_FAMILY, (top,))
        fam = cur.fetchall()
    conn.rollback()
    tin, tout = sum(f[1] for f in flow), sum(f[2] for f in flow)
    lines = [f"open items: {open_n}", "day | inflow | outflow"]
    lines += [f"{d} | {i} | {o}" for d, i, o in flow]
    verdict = "outflow >= inflow" if tout >= tin else "INFLOW EXCEEDS OUTFLOW"
    lines.append(f"last {days} days: inflow {tin}, outflow {tout} ({verdict})")
    lines.append("open by root_cause_family, ranked by cells affected across companies")
    lines.append("family | kind | owner | items | cells_affected | companies")
    lines += [" | ".join(str(x) for x in r) for r in fam]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ld, rp, cl = (sub.add_parser(n) for n in ("load", "report", "close"))
    for p in (ld, rp, cl):
        p.add_argument("--db-url", default=os.environ.get("DATABASE_URL"))
    g = ld.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    ld.add_argument("--extra-csv", action="append", default=[], type=Path)
    ld.add_argument("--root", type=Path, default=ROOT)
    rp.add_argument("--days", type=int, default=14)
    rp.add_argument("--top", type=int, default=25)
    cl.add_argument("key")
    cl.add_argument("--by", required=True)
    cl.add_argument("--rule-id")
    cl.add_argument("--test-path")
    cl.add_argument("--hide-class")
    cl.add_argument("--evidence")
    a = ap.parse_args(argv)

    if a.cmd == "load":
        rows = build(a.root, a.extra_csv)
        print(format_counts(rows))
        if a.dry_run and not a.db_url:
            print("dry run: files only (no --db-url / DATABASE_URL), nothing written")
            return 0
        if not a.db_url:
            print("--apply needs --db-url or DATABASE_URL", file=sys.stderr)
            return 2
        import psycopg

        with psycopg.connect(a.db_url) as conn:
            print(load(conn, rows, apply=a.apply))
        return 0
    if not a.db_url:
        print("--db-url or DATABASE_URL required", file=sys.stderr)
        return 2
    import psycopg

    with psycopg.connect(a.db_url) as conn:
        if a.cmd == "report":
            print(report(conn, a.days, a.top))
            return 0
        ok = close_item(conn, a.key, a.by, a.rule_id, a.test_path, a.hide_class, a.evidence)
        print("closed" if ok else "no open item with that key")
        return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

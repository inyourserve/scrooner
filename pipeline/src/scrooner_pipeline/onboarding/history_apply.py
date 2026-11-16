"""Apply a REVIEWED history-source CSV to core.company_history_source (migration 0121). Production write when
--apply; the default is a dry run in a transaction that is rolled back.

Input: a CSV committed to the repo, in the format of data-team/47-fsn-store/company_history_sources.csv (the
predecessors detector's proposed_history_sources.csv after review: `klass` filled with A, B or C by the reviewer,
`status` ignored). A row with an empty `klass` is refused: it has not been reviewed.

Idempotent: `on conflict (company_id, source_cik, valid_from) do nothing`; a rerun inserts nothing. The overlap
trigger of 0121 still guards predecessor windows. The whole file goes in one transaction.
Periods for a new predecessor (core.period rows) are NOT written here: see pipeline/scripts/history_periods.py.

Usage: python -m scrooner_pipeline.onboarding.history_apply reviewed.csv [--apply]
"""

from __future__ import annotations

import argparse
import calendar
import csv
import os
import sys
from datetime import date

NEED = {
    "company_id",
    "source_cik",
    "relation",
    "source_name",
    "valid_from",
    "valid_to",
    "reason",
    "evidence",
    "klass",
}


def validate(rows: list[dict]) -> list[str]:
    """Problems with the reviewed rows (empty = valid). Pure."""
    if not rows:
        return ["no rows"]
    if NEED - set(rows[0]):
        return [f"missing columns {sorted(NEED - set(rows[0]))}"]
    problems: list[str] = []
    keys: set[tuple] = set()
    preds: dict[str, list[tuple[date, date, str]]] = {}
    for i, r in enumerate(rows, 2):
        try:
            f, t = (
                date.fromisoformat(r["valid_from"]),
                date.fromisoformat(r["valid_to"]),
            )
        except ValueError:
            problems.append(f"line {i}: bad date")
            continue
        if f > t:
            problems.append(f"line {i}: valid_from after valid_to")
        if t.day != calendar.monthrange(t.year, t.month)[1]:
            problems.append(f"line {i}: valid_to {t} is not a month end")
        if r["relation"] not in ("predecessor", "exclude"):
            problems.append(f"line {i}: relation {r['relation']!r}")
        if not (len(r["source_cik"]) == 10 and r["source_cik"].isdigit()):
            problems.append(f"line {i}: source_cik {r['source_cik']!r}")
        if not r["reason"].strip():
            problems.append(f"line {i}: empty reason")
        if r["klass"] not in ("A", "B", "C"):
            problems.append(
                f"line {i}: not reviewed (klass {r['klass']!r}, need A, B or C)"
            )
        k = (r["company_id"], r["source_cik"], r["valid_from"])
        if k in keys:
            problems.append(f"line {i}: duplicate key {k}")
        keys.add(k)
        if r["relation"] == "predecessor":
            preds.setdefault(r["company_id"], []).append((f, t, r["source_cik"]))
    for cid, ws in preds.items():
        ws.sort()
        for a, b in zip(ws, ws[1:]):
            if b[0] <= a[1]:
                problems.append(
                    f"company {cid}: predecessor windows overlap ({a[2]} vs {b[2]})"
                )
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument(
        "--apply", action="store_true", help="commit (default: dry run, rolled back)"
    )
    a = ap.parse_args(argv)
    with open(a.csv_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    problems = validate(rows)
    if problems:
        print("ABORT:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 2
    import psycopg

    with psycopg.connect(
        os.environ.get("SCROONER_DATABASE_URL") or os.environ["DATABASE_URL"]
    ) as conn:
        conn.execute("set statement_timeout = '2min'")
        conn.execute("set lock_timeout = '5s'")
        known = {
            r[0]
            for r in conn.execute(
                "select id from core.company where id = any(%s)",
                (sorted({int(r["company_id"]) for r in rows}),),
            ).fetchall()
        }
        unknown = sorted({int(r["company_id"]) for r in rows} - known)
        if unknown:
            print(f"ABORT: company ids not in core.company: {unknown}", file=sys.stderr)
            return 2
        inserted = 0
        for r in rows:
            got = conn.execute(
                """insert into core.company_history_source
                   (company_id, source_cik, relation, source_name, valid_from, valid_to, reason, evidence)
                   values (%s, %s, %s, %s, %s, %s, %s, %s)
                   on conflict (company_id, source_cik, valid_from) do nothing returning 1""",
                (
                    int(r["company_id"]),
                    r["source_cik"],
                    r["relation"],
                    r["source_name"],
                    r["valid_from"],
                    r["valid_to"],
                    r["reason"],
                    r["evidence"] or None,
                ),
            ).fetchone()
            inserted += 1 if got else 0
        mode = "apply" if a.apply else "dry run, rolled back"
        if a.apply:
            conn.commit()
        else:
            conn.rollback()
    print(
        f"history_apply [{mode}]: {len(rows)} rows read, {inserted} {'inserted' if a.apply else 'would be inserted'}, "
        f"{len(rows) - inserted} already present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

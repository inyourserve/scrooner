"""Regression guard for CERTIFIED companies and the before-image restore the flow uses to hold them.

certified-guard: the new coverage rows of a company are compared with its certified coverage file, keyed
(data_point, fiscal_year). A certified cell (class PROVEN / REASON / DERIVED) regresses when it is missing from the
new rows, leaves those classes, or its shown_value changes. The regression report carries the cause (class,
reason_code, reason, proof checks).

restore_before_image: puts exactly one company's rows back from a tagmap-plan before-image directory
(canonical_fact, cell_blank_reason, slot_protected_cell csv.gz): in ONE transaction, delete the company's current
rows of the three tables and insert the image rows (original ids), batched through a temp table. Dry run (rolled
back) unless apply. company_value_owner is not part of the image and is left as is. Idempotent.
"""

from __future__ import annotations

import csv
import gzip
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import psycopg

OK_CLASSES = ("PROVEN", "REASON", "DERIVED")
REPORT_COLUMNS = [
    "data_point",
    "fiscal_year",
    "regression",
    "certified_class",
    "certified_value",
    "new_class",
    "new_value",
    "reason_code",
    "reason",
    "proof_verdict",
    "verdict",
    "evidence",
]
BEFORE_TABLES = (
    ("canonical_fact", "canonical_fact.csv.gz"),
    ("cell_blank_reason", "cell_blank_reason.csv.gz"),
    ("slot_protected_cell", "slot_protected_cell.csv.gz"),
)


class _Rollback(Exception):
    pass


def _read(path: Path, company_id: int) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("company_id") and int(r["company_id"]) != company_id:
                continue
            out[(r["data_point"], str(r["fiscal_year"]))] = r
    return out


def _same_value(a: str, b: str) -> bool:
    if a == b:
        return True
    try:
        return Decimal(a) == Decimal(b)
    except (InvalidOperation, ValueError):
        return False


def compare(certified: dict, new: dict) -> list[dict[str, str]]:
    regs: list[dict[str, str]] = []
    for key in sorted(certified):
        c = certified[key]
        if c.get("class") not in OK_CLASSES:
            continue
        n = new.get(key)
        kind = ""
        if n is None:
            kind = "missing"
        elif n.get("class") not in OK_CLASSES:
            kind = "class_left_ok"
        elif not _same_value(c.get("shown_value", ""), n.get("shown_value", "")):
            kind = "value_changed"
        if not kind:
            continue
        n = n or {}
        regs.append(
            {
                "data_point": key[0],
                "fiscal_year": key[1],
                "regression": kind,
                "certified_class": c.get("class", ""),
                "certified_value": c.get("shown_value", ""),
                "new_class": n.get("class", ""),
                "new_value": n.get("shown_value", ""),
                "reason_code": n.get("reason_code", ""),
                "reason": n.get("reason", ""),
                "proof_verdict": n.get("proof_verdict", ""),
                "verdict": n.get("verdict", ""),
                "evidence": n.get("evidence", ""),
            }
        )
    return regs


def guard(
    company_id: int, certified_csv: Path, coverage_csv: Path, report: Path | None
) -> list[dict[str, str]]:
    regs = compare(_read(certified_csv, company_id), _read(coverage_csv, company_id))
    if regs and report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        with report.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=REPORT_COLUMNS)
            w.writeheader()
            w.writerows(regs)
    return regs


def restore_before_image(
    conn: psycopg.Connection, company_id: int, image_dir: Path, *, apply: bool
) -> dict[str, Any]:
    """One transaction: the company's rows of the three tables are replaced by the image's rows of that company."""
    staged: dict[str, tuple[str, str]] = {}
    for table, fname in BEFORE_TABLES:
        path = image_dir / fname
        with gzip.open(path, "rt") as fh:
            header = fh.readline().strip()
        tmp = "_bi_" + table
        conn.execute(f"create temp table if not exists {tmp} (like analytics.{table})")
        conn.execute(f"truncate {tmp}")
        with (
            gzip.open(path, "rb") as fh,
            conn.cursor().copy(
                f"copy {tmp} ({header}) from stdin with csv header"
            ) as cp,
        ):
            while chunk := fh.read(1 << 20):
                cp.write(chunk)
        staged[table] = (tmp, header)
    conn.commit()
    counts: dict[str, int] = {}
    try:
        with conn.transaction():
            conn.execute("set local scrooner.writer = 'company_tag_map'")
            conn.execute("set local scrooner.slot_writer = 'on'")
            for table, _ in BEFORE_TABLES:
                counts[f"{table}.deleted"] = conn.execute(
                    f"delete from analytics.{table} where company_id = %s",
                    (company_id,),
                ).rowcount
            for table, _ in BEFORE_TABLES:
                tmp, header = staged[table]
                overriding = (
                    "" if table == "slot_protected_cell" else " overriding system value"
                )
                counts[f"{table}.restored"] = conn.execute(
                    f"insert into analytics.{table} ({header}){overriding} "
                    f"select {header} from {tmp} where company_id = %s",
                    (company_id,),
                ).rowcount
            if not apply:
                raise _Rollback
    except _Rollback:
        pass
    return {"mode": "apply" if apply else "dry_run", "counts": counts}

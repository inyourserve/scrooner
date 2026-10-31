"""Proof runner: shown cells -> their filing's FSN structure -> verdicts.

Dry run writes a JSONL report (one Proof.row() per cell) and prints verdict
counts; `write=True` upserts into analytics.cell_proof (migration 0114) when
the table exists. The page never reads this table until
proof.serve_proven_only@1 is ON, so writing proofs is evidence, not serving.

FSN quarters are read from `fsn_root` (downloaded from the fsn-notes bucket
on first use, proof/fsn.py). Cells whose filing falls in a quarter the bucket
does not hold (2024q1 onward as of 2026-10-31) come out UNCHECKED with that
reason, never blank.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.proof.fsn import FilingStructure, load_quarter, quarter_of
from scrooner_pipeline.proof.prove import Proof, Shown, prove_cell
from scrooner_pipeline.proof.shown import group_by_accession, load_shown

logger = structlog.get_logger()

_UPSERT = """
insert into analytics.cell_proof
    (company_id, data_point_name, period_grain, period_start, period_end, basis,
     shown_value, shown_tag, shown_accession, shown_source_fact_ids,
     position_value, position_tag, position_accession, position_source,
     fsn_set, fsn_stmt, fsn_line, fsn_label, fsn_calc_parent, position_is_expected_line,
     checks, verdict, reason_code, reason_text, rule_id, detector_version)
values
    (%(company_id)s, %(data_point_name)s, %(period_grain)s, %(period_start)s, %(period_end)s, %(basis)s,
     %(shown_value)s, %(shown_tag)s, %(shown_accession)s, %(shown_source_fact_ids)s,
     %(position_value)s, %(position_tag)s, %(position_accession)s, %(position_source)s,
     %(fsn_set)s, %(fsn_stmt)s, %(fsn_line)s, %(fsn_label)s, %(fsn_calc_parent)s, %(position_is_expected_line)s,
     %(checks)s::jsonb, %(verdict)s, %(reason_code)s, %(reason_text)s, %(rule_id)s, %(detector_version)s)
on conflict (company_id, data_point_name, period_grain, period_start, period_end, basis, rule_id) do update set
    shown_value = excluded.shown_value, shown_tag = excluded.shown_tag, shown_accession = excluded.shown_accession,
    shown_source_fact_ids = excluded.shown_source_fact_ids, position_value = excluded.position_value,
    position_tag = excluded.position_tag, position_accession = excluded.position_accession,
    position_source = excluded.position_source, fsn_set = excluded.fsn_set, fsn_stmt = excluded.fsn_stmt,
    fsn_line = excluded.fsn_line, fsn_label = excluded.fsn_label, fsn_calc_parent = excluded.fsn_calc_parent,
    position_is_expected_line = excluded.position_is_expected_line, checks = excluded.checks,
    verdict = excluded.verdict, reason_code = excluded.reason_code, reason_text = excluded.reason_text,
    detector_version = excluded.detector_version, proved_at = now()
"""


def _json_default(o: Any) -> Any:
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(type(o))


class StructureCache:
    """FSN structures per accession, loading each quarter once for all the
    accessions that fall in it. Quarters missing from the bucket are remembered."""

    def __init__(self, fsn_root: Path):
        self.fsn_root = fsn_root
        self.loaded: dict[str, dict[str, FilingStructure]] = {}
        self.missing_quarters: set[str] = set()

    def get_many(self, by_quarter: dict[str, set[str]]) -> dict[str, FilingStructure]:
        out: dict[str, FilingStructure] = {}
        for q, accs in sorted(by_quarter.items()):
            if q in self.missing_quarters:
                continue
            have = self.loaded.setdefault(q, {})
            need = {a for a in accs if a not in have}
            if need:
                try:
                    have.update(load_quarter(self.fsn_root, q, need))
                except FileNotFoundError:
                    self.missing_quarters.add(q)
                    logger.warning("cell_proof.fsn_quarter_missing", quarter=q)
                    continue
            out.update({a: have[a] for a in accs if a in have})
        return out


def _filing_dates(conn: psycopg.Connection, accessions: list[str]) -> dict[str, date]:
    if not accessions:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            "select accession_number, filing_date from core.filing where accession_number = any(%s)",
            (accessions,),
        )
        return {a: d for a, d in cur.fetchall() if d}


def prove_company(
    conn: psycopg.Connection, company_id: int, cache: StructureCache
) -> list[Proof]:
    shown = load_shown(conn, company_id)
    groups = group_by_accession(shown)
    accs = [a for a in groups if a]
    fdates = _filing_dates(conn, accs)
    by_quarter: dict[str, set[str]] = defaultdict(set)
    for a in accs:
        if a in fdates:
            by_quarter[quarter_of(fdates[a])].add(a)
    structures = cache.get_many(by_quarter)
    proofs: list[Proof] = []
    for acc, cells in groups.items():
        structure = structures.get(acc) if acc else None
        q = quarter_of(fdates[acc]) if acc in fdates else None
        for s in cells:
            p = prove_cell(s, structure, q)
            if structure is None and acc and q in cache.missing_quarters:
                p.reason_text = f"FSN quarter {q} is not in the fsn-notes bucket yet"
            proofs.append(p)
    return proofs


def write_proofs(conn: psycopg.Connection, proofs: list[Proof]) -> int:
    rows = []
    for p in proofs:
        r = p.row()
        r["checks"] = json.dumps(r["checks"], default=_json_default)
        rows.append(r)
    with conn.cursor() as cur:
        cur.executemany(_UPSERT, rows)
    conn.commit()
    return len(rows)


def table_exists(conn: psycopg.Connection) -> bool:
    with conn.cursor() as cur:
        cur.execute("select to_regclass('analytics.cell_proof')")
        return cur.fetchone()[0] is not None


def run(
    conn: psycopg.Connection,
    ciks: set[str],
    *,
    fsn_root: Path,
    report_path: Path | None = None,
    write: bool = False,
) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        ids = dict(cur.fetchall())
    if write and not table_exists(conn):
        raise RuntimeError(
            "analytics.cell_proof does not exist (migration 0114 not applied); use the report instead"
        )
    cache = StructureCache(fsn_root)
    totals: dict[str, Any] = {"companies": 0, "cells": 0, "errored": 0}
    verdicts: Counter = Counter()
    reasons: Counter = Counter()
    per_company: dict[str, dict[str, int]] = {}
    report = report_path.open("a") if report_path else None
    try:
        for cik in sorted(ciks):
            company_id = ids.get(cik)
            if company_id is None:
                continue
            totals["companies"] += 1
            try:
                proofs = prove_company(conn, company_id, cache)
                if write and proofs:
                    write_proofs(conn, proofs)
            except Exception as exc:  # noqa: BLE001
                totals["errored"] += 1
                logger.error(
                    "cell_proof.company_failed", cik=cik, error=repr(exc)[:200]
                )
                conn.rollback()
                continue
            c = Counter(p.verdict for p in proofs)
            per_company[cik] = dict(c)
            verdicts.update(c)
            reasons.update(p.reason_code for p in proofs if p.reason_code)
            totals["cells"] += len(proofs)
            if report is not None:
                for p in proofs:
                    report.write(
                        json.dumps({"cik": cik, **p.row()}, default=_json_default)
                        + "\n"
                    )
    finally:
        if report is not None:
            report.close()
    totals["verdicts"] = dict(verdicts)
    totals["reasons"] = dict(reasons.most_common())
    totals["fsn_quarters_missing"] = sorted(cache.missing_quarters)
    totals["per_company"] = per_company
    logger.info(
        "cell_proof.done", **{k: v for k, v in totals.items() if k != "per_company"}
    )
    return totals

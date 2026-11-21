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
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.proof.fsn import (
    DecompressError,
    FilingStructure,
    load_quarter,
    quarter_of,
    require_zstd,
)
from scrooner_pipeline.proof.fsn_db import load_filings
from scrooner_pipeline.proof.identities import (
    apply_identities,
    load_filing_checks,
    load_printed,
)
from scrooner_pipeline.proof.perimeter import apply_perimeter
from scrooner_pipeline.proof.prove import DETECTOR_VERSION, RULE_ID, Proof, prove_cell
from scrooner_pipeline.proof.rules import (
    RULES_KEY,
    reproof_rules,
    rules_used,
    stale_rules,
    stored_rules,
)
from scrooner_pipeline.proof.shown import (
    HISTORY_FLOOR,
    group_by_accession,
    load_shown,
)

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

    def __init__(
        self,
        fsn_root: Path,
        conn: psycopg.Connection | None = None,
        source: str = "files",
    ):
        """source 'db' (needs conn) reads each company's filings from schema fsn (proof/fsn_db.py); a filing the
        store does not hold falls back to the quarter files and is logged and counted in `fallbacks`."""
        if source not in ("db", "files"):
            raise ValueError(f"fsn source must be db or files, not {source!r}")
        if source == "db" and conn is None:
            raise ValueError("the db fsn source needs a connection")
        self.conn = conn
        self.source = source
        self.company: str = ""  # the cik being proved, for the fallback log
        self.fallbacks: list[tuple[str, str, str]] = []  # (cik, accession, quarter)
        self.fsn_root = fsn_root
        self.loaded: dict[str, dict[str, FilingStructure]] = {}
        self.missing_quarters: set[str] = set()
        self.dims_loaded: set[tuple[str, str]] = (
            set()
        )  # (quarter, adsh) loaded with dimensional rows

    def get_many(
        self, by_quarter: dict[str, set[str]], dims: bool = False
    ) -> dict[str, FilingStructure]:
        """dims=True also loads the dimensional num rows (dim.tsv.zst) for member claims; a quarter whose dim file
        is not in the bucket keeps its plain structure, so member parts stay UNCHECKED and plain cells are untouched."""
        out: dict[str, FilingStructure] = {}
        for q, accs in sorted(by_quarter.items()):
            if q in self.missing_quarters:
                continue
            have = self.loaded.setdefault(q, {})
            need = {a for a in accs if a not in have}
            if dims:
                need |= {
                    a for a in accs if a in have and (q, a) not in self.dims_loaded
                }
            if need and self.source == "db":
                assert self.conn is not None
                got_db = load_filings(self.conn, need, with_dims=dims)
                have.update(got_db)
                if dims:
                    self.dims_loaded.update((q, a) for a in got_db)
                need = need - set(got_db)
                for a in sorted(need):
                    self.fallbacks.append((self.company, a, q))
                    logger.warning(
                        "cell_proof.fsn_db_fallback_to_files",
                        cik=self.company,
                        accession=a,
                        quarter=q,
                    )
            if need:
                try:
                    got = None
                    if dims:
                        try:
                            got = load_quarter(self.fsn_root, q, need, with_dims=True)
                            self.dims_loaded.update((q, a) for a in need)
                        except FileNotFoundError:
                            got = None  # no dim file: plain structure below, member parts UNCHECKED
                    if got is None:
                        got = load_quarter(self.fsn_root, q, need)
                    have.update(got)
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


def _own_filing_loader(
    conn: psycopg.Connection,
    cache: StructureCache,
    structures: dict[str, FilingStructure],
    dims: bool,
):
    """accession -> its FilingStructure from the same store (FilingStructure.load_filing): a component sum handed
    another filing's structure reads its parts from the shown value's own filing. None when the store lacks it."""

    def load(adsh: str) -> FilingStructure | None:
        if adsh in structures:
            return structures[adsh]
        filed = _filing_dates(conn, [adsh]).get(adsh)
        if filed is None:
            return None
        got = cache.get_many({quarter_of(filed): {adsh}}, dims=dims).get(adsh)
        if got is not None:
            got.load_filing = load
            structures[adsh] = got
        return got

    return load


def prove_company(
    conn: psycopg.Connection,
    company_id: int,
    cache: StructureCache,
    floor: date | None = None,
) -> list[Proof]:
    shown = (
        load_shown(conn, company_id, floor=floor)
        if floor
        else load_shown(conn, company_id)
    )
    groups = group_by_accession(shown)
    accs = [a for a in groups if a]
    fdates = _filing_dates(conn, accs)
    by_quarter: dict[str, set[str]] = defaultdict(set)
    for a in accs:
        if a in fdates:
            by_quarter[quarter_of(fdates[a])].add(a)
    # derived quarters need the PRIOR quarter's filing too (its year-to-date line), and so does every quarter cell:
    # a quarter column the face does not print is proven by subtraction from the printed year-to-date inputs
    prior_for: dict[tuple[str, date], str] = {}
    if any(s.period_grain == "Q" for s in shown):
        with conn.cursor() as cur:
            cur.execute(
                "select accession_number, period_of_report, filing_date from core.filing "
                "where company_id = %s and form in ('10-K', '10-Q', '10-K/A', '10-Q/A') and period_of_report is not null",
                (company_id,),
            )
            periodic = cur.fetchall()
        for s in shown:
            if s.period_grain != "Q":
                continue
            prior_end = s.period_start - timedelta(days=1)
            best = None
            for acc, por, fdate in periodic:
                if acc == s.accession or abs((por - prior_end).days) > 10:
                    continue
                if (
                    best is None
                    or (abs((por - prior_end).days), -fdate.toordinal()) < best[0]
                ):
                    best = (
                        (abs((por - prior_end).days), -fdate.toordinal()),
                        acc,
                        fdate,
                    )
            if best is not None:
                prior_for[(s.accession, s.period_start)] = best[1]
                fdates[best[1]] = best[2]
                by_quarter[quarter_of(best[2])].add(best[1])
    wants_dims = any(
        s.claim is not None and any("[" in t for _sg, t in s.claim.parts) for s in shown
    )
    structures = cache.get_many(by_quarter, dims=wants_dims)
    load = _own_filing_loader(conn, cache, structures, wants_dims)
    for st in structures.values():
        st.load_filing = load
    proofs: list[Proof] = []
    for acc, cells in groups.items():
        structure = structures.get(acc) if acc else None
        q = quarter_of(fdates[acc]) if acc in fdates else None
        for s in cells:
            prior = (
                structures.get(prior_for.get((acc, s.period_start), ""))
                if s.period_grain == "Q"
                else None
            )
            p = prove_cell(s, structure, q, prior)
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
    with conn.transaction(), conn.cursor() as cur:
        cur.executemany(_UPSERT, rows)
    return len(rows)


def scope_proofs(
    conn: psycopg.Connection,
    company_id: int,
    proofs: list[Proof],
    floor: date | None = None,
) -> tuple[list[Proof], list[tuple[int, dict[str, int]]], int, Counter]:
    """Rule-scoped re-prove (ONE-PATH step 1). Split a company's fresh proofs against its stored rows:
    to_write  cells with no stored row, a row of another floor version, or a row whose rules moved (reproof_rules);
    to_stamp  (row id, rule record) of unselected LEGACY rows (no record yet): their verdict stands, the record is added;
    kept      unselected rows that already carry a current record (untouched);
    why       count of the rules that selected cells.
    The proofs are all computed (identities need the whole period); only the writes are scoped, so a selected cell's
    verdict is exactly what a full re-prove writes."""
    stored: dict[tuple, tuple[int, str, dict]] = {}
    for rid, name, grain, start, end, dv, checks in conn.execute(
        """select id, data_point_name, period_grain, period_start, period_end, detector_version, checks
           from analytics.cell_proof
           where company_id = %s and basis = 'latest' and rule_id = %s and period_end >= %s""",
        (company_id, RULE_ID, floor or HISTORY_FLOOR),
    ).fetchall():
        stored[(name, grain, start, end)] = (rid, dv, checks or {})
    to_write: list[Proof] = []
    to_stamp: list[tuple[int, dict[str, int]]] = []
    kept = 0
    why: Counter = Counter()
    for p in proofs:
        s = p.shown
        row = stored.get(
            (s.data_point_name, s.period_grain, s.period_start, s.period_end)
        )
        if row is None or row[1] != DETECTOR_VERSION:
            to_write.append(p)
            why["no_current_floor_row"] += 1
            continue
        rid, _dv, checks = row
        rec = stored_rules(checks)
        reasons = reproof_rules(rec, s, checks)
        if reasons:
            to_write.append(p)
            why.update(reasons)
        elif rec is None:
            to_stamp.append((rid, rules_used(s, checks)))
        else:
            kept += 1
    return to_write, to_stamp, kept, why


def stamp_rules(
    conn: psycopg.Connection, stamps: list[tuple[int, dict[str, int]]]
) -> int:
    """Add the rule record to legacy rows whose rules are unchanged. Touches only checks->'rules'; verdict, value and
    proved_at stay as they were."""
    rows = [{"id": i, "rec": json.dumps(r)} for i, r in stamps]
    with conn.transaction(), conn.cursor() as cur:
        for k in range(0, len(rows), 5000):
            cur.executemany(
                "update analytics.cell_proof set checks = jsonb_set(coalesce(checks, '{}'::jsonb), "
                f"'{{{RULES_KEY}}}', %(rec)s::jsonb) where id = %(id)s and not (checks ? '{RULES_KEY}')",
                rows[k : k + 5000],
            )
    return len(rows)


def purge_unserved(
    conn: psycopg.Connection,
    company_id: int,
    proofs: list[Proof],
    floor: date | None = None,
) -> int:
    """A PROVEN or UNCHECKED verdict belongs to a served value. After a company's proofs are written, the rows of
    that company in the proof's window whose cell is no longer served (the mapper held or removed it since: NFLX
    total_debt 2015 stayed PROVEN after the era guard unserved it) are deleted. DISAGREE rows stay (the mapper's
    proof guard reads them to keep a wrong value held) and NOT_PRESENTED rows stay (a stored reason for a blank).
    Returns the number of rows deleted."""
    served = {
        (
            p.shown.data_point_name,
            p.shown.period_grain,
            p.shown.period_start,
            p.shown.period_end,
        )
        for p in proofs
    }
    with conn.cursor() as cur:
        cur.execute(
            """select id, data_point_name, period_grain, period_start, period_end
               from analytics.cell_proof
               where company_id = %s and basis = 'latest' and rule_id = %s
                 and verdict in ('PROVEN', 'UNCHECKED') and period_end >= %s""",
            (company_id, RULE_ID, floor or HISTORY_FLOOR),
        )
        stale = [r[0] for r in cur.fetchall() if tuple(r[1:]) not in served]
        for i in range(0, len(stale), 5000):
            cur.execute(
                "delete from analytics.cell_proof where id = any(%s)",
                (stale[i : i + 5000],),
            )
    return len(stale)


def stale_companies(
    conn: psycopg.Connection, company_ids: list[int], floor: date | None = None
) -> dict[int, Counter]:
    """Read-only: the companies holding a floor-version proof row whose recorded rules moved version (or that has no
    record yet), with the count per moved rule. After a rule bump these are exactly the companies a rule-scoped
    `run --write` must touch; every other company's verdicts are current. Reads only checks->'rules' (small)."""
    out: dict[int, Counter] = {}
    for i in range(0, len(company_ids), 50):
        for cid, rec in conn.execute(
            f"""select company_id, checks->'{RULES_KEY}'
               from analytics.cell_proof
               where company_id = any(%s) and basis = 'latest' and rule_id = %s and detector_version = %s
                 and period_end >= %s""",
            (
                company_ids[i : i + 50],
                RULE_ID,
                DETECTOR_VERSION,
                floor or HISTORY_FLOOR,
            ),
        ).fetchall():
            why = stale_rules({RULES_KEY: rec} if isinstance(rec, dict) else {})
            if why:
                out.setdefault(cid, Counter()).update(why)
    return out


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
    floor: date | None = None,
    fsn_source: str = "db",
    scoped: bool = False,
    only_stale: bool = False,
) -> dict[str, Any]:
    # reads run in autocommit: one transaction across companies and FSN downloads held
    # AccessShareLocks on canonical_fact for 19 min and blocked a migration ALTER (2026-11-01)
    require_zstd()  # fail before any work; a missing tool must not degrade to UNCHECKED
    conn.commit()
    conn.autocommit = True
    conn.execute("set idle_in_transaction_session_timeout = '2min'")
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        ids = dict(cur.fetchall())
    if write and not table_exists(conn):
        raise RuntimeError(
            "analytics.cell_proof does not exist (migration 0114 not applied); use the report instead"
        )
    cache = StructureCache(fsn_root, conn, fsn_source)
    totals: dict[str, Any] = {"companies": 0, "cells": 0, "errored": 0}
    # --only-stale: prove only the companies holding a proof row at an older rule version (a rule bump); a company
    # whose rows are all current is skipped without loading a filing
    stale = stale_companies(conn, sorted(ids.values()), floor) if only_stale else None
    if stale is not None:
        totals["stale_rules"] = dict(sum(stale.values(), Counter()).most_common())
        totals["skipped_current"] = 0
    verdicts: Counter = Counter()
    identity_breaks: Counter = Counter()
    reasons: Counter = Counter()
    per_company: dict[str, dict[str, int]] = {}
    scope_why: Counter = Counter()
    report = report_path.open("a") if report_path else None
    try:
        for cik in sorted(ciks):
            company_id = ids.get(cik)
            if company_id is None:
                continue
            if stale is not None and company_id not in stale:
                totals["skipped_current"] += 1
                continue
            totals["companies"] += 1
            cache.company = cik
            try:
                proofs = prove_company(conn, company_id, cache, floor)
                structures = {
                    a: st
                    for by_acc in cache.loaded.values()
                    for a, st in by_acc.items()
                }
                # identities over the served values, after the per-cell proof and before the upsert
                id_counts = apply_identities(
                    proofs,
                    load_printed(conn, company_id, floor or HISTORY_FLOOR),
                    structures,
                    load_filing_checks(conn, company_id),
                )
                identity_breaks.update(id_counts)
                apply_perimeter(proofs, structures)  # total_debt perimeter (audit R07)
                if write and proofs:
                    if scoped:
                        to_write, to_stamp, kept, why = scope_proofs(
                            conn, company_id, proofs, floor
                        )
                        write_proofs(conn, to_write)
                        stamp_rules(conn, to_stamp)
                        for k, v in (
                            ("rewritten", len(to_write)),
                            ("stamped", len(to_stamp)),
                            ("kept", kept),
                        ):
                            totals[k] = totals.get(k, 0) + v
                        scope_why.update(why)
                    else:
                        write_proofs(conn, proofs)
                if write:
                    totals["purged_unserved"] = totals.get(
                        "purged_unserved", 0
                    ) + purge_unserved(conn, company_id, proofs, floor)
            except DecompressError:
                raise  # abort the whole run; never mark cells UNCHECKED for a broken tool
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
    totals["identity_breaks"] = dict(identity_breaks)
    totals["reasons"] = dict(reasons.most_common())
    if scoped:
        totals["scope_reasons"] = dict(scope_why.most_common())
    totals["fsn_source"] = fsn_source
    totals["fsn_db_fallbacks"] = len(cache.fallbacks)
    totals["fsn_quarters_missing"] = sorted(cache.missing_quarters)
    totals["per_company"] = per_company
    logger.info(
        "cell_proof.done", **{k: v for k, v in totals.items() if k != "per_company"}
    )
    return totals

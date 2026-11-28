"""Derived-not-printed cells (Dhairya's identity rulings C1/C2, 2026-11-13).

Two lines are not printed by some filers and are served as DERIVED, labelled `derived_not_printed`
(canonical_fact.family 'company_tag_map:derived_not_printed', no source fact: the proof reports the cell UNCHECKED
and the identities skip it, proof/identities.not_printed):

  C1 gross_profit       = revenue - cost_of_revenue, when the company map says gross profit is NOT PRESENTED for the
                          period and both revenue and cost of revenue are served and PROVEN (analytics.cell_proof,
                          current detector, the verdict judged the very value served).
  C2 total_liabilities  = LiabilitiesAndStockholdersEquity - equity including NCI - every printed temporary-equity
                          operand, when the map says total liabilities is NOT PRESENTED, the printed L&SE equals the
                          PROVEN total_assets, the PROVEN stockholders_equity (plus the printed NCI when the served
                          equity excludes it) is present, and no operand is missing.

ONE-FILING RULE (approved 2026-11-17): every input of a derived cell comes from the SAME filing (cell `_accession`;
operands from core.fact of that accession). Inputs whose winners sit in different filings (MPC FY2018: revenue from
the FY2019 10-K, cost of revenue from the FY2020 10-K) never combine: the cell is not derived.
C1 host filing (Stage 3 Resolve, 2026-11-29): the served revenue and cost of revenue may be the authoritative copies
of two filings while ONE filing still prints both numbers (STX FY2016: revenue 11,160 served from the FY2018 10-K,
cost of revenue 8,545 from the FY2016 10-K; the FY2018 10-K R4 prints both, and no gross profit line). The structural
resolver's gross_profit derived_not_printed row names that filing and its two printed nodes; when the stored facts of
that filing (core.fact / fsn.value) carry exactly the node values and they equal the PROVEN served values, the inputs
are from one filing and the cell is derived (load_gp_hosts). Any other mismatch still leaves the cell underived.

Never derived: a period without every operand served/printed and proven, a cell the mapper already serves or holds,
a concept the template leaves out (not_in_template). Instants are never summed by the mapper (D3); C2 is the single
ruled exception: one subtraction of printed lines, labelled.

The hook is `add_derived_cells(...)`, called by company_tag_map.resolve_for_company after build_cells.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any

import psycopg

from scrooner_pipeline.mapper.dqc_checks import tolerance
from scrooner_pipeline.proof.identities import (
    EQUITY_INCL_NCI_TAG,
    LSE_TAGS,
    NCI_EQUITY_TAGS,
    TEMP_EQUITY_PART_TAGS,
    TEMP_EQUITY_TAGS,
    TEMP_EQUITY_TOTAL_TAG,
)
from scrooner_pipeline.proof.prove import DETECTOR_VERSION
from scrooner_pipeline.proof.rules import row_is_current

LABEL = "derived_not_printed"
ASSETS_TAG = "Assets"
EQUITY_TAG = "StockholdersEquity"
OPERAND_TAGS: tuple[str, ...] = (
    ASSETS_TAG,
    EQUITY_TAG,
    *LSE_TAGS,
    EQUITY_INCL_NCI_TAG,
    *NCI_EQUITY_TAGS,
    *TEMP_EQUITY_TAGS,
)

ProvenKey = tuple[str, str, date, date]  # (base data point, grain, start, end)


def _base(name: str) -> str:
    for suffix in ("_sanity_resolved", "_resolved"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _grain(start: date, end: date, ptype: str) -> str | None:
    if ptype == "instant":
        return "I"
    days = (end - start).days
    if 350 <= days <= 380:
        return "FY"
    if 80 <= days <= 100:
        return "Q"
    return None


def load_proven(
    conn: psycopg.Connection, company_id: int
) -> dict[ProvenKey, set[Decimal]]:
    """(base data point, grain, start, end) -> values the cell's latest verdict (current detector) judged PROVEN."""
    if conn.execute("select to_regclass('analytics.cell_proof')").fetchone()[0] is None:
        return {}
    out: dict[ProvenKey, set[Decimal]] = defaultdict(set)
    for n, g, s, e, v, checks in conn.execute(
        """
        select data_point_name, period_grain, period_start, period_end, shown_value, checks
        from analytics.cell_proof
        where company_id = %s and basis = 'latest' and verdict = 'PROVEN' and shown_value is not null
          and detector_version = %s
        """,
        (company_id, DETECTOR_VERSION),
    ).fetchall():
        if not row_is_current(DETECTOR_VERSION, checks, DETECTOR_VERSION):
            continue
        out[(_base(n), g, s, e)].add(Decimal(v))
    return out


def load_operand_filings(
    conn: psycopg.Connection, company_id: int
) -> dict[tuple[str, int], dict[str, Decimal]]:
    """(tag, period_id) -> {accession: printed value} of the C2 operand tags (operand_filings_from_rows)."""
    rows = conn.execute(
        """
        select c.tag, f.period_id, fl.accession_number, f.value, f.is_authoritative
        from core.fact f join core.concept c on c.id = f.concept_id
        join core.filing fl on fl.id = f.filing_id
        where f.company_id = %s and not f.is_derived
          and c.taxonomy = 'us-gaap' and c.tag = any(%s)
        """,
        (company_id, list(OPERAND_TAGS)),
    ).fetchall()
    return operand_filings_from_rows(rows)


def operand_filings_from_rows(
    rows: list[tuple[str, int, str, Decimal, bool]],
) -> dict[tuple[str, int], dict[str, Decimal]]:
    """(tag, period_id) -> {accession: printed value}, so the operands can be read from the one filing that prints the
    proven assets and equity. Rows: (tag, period_id, accession, value, is_authoritative). Pure.

    Every value is the AUTHORITATIVE value of its (tag, period): an authoritative fact counts in its own filing, and a
    non-authoritative fact counts in its filing only when it carries exactly that authoritative value (the same printed
    number, filed again in a later 10-K). No non-authoritative value ever enters a derivation; it only shows which other
    filing prints the authoritative number. GILD FY2015 (2026-11-22): the authoritative Assets and L&SE are the FY2016
    10-K's (51,716M), the authoritative StockholdersEquity, MinorityInterest and temporary equity the FY2015 10-K's
    (18,534M / 579M / 2M, the same numbers the FY2016 10-K prints). Reading authoritative rows only left no filing that
    prints both, so the cell, certified at 32,601M on 2026-11-16, fell BLANK. A key with two distinct values in one
    accession is dropped."""
    seen: dict[tuple[str, int, str], set[Decimal]] = defaultdict(set)
    auth: dict[tuple[str, int], set[Decimal]] = defaultdict(set)
    for tag, period_id, acc, value, is_auth in rows:
        if is_auth:
            auth[(tag, period_id)].add(Decimal(value))
    for tag, period_id, acc, value, is_auth in rows:
        val = Decimal(value)
        a = auth.get((tag, period_id))
        if is_auth or (a is not None and len(a) == 1 and val in a):
            seen[(tag, period_id, acc)].add(val)
    out: dict[tuple[str, int], dict[str, Decimal]] = defaultdict(dict)
    for (tag, period_id, acc), v in seen.items():
        if len(v) == 1:
            out[(tag, period_id)][acc] = next(iter(v))
    return dict(out)


def derive(
    cells: list[dict],
    stats: dict[str, Any],
    concept_info: dict[int, tuple[str, str]],
    periods: dict[int, tuple[date, date, str]],
    proven: dict[ProvenKey, set[Decimal]],
    operands: dict[tuple[str, int], Decimal],
    operand_filings: dict[tuple[str, int], dict[str, Decimal]] | None = None,
    gp_hosts: dict[int, GpHost] | None = None,
) -> list[dict]:
    """The derived cells (pure); `cells` and `stats` are not touched (add_derived_cells applies them). gp_hosts:
    period_id -> the one filing that prints revenue and cost of revenue (load_gp_hosts)."""
    by_base: dict[tuple[str, int], dict] = {}
    for c in cells:
        by_base[(_base(concept_info[c["canonical_concept_id"]][0]), c["period_id"])] = c
    held = {(h["canonical_concept_id"], h["period_id"]) for h in stats["held"]}
    served = {(c["canonical_concept_id"], c["period_id"]) for c in cells}

    def is_proven(base: str, cell: dict) -> bool:
        start, end, ptype = periods[cell["period_id"]]
        g = _grain(start, end, ptype)
        return g is not None and cell["value"] in proven.get((base, g, start, end), ())

    out: list[dict] = []
    derived: set[tuple[int, int]] = set()
    for b in stats["blanks"]:
        if b.get("state") != "not_presented" or b["period_id"] not in periods:
            continue
        key = (b["canonical_concept_id"], b["period_id"])
        # two not_presented blanks of one key (overlapping era rows: ADI total_liabilities 2018-11-03) derive ONE
        # cell; a second copy made the plan's canonical_fact insert fail (UniqueViolation) and rolled the whole
        # company back (ADI, DE, DIS unserved since 2026-11-16)
        if key in served or key in held or key in derived:
            continue
        base = _base(b["concept_name"])
        pid = b["period_id"]
        value: Decimal | None = None
        note = ""
        if base == "gross_profit" and b["grain"] in ("FY", "Q"):
            rev = by_base.get(("revenue", pid))
            cor = by_base.get(("cost_of_revenue", pid))
            host = (gp_hosts or {}).get(pid)
            one_filing = (
                rev is not None
                and cor is not None
                and (
                    (
                        rev.get("_accession") is not None
                        and rev.get("_accession") == cor.get("_accession")
                    )
                    or (
                        host is not None
                        and host.revenue == rev["value"]
                        and host.cost_of_revenue == cor["value"]
                    )
                )
            )
            if (
                one_filing
                and rev is not None
                and cor is not None
                and is_proven("revenue", rev)
                and is_proven("cost_of_revenue", cor)
            ):
                value = rev["value"] - cor["value"]
                note = f"{LABEL}: revenue {rev['value']} - cost_of_revenue {cor['value']} (both PROVEN); the filing prints no gross profit line"
                if rev.get("_accession") != cor.get("_accession") and host is not None:
                    note += f"; both printed in {host.accession} ({host.locator})"
        elif base == "total_liabilities" and b["grain"] == "I":
            value, note = _total_liabilities(
                pid, by_base, operand_filings or {}, is_proven
            )
        if value is None:
            continue
        derived.add(key)
        out.append(
            {
                "canonical_concept_id": b["canonical_concept_id"],
                "period_id": pid,
                "value": value,
                "value_source": LABEL,
                "source_fact_ids": [],
                "source_value_ids": [],
                "serve_note": note,
                "_scaled": False,
                "_derived_not_printed": True,
            }
        )
    return out


@dataclass(frozen=True)
class GpHost:
    """The one filing that prints a year's revenue and cost of revenue (the resolver's C1 row, re-read from storage)."""

    accession: str
    revenue: Decimal
    cost_of_revenue: Decimal
    locator: str


@dataclass(frozen=True)
class GpClaim:
    accession: str
    period_end: date
    plus: tuple[str, Decimal]
    minus: tuple[str, Decimal]
    locator: str


def gp_claim(row: dict[str, str]) -> GpClaim | None:
    """A structural resolver row (resolver/<TICKER>.csv) that derives gross_profit by ruling C1: decision
    derived_not_printed, grain FY, exactly two undimensioned nodes `Tag=value [R<page>...]; -Tag=value [R<page>...]`,
    each printed in the row's own accession. Anything else is None. Pure."""
    from scrooner_pipeline.mapper import structural_loader as sl

    if (
        row.get("data_point") != "gross_profit"
        or row.get("decision") != "derived_not_printed"
        or row.get("grain") != "FY"
    ):
        return None
    acc = (row.get("accession") or "").strip()
    try:
        pe = date.fromisoformat(row.get("period_end") or "")
    except ValueError:
        return None
    left = (row.get("nodes") or "").partition("| why:")[0]
    nodes = [n.strip() for n in sl.split_nodes(left) if n.strip()]
    if not acc or len(nodes) != 2:
        return None
    got: list[tuple[bool, str, Decimal, str]] = []
    for n in nodes:
        m = sl.NODE_RE.match(n)
        if m is None or m.group("mem") or m.group("tax") or not m.group("val"):
            return None
        loc = (m.group("loc") or "").strip()
        page, _, on = loc.partition("@")
        if not page.startswith("R") or (on and on.strip() != acc):
            return None
        got.append(
            (m.group("neg") == "-", m.group("tag"), Decimal(m.group("val")), page)
        )
    (neg0, t0, v0, l0), (neg1, t1, v1, l1) = got
    if neg0 or not neg1:
        return None
    return GpClaim(acc, pe, (t0, v0), (t1, v1), f"{t0} {l0}; {t1} {l1}")


@lru_cache(maxsize=2)
def _gp_claims(path: str) -> dict[str, tuple[GpClaim, ...]]:
    p = Path(path)
    files = sorted(p.glob("*.csv")) if p.is_dir() else [p]
    out: dict[str, list[GpClaim]] = defaultdict(list)
    for f in files:
        with f.open(newline="") as fh:
            for row in csv.DictReader(fh):
                c = gp_claim(row)
                if c is not None:
                    out[(row.get("cik") or "").zfill(10)].append(c)
    return {k: tuple(v) for k, v in out.items()}


def gp_hosts_from(
    claims: tuple[GpClaim, ...],
    periods: dict[int, tuple[date, date, str]],
    stored_value: Any,
) -> dict[int, GpHost]:
    """period_id -> GpHost for each C1 claim whose FY period is one of `periods` and whose two parts the claim's own
    filing stores with exactly the node values (`stored_value(accession, tag, end, want)` -> Decimal or None). Pure
    given stored_value."""
    from scrooner_pipeline.common.fsn_dates import fsn_end_matches

    out: dict[int, GpHost] = {}
    for c in claims:
        pids = [
            pid
            for pid, (s, e, pt) in periods.items()
            if pt == "duration"
            and _grain(s, e, pt) == "FY"
            and fsn_end_matches(e, c.period_end)
        ]
        if len(pids) != 1:
            continue
        end = periods[pids[0]][1]
        if any(
            stored_value(c.accession, tag, end, want) != want
            for tag, want in (c.plus, c.minus)
        ):
            continue
        out[pids[0]] = GpHost(c.accession, c.plus[1], c.minus[1], c.locator)
    return out


def load_gp_hosts(
    conn: psycopg.Connection,
    company_id: int,
    periods: dict[int, tuple[date, date, str]],
) -> dict[int, GpHost]:
    """The C1 host filings of one company: the resolver's gross_profit derived rows, re-read from the stored facts of
    each row's one filing (structural_direct._stored_values / _part_value, the direct path's own reader)."""
    from scrooner_pipeline.mapper import structural_direct as sd

    path = sd.resolver_path()
    if path is None:
        return {}
    row = conn.execute(
        "select cik from core.company where id = %s", (company_id,)
    ).fetchone()
    if row is None:
        return {}
    claims = _gp_claims(str(path)).get(str(row[0]).zfill(10), ())
    if not claims:
        return {}
    ends = {e for _s, e, _p in periods.values()} | {c.period_end for c in claims}
    stored = sd._stored_values(
        conn,
        company_id,
        {c.accession for c in claims},
        {t for c in claims for t, _v in (c.plus, c.minus)},
        ends,
    )

    def stored_value(acc: str, tag: str, end: date, want: Decimal) -> Decimal | None:
        got = sd._part_value(stored[(acc, tag, end)], want)
        return None if isinstance(got, str) else got[0]

    return gp_hosts_from(claims, periods, stored_value)


def _total_liabilities(
    pid, by_base, operand_filings, is_proven
) -> tuple[Decimal | None, str]:
    ta = by_base.get(("total_assets", pid))
    se = by_base.get(("stockholders_equity", pid))
    if ta is None or se is None:
        return None, ""

    # one-filing rule: assets, equity and every operand from the same filing. The cells' recorded accessions are
    # the filing each value was served from; when they differ (GILD FY2015: assets from the FY2016 10-K, equity from
    # the FY2015 10-K, the same 18,534M) the inputs still come from one filing if ONE accession prints the assets, the
    # equity and the L&SE with the proven values. The cell's own accession is tried first, then the other's.
    def prints(acc: str) -> bool:
        def at(tag: str) -> Decimal | None:
            return operand_filings.get((tag, pid), {}).get(acc)

        a, e = at(ASSETS_TAG), at(EQUITY_TAG)
        if ta.get("_accession") != acc and (
            a is None or abs(a - ta["value"]) > tolerance([a, ta["value"]])
        ):
            return False
        if se.get("_accession") != acc and (
            e is None or abs(e - se["value"]) > tolerance([e, se["value"]])
        ):
            return False
        return any(at(t) is not None for t in LSE_TAGS)

    acc = next(
        (
            a
            for a in dict.fromkeys((ta.get("_accession"), se.get("_accession")))
            if a is not None and prints(a)
        ),
        None,
    )
    if acc is None:
        return None, ""
    operands = {
        (t, p): by_acc[acc]
        for (t, p), by_acc in operand_filings.items()
        if p == pid and acc in by_acc
    }
    lse = next((operands[(t, pid)] for t in LSE_TAGS if (t, pid) in operands), None)
    if ta is None or se is None or lse is None:
        return None, ""
    if not (is_proven("total_assets", ta) and is_proven("stockholders_equity", se)):
        return None, ""
    if abs(lse - ta["value"]) > tolerance([lse, ta["value"]]):
        return (
            None,
            "",
        )  # the printed total does not equal the proven assets: nothing to trust
    equity = se["value"]
    parts = [f"L&SE {lse}", f"equity {equity}"]
    if (EQUITY_INCL_NCI_TAG, pid) in operands:
        # the printed equity-including-NCI total stands for the equity and the NCI
        equity = operands[(EQUITY_INCL_NCI_TAG, pid)]
        parts[1] = f"equity incl NCI {equity}"
    else:
        for t in NCI_EQUITY_TAGS:
            if (t, pid) in operands:
                equity += operands[(t, pid)]
                parts.append(f"{t} {operands[(t, pid)]}")
    mezz = [(t, operands[(t, pid)]) for t in TEMP_EQUITY_TAGS if (t, pid) in operands]
    if any(t == TEMP_EQUITY_TOTAL_TAG for t, _ in mezz):
        mezz = [(t, x) for t, x in mezz if t not in TEMP_EQUITY_PART_TAGS]
    total_mezz = sum((x for _t, x in mezz), Decimal(0))
    parts += [f"{t} {x}" for t, x in mezz]
    value = lse - equity - total_mezz
    return value, f"{LABEL}: " + " - ".join(
        parts
    ) + " (printed lines; the filing prints no total liabilities)"


def add_derived_cells(
    conn: psycopg.Connection,
    company_id: int,
    cells: list[dict],
    stats: dict[str, Any],
    concept_info: dict[int, tuple[str, str]],
    periods: dict[int, tuple[date, date, str]],
) -> int:
    """Append the derived-not-printed cells to `cells` and drop the not_presented blanks they replace. Returns the
    number added. Reads analytics.cell_proof (proven verdicts) and core.fact (printed operands) of one company."""
    if not any(
        b.get("state") == "not_presented"
        and _base(b["concept_name"]) in ("gross_profit", "total_liabilities")
        for b in stats["blanks"]
    ):
        return 0
    new = derive(
        cells,
        stats,
        concept_info,
        periods,
        load_proven(conn, company_id),
        {},
        load_operand_filings(conn, company_id),
        load_gp_hosts(conn, company_id, periods),
    )
    if not new:
        return 0
    keys = {(c["canonical_concept_id"], c["period_id"]) for c in new}
    stats["blanks"] = [
        b
        for b in stats["blanks"]
        if (b.get("canonical_concept_id"), b.get("period_id")) not in keys
    ]
    cells.extend(new)
    stats["derived_not_printed"] = len(new)
    return len(new)

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

Never derived: a period without every operand served/printed and proven, a cell the mapper already serves or holds,
a concept the template leaves out (not_in_template). Instants are never summed by the mapper (D3); C2 is the single
ruled exception: one subtraction of printed lines, labelled.

The hook is `add_derived_cells(...)`, called by company_tag_map.resolve_for_company after build_cells.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
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

LABEL = "derived_not_printed"
OPERAND_TAGS: tuple[str, ...] = (
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
    for n, g, s, e, v in conn.execute(
        """
        select data_point_name, period_grain, period_start, period_end, shown_value
        from analytics.cell_proof
        where company_id = %s and basis = 'latest' and verdict = 'PROVEN' and shown_value is not null
          and detector_version = %s
        """,
        (company_id, DETECTOR_VERSION),
    ).fetchall():
        out[(_base(n), g, s, e)].add(Decimal(v))
    return out


def load_operands(
    conn: psycopg.Connection, company_id: int
) -> dict[tuple[str, int], Decimal]:
    """(tag, period_id) -> the printed (authoritative, non-derived) value of the C2 operand tags; a key with two
    distinct values is dropped (never guess)."""
    seen: dict[tuple[str, int], set[Decimal]] = defaultdict(set)
    for tag, period_id, value in conn.execute(
        """
        select c.tag, f.period_id, f.value
        from core.fact f join core.concept c on c.id = f.concept_id
        where f.company_id = %s and f.is_authoritative and not f.is_derived
          and c.taxonomy = 'us-gaap' and c.tag = any(%s)
        """,
        (company_id, list(OPERAND_TAGS)),
    ).fetchall():
        seen[(tag, period_id)].add(Decimal(value))
    return {k: next(iter(v)) for k, v in seen.items() if len(v) == 1}


def derive(
    cells: list[dict],
    stats: dict[str, Any],
    concept_info: dict[int, tuple[str, str]],
    periods: dict[int, tuple[date, date, str]],
    proven: dict[ProvenKey, set[Decimal]],
    operands: dict[tuple[str, int], Decimal],
) -> list[dict]:
    """The derived cells (pure); `cells` and `stats` are not touched (add_derived_cells applies them)."""
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
    for b in stats["blanks"]:
        if b.get("state") != "not_presented" or b["period_id"] not in periods:
            continue
        key = (b["canonical_concept_id"], b["period_id"])
        if key in served or key in held:
            continue
        base = _base(b["concept_name"])
        pid = b["period_id"]
        value: Decimal | None = None
        note = ""
        if base == "gross_profit" and b["grain"] in ("FY", "Q"):
            rev = by_base.get(("revenue", pid))
            cor = by_base.get(("cost_of_revenue", pid))
            if (
                rev is not None
                and cor is not None
                and is_proven("revenue", rev)
                and is_proven("cost_of_revenue", cor)
            ):
                value = rev["value"] - cor["value"]
                note = f"{LABEL}: revenue {rev['value']} - cost_of_revenue {cor['value']} (both PROVEN); the filing prints no gross profit line"
        elif base == "total_liabilities" and b["grain"] == "I":
            value, note = _total_liabilities(pid, by_base, operands, is_proven)
        if value is None:
            continue
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


def _total_liabilities(pid, by_base, operands, is_proven) -> tuple[Decimal | None, str]:
    ta = by_base.get(("total_assets", pid))
    se = by_base.get(("stockholders_equity", pid))
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
        load_operands(conn, company_id),
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

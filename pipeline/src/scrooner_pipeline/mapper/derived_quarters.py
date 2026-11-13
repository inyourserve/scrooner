"""Derived 3-month quarters by subtraction, served from the mapper's own served year-to-date cells.

The filings print a 3-month column only for Q1 (and for the income statement Q2/Q3); a cash-flow Q2/Q3/Q4 and every
Q4 exists only as a difference of two printed year-to-date lines:  Q2 = 6M - Q1,  Q3 = 9M - 6M,  Q4 = FY - 9M
(founder 2026-11-04). The cell is served only when BOTH inputs are cells this same mapper run serves (single-line
concept cells with a lineage), so each input is a printed line of the filing that carries its column; the proof's
derived-quarter check (proof/prove.prove_derived) re-derives it from the filings' own structure and judges it.

Never derived: EPS and share counts (proof.prove.never_derived / unit_class), instants (balance sheet), a component
sum, a derived-not-printed cell, a quarter that is already served or held, a quarter whose period row does not exist.
A missing input means no cell (the blank stays; no other value is ever substituted).
Family: company_tag_map:derived_quarter. Lineage: source ids of both inputs.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from scrooner_pipeline.proof.prove import PER_SHARE, SHARE_COUNTS, never_derived

LABEL = "derived_quarter"


def _base(name: str) -> str:
    for suffix in ("_sanity_resolved", "_resolved"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def eligible_concept(name: str, statement: str) -> bool:
    if statement == "balance_sheet":
        return False
    full = _base(name) + "_resolved"
    if (
        name in SHARE_COUNTS
        or full in SHARE_COUNTS
        or never_derived(name)
        or never_derived(full)
    ):
        return False
    if name in PER_SHARE or full in PER_SHARE:
        return (
            full == "dividends_per_share_resolved"
        )  # DPS by subtraction: founder 2026-11-04
    return True


def _span(start: date, end: date) -> str | None:
    d = (end - start).days
    if 80 <= d <= 100:
        return "Q1"
    if 170 <= d <= 195:
        return "H1"
    if 260 <= d <= 285:
        return "M9"
    if 350 <= d <= 380:
        return "FY"
    return None


# (minuend span, subtrahend span): the difference is the quarter after the subtrahend
RULES = (("H1", "Q1"), ("M9", "H1"), ("FY", "M9"))


def derive_quarters(
    cells: list[dict],
    stats: dict[str, Any],
    concept_info: dict[int, tuple[str, str]],
    periods: dict[int, tuple[date, date, str]],
) -> list[dict]:
    """The derived quarter cells (pure); `cells`/`stats` are not touched."""
    by_dates = {(s, e): pid for pid, (s, e, t) in periods.items() if t != "instant"}
    held = {(h["canonical_concept_id"], h["period_id"]) for h in stats["held"]}
    served = {(c["canonical_concept_id"], c["period_id"]) for c in cells}
    groups: dict[tuple[int, date], dict[str, dict]] = defaultdict(dict)
    for c in cells:
        info = concept_info.get(c["canonical_concept_id"])
        pid = c["period_id"]
        if info is None or pid not in periods or not eligible_concept(*info):
            continue
        if c.get("_from_components") or c.get("_derived_not_printed"):
            continue
        if not (c.get("source_fact_ids") or c.get("source_value_ids")):
            continue
        start, end, ptype = periods[pid]
        sp = _span(start, end) if ptype != "instant" else None
        if sp is not None:
            groups[(c["canonical_concept_id"], start)][sp] = c
    out: list[dict] = []
    for (cid, _start), g in groups.items():
        for big, small in RULES:
            a, b = g.get(big), g.get(small)
            if a is None or b is None:
                continue
            a_end = periods[a["period_id"]][1]
            b_end = periods[b["period_id"]][1]
            target = by_dates.get((b_end + timedelta(days=1), a_end))
            if target is None or (cid, target) in served or (cid, target) in held:
                continue
            if _span(*periods[target][:2]) != "Q1":
                continue
            out.append(
                {
                    "canonical_concept_id": cid,
                    "period_id": target,
                    "value": a["value"] - b["value"],
                    "value_source": LABEL,
                    "source_fact_ids": sorted(
                        set(a["source_fact_ids"]) | set(b["source_fact_ids"])
                    ),
                    "source_value_ids": sorted(
                        set(a["source_value_ids"]) | set(b["source_value_ids"])
                    ),
                    "serve_note": f"{LABEL}: {big} {a['value']} - {small} {b['value']} (both served printed year-to-date cells)",
                    "_scaled": False,
                    "_derived_quarter": True,
                }
            )
    return out


def add_derived_quarters(
    cells: list[dict],
    stats: dict[str, Any],
    concept_info: dict[int, tuple[str, str]],
    periods: dict[int, tuple[date, date, str]],
) -> int:
    new = derive_quarters(cells, stats, concept_info, periods)
    if not new:
        return 0
    keys = {(c["canonical_concept_id"], c["period_id"]) for c in new}
    stats["blanks"] = [
        b
        for b in stats["blanks"]
        if (b.get("canonical_concept_id"), b.get("period_id")) not in keys
    ]
    cells.extend(new)
    stats["derived_quarters"] = len(new)
    return len(new)

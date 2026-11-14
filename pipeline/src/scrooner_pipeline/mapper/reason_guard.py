"""False-reason guard (Ritwik, PM final draw 2026-11-14).

A `not_presented` reason ("the filing prints no such line") or a `combined` reason ("only a combined figure is
printed, the parent figure is not") is REFUSED when the cited filing's own column holds evidence of the line:

  - an undimensioned fsn.value of one of the data point's tags in that accession and column (a statement or note line:
    PM FY2016 R5 prints 'Comprehensive earnings attributable to PMI', ComprehensiveIncomeNetOfTax), or
  - for not_presented only, a dimensioned fsn.value under one of the tags (member rows: PM amortization of intangibles
    on the income-statement-line members, 58 + 101).

The data point's tags: analytics.concept_mapping of the concept (base name, never `_resolved`) plus the tags of the
resolver's own value claims of the same company and data point. A tag the reason itself names (the combined line's
own node: ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest) is not evidence against it.

A refused reason leaves the cell open (UNCHECKED), never served. Used by structural_loader.load (loader) and
structural_direct.direct_cells (serving: map rows already in the table are dropped from the blanks). Read-only.
Evidence is FILING-CHECKED only in the sense that fsn.value is the filing's own XBRL; the page comes from fsn.line.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from scrooner_pipeline.common.fsn_dates import fsn_end_matches

NOT_PRESENTED = "not_presented"
COMBINED = "combined"
STATEMENTS = ("IS", "BS", "CF", "CI", "EQ", "CP")


@dataclass(frozen=True)
class Fact:
    ddate: date
    qtrs: int
    dim: bool
    segments: str
    value: Decimal


def kind_of(decision: str | None, reason_class: str | None = None) -> str | None:
    """not_presented | combined | None (a reason that claims no printed line is not checked). Pure."""
    if decision == NOT_PRESENTED:
        return NOT_PRESENTED
    if decision == COMBINED or (
        decision == "not_in_template"
        and (reason_class or "") in ("line_presented_combined", "combined")
    ):
        return COMBINED
    return None


def base_name(concept: str) -> str:
    return concept.removesuffix("_resolved")


def evidence_for(
    kind: str,
    end: date,
    instant: bool,
    tags: set[str],
    text: str,
    facts: dict[str, list[Fact]],
) -> list[dict[str, Any]]:
    """Evidence rows {tag, value, member} refuting the reason at column `end`; [] when none. Pure.
    facts: tag -> stored facts of the cited accession. Tags named in `text` are skipped."""
    out: list[dict[str, Any]] = []
    for tag in sorted(tags):
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(tag)}(?![A-Za-z0-9])", text):
            continue
        here = [
            f
            for f in facts.get(tag, [])
            if fsn_end_matches(f.ddate, end)
            and (f.qtrs == 0 if instant else 3 <= f.qtrs <= 5)
        ]
        plain = [f for f in here if not f.dim]
        if plain:
            out.append({"tag": tag, "value": plain[0].value, "member": False})
        elif kind == NOT_PRESENTED:
            members = [f for f in here if f.dim]
            if members:
                out.append(
                    {
                        "tag": tag,
                        "value": sum((f.value for f in members), Decimal(0)),
                        "member": True,
                        "members": "; ".join(f"{f.segments}={f.value}" for f in members),
                    }
                )
    return out


def concept_tags(conn: Any, names: set[str]) -> dict[str, set[str]]:
    """base concept name -> tags of analytics.concept_mapping. One query."""
    out: dict[str, set[str]] = defaultdict(set)
    bases = sorted({base_name(n) for n in names})
    if not bases:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """select k.name, t.tag from analytics.concept_mapping cm
               join analytics.canonical_concept k on k.id = cm.canonical_concept_id
               join core.concept t on t.id = cm.concept_id
               where k.name = any(%s)""",
            (bases,),
        )
        for n, t in cur.fetchall():
            out[n].add(t)
    return out


def read_facts(
    conn: Any, company_id: int, pairs: set[tuple[str, str]]
) -> dict[tuple[str, str], list[Fact]]:
    """(accession, tag) -> stored numeric fsn.values (no coreg, iprx 0, value not null) of the company. One query."""
    out: dict[tuple[str, str], list[Fact]] = defaultdict(list)
    if not pairs:
        return out
    accs = sorted({a for a, _ in pairs})
    tags = sorted({t for _, t in pairs})
    with conn.cursor() as cur:
        cur.execute(
            """select f.accession, t.tag, v.ddate, v.qtrs, v.dim_id, d.segments, v.value
               from fsn.value v
               join fsn.filing f on f.id = v.filing_id
               join fsn.tag t on t.id = v.tag_id
               join fsn.dim d on d.id = v.dim_id
               where v.company_id = %s and f.accession = any(%s) and t.tag = any(%s)
                 and v.coreg = '' and v.iprx = 0 and v.value is not null""",
            (company_id, accs, tags),
        )
        for acc, tag, dd, q, dim, seg, val in cur.fetchall():
            if (acc, tag) in pairs:
                out[(acc, tag)].append(Fact(dd, q, dim != 0, seg or "", Decimal(val)))
    return out


def read_pages(
    conn: Any, pairs: set[tuple[str, str]]
) -> dict[tuple[str, str], int]:
    """(accession, tag) -> lowest report of fsn.line carrying the tag (statements first). One query."""
    out: dict[tuple[str, str], tuple[int, int]] = {}
    if not pairs:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """select f.accession, t.tag, l.report, l.stmt
               from fsn.line l join fsn.filing f on f.id = l.filing_id join fsn.tag t on t.id = l.tag_id
               where f.accession = any(%s) and t.tag = any(%s)""",
            (sorted({a for a, _ in pairs}), sorted({t for _, t in pairs})),
        )
        for acc, tag, rep, stmt in cur.fetchall():
            if (acc, tag) in pairs:
                rank = (0 if stmt in STATEMENTS else 1, rep)
                if (acc, tag) not in out or rank < out[(acc, tag)]:
                    out[(acc, tag)] = rank
    return {k: v[1] for k, v in out.items()}

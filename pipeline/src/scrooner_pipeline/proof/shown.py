"""Source (a) of the proof: the cell as production shows it.

A displayed statement cell is an analytics.canonical_fact row of one of the 24
statement-line concepts (analytics.statement_line). Its provenance is the
source_fact_ids array: the core.fact rows behind it give the XBRL tag(s) and
the filing (accession) the value was taken from, and whether it is derived
(Q4 / interim subtraction). The proof is then made against THAT filing's
structure (proof/fsn.py), so a and b are tied to the same document.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

import psycopg

from scrooner_pipeline.common.presentation_scale import company_presentation_scale
from scrooner_pipeline.proof.prove import EXPECTED, Shown

HISTORY_FLOOR = date(2015, 1, 1)


def _grain(
    period_type: str, fiscal_period: str | None, start: date, end: date
) -> str | None:
    if period_type == "instant":
        return "I"
    if fiscal_period == "FY":
        return "FY"
    if fiscal_period in ("Q1", "Q2", "Q3", "Q4"):
        return "Q" if 80 <= (end - start).days <= 100 else None
    return None


def load_shown(
    conn: psycopg.Connection, company_id: int, *, floor: date = HISTORY_FLOOR
) -> list[Shown]:
    """Every displayed statement cell of the company since `floor`, with its
    source tags, accession (latest-filed source fact wins) and derived flag."""
    scale = company_presentation_scale(conn, company_id)
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, p.period_type, p.fiscal_period, p.start_date, p.end_date, cf.value, cf.source_fact_ids
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join analytics.statement_line sl on sl.canonical_concept_id = cc.id
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and p.end_date >= %s and p.fiscal_period is not null
            """,
            (company_id, floor),
        )
        rows = cur.fetchall()
        fact_ids = sorted({f for r in rows for f in (r[6] or [])})
        facts: dict[int, tuple[str, str | None, date | None, bool, Decimal]] = {}
        for i in range(0, len(fact_ids), 5000):
            cur.execute(
                """
                select f.id, c.tag, fl.accession_number, fl.filing_date, f.is_derived, f.value
                from core.fact f
                join core.concept c on c.id = f.concept_id
                left join core.filing fl on fl.id = f.filing_id
                where f.id = any(%s)
                """,
                (fact_ids[i : i + 5000],),
            )
            for fid, tag, acc, fdate, der, fval in cur.fetchall():
                facts[fid] = (tag, acc, fdate, bool(der), Decimal(fval))
    out: list[Shown] = []
    for name, ptype, fp, start, end, value, src in rows:
        if name not in EXPECTED and name != "total_debt_resolved":
            continue
        grain = _grain(ptype, fp, start, end)
        if grain is None:
            continue
        srcs = [facts[f] for f in (src or []) if f in facts]
        tags = tuple(sorted({t for t, _a, _d, _der, _v in srcs if t}))
        derived = any(der for _t, _a, _d, der, _v in srcs)
        # The proof compares the value against the filing it CAME FROM: among the
        # source facts, prefer those whose value equals the canonical value (a
        # later filing's recast comparative must not be the reference for an
        # as-filed value: MSFT FY2016 total assets 193,694M as filed vs 193,468M
        # recast in the FY2017 10-K), then the latest-filed of those.
        shown_value = Decimal(value)
        carriers = [
            (acc, fdate) for _t, acc, fdate, _der, v in srcs if acc and v == shown_value
        ]
        pool = carriers or [(acc, fdate) for _t, acc, fdate, _der, _v in srcs if acc]
        accession = max(pool, key=lambda af: af[1] or date.min)[0] if pool else None
        out.append(
            Shown(
                company_id=company_id,
                data_point_name=name,
                period_grain=grain,
                period_start=start,
                period_end=end,
                value=Decimal(value),
                tags=tags,
                accession=accession,
                source_fact_ids=tuple(sorted(f for f in (src or []))),
                is_derived=derived,
                presentation_scale=scale,
            )
        )
    return out


def group_by_accession(shown: list[Shown]) -> dict[str | None, list[Shown]]:
    out: dict[str | None, list[Shown]] = defaultdict(list)
    for s in shown:
        out[s.accession].append(s)
    return out

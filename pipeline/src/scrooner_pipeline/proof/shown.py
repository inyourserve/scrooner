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
from datetime import date, timedelta
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


PERIODIC_FORMS = (
    "10-K",
    "10-K/A",
    "10-KT",
    "10-KT/A",
    "10-Q",
    "10-Q/A",
    "10-QT",
    "10-QT/A",
)


def _periodic_copies(
    conn: psycopg.Connection, company_id: int, floor: date
) -> dict[tuple[str, int], list[tuple[str, Decimal, str]]]:
    """(base canonical name, period_id) -> every periodic-form copy (accession,
    value, xbrl tag) of the cell in core.fact, authoritative or not: the resolver keeps
    one, the proof must see them all (restated copies that disagree are hidden,
    founder ruling)."""
    out: dict[tuple[str, int], list[tuple[str, Decimal, str]]] = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, f.period_id, fl.accession_number, f.value, p.period_type, p.end_date,
                   fl.period_of_report, c.tag
            from core.fact f
            join core.filing fl on fl.id = f.filing_id
            join core.period p on p.id = f.period_id
            join core.concept c on c.id = f.concept_id
            join analytics.concept_mapping cm on cm.concept_id = f.concept_id and cm.confidence <> 'rejected'
            join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id
            where f.company_id = %s and not f.is_derived and fl.form = any(%s) and p.end_date >= %s
            """,
            (company_id, list(PERIODIC_FORMS), floor),
        )
        for name, pid, acc, value, ptype, end, por, tag in cur.fetchall():
            # an instant copy counts only where the filing's balance sheet can print it (its own
            # date or the prior year end): older instants are cash-flow/equity opening balances,
            # and a filer that misdates one (HD 0000354950-19-000010 files the 2016-01-31 cash
            # at 2015-01-31) must not make a shown cell "restated copies disagree"
            if (
                ptype == "instant"
                and por is not None
                and end < por - timedelta(days=375)
            ):
                continue
            out[(name, pid)].append((acc, Decimal(value), tag))
    return out


def matching_copies(
    copies: list[tuple[str, Decimal, str]], tags: tuple[str, ...]
) -> list[tuple[str, Decimal]]:
    """Copies of the shown cell: facts under the cell's own XBRL tag(s). A fact
    reported under another tag that maps to the same canonical name is not a copy
    (MDT FY17 net income NetIncomeLoss 4,028 vs ProfitLoss 4,024, Release approver
    ruling 2026-11-10). A cell with no source tag keeps the by-canonical-name
    behaviour."""
    if not tags:
        return [(a, v) for a, v, _t in copies]
    return [(a, v) for a, v, t in copies if t in tags]


def disagreeing_copies(
    copies: list[tuple[str, Decimal]], shown_value: Decimal, scale: int
) -> list[tuple[str, str]]:
    from scrooner_pipeline.common.presentation_scale import same_number

    return sorted(
        {(a, str(v)) for a, v in copies if not same_number(v, shown_value, scale)}
    )


def _base_name(name: str) -> str:
    for suffix in ("_sanity_resolved", "_resolved"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def load_shown(
    conn: psycopg.Connection, company_id: int, *, floor: date = HISTORY_FLOOR
) -> list[Shown]:
    """Every displayed statement cell of the company since `floor`, with its
    source tags, accession (latest-filed source fact wins) and derived flag."""
    scale = company_presentation_scale(conn, company_id)
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, p.period_type, p.fiscal_period, p.start_date, p.end_date, cf.value, cf.source_fact_ids, p.id
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and p.end_date >= %s and p.fiscal_period is not null
              and cc.name = any(%s)
            """,
            # the proof's own concepts: joining analytics.statement_line dropped every concept
            # without a statement row (D&A) and repeated a concept with two rows
            (company_id, floor, sorted({*EXPECTED, "total_debt_resolved"})),
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
    copies_by = _periodic_copies(conn, company_id, floor)
    for name, ptype, fp, start, end, value, src, period_id in rows:
        if name not in EXPECTED and name != "total_debt_resolved":
            continue
        grain = _grain(ptype, fp, start, end)
        if grain is None:
            continue
        srcs = [facts[f] for f in (src or []) if f in facts]
        tags = tuple(sorted({t for t, _a, _d, _der, _v in srcs if t}))
        # derived: a source fact is derived, or (cell loader cells) a quarter whose value equals
        # none of its source facts was computed from them (FY - 9M, YTD differences)
        derived = any(der for _t, _a, _d, der, _v in srcs) or (
            grain == "Q" and bool(srcs) and all(v != Decimal(value) for *_r, v in srcs)
        )
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
        copies = matching_copies(copies_by.get((_base_name(name), period_id), []), tags)
        disagreeing = disagreeing_copies(copies, shown_value, scale)
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
                copies_disagree=tuple(disagreeing) or None,
                copies=len(copies),
            )
        )
    return out


def group_by_accession(shown: list[Shown]) -> dict[str | None, list[Shown]]:
    out: dict[str | None, list[Shown]] = defaultdict(list)
    for s in shown:
        out[s.accession].append(s)
    return out

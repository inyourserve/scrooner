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

from scrooner_pipeline.common.authority import face_column_eligible

from scrooner_pipeline.common.presentation_scale import company_presentation_scale
from scrooner_pipeline.proof.prove import EXPECTED, Claim, Shown

HISTORY_FLOOR = date(2015, 1, 1)


# one company_tag_map row that can drive a claim: (id, decision, stmt, tag, concept, parent, sign,
# era_from, era_to)
MapRow = tuple[
    int, str, str, str | None, str | None, str | None, int, date, date | None
]


def load_map_rows(conn: psycopg.Connection, company_id: int) -> list[MapRow]:
    """The company's value-bearing company_tag_map rows ('concept' and 'component'): the map is the
    claim, the filing is the check."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select m.id, m.decision, m.stmt, m.tag, cc.name, pc.name, m.sign, m.era_from, m.era_to
            from analytics.company_tag_map m
            left join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
            left join analytics.canonical_concept pc on pc.id = m.parent_concept_id
            where m.company_id = %s and m.decision in ('concept', 'component') and m.tag is not null
            """,
            (company_id,),
        )
        return [tuple(r) for r in cur.fetchall()]  # type: ignore[misc]


def load_combined(
    conn: psycopg.Connection, company_id: int
) -> list[tuple[str, tuple[str, ...], date, date | None]]:
    """The company's 'combined' map rows: (tag, spanned concept names, era_from, era_to)."""
    with conn.cursor() as cur:
        cur.execute(
            "select tag, components, era_from, era_to from analytics.company_tag_map "
            "where company_id = %s and decision = 'combined' and tag is not null",
            (company_id,),
        )
        return [(t, tuple(c or ()), a, b) for t, c, a, b in cur.fetchall()]


def combined_for(
    rows: list[tuple[str, tuple[str, ...], date, date | None]],
    name: str,
    period_end: date,
) -> tuple[str, ...]:
    base = _base_name(name)
    return tuple(
        sorted(
            {
                t
                for t, comps, a, b in rows
                if a <= period_end
                and (b is None or period_end <= b)
                and (name in comps or base in comps)
            }
        )
    )


def claim_for(rows: list[MapRow], name: str, period_end: date) -> Claim | None:
    """The claim of one cell: the company's rows for this concept whose era holds the period end.
    'concept' rows win over 'component' rows. The statement is the latest era's; the tags are those
    rows of that statement (latest era first). Parts of a component claim are (sign, tag)."""
    live = [
        r for r in rows if r[7] <= period_end and (r[8] is None or period_end <= r[8])
    ]
    concept = sorted(
        (r for r in live if r[1] == "concept" and r[4] == name),
        key=lambda r: (r[7], r[0]),
        reverse=True,
    )
    if concept:
        stmt = concept[0][2]
        tags = tuple(dict.fromkeys(r[3] for r in concept if r[2] == stmt and r[3]))
        return Claim("concept", stmt, tags=tags, sign=concept[0][6])
    comps = sorted(
        (r for r in live if r[1] == "component" and r[5] == name),
        key=lambda r: r[0],
    )
    if comps:
        # a claim may mix statements (face debt lines + a note finance-lease total, audit R06): each
        # part keeps its own statement; the same (sign, tag) on two statements counts once
        stmt = comps[0][2]
        seen: dict[tuple[int, str], str] = {}
        for r in comps:
            if r[3]:
                seen.setdefault((r[6], r[3]), r[2])
        return Claim(
            "component",
            stmt,
            parts=tuple(seen),
            part_stmts=tuple(seen.values()),
        )
    return None


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
) -> tuple[
    dict[tuple[str, int], list[tuple[str, Decimal, str]]],
    dict[tuple[str, int], set[str]],
]:
    """(base canonical name, period_id) -> every periodic-form copy (accession,
    value, xbrl tag) of the cell in core.fact, authoritative or not: the resolver keeps
    one, the proof must see them all (restated copies that disagree are hidden,
    founder ruling)."""
    out: dict[tuple[str, int], list[tuple[str, Decimal, str]]] = defaultdict(list)
    auth: dict[tuple[str, int], set[str]] = defaultdict(set)
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, f.period_id, fl.accession_number, f.value, p.period_type, p.end_date,
                   fl.period_of_report, c.tag, f.is_authoritative, fl.form
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
        for (
            name,
            pid,
            acc,
            value,
            ptype,
            end,
            por,
            tag,
            is_auth,
            form,
        ) in cur.fetchall():
            # a copy counts only where its filing can print the period as a face column (shared
            # authority rule, common/authority.py): older instants are cash-flow/equity opening
            # balances, and a filer that misdates one (HD 0000354950-19-000010 files the 2018
            # goodwill at 2015-02-01) must neither make a shown cell "restated" nor be its
            # authoritative copy. The filing of the period itself is always eligible.
            if not face_column_eligible(
                form=form,
                period_type=ptype,
                end_date=end,
                period_of_report=por,
                is_original=por == end,
            ):
                continue
            out[(name, pid)].append((acc, Decimal(value), tag))
            if is_auth:
                auth[(name, pid)].add(acc)
    return out, auth


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
    map_rows = load_map_rows(conn, company_id)
    combined_rows = load_combined(conn, company_id)
    names = {*EXPECTED, "total_debt_resolved"}
    for r in map_rows:
        names.update(n for n in (r[4], r[5]) if n)
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
            (company_id, floor, sorted(names)),
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
    copies_by, auth_by = _periodic_copies(conn, company_id, floor)
    for name, ptype, fp, start, end, value, src, period_id in rows:
        if name not in names:
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
        auth_accs = auth_by.get((_base_name(name), period_id), set())
        # the authoritative (latest accepted periodic filing) copy is what the cell must show; an
        # earlier copy that differs is restated history (audit R13)
        auth_differs = [d for d in disagreeing if d[0] in auth_accs]
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
                authoritative_disagrees=tuple(auth_differs) or None,
                copies=len(copies),
                claim=claim_for(map_rows, name, end),
                combined=combined_for(combined_rows, name, end),
            )
        )
    return out


def group_by_accession(shown: list[Shown]) -> dict[str | None, list[Shown]]:
    out: dict[str | None, list[Shown]] = defaultdict(list)
    for s in shown:
        out[s.accession].append(s)
    return out

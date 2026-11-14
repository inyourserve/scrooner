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

from scrooner_pipeline.common.authority import (
    FaceIndex,
    face_column_eligible,
    load_face_indexes,
    absent_part_is_zero,
    latest_complete_filing,
    latest_eligible,
    load_calc_parents,
    load_calc_ties,
)
from scrooner_pipeline.common.fsn_dates import era_holds
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


def load_part_parents(conn: psycopg.Connection, company_id: int) -> dict[str, set[str]]:
    """tag -> local calc-parent tags of the company's component rows (evidence_cal_parent 'A;B'): what rule 1 ties."""
    out: dict[str, set[str]] = defaultdict(set)
    with conn.cursor() as cur:
        cur.execute(
            """
            select tag, evidence_cal_parent from analytics.company_tag_map
            where company_id = %s and decision = 'component' and tag is not null and evidence_cal_parent is not null
            """,
            (company_id,),
        )
        for tag, parents in cur.fetchall():
            out[tag].update(
                p.strip().rsplit(":", 1)[-1] for p in parents.split(";") if p.strip()
            )
    return out


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


def claim_for(
    rows: list[MapRow],
    name: str,
    period_end: date,
    filing_por: date | None = None,
) -> Claim | None:
    """The claim of one cell: the company's rows for this concept whose era holds the period end, or (concept rows,
    per-filing tag era) whose era holds the period of the filing the value was printed in (`filing_por`: MSFT
    FY2016 revenue read from the FY2018 10-K is claimed by the row of THAT filing's era). 'concept' rows win over
    'component' rows. The statement is the latest era's; the tags are those rows of that statement (latest era
    first). Other statements the live concept rows name are kept as `alts` (S16: the printed line may sit on
    another statement than the latest row's). Parts of a component claim are (sign, tag)."""
    held = [r for r in rows if era_holds(r[7], r[8], period_end)]
    # the claim is made by the rows whose era holds the CELL's period. The filing's own period only adds concept rows
    # of the same kind (a per-filing tag era), never over rows that hold the cell's period as components: SHOP
    # total_debt FY2023, read from the FY2024 10-K, is the component sum of FY2023's rows, not the FY2024 era's
    # current-line concept row (916 judged against 0).
    mine = [r for r in held if r[4] == name or r[5] == name]
    cell_has_concept = any(r[1] == "concept" and r[4] == name for r in mine)
    live = list(held)
    if filing_por is not None and (cell_has_concept or not mine):
        live += [
            r
            for r in rows
            if r not in held and r[1] == "concept" and era_holds(r[7], r[8], filing_por)
        ]
    concept = sorted(
        (r for r in live if r[1] == "concept" and r[4] == name),
        key=lambda r: (r[7], r[0]),
        reverse=True,
    )
    if concept:
        stmt = concept[0][2]
        tags = tuple(dict.fromkeys(r[3] for r in concept if r[2] == stmt and r[3]))
        alts: dict[str, tuple[list[str], int]] = {}
        for r in concept:
            if r[2] != stmt and r[3]:
                alts.setdefault(r[2], ([], r[6]))[0].append(r[3])
        return Claim(
            "concept",
            stmt,
            tags=tags,
            sign=concept[0][6],
            alts=tuple(
                (st, tuple(dict.fromkeys(ts)), sg) for st, (ts, sg) in alts.items()
            ),
        )
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
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
    "10-Q",
    "10-Q/A",
    "10-QT",
    "10-QT/A",
)


def _periodic_copies(
    conn: psycopg.Connection,
    company_id: int,
    floor: date,
    face: FaceIndex | None = None,
) -> tuple[
    dict[tuple[str, int], list[tuple[str, Decimal, str]]],
    dict[tuple[str, int], set[tuple[str, str]]],
    dict[str, date | None],
    dict[str, date | None],
    dict[str, int],
]:
    """(base canonical name, period_id) -> every periodic-form copy (accession,
    value, xbrl tag) of the cell in core.fact, authoritative or not: the resolver keeps
    one, the proof must see them all (restated copies that disagree are hidden,
    founder ruling)."""
    out: dict[tuple[str, int], list[tuple[str, Decimal, str]]] = defaultdict(list)
    auth: dict[tuple[str, int], set[tuple[str, str]]] = defaultdict(set)
    filed: dict[str, date | None] = {}
    por_of: dict[str, date | None] = {}
    vals_by_acc: dict[str, list[Decimal]] = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name, f.period_id, fl.accession_number, f.value, p.period_type, p.end_date,
                   fl.period_of_report, c.tag, f.is_authoritative, fl.form, fl.filing_date, p.start_date
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
            fdate,
            pstart,
        ) in cur.fetchall():
            # a copy counts only where its filing can print the period as a face column (shared
            # authority rule, common/authority.py): older instants are cash-flow/equity opening
            # balances, and a filer that misdates one (HD 0000354950-19-000010 files the 2018
            # goodwill at 2015-02-01) must neither make a shown cell "restated" nor be its
            # authoritative copy. The filing of the period itself is always eligible.
            if not face_column_eligible(form, por, end, ptype):
                continue
            # statement coherence: the filing's FACE statement must print this tag for the column (a summary table
            # of a later 10-Q is no copy of the cell); note-claimed tags and filings outside the FSN store are exempt
            if face is not None and not face.printed_ok(acc, tag, pstart, end, ptype):
                continue
            out[(name, pid)].append((acc, Decimal(value), tag))
            filed[acc] = fdate
            por_of[acc] = por
            if is_auth:
                auth[(name, pid)].add((acc, tag))
            vals_by_acc[acc].append(Decimal(value))
    # a filing's own rounding: the median trailing-zero exponent of its printed values (LLY FY2024 10-K prints
    # 96.7M, its FY2025 10-K prints the same figure as 97M)
    from scrooner_pipeline.common.presentation_scale import presentation_scale

    scale_by = {a: presentation_scale(vs) for a, vs in vals_by_acc.items()}
    return out, auth, filed, por_of, scale_by


def _same_number(a: Decimal, b: Decimal, scale: int) -> bool:
    from scrooner_pipeline.common.presentation_scale import same_number

    return same_number(a, b, scale)


def component_sum_authority(
    copies: list[tuple[str, Decimal, str]],
    parts: tuple[tuple[int, str], ...],
    filed: dict[str, date | None],
    prefer: str | None = None,
    zero_ok=None,
) -> tuple[str, Decimal] | None:
    """(accession, sum) a component-sum cell is authoritatively read from: the latest face-column-eligible filing
    that prints EVERY part (common/authority.latest_complete_filing, the function the mapper picks its parts with).
    `copies` are the eligible per-part facts, `parts` the claim's (sign, tag). A part's own per-tag authoritative
    flag says nothing about the sum: SG&A parts live in different filings (MSFT FY2016: G&A kept its original copy,
    S&M restated in the FY2018 10-K), and comparing one part with the total is a category error. None when no
    filing prints every part or a part is printed twice with different values in that filing."""
    by_part: list[dict[str, Decimal]] = []
    for _sign, tag in parts:
        prints: dict[str, set[Decimal]] = defaultdict(set)
        for acc, v, t in copies:
            if t == tag:
                prints[acc].add(v)
        if any(len(vs) > 1 for vs in prints.values()):
            return None
        by_part.append({a: next(iter(vs)) for a, vs in prints.items()})
    if zero_ok is not None:
        # rule 1 (common/authority.absent_part_is_zero): a part absent from a filing whose face omits it and whose calc
        # parent ties without it is 0 in that filing, so that filing prints every part
        every = set().union(*(set(p) for p in by_part)) if by_part else set()
        for (_sign, tag), p in zip(parts, by_part):
            for a in every - set(p):
                if zero_ok(a, tag):
                    p[a] = Decimal(0)
    best = latest_complete_filing(
        [{a: filed.get(a) for a in p} for p in by_part], prefer
    )
    if best is None:
        return None
    total = sum((s * p[best] for (s, _t), p in zip(parts, by_part)), Decimal(0))
    return str(best), total


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


def era_tag_copies(
    copies: list[tuple[str, Decimal, str]],
    map_rows: list[MapRow],
    name: str,
    shown_tags: tuple[str, ...],
    por_by: dict[str, date | None],
) -> list[tuple[str, Decimal, str]]:
    """Copies under ANOTHER tag that the company's map assigns to this concept in the era of the copy's own filing
    (per-filing tag era; the mapper reads the same rows, company_tag_map._filing_in_era). Not a copy: a fact under
    a tag no concept row of that filing's era names (MDT NetIncomeLoss vs ProfitLoss stays two lines)."""
    if not shown_tags:
        return []
    out = []
    for acc, v, t in copies:
        if t in shown_tags:
            continue
        por = por_by.get(acc)
        if por is None:
            continue
        if any(
            r[1] == "concept"
            and r[4] == name
            and r[3] == t
            and era_holds(r[7], r[8], por)
            for r in map_rows
        ):
            out.append((acc, v, t))
    return out


def rounding_equal(
    a: Decimal, b: Decimal, scale_a: int | None, scale_b: int | None
) -> bool:
    """One figure printed at two precisions: the values differ by at most half a unit of the COARSER filing's own
    rounding scale (96.7M vs 97M, the later filing prints whole millions). Only when the coarser value really sits on
    that grid (a multiple of the unit), so a genuine restatement is never absorbed."""
    s = max(scale_a or 0, scale_b or 0)
    if s <= 0:
        return False
    unit = Decimal(10) ** s
    coarse = a if (scale_a or 0) >= (scale_b or 0) else b
    if coarse % unit != 0:
        return False
    return abs(a - b) <= unit / 2


def disagreeing_copies(
    copies: list[tuple[str, Decimal]],
    shown_value: Decimal,
    scale: int,
    copy_scales: dict[str, int] | None = None,
    shown_scale: int | None = None,
) -> list[tuple[str, str]]:
    from scrooner_pipeline.common.presentation_scale import same_number

    cs = copy_scales or {}
    return sorted(
        {
            (a, str(v))
            for a, v in copies
            if not same_number(v, shown_value, scale)
            and not rounding_equal(v, shown_value, cs.get(a), shown_scale)
        }
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
            select cc.name, p.period_type, p.fiscal_period, p.start_date, p.end_date, cf.value, cf.source_fact_ids, p.id,
                   cf.source_value_ids
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
        # a cell built from the filing's own XBRL (value_source fsn_xbrl, e.g. a component sum with a custom
        # tag) carries fsn.value ids, not core.fact ids: tag, accession and filing date come from fsn
        value_ids = sorted({v for r in rows for v in (r[8] or [])})
        fsn_facts: dict[int, tuple[str, str | None, date | None, bool, Decimal]] = {}
        for i in range(0, len(value_ids), 5000):
            cur.execute(
                """
                select v.id, t.tag, f.accession, f.filed, v.value
                from fsn.value v
                join fsn.tag t on t.id = v.tag_id
                join fsn.filing f on f.id = v.filing_id
                where v.id = any(%s)
                """,
                (value_ids[i : i + 5000],),
            )
            for vid, tag, acc, filed, vval in cur.fetchall():
                fsn_facts[vid] = (tag, acc, filed, False, Decimal(vval))
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
    face = load_face_indexes(conn, [company_id])[company_id]
    ties = load_calc_ties(conn, [company_id])
    part_parents = load_part_parents(conn, company_id)
    for t, ps in load_calc_parents(
        conn,
        company_id,
        [r[3] for r in map_rows if r[1] == "component" and r[3]],
    ).items():
        part_parents[t] |= ps
    copies_by, auth_by, filed_by, por_by, scale_by = _periodic_copies(
        conn, company_id, floor, face
    )
    for name, ptype, fp, start, end, value, src, period_id, src_vals in rows:
        if name not in names:
            continue
        grain = _grain(ptype, fp, start, end)
        if grain is None:
            continue
        srcs = [facts[f] for f in (src or []) if f in facts]
        srcs += [fsn_facts[v] for v in (src_vals or []) if v in fsn_facts]
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
        all_copies = copies_by.get((_base_name(name), period_id), [])
        # per-filing tag era: a later filing may print the period under the tag ITS OWN era row uses (MSFT revenue)
        cell_triples = (
            [(a, v, t) for a, v, t in all_copies if t in tags]
            + era_tag_copies(all_copies, map_rows, name, tags, por_by)
            if tags
            else list(all_copies)
        )
        copies = [(a, v) for a, v, _t in cell_triples]
        disagreeing = disagreeing_copies(
            copies,
            shown_value,
            scale,
            scale_by,
            scale_by.get(accession) if accession else None,
        )
        # the authoritative copies OF THIS CELL: only flags of the cell's own copies (its tags, and the tags its
        # filings' eras name) count; flags of OTHER tags say nothing about the cell (JNJ cash 2022: the
        # restricted-cash tag's FY2022 copy was taken for the cell's authority). A flagged copy under one tag is
        # superseded by a LATER flagged copy under another tag of the cell (MSFT revenue: FY2017 SalesRevenueNet
        # vs the FY2018 10-K's renamed tag), the later filing chosen by common/authority.latest_eligible. No
        # flagged copy: the latest eligible copy of the cell.
        flags = auth_by.get((_base_name(name), period_id), set())
        flagged: dict[str, set[str]] = defaultdict(set)
        for a, _v, t in cell_triples:
            if (a, t) in flags:
                flagged[a].add(t)
        newest = latest_eligible({a: filed_by.get(a) for a in flagged})
        auth_accs = {
            a
            for a, ts in flagged.items()
            if a == newest
            or (filed_by.get(a) or date.min) >= (filed_by.get(newest) or date.min)
            or ts & flagged[newest]
        }
        if not flagged:
            only = latest_eligible({a: filed_by.get(a) for a, _v, _t in cell_triples})
            auth_accs = {only} if only else set()
        claim = claim_for(
            map_rows, name, end, por_by.get(accession) if accession else None
        )
        # rule 1: the parts of a component claim the cell's own filing omits on its face while its calc parent ties
        zero_parts = tuple(
            t
            for _s, t in (claim.parts if claim is not None else ())
            if absent_part_is_zero(
                face, ties, accession, t, part_parents.get(t), start, end, ptype
            )
        )
        # statement coherence: every member of the statement and period is read from the statement filing (the
        # latest face-eligible filing that prints the column, common/authority); its copy is THE authoritative one
        # of this cell when it has one. Notes-claimed cells follow their own note rule.
        cstmt = claim.stmt if claim is not None else ""
        cstmt = "IS" if cstmt == "CI" else cstmt
        sf = (
            face.statement_filing(cstmt, start, end, ptype)
            if cstmt in ("BS", "IS", "CF")
            else None
        )
        if sf is not None and any(a == sf for a, _v, _t in cell_triples):
            auth_accs = {sf}
        if claim is not None and claim.kind == "component" and len(claim.parts) > 1:
            # a component sum is judged as a sum, never part against total
            win = component_sum_authority(
                copies_by.get((_base_name(name), period_id), []),
                tuple((s, t) for s, t in claim.parts),
                filed_by,
                sf,
                zero_ok=lambda a, t, _s=start, _e=end, _p=ptype: (
                    absent_part_is_zero(
                        face, ties, a, t, part_parents.get(t), _s, _e, _p
                    )
                    is not None
                ),
            )
            disagreeing = []
            auth_accs = set()
            if win is not None:
                acc_w, total_w = win
                auth_accs = {acc_w}
                if not _same_number(total_w, shown_value, scale):
                    disagreeing = [(acc_w, str(total_w))]
        # the authoritative (latest accepted periodic filing) copy is what the cell must show; an
        # earlier copy that differs is restated history (audit R13)
        # a differing fact of the SAME filing the value was taken from is no other vintage: the
        # filing's own printed line judges it
        auth_differs = [
            d for d in disagreeing if d[0] in auth_accs and d[0] != accession
        ]
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
                claim=claim,
                combined=combined_for(combined_rows, name, end),
                zero_parts=zero_parts,
            )
        )
    return out


def group_by_accession(shown: list[Shown]) -> dict[str | None, list[Shown]]:
    out: dict[str | None, list[Shown]] = defaultdict(list)
    for s in shown:
        out[s.accession].append(s)
    return out

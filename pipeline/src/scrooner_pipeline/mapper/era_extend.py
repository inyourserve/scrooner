"""Evidence-based era back-extension for docmap rows (rule company_tag_map.era_extend@1).

A docmap row carries an era only as far as its read says (fy1 by default). For a company the library never mapped
that leaves company_tag_map covering one or two fiscal years. This walks the company's EARLIER annual filings
(10-K, 10-K/A; FSN store, schema fsn) one at a time, newest first, and extends era_from while the SAME tag is there
and nothing says the company switched:

  * line check (tag has a statement line in the read 10-K): the earlier 10-K prints the tag on a line with the same
    statement code, matching presentation role or normalized label, and a compatible calculation parent (a shared
    parent, or no calc arc on either side; a different parent cuts);
  * value check (note-sourced / CF-supplemental tags with no face line in the read): the earlier 10-K carries the
    tag non-dimensionally at its own period end with the same period type (instant / annual) and unit class;
  * both: no other tag of this company is mapped (fsn.line_map) to the concept in that filing.

The walk cuts at the first filing that fails or when a fiscal year has no filing; a gap is never bridged. Each
filing is evidence for the two fiscal-year columns it prints (as the docmap read itself is). Floor: 2015-01-01.
A failed 'tag not printed' check also logs the other tag the filing used (line_map, or a same-label line), the
lead for the Tag Expert fallback. Pure logic here; fetch() is the only DB access (four queries per company)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import psycopg

EXT_RULE_ID = "company_tag_map.era_extend@1"
EXT_MARK = "ERA-EXT"
EXT_MARK_VALUE = "ERA-EXT(value)"
FLOOR = date(2015, 1, 1)
GAP_DAYS = 380  # consecutive annual periods are 364-371 days apart (52/53-week years); more is a missing year


@dataclass(frozen=True)
class Line:
    stmt: str
    prole: str
    label: str
    parents: frozenset


@dataclass
class FsnData:
    periods: dict  # period end -> [accession, ...] (10-K and 10-K/A of that period)
    lines: dict  # accession -> {tag: [Line]}
    mapped: dict  # accession -> {concept_id: {tag}}  (fsn.line_map status 'mapped')
    values: dict = field(
        default_factory=dict
    )  # accession -> {tag: {(kind, unit class)}} (non-dimensional, own period)
    by_label: dict = field(
        default_factory=dict
    )  # accession -> {(stmt, label): {tag}} (every statement line)


def _norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _shift(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 February
        return d.replace(year=d.year + years, day=28)


def _fy_start2(end: date) -> date:
    """First day of the two fiscal years a 10-K ending `end` prints."""
    return _shift(end, -2) + timedelta(days=1)


def unit_class(uom: str) -> str:
    u = (uom or "").lower()
    if "per" in u or "/" in u:
        return "per"
    if u == "usd":
        return "usd"
    if "share" in u:
        return "shares"
    return u


def fetch(
    conn: psycopg.Connection, company_id: int, tags: set[str], concept_ids: set[int]
) -> FsnData:
    periods: dict = {}
    lines: dict = {}
    mapped: dict = {}
    values: dict = {}
    by_label: dict = {}
    with conn.cursor() as cur:
        cur.execute(
            """select accession, period from fsn.filing
               where company_id = %s and form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A') and period is not null""",
            (company_id,),
        )
        for acc, period in cur.fetchall():
            periods.setdefault(period, []).append(acc)
        cur.execute(
            """select f.accession, t.tag, l.stmt, coalesce(l.prole, ''), coalesce(l.plabel, ''),
                      coalesce(array_agg(distinct pt.tag) filter (where pt.tag is not null), '{}')
               from fsn.filing f
               join fsn.line l on l.filing_id = f.id
               join fsn.tag t on t.id = l.tag_id
               left join fsn.calc_arc a on a.filing_id = f.id and a.child_tag_id = l.tag_id
               left join fsn.tag pt on pt.id = a.parent_tag_id
               where f.company_id = %s and f.form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A')
               group by f.accession, t.tag, l.stmt, l.prole, l.plabel, l.report, l.line""",
            (company_id,),
        )
        for acc, tag, stmt, prole, plabel, parents in cur.fetchall():
            label = _norm(plabel)
            by_label.setdefault(acc, {}).setdefault((stmt, label), set()).add(tag)
            if tag in tags:
                lines.setdefault(acc, {}).setdefault(tag, []).append(
                    Line(stmt, prole, label, frozenset(parents))
                )
        cur.execute(
            """select f.accession, t.tag, v.qtrs, v.uom
               from fsn.filing f
               join fsn.value v on v.filing_id = f.id and v.ddate = f.period and v.dim_id = 0
               join fsn.tag t on t.id = v.tag_id
               where f.company_id = %s and f.form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A') and t.tag = any(%s)
               group by f.accession, t.tag, v.qtrs, v.uom""",
            (company_id, sorted(tags)),
        )
        for acc, tag, qtrs, uom in cur.fetchall():
            kind = "instant" if qtrs == 0 else "annual" if qtrs == 4 else None
            if kind:
                values.setdefault(acc, {}).setdefault(tag, set()).add(
                    (kind, unit_class(uom))
                )
        if concept_ids:
            cur.execute(
                """select f.accession, lm.canonical_concept_id, t.tag
                   from fsn.filing f
                   join fsn.line_map lm on lm.filing_id = f.id
                   join fsn.line l on l.filing_id = lm.filing_id and l.report = lm.report and l.line = lm.line
                   join fsn.tag t on t.id = l.tag_id
                   where f.company_id = %s and f.form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A') and lm.status = 'mapped'
                     and lm.canonical_concept_id = any(%s)""",
                (company_id, sorted(concept_ids)),
            )
            for acc, cid, tag in cur.fetchall():
                mapped.setdefault(acc, {}).setdefault(cid, set()).add(tag)
    return FsnData(periods, lines, mapped, values, by_label)


def _same_line(ref: Line, cand: Line) -> tuple[bool, str]:
    if cand.stmt != ref.stmt:
        return False, f"stmt {cand.stmt}!={ref.stmt}"
    if not (cand.prole == ref.prole or cand.label == ref.label):
        return False, "role and label differ"
    # no calc arc on either side is no evidence of a different parent; two different parents cut
    if cand.parents and ref.parents and not (cand.parents & ref.parents):
        return False, "calc parent differs"
    return True, ""


def _check(
    tags: list[str], ref: tuple[dict, dict], cand: tuple[dict, dict]
) -> tuple[bool, str, str, bool]:
    """Every tag of the row must hold in the earlier filing; (ok, why not, line shown, any tag used the value check).
    ref/cand = (lines, values) of the read 10-K / the earlier 10-K."""
    ref_lines, ref_vals = ref
    lines, vals = cand
    shown: list[str] = []
    used_value = False
    for tag in tags:
        if tag in ref_lines:
            cands = lines.get(tag)
            if not cands:
                return False, f"{tag} not printed", "", used_value
            why = []
            for c in cands:
                if any(_same_line(r, c)[0] for r in ref_lines[tag]):
                    shown.append(
                        f"{c.stmt}/{c.prole}/{c.label}/{'|'.join(sorted(c.parents))}"
                    )
                    break
                why.append(_same_line(ref_lines[tag][0], c)[1])
            else:
                return False, f"{tag}: {'; '.join(why)}", "", used_value
        elif tag in ref_vals:
            used_value = True
            if not (ref_vals[tag] & vals.get(tag, set())):
                return False, f"{tag} not carried as a value of the same type", "", True
            shown.append(f"value/{sorted(ref_vals[tag] & vals[tag])[0][0]}")
        else:
            return False, f"{tag} not in the read 10-K (line or value)", "", used_value
    return True, "", " ; ".join(shown), used_value


def _others(
    tags: list[str], concept_ids: set[int], acc: str, data: FsnData, ref_lines: dict
) -> str:
    """The other tag(s) an earlier filing used for the line: line_map for the concept, or a same-label line."""
    found: set[str] = set()
    for c in concept_ids:
        found |= {f"line_map:{t}" for t in data.mapped.get(acc, {}).get(c, ())}
    for tag in tags:
        for r in ref_lines.get(tag, ()):
            found |= {
                f"label:{t}"
                for t in data.by_label.get(acc, {}).get((r.stmt, r.label), ())
            }
    mine = {f"{p}:{t}" for p in ("line_map", "label") for t in tags}
    return ";".join(sorted(found - mine))


def _walk(
    tags: list[str],
    base_era: date,
    data: FsnData,
    floor: date,
    test,  # accession -> (ok, why, shown, used_value)
    other,  # first accession of a failed year -> text for the log's other_tag column
    log: list[dict],
) -> tuple[date, str | None, bool]:
    """Walk the earlier 10-Ks newest first; `test` decides each. Cut at the first failure or missing year."""

    def rec(acc, period, ok, detail, shown="", oth=""):
        log.append(
            {
                "adsh": acc,
                "period": period,
                "tags": "+".join(tags),
                "check": "pass" if ok else "fail",
                "detail": detail,
                "stmt_role_label_calc_parent": shown,
                "other_tag": oth,
            }
        )

    era, earliest, value_used = base_era, None, False
    # the 10-K whose two columns start at base_era ends here; the next one tested is a year before it
    prev = _shift(base_era, 2) - timedelta(days=1)
    for period in sorted(
        (p for p in data.periods if _fy_start2(p) < base_era), reverse=True
    ):
        if era <= floor:
            break
        gap = (prev - period).days
        if (
            gap < 300
        ):  # the same fiscal year again (an amendment's period), not the previous one
            continue
        if gap > GAP_DAYS:
            rec(
                None,
                period,
                False,
                f"gap: no 10-K for the year ending near {_shift(prev, -1)}",
            )
            break
        ok, why, shown, acc_ok, used = False, "", "", None, False
        for acc in sorted(data.periods[period]):
            ok, why, shown, used = test(acc)
            if ok:
                acc_ok = acc
                break
        if not ok:
            first = sorted(data.periods[period])[0]
            rec(first, period, False, why, oth=other(first))
            break
        rec(acc_ok, period, True, "", shown)
        era, earliest, value_used = (
            max(floor, _fy_start2(period)),
            acc_ok,
            value_used or used,
        )
        prev = period
    return min(era, base_era), earliest, value_used


def extend(
    tags: list[str],
    concept_ids: set[int],
    base_era: date,
    ref_accession: str,
    data: FsnData,
    floor: date = FLOOR,
) -> tuple[date, str | None, list[dict], bool]:
    """(new era_from, accession of the earliest verified filing | None, per-filing check log, any value check). Pure."""
    log: list[dict] = []
    ref = (data.lines.get(ref_accession, {}), data.values.get(ref_accession, {}))
    ref_period = next(
        (p for p, accs in data.periods.items() if ref_accession in accs), None
    )
    if ref_period is None or not all(t in ref[0] or t in ref[1] for t in tags):
        log.append(
            {
                "adsh": ref_accession,
                "period": ref_period,
                "tags": "+".join(tags),
                "check": "fail",
                "detail": "reference 10-K: tag has no line and no value in the FSN store",
                "stmt_role_label_calc_parent": "",
                "other_tag": "",
            }
        )
        return base_era, None, log, False

    def test(acc):
        ok, why, shown, used = _check(
            tags, ref, (data.lines.get(acc, {}), data.values.get(acc, {}))
        )
        if ok and any(
            (m := data.mapped.get(acc, {}).get(c)) and not (m & set(tags))
            for c in concept_ids
        ):
            return (
                False,
                "another tag is mapped to the concept in this filing",
                "",
                used,
            )
        return ok, why, shown, used

    era, earliest, used = _walk(
        tags,
        base_era,
        data,
        floor,
        test,
        lambda a: _others(tags, concept_ids, a, data, ref[0]),
        log,
    )
    return era, earliest, log, used


EXT_MARK_ABSENT = "ERA-EXT(absent)"


def fetch_facts(
    conn: psycopg.Connection, company_id: int, tags: set[str]
) -> tuple[set, dict]:
    """(accessions of the company's 10-Ks that carry XBRL facts at all, accession -> candidate tags among its facts)
    from core.fact (any authority: presence is the question; notes included). Same source as fy_era_extract.py."""
    with_facts: set = set()
    present: dict = {}
    with conn.cursor() as cur:
        cur.execute(
            """select fl.accession_number from core.fact f join core.filing fl on fl.id = f.filing_id
               where f.company_id = %s and fl.form in ('10-K', '10-K/A', '10-KT', '10-KT/A', '20-F', '20-F/A', '40-F', '40-F/A')
                 and fl.filing_date >= '2015-01-01' group by 1""",
            (company_id,),
        )
        with_facts = {a for (a,) in cur.fetchall()}
        cur.execute(
            """select distinct fl.accession_number, c.tag from core.fact f
               join core.filing fl on fl.id = f.filing_id join core.concept c on c.id = f.concept_id
               where f.company_id = %s and fl.form in ('10-K', '10-K/A', '10-KT', '10-KT/A', '20-F', '20-F/A', '40-F', '40-F/A')
                 and fl.filing_date >= '2015-01-01' and c.tag = any(%s)""",
            (company_id, sorted(tags)),
        )
        for a, tag in cur.fetchall():
            present.setdefault(a, set()).add(tag)
    return with_facts, present


def extend_absent(
    candidates: set[str],
    combined: list[str],
    base_era: date,
    data: FsnData,
    with_facts: set,
    present: dict,
    floor: date = FLOOR,
) -> tuple[date, str | None, list[dict]]:
    """Reason rows (not_presented; combined not_in_template with `combined` = its line's tags). Extends back one 10-K
    at a time while the filing has XBRL facts, no statement line (fsn.line) and no fact (core.fact) carries any
    candidate tag of the concept (for a combined row: the candidates exclude the combined tags, and the combined
    line itself must still be printed). Cut at the first year with a candidate. Pure."""
    cands = candidates - set(combined)
    log: list[dict] = []

    def line_tags(acc) -> set:
        return {t for tags in data.by_label.get(acc, {}).values() for t in tags}

    def test(acc):
        if acc not in with_facts:
            return (
                False,
                "no XBRL facts for the filing: absence cannot be shown",
                "",
                False,
            )
        lt = line_tags(acc)
        hit = sorted((cands & lt) | (cands & present.get(acc, set())))
        if hit:
            where = "statement line" if cands & lt else "XBRL fact"
            return False, f"candidate tag present ({where})", ",".join(hit), False
        if combined and not set(combined) <= lt:
            return False, "the combined line is not printed", "", False
        return (
            True,
            "",
            "absent" if not combined else "combined line printed, concept untagged",
            False,
        )

    era, earliest, _ = _walk(
        sorted(combined) or sorted(cands)[:1],
        base_era,
        data,
        floor,
        test,
        lambda a: ",".join(
            sorted((cands & line_tags(a)) | (cands & present.get(a, set())))
        ),
        log,
    )
    return era, earliest, log


# --- comparative-column extension (founder-approved rule, 2026-11-13) -------------------------------------------------
# A fiscal year the map does not cover (FY-1 of a read, a year outside the era set) takes the value from the NEXT
# 10-K's comparative column when that 10-K prints the SAME tag(s) for that year as the nearest covered year. The next
# 10-K prints the year as its prior-year column, so the nearest value row's era extends by one year, justified by it.
# One year at a time, only next to a covered year (the chain is contiguous: nothing bridges a gap), only when that 10-K
# exists in the FSN store and prints every tag non-dimensionally at the year's end with the kind (instant / annual) the
# tag has in its own year.
COMP_MARK = "ERA-EXT(comparative)"
COMP_BY = "era_comparative"
YEAR_BACK = (
    350,
    385,
)  # days from a 10-K's period end to its prior-year column's end (52/53-week years)
YEAR_BACK2 = (
    715,
    750,
)  # the second prior column of a 10-K's income and cash-flow statements (three printed years; balance sheets print two)


@dataclass(frozen=True)
class Covered:
    """One map row group of a concept: era and, for a value group, its tags (None for a reason group)."""

    era_from: date
    era_to: date | None
    tags: frozenset | None
    payload: Any = None  # the caller's rows, copied into the extension


@dataclass(frozen=True)
class CompSlice:
    key: object
    era_from: date
    era_to: date
    adsh: str  # the next 10-K whose prior-year column is the evidence
    tags: frozenset
    source: Covered  # the nearest covered group whose tags were carried


def fetch_printed(
    conn: psycopg.Connection,
    company_id: int,
    tags: set[str],
    concept_ids: set[int] | None = None,
) -> tuple[dict, dict, dict, dict]:
    """(filings {accession: period end}, printed {(accession, tag): {ddate: {kind}}}, own {(accession, tag): {kind}},
    mapped {accession: {concept id: {tag}}} from fsn.line_map): the company's 10-K / 10-K/A non-dimensional annual
    (qtrs 4) and instant (qtrs 0) values of `tags` in FSN."""
    filings: dict = {}
    printed: dict = {}
    own: dict = {}
    mapped: dict = {}
    with conn.cursor() as cur:
        cur.execute(
            """select accession, period from fsn.filing
               where company_id = %s and form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A') and period is not null""",
            (company_id,),
        )
        filings = {a: p for a, p in cur.fetchall()}
        cur.execute(
            """select f.accession, t.tag, v.ddate, v.qtrs, f.period
               from fsn.filing f join fsn.value v on v.filing_id = f.id and v.dim_id = 0 and v.qtrs in (0, 4)
               join fsn.tag t on t.id = v.tag_id
               where f.company_id = %s and f.form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A') and t.tag = any(%s)
               group by 1, 2, 3, 4, 5""",
            (company_id, sorted(tags)),
        )
        for acc, tag, ddate, qtrs, period in cur.fetchall():
            kind = "instant" if qtrs == 0 else "annual"
            printed.setdefault((acc, tag), {}).setdefault(ddate, set()).add(kind)
            if ddate == period:
                own.setdefault((acc, tag), set()).add(kind)
        # the SEC company-facts store (core.fact, undimensioned) covers 10-Ks the FSN store lacks
        cur.execute(
            """select accession_number, period_of_report from core.filing
               where company_id = %s and form in ('10-K', '10-K/A', '10-KT', '10-KT/A', '20-F', '20-F/A', '40-F', '40-F/A')
                 and period_of_report is not null and period_of_report >= '2014-01-01'""",
            (company_id,),
        )
        for acc, period in cur.fetchall():
            filings.setdefault(acc, period)
        cur.execute(
            """select fl.accession_number, c.tag, p.end_date, p.period_type, p.end_date - p.start_date
               from core.fact f
               join core.filing fl on fl.id = f.filing_id
               join core.concept c on c.id = f.concept_id
               join core.period p on p.id = f.period_id
               where f.company_id = %s and fl.form in ('10-K', '10-K/A', '10-KT', '10-KT/A', '20-F', '20-F/A', '40-F', '40-F/A')
                 and fl.period_of_report >= '2014-01-01' and c.tag = any(%s)
               group by 1, 2, 3, 4, 5""",
            (company_id, sorted(tags)),
        )
        for acc, tag, end, ptype, days in cur.fetchall():
            if ptype == "instant":
                kind = "instant"
            elif 350 <= days <= 380:
                kind = "annual"
            else:
                continue
            printed.setdefault((acc, tag), {}).setdefault(end, set()).add(kind)
            if end == filings.get(acc):
                own.setdefault((acc, tag), set()).add(kind)
        if concept_ids:
            cur.execute(
                """select f.accession, lm.canonical_concept_id, t.tag
                   from fsn.filing f
                   join fsn.line_map lm on lm.filing_id = f.id
                   join fsn.line l on l.filing_id = lm.filing_id and l.report = lm.report and l.line = lm.line
                   join fsn.tag t on t.id = l.tag_id
                   where f.company_id = %s and f.form in ('10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A') and lm.status = 'mapped'
                     and lm.canonical_concept_id = any(%s)""",
                (company_id, sorted(concept_ids)),
            )
            for acc, cid, tag in cur.fetchall():
                mapped.setdefault(acc, {}).setdefault(cid, set()).add(tag)
    return filings, printed, own, mapped


def comparative_slices(
    groups: dict,
    filings: dict,
    printed: dict,
    own: dict,
    other_mapped=None,
    floor: date = FLOOR,
) -> tuple[list[CompSlice], list[dict]]:
    """groups: key -> [Covered] (every map row group of the concept, value and reason; a reason group only covers).
    filings / printed / own: fetch_printed. other_mapped(accession, key) -> tags mapped to the concept in that filing
    (fsn.line_map), a tag outside the carried tags stops the extension. Returns (slices, log). Pure.

    For each 10-K N and its prior-year column P (printed within YEAR_BACK days before N's period): if no group covers P
    and a value group covers N's own period (back-extension) or the year before P (forward), and N prints every tag of
    that group at P as the kind it has at N's own period, P becomes a slice [P minus a year plus a day (clipped after
    any row ending inside), P] on N's evidence. Repeats until nothing changes (a new slice is itself a neighbor)."""
    log: list[dict] = []
    out: list[CompSlice] = []
    cur = {k: list(v) for k, v in groups.items()}

    def covers(g: Covered, d: date) -> bool:
        return g.era_from <= d and (g.era_to is None or d <= g.era_to)

    changed = True
    while changed:
        changed = False
        for key in sorted(cur, key=repr):
            for acc in sorted(filings):
                n_period = filings[acc]
                ps = sorted(
                    {
                        d
                        for (a, _t), by in printed.items()
                        if a == acc
                        for d in by
                        if YEAR_BACK[0] <= (n_period - d).days <= YEAR_BACK[1]
                        or (
                            YEAR_BACK2[0] <= (n_period - d).days <= YEAR_BACK2[1]
                            and "annual"
                            in by[
                                d
                            ]  # a duration only: instants are not printed three years back
                        )
                    }
                )
                for p in ps:
                    if p < floor or any(covers(g, p) for g in cur[key]):
                        continue
                    nbrs = [
                        g
                        for g in cur[key]
                        if g.tags
                        and (covers(g, n_period) or covers(g, p - timedelta(days=400)))
                    ]
                    for g in nbrs:
                        why = _comparative_check(
                            g, acc, p, printed, own, other_mapped, key
                        )
                        if why:
                            log.append(
                                {
                                    "adsh": acc,
                                    "period": p,
                                    "check": "fail",
                                    "detail": why,
                                }
                            )
                            continue
                        win_from = max(floor, _shift(p, -1) + timedelta(days=1))
                        ends = [
                            x.era_to + timedelta(days=1)
                            for x in cur[key]
                            if x.era_to is not None
                            and x.era_to < p
                            and x.era_to >= win_from
                        ]
                        era_from = max([win_from, *ends])
                        if era_from > p:
                            continue
                        sl = CompSlice(key, era_from, p, acc, g.tags, g)
                        out.append(sl)
                        cur[key].append(Covered(era_from, p, g.tags, g.payload))
                        log.append(
                            {"adsh": acc, "period": p, "check": "pass", "detail": ""}
                        )
                        changed = True
                        break
    return out, log


def fetch_quarter_prints(
    conn: psycopg.Connection, company_id: int, tags: set[str]
) -> tuple[dict, dict]:
    """(tenqs {accession: period end}, printed {accession: {tag}}): the company's 10-Q filings in FSN and, per 10-Q, the
    `tags` it carries non-dimensionally at its own period end for a quarter or year-to-date column (qtrs 1-3)."""
    with conn.cursor() as cur:
        cur.execute(
            """select accession, period from fsn.filing
               where company_id = %s and form in ('10-Q', '10-Q/A') and period is not null""",
            (company_id,),
        )
        tenqs = {a: p for a, p in cur.fetchall()}
        printed: dict = {}
        if tags and tenqs:
            cur.execute(
                """select f.accession, t.tag
                   from fsn.filing f join fsn.value v on v.filing_id = f.id and v.dim_id = 0
                        and v.qtrs in (1, 2, 3) and v.ddate = f.period
                   join fsn.tag t on t.id = v.tag_id
                   where f.company_id = %s and f.form in ('10-Q', '10-Q/A') and t.tag = any(%s)
                   group by 1, 2""",
                (company_id, sorted(tags)),
            )
            for acc, tag in cur.fetchall():
                printed.setdefault(acc, set()).add(tag)
    return tenqs, printed


def fetch_quarter_mapped(
    conn: psycopg.Connection, company_id: int, concept_ids: set[int]
) -> dict[str, dict[int, dict[str, str]]]:
    """{10-Q accession: {concept id: {full tag 'prefix:Local': statement code}}} from fsn.line_map (status mapped)
    and fsn.line: the tag each of the company's 10-Qs prints on a face line mapped to the concept."""
    out: dict[str, dict[int, dict[str, str]]] = {}
    if not concept_ids:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """select f.accession, lm.canonical_concept_id, t.tag, l.stmt
               from fsn.filing f
               join fsn.line_map lm on lm.filing_id = f.id and lm.status = 'mapped'
               join fsn.line l on l.filing_id = lm.filing_id and l.report = lm.report and l.line = lm.line
               join fsn.tag t on t.id = l.tag_id
               where f.company_id = %s and f.form in ('10-Q', '10-Q/A') and lm.canonical_concept_id = any(%s)""",
            (company_id, sorted(concept_ids)),
        )
        for acc, cid, tag, stmt in cur.fetchall():
            out.setdefault(acc, {}).setdefault(cid, {})[tag] = stmt
    return out


def fetch_quarter_face(
    conn: psycopg.Connection, company_id: int, tags: set[str]
) -> dict[str, tuple[str, str]]:
    """{local tag: (full 'prefix:Local' tag, statement code)} of `tags` (local names) printed on a face statement line
    (BS/IS/CF/CI/EQ) of one of the company's 10-Qs."""
    out: dict[str, tuple[str, str]] = {}
    if not tags:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """select distinct t.tag, l.stmt
               from fsn.filing f join fsn.line l on l.filing_id = f.id
               join fsn.tag t on t.id = l.tag_id
               where f.company_id = %s and f.form in ('10-Q', '10-Q/A') and l.stmt in ('BS', 'IS', 'CF', 'CI', 'EQ')
                 and substring(t.tag from '[^:]*$') = any(%s)""",
            (company_id, sorted(tags)),
        )
        for full, stmt in cur.fetchall():
            out.setdefault(full.rsplit(":", 1)[-1], (full, stmt))
    return out


@dataclass(frozen=True)
class QuarterSplit:
    tags: frozenset  # the tag set the year's own 10-Qs print
    last_quarter_end: date  # the latest 10-Q period end inside the year
    adsh: str  # that 10-Q: the evidence


def quarter_split(
    year_start: date,
    year_end: date,
    year_tags: frozenset,
    candidates: list[frozenset],
    tenqs: dict,
    printed: dict,
) -> QuarterSplit | None:
    """Rule 3 (Dhairya 2026-11-14): a fiscal year the next 10-K's comparative column carries under `year_tags` keeps, for
    its own quarters, the tag set its own 10-Qs print. Every 10-Q of the year (period in [year_start, year_end)) must
    print exactly one candidate tag set other than `year_tags` (all its tags, and that set the same in every 10-Q); a
    10-Q that already prints `year_tags` in full, no 10-Q in FSN, or no unique candidate gives None. Pure."""
    qs = sorted((p, a) for a, p in tenqs.items() if year_start <= p < year_end)
    if not qs:
        return None
    per = [printed.get(a, set()) for _p, a in qs]
    if any(year_tags <= got for got in per):
        return None
    common = set.intersection(*per) if per else set()
    fits = [c for c in candidates if c != year_tags and c and c <= common]
    if len(fits) != 1:
        return None
    return QuarterSplit(fits[0], qs[-1][0], qs[-1][1])


def _comparative_check(g, acc, p, printed, own, other_mapped, key) -> str:
    for tag in sorted(g.tags):
        at = printed.get((acc, tag), {}).get(p)
        mine = own.get((acc, tag))
        if not at:
            return f"{tag} not printed for the prior-year column"
        if not mine:
            return f"{tag} has no value for the 10-K's own year"
        if not (at & mine):
            return f"{tag} prior-year column has a different kind than its own year"
    if other_mapped is not None:
        om = other_mapped(acc, key)
        if om and not (om & set(g.tags)):
            return "another tag is mapped to the concept in this filing"
    return ""

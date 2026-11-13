"""Evidence-based era back-extension for docmap rows (rule company_tag_map.era_extend@1).

A docmap row carries an era only as far as its read says (fy1 by default). For a company the library never mapped
that leaves company_tag_map covering one or two fiscal years. This walks the company's EARLIER annual filings
(10-K, 10-K/A; FSN store, schema fsn) one at a time, newest first, and extends era_from while the SAME tag is printed
on the SAME line there: same statement code, matching presentation role or label, a shared calculation parent (or
none in both), and no other tag of this company mapped to the same concept in that filing (fsn.line_map). The walk
cuts at the first filing that fails or when a fiscal year has no filing; a gap is never bridged. Each filing is
evidence for the two fiscal-year columns it prints (as the docmap read itself is: fy0 and fy1). Floor: 2015-01-01.
Pure logic here; fetch() is the only DB access (three queries per company)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta

import psycopg

EXT_RULE_ID = "company_tag_map.era_extend@1"
EXT_MARK = "ERA-EXT"
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


def fetch(
    conn: psycopg.Connection, company_id: int, tags: set[str], concept_ids: set[int]
) -> FsnData:
    periods: dict = {}
    lines: dict = {}
    mapped: dict = {}
    with conn.cursor() as cur:
        cur.execute(
            """select accession, period from fsn.filing
               where company_id = %s and form in ('10-K', '10-K/A') and period is not null""",
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
               where f.company_id = %s and f.form in ('10-K', '10-K/A') and t.tag = any(%s)
               group by f.accession, t.tag, l.stmt, l.prole, l.plabel, l.report, l.line""",
            (company_id, sorted(tags)),
        )
        for acc, tag, stmt, prole, plabel, parents in cur.fetchall():
            lines.setdefault(acc, {}).setdefault(tag, []).append(
                Line(stmt, prole, _norm(plabel), frozenset(parents))
            )
        if concept_ids:
            cur.execute(
                """select f.accession, lm.canonical_concept_id, t.tag
                   from fsn.filing f
                   join fsn.line_map lm on lm.filing_id = f.id
                   join fsn.line l on l.filing_id = lm.filing_id and l.report = lm.report and l.line = lm.line
                   join fsn.tag t on t.id = l.tag_id
                   where f.company_id = %s and f.form in ('10-K', '10-K/A') and lm.status = 'mapped'
                     and lm.canonical_concept_id = any(%s)""",
                (company_id, sorted(concept_ids)),
            )
            for acc, cid, tag in cur.fetchall():
                mapped.setdefault(acc, {}).setdefault(cid, set()).add(tag)
    return FsnData(periods, lines, mapped)


def _same_line(ref: Line, cand: Line) -> tuple[bool, str]:
    if cand.stmt != ref.stmt:
        return False, f"stmt {cand.stmt}!={ref.stmt}"
    if not (cand.prole == ref.prole or cand.label == ref.label):
        return False, "role and label differ"
    if cand.parents != ref.parents and not (cand.parents & ref.parents):
        return False, "calc parent differs"
    return True, ""


def _line_check(
    tags: list[str], ref_lines: dict, acc_lines: dict
) -> tuple[bool, str, str]:
    """Every tag of the row must print on a line matching a reference line; (ok, why not, line shown)."""
    shown = []
    for tag in tags:
        refs = ref_lines.get(tag)
        cands = acc_lines.get(tag)
        if not refs:
            return False, f"{tag} not on a reference line", ""
        if not cands:
            return False, f"{tag} not printed", ""
        why = []
        for c in cands:
            if any(_same_line(r, c)[0] for r in refs):
                shown.append(
                    f"{c.stmt}/{c.prole}/{c.label}/{'|'.join(sorted(c.parents))}"
                )
                break
            why.append(_same_line(refs[0], c)[1])
        else:
            return False, f"{tag}: {'; '.join(why)}", ""
    return True, "", " ; ".join(shown)


def extend(
    tags: list[str],
    concept_ids: set[int],
    base_era: date,
    ref_accession: str,
    data: FsnData,
    floor: date = FLOOR,
) -> tuple[date, str | None, list[dict]]:
    """(new era_from, accession of the earliest verified filing | None, per-filing check log). Pure."""
    log: list[dict] = []
    ref_lines = data.lines.get(ref_accession, {})
    ref_period = next(
        (p for p, accs in data.periods.items() if ref_accession in accs), None
    )

    def rec(acc, period, ok, detail, shown=""):
        log.append(
            {
                "adsh": acc,
                "period": period,
                "tags": "+".join(tags),
                "check": "pass" if ok else "fail",
                "detail": detail,
                "stmt_role_label_calc_parent": shown,
            }
        )

    if ref_period is None or not all(t in ref_lines for t in tags):
        rec(
            ref_accession,
            ref_period,
            False,
            "reference 10-K lines not in the FSN store",
        )
        return base_era, None, log
    era, earliest = base_era, None
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
        ok, why, shown, acc_ok = False, "", "", None
        for acc in sorted(data.periods[period]):
            ok, why, shown = _line_check(tags, ref_lines, data.lines.get(acc, {}))
            if ok:
                switched = [
                    c
                    for c in concept_ids
                    if (m := data.mapped.get(acc, {}).get(c)) and not (m & set(tags))
                ]
                if switched:
                    ok, why = (
                        False,
                        "another tag is mapped to the concept in this filing",
                    )
            if ok:
                acc_ok = acc
                break
        if not ok:
            rec(sorted(data.periods[period])[0], period, False, why)
            break
        rec(acc_ok, period, True, "", shown)
        era, earliest = max(floor, _fy_start2(period)), acc_ok
        prev = period
    return min(era, base_era), earliest, log

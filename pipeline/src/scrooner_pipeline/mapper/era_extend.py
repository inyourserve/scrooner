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
               where f.company_id = %s and f.form in ('10-K', '10-K/A')
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
               where f.company_id = %s and f.form in ('10-K', '10-K/A') and t.tag = any(%s)
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
                   where f.company_id = %s and f.form in ('10-K', '10-K/A') and lm.status = 'mapped'
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

    def rec(acc, period, ok, detail, shown="", other=""):
        log.append(
            {
                "adsh": acc,
                "period": period,
                "tags": "+".join(tags),
                "check": "pass" if ok else "fail",
                "detail": detail,
                "stmt_role_label_calc_parent": shown,
                "other_tag": other,
            }
        )

    if ref_period is None or not all(t in ref[0] or t in ref[1] for t in tags):
        rec(
            ref_accession,
            ref_period,
            False,
            "reference 10-K: tag has no line and no value in the FSN store",
        )
        return base_era, None, log, False
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
            ok, why, shown, used = _check(
                tags, ref, (data.lines.get(acc, {}), data.values.get(acc, {}))
            )
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
            first = sorted(data.periods[period])[0]
            rec(
                first,
                period,
                False,
                why,
                other=_others(tags, concept_ids, first, data, ref[0]),
            )
            break
        rec(acc_ok, period, True, "", shown)
        era, earliest, value_used = (
            max(floor, _fy_start2(period)),
            acc_ok,
            value_used or used,
        )
        prev = period
    return min(era, base_era), earliest, log, value_used

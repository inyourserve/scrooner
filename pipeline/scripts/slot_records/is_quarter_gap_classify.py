"""Classify FSN-store income-statement gap keys by what the stored filings actually hold (read-only).

For each gap key of an income-statement concept (pilot.report_company: a template key with no cell), this
looks at the company's stored filings and says why no cell was made. One class per key:

  no_covering_filing           no stored 10-Q / 10-K whose period of report is within 15 days of the key
  no_income_statement_face     the covering filing has no income-statement line at all
  printed_not_face_column      a mapped line prints the key's column, but the store does not count the column as
                               face (no anchor total NetIncomeLoss / ProfitLoss / ... printed in that column on the
                               income statement): the face-column test fails
  printed_other_statement      the mapped tag prints the key's column only on a line outside the income statement
                               (comprehensive income, equity, ...): the IS line itself is not mapped in that filing
  ytd_only_no_prior            the face prints only a year-to-date column for the key (6M / 9M / FY) and there is
                               no face print of the previous year-to-date column to subtract (Q2-Q4 not derivable)
  ytd_only_input_not_face      a year-to-date column ends at the key, but it is not a face column either
  line_held_<status>           the covering filing's line for the concept is held / combined / excluded
  unmapped_line_<tag>          the covering filing's income statement prints a line that carries the concept in
                               another filing of the company (a tag mapped elsewhere) but is not mapped here
  other_tag_on_face            the concept's mapped tag is absent from the covering filing; the face prints a line
                               with the concept's label under another tag (listed): a mapping coverage gap
  no_line_for_concept          neither the mapped tag nor a line with the concept's label is on the covering face

The covering filing of a quarter key is the earliest original 10-Q whose period is within 15 days of the key
(for the fourth quarter: the 10-K of that fiscal year); of a FY key, the earliest original 10-K. Amendments are
used only when no original exists.

usage: is_quarter_gap_classify.py <database url> <gaps.csv> <out_dir> [cik,cik,...]
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

IS_CONCEPTS = (
    "revenue_sanity_resolved",
    "cost_of_revenue_resolved",
    "gross_profit_resolved",
    "operating_income_resolved",
    "income_before_tax_resolved",
    "income_tax_expense_resolved",
    "net_income_resolved",
    "interest_expense_resolved",
    "basic_eps_resolved",
    "diluted_eps_resolved",
)
# label words of each concept (a lead for the other-tag class only, never a mapping)
LABEL_RX = {
    "revenue_sanity_resolved": r"\b(total )?(net )?(revenues?|sales)\b",
    "cost_of_revenue_resolved": r"\bcost of (revenues?|sales|goods|products|services)",
    "gross_profit_resolved": r"\bgross (profit|margin)\b",
    "operating_income_resolved": r"\b(operating (income|profit|loss)|income from operations)\b",
    "income_before_tax_resolved": r"\bbefore (income )?tax",
    "income_tax_expense_resolved": r"\b(provision for|benefit from)? ?income tax",
    "net_income_resolved": r"^net (income|earnings|loss)\b",
    "interest_expense_resolved": r"\binterest expense\b",
    "basic_eps_resolved": r"\bbasic\b",
    "diluted_eps_resolved": r"\bdiluted\b",
}
ANCHORS = ("NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic",
           "IncomeLossFromContinuingOperations")
QTRS = {"Q": 1, "FY": 4}


@dataclass
class Company:
    filings: dict[int, dict[str, Any]]
    # (filing_id) -> [(report, line, stmt, tag, plabel, concept or None, status or None)]
    lines: dict[int, list[tuple]] = field(default_factory=dict)
    # (filing_id, tag) -> {(ddate, qtrs): value}
    values: dict[tuple[int, str], dict[tuple[date, int], Any]] = field(default_factory=dict)
    # face columns of the income statement: (filing_id, ddate, qtrs)
    face: set[tuple[int, date, int]] = field(default_factory=set)


def month_end(d: date, months: int) -> date:
    import calendar

    m = d.year * 12 + d.month - 1 + months
    y, mo = divmod(m, 12)
    return date(y, mo + 1, calendar.monthrange(y, mo + 1)[1])


def covering(co: Company, grain: str, end: date) -> int | None:
    def ok(f: dict[str, Any]) -> bool:
        if f["period"] is None or abs((f["period"] - end).days) > 15:
            return False
        if grain == "FY":
            return f["form"].startswith("10-K")
        return True

    c = [(fid, f) for fid, f in co.filings.items() if ok(f)]
    if grain == "Q":  # a 10-Q when one exists, else the 10-K (fourth quarter)
        c = [x for x in c if x[1]["form"].startswith("10-Q")] or c
    orig = [x for x in c if not x[1]["form"].endswith("/A")] or c
    orig.sort(key=lambda x: (x[1]["filed"], x[0]))
    return orig[0][0] if orig else None


def concept_tags(co: Company, concept: str) -> set[str]:
    return {ln[3] for ls in co.lines.values() for ln in ls if ln[5] == concept and ln[6] == "mapped"}


def classify(co: Company, concept: str, grain: str, end: date) -> tuple[str, str, int | None]:
    """(class, detail, covering filing id) of one gap key."""
    fid = covering(co, grain, end)
    if fid is None:
        return "no_covering_filing", "", None
    lines = co.lines.get(fid, [])
    is_lines = [ln for ln in lines if ln[2] == "IS"]
    if not is_lines:
        return "no_income_statement_face", "", fid
    q = QTRS[grain]
    mine = [ln for ln in lines if ln[5] == concept]
    mapped = [ln for ln in mine if ln[6] == "mapped"]
    if mapped:
        for ln in mapped:
            v = co.values.get((fid, ln[3]), {})
            if (end, q) in v:
                if (fid, end, q) not in co.face:
                    anchors = sorted({t for t in ANCHORS if (end, q) in co.values.get((fid, t), {})})
                    is_tags = sorted({x[3] for x in is_lines})
                    a_on_is = sorted(set(anchors) & set(is_tags))
                    detail = (f"line {ln[3]} ({ln[2]}) prints {v[(end, q)]}; anchors with a value: {anchors or 'none'};"
                              f" anchors on the IS face: {a_on_is or 'none'}")
                    return "printed_not_face_column", detail, fid
                return "printed_face_not_selected", f"{ln[3]}={v[(end, q)]}", fid
        if grain == "Q":
            for n in (2, 3, 4):
                for ln in mapped:
                    v = co.values.get((fid, ln[3]), {})
                    if (end, n) in v:
                        if (fid, end, n) not in co.face:
                            return "ytd_only_input_not_face", f"{ln[3]} {n}Q={v[(end, n)]}", fid
                        prior = (month_end(end, -3), n - 1)
                        have = [(f2, t) for (f2, t), vv in co.values.items()
                                if t in concept_tags(co, concept) and prior in vv and (f2, *prior) in co.face]
                        if not have:
                            return "ytd_only_no_prior", f"{ln[3]} {n}Q={v[(end, n)]}; no face {n - 1}Q at {prior[0]}", fid
                        return "ytd_only_prior_present", f"{ln[3]} {n}Q; prior face in {len(have)} filing(s)", fid
        other = sorted({ln[2] for ln in mapped})
        return "mapped_line_no_value_for_column", f"mapped on {','.join(other)}; no ({end},{q}) value", fid
    if mine:
        st = sorted({ln[6] or "none" for ln in mine})
        return "line_held_" + "_".join(st), "; ".join(f"{ln[3]}:{ln[4][:50]}" for ln in mine[:3]), fid
    elsewhere = concept_tags(co, concept)
    hits = [ln for ln in is_lines if ln[3] in elsewhere]
    if hits:
        return "unmapped_line_" + hits[0][3], f"{hits[0][4][:60]}", fid
    # the mapped tag printed on another statement of this filing (comprehensive income, equity)
    for t in sorted(elsewhere):
        v = co.values.get((fid, t), {})
        if (end, q) in v:
            stmts = sorted({ln[2] for ln in lines if ln[3] == t})
            return "printed_other_statement", f"{t}={v[(end, q)]} on {','.join(stmts) or 'no line'}", fid
    rx = re.compile(LABEL_RX[concept], re.IGNORECASE)
    lab = [ln for ln in is_lines if rx.search(ln[4] or "")]
    if lab:
        return "other_tag_on_face", "; ".join(f"{ln[3]}:{ln[4][:50]}" for ln in lab[:4]), fid
    return "no_line_for_concept", "", fid


def load(conn: Any, company_id: int) -> Company:
    from scrooner_pipeline.fsn_store import select as sel

    cur = conn.cursor()
    cur.execute("select id, accession, form, period, filed, accepted from fsn.filing where company_id = %s", (company_id,))
    filings = {r[0]: {"accession": r[1], "form": r[2], "period": r[3], "filed": r[4], "accepted": r[5]} for r in cur.fetchall()}
    cur.execute(
        """
        select l.filing_id, l.report, l.line, l.stmt, t.tag, l.plabel, cc.name, lm.status
        from fsn.line l join fsn.tag t on t.id = l.tag_id join fsn.filing f on f.id = l.filing_id
        left join fsn.line_map lm using (filing_id, report, line)
        left join analytics.canonical_concept cc on cc.id = lm.canonical_concept_id
        where f.company_id = %s and not l.inpth
        """,
        (company_id,),
    )
    lines: dict[int, list[tuple]] = defaultdict(list)
    for fid, rep, ln, stmt, tag, plabel, cname, status in cur.fetchall():
        lines[fid].append((rep, ln, stmt, tag, plabel, cname, status))
    cur.execute(
        """
        select v.filing_id, t.tag, v.ddate, v.qtrs, v.value
        from fsn.value v join fsn.tag t on t.id = v.tag_id
        where v.company_id = %s and v.dim_id = 0 and v.iprx = 0 and v.coreg = '' and v.value is not null
          and v.qtrs in (0, 1, 2, 3, 4) and exists (select 1 from fsn.line l where l.filing_id = v.filing_id
                                                    and l.tag_id = v.tag_id and not l.inpth)
        """,
        (company_id,),
    )
    values: dict[tuple[int, str], dict] = defaultdict(dict)
    for fid, tag, d, q, v in cur.fetchall():
        values[(fid, tag)].setdefault((d, q), v)
    data = sel.load_company(conn, company_id)
    face = {(f, d, q) for f, s, d, q in data["face_cols"] if s == "IS"}
    return Company(filings, dict(lines), dict(values), face)


def main(url: str, gaps_path: str, out: str, ciks: str = "") -> None:
    import psycopg

    want = set(ciks.split(",")) if ciks else None
    with open(gaps_path, newline="") as fi:
        keys = [r for r in csv.DictReader(fi)
                    if r["data_point"] in IS_CONCEPTS and r["grain"] in QTRS and (want is None or r["cik"] in want)]
    by_co: dict[int, list[dict[str, str]]] = defaultdict(list)
    for r in keys:
        by_co[int(r["company_id"])].append(r)
    rows, summary = [], Counter()
    with psycopg.connect(url) as conn:
        for cid, ks in sorted(by_co.items()):
            co = load(conn, cid)
            for k in ks:
                cls, detail, fid = classify(co, k["data_point"], k["grain"], date.fromisoformat(k["period_end"]))
                f = co.filings.get(fid, {}) if fid else {}
                rows.append({**k, "class": cls, "accession": f.get("accession", ""), "form": f.get("form", ""), "detail": detail})
                summary[(k["data_point"], k["grain"], cls)] += 1
    outp = Path(out)
    outp.mkdir(parents=True, exist_ok=True)
    with open(outp / "is_gap_keys_classified.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, ["cik", "company_id", "data_point", "grain", "period_end", "cause", "class", "accession", "form", "detail"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    res = [{"data_point": d, "grain": g, "class": c, "keys": n,
            "companies": len({r["cik"] for r in rows if (r["data_point"], r["grain"], r["class"]) == (d, g, c)})}
           for (d, g, c), n in sorted(summary.items(), key=lambda kv: -kv[1])]
    (outp / "is_gap_summary.json").write_text(json.dumps({"keys": len(rows), "by_class": res}, indent=1) + "\n")
    for b in res:
        print(b)


if __name__ == "__main__":
    main(*sys.argv[1:5])

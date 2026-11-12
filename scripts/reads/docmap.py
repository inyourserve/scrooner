"""Document-first company read (founder order 2026-11-12: "read filings"), the method of
data-team/companies/reads/ABT-docmap-2026-11-12.md, automated so the read is the same for every company.

For one company:
  1. data.sec.gov submissions -> the latest 10-K (and one 10-K per tag-change era, step 5);
  2. the filing's FilingSummary.xml -> its statement R pages (the rendered filing) and the cover page;
  3. every printed face line: label, the element it is tagged with (the R page's element reference = the tag FSN
     stores), the printed values of the fiscal-year columns, scaled by the page's own "$ in Millions" header;
  4. data.sec.gov companyfacts: the API value of the same tag, same accession, same period end and duration;
     printed vs API: Y / Y (sign differs) / N (the filing decides: printed wins) / n/a (extension tag: not in the API);
  5. the headline data points from the printed lines with the Tag Expert's standard-tag library
     (data-team/tags/library/standard-tag-library.csv): one `map` line = mapped; several distinct = conflict;
     else library `component` lines summed for DURATIONS and total_debt only (sums rule, fsn-line-to-concept.md
     sec. Q); else not_presented. Era check: a data point's tag whose annual series in the API starts inside the
     last five fiscal years means a tag change; the 10-K of the year before is read the same way.

Read-only. SEC fair access: one request at a time, at most 0.4 per second (--rate), declared User-Agent.
Outputs data-team/companies/reads/<TICKER>-docmap-<date>.{md,csv} and quirk rows for the Tag Expert.
Evidence: FILING-CHECKED for every row read from the filing's R pages; the API column is companyfacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

UA_DEFAULT = "Scrooner research admin@scrooner.com"
SEC = "https://www.sec.gov"
DATA = "https://data.sec.gov"


class Sec:
    def __init__(self, ua: str, rate: float, cache: Path):
        self.client = httpx.Client(headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}, timeout=60)
        self.gap = 1.0 / rate
        self.last = 0.0
        self.cache = cache
        self.requests = 0
        cache.mkdir(parents=True, exist_ok=True)

    def get(self, url: str) -> str:
        key = self.cache / re.sub(r"[^A-Za-z0-9._-]", "_", url.split("://", 1)[1])
        if key.exists():
            return key.read_text(errors="replace")
        for attempt in range(5):
            wait = self.gap - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()
            self.requests += 1
            r = self.client.get(url)
            if r.status_code == 200:
                key.write_text(r.text)
                return r.text
            if r.status_code in (403, 404):
                raise FileNotFoundError(f"{r.status_code} {url}")
            time.sleep(5 * (attempt + 1))
        raise RuntimeError(f"failed {url}")


# ----------------------------------------------------------------- R pages
SCALE = {"thousands": Decimal(1000), "millions": Decimal(10**6), "billions": Decimal(10**9)}
STMT_PATTERNS = [
    ("BSP", re.compile(r"(balance sheet|financial (position|condition)).*parenthetical", re.I)),
    ("BS", re.compile(r"balance sheet|financial (position|condition)|statements? of condition", re.I)),
    ("CI", re.compile(r"comprehensive (income|loss|earnings)", re.I)),
    ("EQP", re.compile(r"(equity|stockholders|shareholders|capital|partners).*parenthetical", re.I)),
    ("EQ", re.compile(r"(changes in|statements? of) .*(equity|stockholders|shareholders|capital|partners)|^.*(shareholders|stockholders).? equity", re.I)),
    ("CF", re.compile(r"cash flow", re.I)),
    ("ISP", re.compile(r"(income|operations|earnings).*parenthetical", re.I)),
    ("IS", re.compile(r"income|operations|earnings|statements? of (net )?(loss|revenue)", re.I)),
]


def stmt_of(short: str) -> str | None:
    for k, rx in STMT_PATTERNS:
        if rx.search(short):
            return k
    return None


def _date(s: str) -> date | None:
    s = s.replace("Sept.", "Sep.").strip()
    for fmt in ("%b. %d, %Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def _num(text: str) -> Decimal | None:
    t = text.replace("$", "").replace(",", "").replace("\xa0", " ").strip()
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").strip()
    if not t or not re.fullmatch(r"-?\d+(\.\d+)?", t):
        return None
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    return -v if neg else v


@dataclass
class Line:
    stmt: str
    r_page: str
    order: int
    label: str
    tag: str  # prefix:Name
    values: dict[tuple[date, int], Decimal]  # (period end, months) -> printed value scaled
    abstract: bool


@dataclass
class Page:
    stmt: str
    r_page: str
    title: str
    lines: list[Line] = field(default_factory=list)


def parse_r(html: str, stmt: str, r_page: str) -> Page:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="report")
    title = table.find("th", class_="tl").get_text(" ", strip=True) if table else ""
    money = next((v for k, v in SCALE.items() if re.search(rf"\$ in {k}", title, re.I)), Decimal(1))
    shares = next((v for k, v in SCALE.items() if re.search(rf"shares in {k}", title, re.I)), Decimal(1))
    page = Page(stmt, r_page, title)
    if table is None:
        return page
    rows = table.find_all("tr")
    # header: groups ("12 Months Ended", colspan) then dates; an instant page has dates only
    head = [r for r in rows if r.find("th", class_="th")]
    cols: list[tuple[date | None, int]] = []
    if head:
        groups = []
        first = head[0].find_all("th", class_="th")
        dates_row = head[1].find_all("th", class_="th") if len(head) > 1 else first
        for th in first:
            m = re.search(r"(\d+)\s+Months Ended", th.get_text(" ", strip=True))
            groups += [int(m.group(1)) if m else 0] * int(th.get("colspan", 1))
        for i, th in enumerate(dates_row):
            months = groups[i] if i < len(groups) and len(head) > 1 else 0
            cols.append((_date(th.get_text(" ", strip=True)), months))
    order = 0
    for tr in rows:
        if "rh" in (tr.get("class") or []):
            break  # a dimensional section starts (legal entity, product, segment member): not the face
        a = tr.find("a", onclick=True)
        if not a:
            continue
        m = re.search(r"defref_([A-Za-z0-9-]+)_(\w+)", a["onclick"])
        if not m:
            continue
        prefix, name = m.group(1), m.group(2)
        label = a.get_text(" ", strip=True)
        # value cells only: footnote-marker (th) and footnote (fn) cells sit between them on some pages (AFL)
        cells = [td for td in tr.find_all("td") if set(td.get("class") or []) & {"nump", "num", "text"}]
        per_share = "PerShare" in name or "PerUnit" in name or re.search(r"\(in [^)]*per (share|unit)\)", label, re.I)
        is_shares = not per_share and (
            re.search(r"Shares|NumberOf|Units(Issued|Outstanding)|UnitsAuthorized", name) or re.search(r"\((shares|units)\)", label, re.I)
        ) and not re.search(r"Value|Amount|Cost", name)
        scale = Decimal(1) if per_share else (shares if is_shares else money)
        vals: dict[tuple[date, int], Decimal] = {}
        for i, td in enumerate(cells[: len(cols)]):
            v = _num(td.get_text(" ", strip=True))
            if v is not None and cols[i][0] is not None:
                vals.setdefault(cols[i], v * scale)
        order += 1
        page.lines.append(
            Line(stmt, r_page, order, label, f"{prefix}:{name}", vals,
                 abstract=name.endswith("Abstract") or bool(re.search(r"(Axis|Domain|Member|Table|LineItems)$", name)))
        )
    return page


# ----------------------------------------------------------------- filing
@dataclass
class Filing:
    cik: str
    accession: str
    report_date: date
    form: str
    pages: list[Page]
    cover: Page | None


def statements(sec: Sec, cik: str, acc: str) -> tuple[list[tuple[str, str, str]], str | None]:
    base = f"{SEC}/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}"
    xml = sec.get(f"{base}/FilingSummary.xml")
    out, cover, seen = [], None, set()
    for m in re.finditer(r"<Report instance[^>]*>(.*?)</Report>", xml, re.S):
        b = m.group(1)
        g = lambda t: (re.search(f"<{t}>(.*?)</{t}>", b, re.S) or [None, ""])[1].strip()  # noqa: E731
        cat, short, fn = g("MenuCategory"), g("ShortName"), g("HtmlFileName")
        if cat == "Cover" and cover is None:
            cover = fn
        if cat != "Statements" or not fn:
            continue
        st = stmt_of(short)
        if st and st not in seen:  # the first statement of each kind: the parent registrant's
            seen.add(st)
            out.append((st, fn, short))
    return [(st, f"{base}/{fn}", fn) for st, fn, _ in out], (f"{base}/{cover}" if cover else None)


def read_filing(sec: Sec, cik: str, acc: str, report_date: date, form: str) -> Filing:
    pages_meta, cover_url = statements(sec, cik, acc)
    pages = [parse_r(sec.get(url), st, fn) for st, url, fn in pages_meta]
    cover = parse_r(sec.get(cover_url), "COVER", cover_url.rsplit("/", 1)[1]) if cover_url else None
    return Filing(cik, acc, report_date, form, pages, cover)


# ----------------------------------------------------------------- API
def api_value(facts: dict, tag: str, accession: str, end: date, months: int) -> Decimal | None:
    prefix, name = tag.split(":", 1)
    node = facts.get("facts", {}).get(prefix, {}).get(name)
    if not node:
        return None
    for unit, rows in node.get("units", {}).items():
        for r in rows:
            if r.get("accn") != accession or r.get("end") != end.isoformat():
                continue
            if months:
                if not r.get("start"):
                    continue
                days = (end - date.fromisoformat(r["start"])).days
                if abs(days - months * 30.4) > 20:
                    continue
            elif r.get("start"):
                continue
            return Decimal(str(r["val"]))
    return None


def compare(printed: Decimal | None, api: Decimal | None, extension: bool) -> str:
    if printed is None and api is None:
        return ""
    if extension:
        return "n/a (extension tag: not in companyfacts)"
    if api is None:
        return "N (no API value for this accession/period)"
    if printed is None:
        return "N (not printed in this column)"
    tol = Decimal("0.005") if abs(printed) < 1000 and printed != printed.to_integral_value() else Decimal("0.5")
    if abs(printed - api) <= tol:
        return "Y"
    if abs(printed + api) <= tol:
        return "Y (sign differs: printed in parentheses/negated label)"
    return "N"


# ----------------------------------------------------------------- data points
HEADLINE = [
    ("revenue", "revenue_sanity_resolved", "IS", True),
    ("cost_of_revenue", "cost_of_revenue_resolved", "IS", True),
    ("gross_profit", "gross_profit_resolved", "IS", True),
    ("operating_income", "operating_income_resolved", "IS", True),
    ("interest_expense", "interest_expense_resolved", "IS", True),
    ("income_before_tax", "income_before_tax_resolved", "IS", True),
    ("income_tax_expense", "income_tax_expense_resolved", "IS", True),
    ("net_income", "net_income_resolved", "IS", True),
    ("basic_eps", "basic_eps_resolved", "IS", True),
    ("diluted_eps", "diluted_eps_resolved", "IS", True),
    ("dividends_per_share", "dividends_per_share_resolved", "IS|EQ|EQP|ISP", True),
    ("cash_and_equivalents", "cash_and_equivalents_resolved", "BS", False),
    ("current_assets", "current_assets_resolved", "BS", False),
    ("total_assets", "total_assets_resolved", "BS", False),
    ("current_liabilities", "current_liabilities_resolved", "BS", False),
    ("total_liabilities", "total_liabilities_resolved", "BS", False),
    ("total_debt", "total_debt_resolved", "BS", False),
    ("stockholders_equity", "stockholders_equity_resolved", "BS", False),
    ("shares_outstanding", "shares_outstanding_resolved", "BS|BSP|EQ", False),
    ("cfo", "cfo_resolved", "CF", True),
    ("capex", "capex_resolved", "CF", True),
    ("depreciation_and_amortization", "depreciation_and_amortization_resolved", "CF", True),
    ("share_buybacks", "share_buybacks_resolved", "CF", True),
    ("dividends_paid", "dividends_paid_resolved", "CF", True),
]
LIB_STMT = {"BSP": "BS", "EQP": "EQ", "ISP": "IS"}
COMBINED_LABEL = {
    "share_buybacks_resolved": re.compile(r"excise|withh?olding", re.I),
    "depreciation_and_amortization_resolved": re.compile(r"impairment|accretion|nuclear fuel", re.I),
    "cash_and_equivalents_resolved": re.compile(r"restricted", re.I),
}
BEFORE_TAX = re.compile(r"\bbefore\b.{0,45}?\btax|pre-?tax", re.I)


def load_library(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with path.open(newline="") as fh:
        return {(r["stmt"], r["tag"]): r for r in csv.DictReader(fh) if r.get("decision")}


def fy_cols(f: Filing, duration: bool) -> tuple[tuple[date, int] | None, tuple[date, int] | None]:
    keys = sorted({k for p in f.pages for ln in p.lines for k in ln.values}, key=lambda k: k[0], reverse=True)
    want = [k for k in keys if (k[1] == 12 if duration else k[1] == 0)]
    fy0 = next((k for k in want if abs((k[0] - f.report_date).days) <= 7), want[0] if want else None)
    fy1 = next((k for k in want if fy0 and 330 <= (fy0[0] - k[0]).days <= 400), None)
    return fy0, fy1


def data_points(f: Filing, facts: dict, lib: dict) -> list[dict[str, Any]]:
    out = []
    lines = [ln for p in f.pages for ln in p.lines if not ln.abstract]
    for dp, concept, stmts, duration in HEADLINE:
        fy0, fy1 = fy_cols(f, duration)
        cand = [ln for ln in lines if ln.stmt in stmts.split("|")]
        maps, comps = [], []
        for ln in cand:
            row = lib.get((LIB_STMT.get(ln.stmt, ln.stmt), ln.tag.split(":", 1)[1]))
            if not row:
                continue
            guard = COMBINED_LABEL.get(concept)
            if guard and guard.search(ln.label):
                continue
            if row["decision"] == "map" and row["concept"] == concept:
                maps.append(ln)
            elif row["decision"] == "component" and row["parent_concept"] == concept:
                comps.append(ln)
        how, note = "", ""
        if not maps and dp == "income_before_tax":  # by position: the line above the tax line, before-tax label
            seq = [ln for ln in lines if ln.stmt == "IS"]
            for i, ln in enumerate(seq[1:], 1):
                if ln.tag.endswith(":IncomeTaxExpenseBenefit") and BEFORE_TAX.search(seq[i - 1].label):
                    maps, how = [seq[i - 1]], "by position above the tax line"
                    break
        if not maps and dp == "shares_outstanding" and f.cover:
            cov = [ln for ln in f.cover.lines if ln.tag == "dei:EntityCommonStockSharesOutstanding" and ln.values]
            if len(cov) == 1:
                k, v = next(iter(cov[0].values.items()))
                out.append(_row(dp, "mapped", [cov[0]], "COVER", v, api_value(facts, cov[0].tag, f.accession, k[0], 0),
                                None, None, f, k, None, "cover share count (balance sheet prints none)"))
                continue
        distinct = {ln.tag for ln in maps}
        if concept == "stockholders_equity_resolved" and len(distinct) > 1:
            # Tag Expert 2026-11-11: equity including NCI is equity only when no parent line is printed
            parent = [x for x in maps if not x.tag.endswith("IncludingPortionAttributableToNoncontrollingInterest")]
            if parent:
                maps, distinct = parent, {x.tag for x in parent}
        same_note = ""
        if len(distinct) > 1 and fy0:
            v0 = {x.values.get(fy0) for x in maps}
            if len(v0) == 1 and None not in v0:  # the same printed figure on two statements: one fact
                same_note = "same value printed as " + " and ".join(sorted(distinct))
                distinct = {maps[0].tag}
        if len(distinct) == 1:
            ln = maps[0]
            how = "; ".join(x for x in (how, same_note) if x)
            p0, p1 = ln.values.get(fy0) if fy0 else None, ln.values.get(fy1) if fy1 else None
            a0 = api_value(facts, ln.tag, f.accession, fy0[0], fy0[1]) if fy0 else None
            a1 = api_value(facts, ln.tag, f.accession, fy1[0], fy1[1]) if fy1 else None
            out.append(_row(dp, "mapped", [ln], ln.stmt, p0, a0, p1, a1, f, fy0, fy1, how or note))
        elif len(distinct) > 1:
            out.append(_row(dp, "conflict", maps, "/".join(sorted({x.stmt for x in maps})), None, None, None, None, f,
                            fy0, fy1, "several library map lines: " + "; ".join(f"{x.label} ({x.tag})" for x in maps)))
        elif comps and (duration or concept == "total_debt_resolved"):
            def tot(k, api=False):
                vals = [api_value(facts, x.tag, f.accession, k[0], k[1]) if api else x.values.get(k) for x in comps] if k else []
                return sum((v for v in vals if v is not None), Decimal(0)) if vals and any(v is not None for v in vals) else None
            out.append(_row(dp, "component sum", comps, comps[0].stmt, tot(fy0), tot(fy0, True), tot(fy1), tot(fy1, True),
                            f, fy0, fy1, "printed lines summed: " + " + ".join(x.label for x in comps)))
        else:
            why = "no printed line" + ("; instant: components never summed" if comps else "")
            out.append(_row(dp, "not_presented", [], stmts.split("|")[0], None, None, None, None, f, fy0, fy1, why))
    return out


def _row(dp, status, lns, stmt, p0, a0, p1, a1, f, fy0, fy1, note):
    ext = any(not ln.tag.startswith(("us-gaap:", "dei:", "srt:", "ifrs-full:")) for ln in lns)
    m0 = compare(p0, a0, ext)
    m1 = compare(p1, a1, ext)
    match = m0 if not m1 or m0.startswith("N") else (m1 if m1.startswith("N") else m0)
    return {
        "data_point": dp, "status": status, "tags": "+".join(sorted({ln.tag for ln in lns})), "stmt": stmt,
        "r_page": "+".join(sorted({ln.r_page for ln in lns})), "label": " + ".join(ln.label for ln in lns)[:160],
        "fy0_printed": p0, "fy0_api": a0, "fy1_printed": p1, "fy1_api": a1, "match": match,
        "evidence_class": "FILING-CHECKED",
        "note": (note + " | " if note else "") + f"accn {f.accession} FY0 {fy0[0] if fy0 else ''} FY1 {fy1[0] if fy1 else ''}",
    }


def face_lines(f: Filing, facts: dict) -> list[dict[str, Any]]:
    rows = []
    for p in f.pages:
        dur = p.stmt in ("IS", "CI", "CF", "EQ", "ISP", "EQP")
        fy0, fy1 = fy_cols(f, dur)
        for ln in p.lines:
            if ln.abstract or not ln.values:
                continue
            ext = not ln.tag.startswith(("us-gaap:", "dei:", "srt:", "ifrs-full:"))
            k0 = fy0 if fy0 in ln.values else next(iter(ln.values))
            p0 = ln.values.get(k0)
            a0 = None if ext else api_value(facts, ln.tag, f.accession, k0[0], k0[1])
            rows.append({"stmt": p.stmt, "r_page": p.r_page, "order": ln.order, "label": ln.label[:120], "tag": ln.tag,
                         "period_end": k0[0], "months": k0[1], "printed": p0, "api": a0, "match": compare(p0, a0, ext)})
    return rows


# ----------------------------------------------------------------- eras
def tag_eras(facts: dict, dps: list[dict], fy0_end: date) -> list[tuple[str, str, int]]:
    """(data point, tag, first annual fiscal year in the API) for mapped tags that start inside the last 5 FY"""
    out = []
    for r in dps:
        if r["status"] != "mapped" or "+" in r["tags"] or not r["tags"]:
            continue
        prefix, name = r["tags"].split(":", 1)
        node = facts.get("facts", {}).get(prefix, {}).get(name, {})
        ends = sorted({x["end"] for rows in node.get("units", {}).values() for x in rows if x.get("form") == "10-K"})
        if not ends:
            continue
        first = date.fromisoformat(ends[0])
        if first.year > fy0_end.year - 4:
            out.append((r["data_point"], r["tags"], first.year))
    return out


# ----------------------------------------------------------------- run one company
def read_company(sec: Sec, cik: str, ticker: str, lib: dict, out_dir: Path, day: str) -> dict[str, Any]:
    cik = cik.zfill(10)
    sub = json.loads(sec.get(f"{DATA}/submissions/CIK{cik}.json"))
    rec = sub["filings"]["recent"]
    tenks = [(rec["accessionNumber"][i], date.fromisoformat(rec["reportDate"][i]), rec["form"][i])
             for i, fm in enumerate(rec["form"]) if fm in ("10-K", "10-K/A", "10-KT") and rec["reportDate"][i]]
    tenks = [t for t in tenks if t[2] != "10-K/A"] or tenks
    if not tenks:
        raise RuntimeError("no 10-K in recent submissions")
    facts = json.loads(sec.get(f"{DATA}/api/xbrl/companyfacts/CIK{cik}.json"))
    latest = read_filing(sec, cik, *tenks[0])
    dps = data_points(latest, facts, lib)
    faces = face_lines(latest, facts)
    eras = tag_eras(facts, dps, latest.report_date)
    era_reads = []
    for year in sorted({y - 1 for _, _, y in eras}, reverse=True)[:2]:
        older = next((t for t in tenks if t[1].year == year), None)
        if older:
            f2 = read_filing(sec, cik, *older)
            era_reads.append((year, f2, data_points(f2, facts, lib)))
    write_outputs(out_dir, day, ticker, cik, sub.get("name", ""), latest, dps, faces, eras, era_reads)
    quirks = []
    for r in dps:
        if r["match"].startswith("N") and not r["match"].startswith("N (not printed"):
            quirks.append((ticker, r["tags"], f"printed {r['fy0_printed']} vs companyfacts {r['fy0_api']} for {r['data_point']}"
                                              f" ({r['match']}); the filing decides", latest.accession, r["r_page"]))
        if r["status"] == "mapped" and any(not t.startswith(("us-gaap:", "dei:")) for t in r["tags"].split("+")):
            quirks.append((ticker, r["tags"], f"{r['data_point']} printed under an extension tag ('{r['label']}')",
                           latest.accession, r["r_page"]))
        if r["status"] == "conflict":
            quirks.append((ticker, r["tags"], f"{r['data_point']}: several lines the library maps to one concept: {r['note'].split(' | ')[0]}",
                           latest.accession, r["stmt"]))
    for r in dps:
        p0, p1 = r.get("fy0_printed"), r.get("fy1_printed")
        if p0 and p1 and r["status"] == "mapped" and (abs(p0 / p1) > 300 or abs(p1 / p0) > 300):
            quirks.append((ticker, r["tags"], f"{r['data_point']}: scale break between columns of the same filing "
                                              f"(FY0 {_fmt(p0)} vs FY1 {_fmt(p1)}); printed and API agree, one column is off by ~1000x",
                           latest.accession, r["r_page"]))
            r["note"] = "SCALE BREAK between FY0 and FY1 | " + r["note"]
    for dp, tag, y in eras:
        quirks.append((ticker, tag, f"{dp}: annual series under this tag starts FY{y} (tag change era; FY{y - 1} 10-K read)",
                       latest.accession, ""))
    return {"ticker": ticker, "data_points": len(dps), "face_lines": len(faces),
            "mismatches": sum(1 for r in dps + [x for _, _, d in era_reads for x in d] if r["match"].startswith("N") and not r["match"].startswith("N (not printed")),
            "face_mismatches": sum(1 for r in faces if r["match"] == "N"),
            "eras": len(era_reads), "quirks": quirks,
            "library_corrections": sum(1 for r in dps if r["status"] == "conflict")}


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, Decimal):
        return format(v.normalize(), "f")
    return str(v)


COLS = ["ticker", "data_point", "status", "tags", "stmt", "r_page", "label", "fy0_printed", "fy0_api", "fy1_printed",
        "fy1_api", "match", "era_from_note", "evidence_class", "note"]


def write_outputs(out_dir, day, ticker, cik, name, f, dps, faces, eras, era_reads):
    out_dir.mkdir(parents=True, exist_ok=True)
    era_note = {dp: f"tag starts FY{y} in companyfacts" for dp, _, y in eras}
    with (out_dir / f"{ticker}-docmap-{day}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in dps:
            w.writerow({"ticker": ticker, **{k: _fmt(r.get(k)) for k in COLS if k in r},
                        "era_from_note": era_note.get(r["data_point"], "tag covers last 5 FY in companyfacts")})
        for year, f2, d2 in era_reads:
            for r in d2:
                w.writerow({"ticker": ticker, **{k: _fmt(r.get(k)) for k in COLS if k in r}, "data_point": f"{r['data_point']}@FY{year}",
                            "era_from_note": f"era read: {f2.accession}"})
        for r in faces:
            w.writerow({"ticker": ticker, "data_point": f"face:{r['stmt']}:{r['r_page']}:{r['order']}", "status": "face_line",
                        "tags": r["tag"], "stmt": r["stmt"], "r_page": r["r_page"], "label": r["label"],
                        "fy0_printed": _fmt(r["printed"]), "fy0_api": _fmt(r["api"]), "match": r["match"],
                        "evidence_class": "FILING-CHECKED", "note": f"period end {r['period_end']} months {r['months']}"})
    md = [f"# {ticker} document-first map {day} (read-only, generated by scripts/reads/docmap.py)", "",
          "Evidence: FILING-CHECKED (the filing's own R pages; tags from the R pages' element references; API = SEC "
          "companyfacts, undimensioned, same accession, same period). Printed values are scaled by each page's header.", "",
          "## Filings opened",
          f"- Latest 10-K {f.accession} ({name}, CIK {cik}, period {f.report_date}): "
          + ", ".join(f"{p.stmt} {p.r_page}" for p in f.pages) + (f", cover {f.cover.r_page}" if f.cover else "")]
    for year, f2, _ in era_reads:
        md.append(f"- Era 10-K {f2.accession} (period {f2.report_date}): " + ", ".join(f"{p.stmt} {p.r_page}" for p in f2.pages))
    md.append("- companyfacts CIK{}.json".format(cik))
    md += ["", "## Data points", "| data point | status | tag(s) | stmt R | printed label | FY0 printed | FY0 API | FY1 printed | FY1 API | match | note |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in dps:
        md.append("| " + " | ".join(_fmt(r.get(k)).replace("|", "/") for k in
                  ("data_point", "status", "tags", "r_page", "label", "fy0_printed", "fy0_api", "fy1_printed", "fy1_api", "match", "note")) + " |")
    md += ["", "## Era checks (tag changes in the last 5 fiscal years)"]
    md += [f"- {dp}: {tag} starts FY{y} in companyfacts; FY{y - 1} 10-K read" for dp, tag, y in eras] or ["- none"]
    for year, f2, d2 in era_reads:
        md.append(f"- FY{year} ({f2.accession}): " + "; ".join(f"{r['data_point']} {r['status']} {r['tags']} {r['match']}" for r in d2 if r["status"] != "not_presented"))
    mism = [r for r in faces if r["match"] == "N"]
    md += ["", f"## Face lines: {len(faces)} printed lines matched to their tag and the API (full list in the CSV)",
           f"- printed = API: {sum(1 for r in faces if r['match'].startswith('Y'))}; extension tags (no API): "
           f"{sum(1 for r in faces if r['match'].startswith('n/a'))}; no API value: {sum(1 for r in faces if r['match'].startswith('N ('))}; mismatches: {len(mism)}"]
    md += [f"  - {r['stmt']} {r['r_page']} '{r['label']}' {r['tag']}: printed {_fmt(r['printed'])} vs API {_fmt(r['api'])} (the filing decides)" for r in mism]
    (out_dir / f"{ticker}-docmap-{day}.md").write_text("\n".join(md) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", default="data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv")
    ap.add_argument("--ranks", default="201-300")
    ap.add_argument("--library", default="data-team/tags/library/standard-tag-library.csv")
    ap.add_argument("--out", default="data-team/companies/reads")
    ap.add_argument("--inbox", default="data-team/tags/feedback-inbox-201-300.md")
    ap.add_argument("--day", default=date.today().isoformat())
    ap.add_argument("--ua", default=UA_DEFAULT)
    ap.add_argument("--rate", type=float, default=0.4)
    ap.add_argument("--cache", default=".cache/sec-reads")
    ap.add_argument("--progress", default="")
    a = ap.parse_args(argv)
    lo, hi = (int(x) for x in a.ranks.split("-"))
    rows = list(csv.DictReader(open(a.cohort)))[lo - 1: hi]
    lib = load_library(Path(a.library))
    sec = Sec(a.ua, a.rate, Path(a.cache))
    prog = Path(a.progress) if a.progress else None
    done = json.loads(prog.read_text()) if prog and prog.exists() else {}
    for i, r in enumerate(rows, lo):
        t = r["ticker"].replace(".", "-")
        if t in done:
            continue
        try:
            res = read_company(sec, r["cik"], t, lib, Path(a.out), a.day)
            res["rank"] = i
        except Exception as e:  # noqa: BLE001  one company must not stop the range
            res = {"ticker": t, "rank": i, "error": repr(e)[:300], "quirks": []}
        quirks = res.pop("quirks", [])
        if quirks:
            new = not Path(a.inbox).exists()
            with open(a.inbox, "a") as fh:
                if new:
                    fh.write("# Tag feedback inbox, ranks 201-300 (document-first reads 2026-11-12)\n\n"
                             "| date | from | company | tag | what was learned | evidence | class | status |\n|---|---|---|---|---|---|---|---|\n")
                for tk, tag, what, acc, rp in quirks:
                    fh.write(f"| {a.day} | reads 201-300 (docmap.py) | {tk} | {tag} | {what} | {acc} {rp} | FILING-CHECKED | new |\n")
        done[t] = res
        if prog:
            prog.write_text(json.dumps(done, indent=1, default=str))
        print(json.dumps({k: v for k, v in res.items()}, default=str), flush=True)
    print(f"sec requests: {sec.requests}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

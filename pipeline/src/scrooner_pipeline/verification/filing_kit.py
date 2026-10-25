"""Shared Verifier kit: read a filing's R pages, derive face liabilities,
sample a manifest by seed, write a verdict skeleton.

Pure functions plus one thin fetch helper. Network access goes through an
injected client with ``get(url) -> bytes`` (the slot-records ``SecClient``:
sec.gov only, SEC_USER_AGENT, <= 4 requests/second). No database, no writes
other than the verdict file the caller asks for.
"""

from __future__ import annotations

import html
import random
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable, Protocol

_MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
_DATE_RX = re.compile(rf"^({_MONTHS})[a-z]*\.?\s+(\d{{1,2}}),\s+(\d{{4}})$", re.I)
_SCALE = {"thousands": 1_000, "millions": 1_000_000, "billions": 1_000_000_000}

STATEMENT_PATTERNS = {
    "BS": r"balance sheet|financial position|financial condition|assets and liabilities",
    "IS": r"income|operations|earnings|loss",
    "CF": r"cash flow",
}
_EXCLUDED_NAMES = re.compile(r"parenthetical|details|tables?\b|policies|comprehensive", re.I)


class Client(Protocol):
    def get(self, url: str) -> bytes: ...


@dataclass
class Row:
    label: str
    values: list[Decimal | None]


@dataclass
class RPage:
    title: str
    multiplier: int  # printed unit: 1, 1_000, 1_000_000 ...
    columns: list[date]
    rows: list[Row] = field(default_factory=list)

    def column(self, when: date) -> int:
        if when not in self.columns:
            raise KeyError(f"{when} not among columns {self.columns}")
        return self.columns.index(when)

    def find(self, rx: str, exclude: str | None = None) -> list[Row]:
        pat = re.compile(rx, re.I)
        bad = re.compile(exclude, re.I) if exclude else None
        return [r for r in self.rows if pat.search(r.label) and not (bad and bad.search(r.label))]


def _clean(cell: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", cell))).strip()


def parse_number(text: str) -> Decimal | None:
    """'$ 1,234' -> 1234; '(1,234)' -> -1234; blank/dash -> None."""
    t = text.replace("$", "").replace(",", "").replace("—", "").replace("–", "").strip()
    t = re.sub(r"\[\d+\]", "", t).strip()  # footnote markers
    if not t or t == "-":
        return None
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").strip()
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    return -v if neg else v


def parse_date(text: str) -> date | None:
    m = _DATE_RX.match(text.strip())
    if not m:
        return None
    mon = m.group(1)[:3].title()
    return datetime.strptime(f"{mon} {m.group(2)} {m.group(3)}", "%b %d %Y").date()


def parse_rpage(page_html: str) -> RPage:
    """Parse one R page. Columns come from the last header row made of dates.
    A data row with more cells than columns (a leading blank column on old R
    pages) is aligned from the right, never from the left."""
    title, multiplier, columns = "", 1, []
    rows: list[Row] = []
    for tr in re.findall(r"<tr.*?</tr>", page_html, re.S | re.I):
        cells = [_clean(c) for c in re.findall(r"<t[dh].*?</t[dh]>", tr, re.S | re.I)]
        if not any(cells):
            continue
        if not title:
            title = cells[0]
            m = re.search(r"in (thousands|millions|billions)", " ".join(cells), re.I)
            multiplier = _SCALE[m.group(1).lower()] if m else 1
        tail = [c for c in cells[1:] if c]
        if tail and all(parse_date(c) for c in tail):
            columns = [parse_date(c) for c in tail]  # type: ignore[misc]
            continue
        if not columns or not cells[0]:
            continue  # header rows ("12 Months Ended") and spacer rows
        vals = [parse_number(c) for c in cells[1:]]
        if len(vals) > len(columns):
            vals = vals[-len(columns):]
        elif len(vals) < len(columns):
            vals += [None] * (len(columns) - len(vals))
        rows.append(Row(cells[0], vals))
    return RPage(title, multiplier, columns, rows)


def find_report_files(filing_summary_xml: str) -> dict[str, tuple[str, str]]:
    """First matching (ShortName, HtmlFileName) per statement kind BS/IS/CF."""
    reps = re.findall(
        r"<Report[^>]*>.*?<ShortName>(.*?)</ShortName>.*?<HtmlFileName>(.*?)</HtmlFileName>",
        filing_summary_xml, re.S)
    out: dict[str, tuple[str, str]] = {}
    for name, fn in reps:
        n = html.unescape(name)
        if _EXCLUDED_NAMES.search(n):
            continue
        for kind in ("BS", "CF", "IS"):  # BS/CF first so "income" never claims them
            if kind not in out and re.search(STATEMENT_PATTERNS[kind], n, re.I):
                out[kind] = (n, fn)
                break
    return out


def fetch_statements(client: Client, folder_url: str, kinds: Iterable[str] = ("BS", "IS", "CF")) -> dict[str, RPage]:
    """Fetch FilingSummary.xml then each wanted R page (1 + len(kinds) requests)."""
    fs = client.get(folder_url + "FilingSummary.xml").decode("utf8", "ignore")
    files = find_report_files(fs)
    return {k: parse_rpage(client.get(folder_url + files[k][1]).decode("utf8", "ignore"))
            for k in kinds if k in files}


# ---- face-derived liabilities -------------------------------------------------

_MEZZ = re.compile(r"redeemable|mezzanine|temporary equity|operating partnership|puttable|"
                   r"preferred (stock|units|shares).*(subject|redeem)|subject to (possible )?redemption", re.I)
_TOTAL_LIAB = re.compile(r"^total liabilities$", re.I)
_TOTAL_LE = re.compile(r"^total liabilities,? (and|&) .*(equity|deficit|capital|shareholders|stockholders)", re.I)
_TOTAL_EQ = re.compile(r"^total .*(equity|deficit|capital)$|^total (stockholders|shareholders)", re.I)


@dataclass
class FaceLiabilities:
    value: Decimal | None  # in the page's printed unit
    method: str  # printed_total | derived | unavailable
    parts: dict[str, Decimal]
    note: str = ""


def face_liabilities(page: RPage, when: date) -> FaceLiabilities:
    """Printed 'Total liabilities' if present; else total L&E - total equity
    (incl. NCI) - printed mezzanine. Never sums children. Unavailable if a
    needed printed line is missing: the caller marks the cell 'cannot derive'."""
    c = page.column(when)

    def pick(rx: re.Pattern[str]) -> list[tuple[str, Decimal]]:
        return [(r.label, r.values[c]) for r in page.rows if rx.search(r.label) and r.values[c] is not None]

    tl = pick(_TOTAL_LIAB)
    if tl:
        return FaceLiabilities(tl[0][1], "printed_total", {tl[0][0]: tl[0][1]})
    le = pick(_TOTAL_LE)
    if not le:
        return FaceLiabilities(None, "unavailable", {}, "no total L&E line")
    eq = [x for x in pick(_TOTAL_EQ) if not _TOTAL_LE.search(x[0])]
    if not eq:
        return FaceLiabilities(None, "unavailable", {}, "no total equity line")
    # prefer the NCI-inclusive total ("Total equity"); else the last total-equity line
    incl = [x for x in eq if re.fullmatch(r"total (equity|deficit|capital|\(deficit\) equity|equity \(deficit\))", x[0], re.I)]
    equity = (incl or eq)[-1]
    mezz = [(r.label, r.values[c]) for r in page.rows
            if _MEZZ.search(r.label) and r.values[c] is not None and not r.label.lower().startswith("total")
            and not re.search(r"\bequity\b.*attributable|total", r.label, re.I)]
    parts = {le[0][0]: le[0][1], equity[0]: equity[1], **{k: v for k, v in mezz}}
    value = le[0][1] - equity[1] - sum((v for _, v in mezz), Decimal(0))
    return FaceLiabilities(value, "derived", parts, "L&E - equity - mezzanine")


def cell_matches(shown: Decimal, face: Decimal, multiplier: int, rounding_unit: int | None = None) -> bool:
    """shown is in full units; face in the page's printed unit. Tolerance is
    half the printed rounding unit (default: one printed unit / 2)."""
    tol = Decimal(rounding_unit if rounding_unit is not None else multiplier) / 2
    return abs(shown - face * multiplier) <= tol


# ---- sampling -----------------------------------------------------------------

def seeded_sample(manifest: list[dict], seed: int, extra_per_company: int = 2) -> list[dict]:
    """manifest rows: {cik, instant (ISO), shown (bool), era (optional str)}.
    Per company: first, last, every era boundary (first row of a new era),
    every withheld (shown=False) row, plus ``extra_per_company`` seeded picks.
    Deterministic for a given (manifest, seed). Each pick gets ``why``."""
    rng = random.Random(seed)
    by: dict[str, list[dict]] = {}
    for r in sorted(manifest, key=lambda r: (str(r["cik"]), r["instant"])):
        by.setdefault(str(r["cik"]), []).append(r)
    out: list[dict] = []
    for cik in sorted(by):
        rows, why = by[cik], {}
        why[0] = "first"
        why.setdefault(len(rows) - 1, "last")
        for i in range(1, len(rows)):
            if rows[i].get("era") != rows[i - 1].get("era"):
                why.setdefault(i, "boundary")
        for i, r in enumerate(rows):
            if not r.get("shown", True):
                why.setdefault(i, "withheld")
        rest = [i for i in range(len(rows)) if i not in why]
        for i in sorted(rng.sample(rest, min(extra_per_company, len(rest)))):
            why[i] = "random"
        out += [{**rows[i], "why": why[i]} for i in sorted(why)]
    return out


# ---- verdict skeleton -----------------------------------------------------------

VERDICT_SECTIONS = ("Result", "Method", "Sample", "Cell table", "Withheld cells (avoidable holds)",
                    "False holds", "Findings for the builder", "Requests and disk", "Untested scope")


def verdict_skeleton(name: str, day: str, branch: str, commit: str, seed: int,
                     claimed: dict[str, int], files: list[str]) -> str:
    claims = ", ".join(f"{k}={v}" for k, v in claimed.items()) or "none"
    head = (f"# Verify: {name} ({branch} {commit}), {day}\n\n"
            f"Seed {seed}. Files: {', '.join(files)}. Claimed counts: {claims}. Evidence class: FILING-CHECKED.\n\n")
    body = {
        "Result": "GATE: zero wrong shown values. PASSES / FAILS: N of N shown cells right; M wrong.",
        "Method": "Face liabilities from the filing's own R page (printed total, else L&E - equity - mezzanine).",
        "Sample": "first / last / boundary eras / reading B instants / withheld; seeded picks.",
        "Cell table": "| Company (CIK) | Instant | Accession+R page | Shown | Face | Verdict |\n|---|---|---|---|---|---|",
        "Withheld cells (avoidable holds)": "List cells withheld where the face gives the value (not wrong values).",
        "False holds": "List separately: holds that were right to hold.",
        "Findings for the builder": "Specific, with accession and R page.",
        "Requests and disk": "SEC requests: N. Downloads deleted: yes/no. Free disk: X GB.",
        "Untested scope": "What this sample does not cover.",
    }
    return head + "\n".join(f"## {s}\n{body[s]}\n" for s in VERDICT_SECTIONS)

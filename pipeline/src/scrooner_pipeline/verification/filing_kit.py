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
_EXCLUDED_NAMES = re.compile(r"par[ae]nthetical|details|tables?\b|policies|(?<!and )comprehensive", re.I)


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
    t = re.sub(r"\[\d+\]", "", t)  # footnote markers
    t = re.sub(r"[A-Za-z][\w-]*_\w+$", "", t).strip()  # old pages: '2,341us-gaap_Liabilities'
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


_POPUP = re.compile(r"^(X|Namespace Prefix:|Data Type:|Balance Type:|Period Type:|Definition:?|References?:?|Details? .*)$", re.I)
_FOOT = re.compile(r"^(\[\d+\]\s*)*$")  # empty or footnote-only cell


def _cells(tr: str) -> list[tuple[str, str]]:
    """(css class, clean text) per cell."""
    out = []
    for m in re.finditer(r"<t([dh])([^>]*)>(.*?)</t\1>", tr, re.S | re.I):
        cls = re.search(r"""class=["']([^"']*)["']""", m.group(2))
        out.append((cls.group(1) if cls else "", _clean(m.group(3))))
    return out


def parse_rpage(page_html: str) -> RPage:
    """Parse one R page. Columns come from the last header row made of dates
    (footnote header cells ignored). In data rows only value cells count:
    footnote cells ('[1]', class fn) and blank spacer cells (class th) are
    dropped, then a row with more cells than columns (leading blank column on
    old pages) is aligned from the right. Hidden '- Definition' rows skipped."""
    title, multiplier, columns = "", 1, []
    rows: list[Row] = []
    for tr in re.findall(r"<tr.*?</tr>", page_html, re.S | re.I):
        cells = _cells(tr)
        if not any(t for _, t in cells):
            continue
        if not title:
            title = cells[0][1]
            m = re.search(r"in (thousands|millions|billions)", " ".join(t for _, t in cells), re.I)
            multiplier = _SCALE[m.group(1).lower()] if m else 1
        tail = [t for _, t in cells[1:] if t and not _FOOT.match(t)]
        if tail and all(parse_date(c) for c in tail):
            columns = [parse_date(c) for c in tail]  # type: ignore[misc]
            continue
        label = re.sub(r"\s*\[\d+\]", "", cells[0][1]).strip()
        if not columns or not label or label.startswith("- ") or _POPUP.match(label):
            continue  # header rows ("12 Months Ended"), spacers, popup definitions
        vals = [parse_number(t) for c, t in cells[1:] if c not in ("fn", "th") and not (t and _FOOT.match(t))]
        if len(vals) > len(columns):
            vals = vals[-len(columns):]
        elif len(vals) < len(columns):
            vals += [None] * (len(columns) - len(vals))
        rows.append(Row(label, vals))
    return RPage(title, multiplier, columns, rows)


def find_report_files(filing_summary_xml: str) -> dict[str, tuple[str, str]]:
    """First matching (ShortName, HtmlFileName) per statement kind BS/IS/CF.
    Each <Report> block is read on its own (HtmlFileName precedes ShortName)."""
    out: dict[str, tuple[str, str]] = {}
    for block in re.findall(r"<Report\b.*?</Report>", filing_summary_xml, re.S):
        sn, fn = re.search(r"<ShortName>(.*?)</ShortName>", block, re.S), re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", block, re.S)
        if not sn or not fn:
            continue
        n = html.unescape(sn.group(1))
        if _EXCLUDED_NAMES.search(n):
            continue
        for kind in ("BS", "CF", "IS"):  # BS/CF first so "income" never claims them
            if kind not in out and re.search(STATEMENT_PATTERNS[kind], n, re.I):
                out[kind] = (n, fn.group(1).strip())
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
                   r"subject to (possible )?redemption|convertible preferred (units|stock|shares)", re.I)
_NOT_MEZZ = re.compile(r"non-?redeemable|^total|attributable|long-term debt|debt", re.I)
_TOTAL_LIAB = re.compile(r"^total liabilities$", re.I)
_TOTAL_LE = re.compile(
    r"^total (capitalization and )?liabilities\b.*(\band\b|&).*(equity|deficit|capital|investment|shareholders|stockholders)"
    r"|^total capitalization and liabilities$|^liabilities and .*(equity|deficit|capital),? total$", re.I)
_BARE_TOTAL = re.compile(r"^total$", re.I)  # accepted as L&E only as the last row
_TOTAL_EQ = re.compile(
    r"^total .*(equity|deficit|capital|investment)\b|^total (stockholders|shareholders)"
    r"|(stockholders|shareholders)'? equity,? including (the )?portion attributable to non-?controlling", re.I)
_EQ_INCL = re.compile(
    r"^total (equity|deficit|capital|\(deficit\) equity|equity \(deficit\))$"
    r"|including (the )?portion attributable to non-?controlling", re.I)


@dataclass
class FaceLiabilities:
    value: Decimal | None  # in the page's printed unit
    method: str  # printed_total | derived | unavailable
    parts: dict[str, Decimal]
    note: str = ""
    combined: bool = False  # several registrant blocks; first block used


def face_liabilities(page: RPage, when: date) -> FaceLiabilities:
    """Printed 'Total liabilities' if present; else total L&E - total equity
    (incl. NCI) - mezzanine. Never sums children. Unavailable if a needed
    printed line is missing: the caller marks the cell 'cannot derive'.

    Combined filings stack one balance sheet per registrant: only rows up to
    the FIRST total-L&E line are searched. Mezzanine is by position: a
    redeemable line must sit AFTER the liabilities total/last liability
    section and BEFORE equity, never inside debt (AWK) and never 'nonredeemable'."""
    c = page.column(when)
    rows = [(i, r.label, r.values[c]) for i, r in enumerate(page.rows)]
    le_idx = [i for i, lab, v in rows if v is not None and _TOTAL_LE.search(lab)]
    if not le_idx and rows:  # bare 'Total' as the page's last printed row (IDACORP)
        last = [(i, lab, v) for i, lab, v in rows if v is not None][-1:]
        if last and _BARE_TOTAL.match(last[0][1]):
            le_idx = [last[0][0]]
    combined = len(le_idx) > 1
    end = le_idx[0] + 1 if le_idx else len(rows)
    blk = [(i, lab, v) for i, lab, v in rows[:end] if v is not None]
    tl = [x for x in blk if _TOTAL_LIAB.match(x[1])]
    if tl:
        return FaceLiabilities(tl[0][2], "printed_total", {tl[0][1]: tl[0][2]}, combined=combined)
    if not le_idx:
        return FaceLiabilities(None, "unavailable", {}, "no total L&E line")
    le = next(x for x in blk if x[0] == le_idx[0])
    eq = [x for x in blk if _TOTAL_EQ.search(x[1]) and not _TOTAL_LE.search(x[1])]
    foot = False
    if not eq:  # XEL: equity total printed on a 'Common stock' line; accept only if it foots
        eq = _common_stock_footing(blk)
        foot = bool(eq)
    if not eq:
        return FaceLiabilities(None, "unavailable", {}, "no total equity line")
    incl = [x for x in eq if _EQ_INCL.search(x[1])]
    equity = (incl or eq)[-1]
    # mezzanine: by position, before the first equity-section line, never inside debt
    eq_rows = [x[0] for x in blk if re.search(r"equity|deficit|capital|stockholders|shareholders|common stock", x[1], re.I)
               and not _MEZZ.search(x[1]) and x[0] <= equity[0]]
    first_eq = min(eq_rows, default=equity[0])
    mezz = [x for x in blk if x[0] < first_eq and _MEZZ.search(x[1]) and not _NOT_MEZZ.search(x[1])
            and not _is_inside_debt(page, x[0])]
    parts = {le[1]: le[2], equity[1]: equity[2], **{x[1]: x[2] for x in mezz}}
    value = le[2] - equity[2] - sum((x[2] for x in mezz), Decimal(0))
    return FaceLiabilities(value, "derived", parts, "L&E - equity - mezzanine" + (" (equity footed from components)" if foot else ""), combined)


def _common_stock_footing(blk: list) -> list:
    """A 'Common stock...' line whose value equals the sum of the consecutive
    rows right before it (APIC, retained earnings, AOCI ...): a printed equity total."""
    for k, x in enumerate(blk):
        if re.match(r"common stock", x[1], re.I):
            acc, n = Decimal(0), 0
            for y in reversed(blk[max(0, k - 6):k]):
                acc, n = acc + y[2], n + 1
                if n >= 2 and acc == x[2]:
                    return [x]
    return []


def _is_inside_debt(page: RPage, idx: int) -> bool:
    """True when a later 'Total ... debt' line closes a section containing row idx
    with no other 'Total' line in between (redeemable preferred inside debt)."""
    for r in page.rows[idx + 1:]:
        if re.match(r"^total\b", r.label, re.I):
            return bool(re.search(r"debt|borrowings", r.label, re.I))
    return False


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

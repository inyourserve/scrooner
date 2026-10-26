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
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Protocol

_MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
_DATE_RX = re.compile(
    rf"^({_MONTHS})[a-z]*\.?\s+(\d{{1,2}}),\s+(\d{{4}})$", re.IGNORECASE
)
_SCALE = {"thousands": 1_000, "millions": 1_000_000, "billions": 1_000_000_000}

STATEMENT_PATTERNS = {
    "BS": r"balance sheet|financial position|financial condition|assets and liabilities",
    "IS": r"income|operations|earnings|loss",
    "CF": r"cash flow",
}
_EXCLUDED_NAMES = re.compile(
    r"par[ae]nthetical|details|tables?\b|policies|(?<!and )comprehensive", re.IGNORECASE
)


class Client(Protocol):
    def get(self, url: str) -> bytes: ...


@dataclass
class Row:
    label: str
    values: list[Decimal | None]
    decimals: list[int | None] = field(
        default_factory=list
    )  # digits after the point as printed


class AmbiguousColumn(KeyError):
    """The end date appears under several duration columns; say which (months=)."""


@dataclass
class RPage:
    title: str
    multiplier: int  # printed unit: 1, 1_000, 1_000_000 ...
    columns: list[date]
    rows: list[Row] = field(default_factory=list)
    months: list[int | None] = field(
        default_factory=list
    )  # "N Months Ended" per column; None = instant

    def column(self, when: date, months: int | None = None) -> int:
        """Index of the column ending ``when``. Duration pages repeat the end date
        (3 months and 9 months both end Sep. 30): pass ``months``; without it an
        ambiguous date raises instead of silently taking the first."""
        idx = [
            i
            for i, d in enumerate(self.columns)
            if d == when
            and (months is None or (self.months[i : i + 1] or [None])[0] == months)
        ]
        if not idx:
            raise KeyError(
                f"{when} (months={months}) not among columns {list(zip(self.columns, self.months))}"
            )
        if len(idx) > 1:
            raise AmbiguousColumn(
                f"{when} is ambiguous; pass months= one of {[self.months[i] for i in idx]}"
            )
        return idx[0]

    def printed_unit(self, row: Row, col: int) -> Decimal:
        """Rounding unit of a printed cell: scale x 10^-decimals, from the printed
        text (never from trailing zeros of the value)."""
        d = row.decimals[col] if col < len(row.decimals) else None
        return Decimal(self.multiplier).scaleb(-(d or 0))

    def find(self, rx: str, exclude: str | None = None) -> list[Row]:
        pat = re.compile(rx, re.IGNORECASE)
        bad = re.compile(exclude, re.IGNORECASE) if exclude else None
        return [
            r
            for r in self.rows
            if pat.search(r.label) and not (bad and bad.search(r.label))
        ]


def _clean(cell: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", cell))).strip()


def parse_number(text: str) -> Decimal | None:
    """'$ 1,234' -> 1234; '(1,234)' -> -1234; blank/dash -> None."""
    t = text.replace("$", "").replace(",", "").replace("—", "").replace("–", "").strip()
    t = re.sub(r"\[\d+\]", "", t)  # footnote markers
    t = re.sub(
        r"[A-Za-z][\w-]*_\w+$", "", t
    ).strip()  # old pages: '2,341us-gaap_Liabilities'
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


_POPUP = re.compile(
    r"^(X|Namespace Prefix:|Data Type:|Balance Type:|Period Type:|Definition:?|References?:?|Details? .*)$",
    re.IGNORECASE,
)
_FOOT = re.compile(r"^(\[\d+\]\s*)*$")  # empty or footnote-only cell


def _cells(tr: str) -> list[tuple[str, str]]:
    """(css class, clean text) per cell."""
    return [(c, t) for c, t, _ in _cells3(tr)]


def _cells3(tr: str) -> list[tuple[str, str, int]]:
    """(css class, clean text, colspan) per cell."""
    out = []
    for m in re.finditer(r"<t([dh])([^>]*)>(.*?)</t\1>", tr, re.DOTALL | re.IGNORECASE):
        cls = re.search(r"""class=["']([^"']*)["']""", m.group(2))
        span = re.search(r"""colspan=["']?(\d+)""", m.group(2))
        out.append(
            (
                cls.group(1) if cls else "",
                _clean(m.group(3)),
                int(span.group(1)) if span else 1,
            )
        )
    return out


_UNIT_PHRASE = re.compile(r"(\$|[A-Za-z]+)?\s*\bin (thousands|millions|billions)", re.IGNORECASE)
_NON_MONEY = {"shares", "share", "units", "unit", "options", "warrants"}


def money_multiplier(header: str) -> int:
    """Scale of the MONEY figures from the header phrase: '$ in Millions' or a bare
    'In Thousands' (old pages). 'shares in Millions' / 'units in Thousands' scale
    share counts, never money; 'USD ($)' alone means whole dollars (ABNB)."""
    for m in _UNIT_PHRASE.finditer(header):
        if (m.group(1) or "").lower() in _NON_MONEY:
            continue
        return _SCALE[m.group(2).lower()]
    return 1


def _decimals(text: str) -> int | None:
    t = re.sub(r"\[\d+\]|[A-Za-z][\w-]*_\w+$", "", text)
    if parse_number(t) is None:
        return None
    m = re.search(r"\.(\d+)", t)
    return len(m.group(1)) if m else 0


_DURATION_HDR = re.compile(r"^(\d+) Months? Ended$", re.IGNORECASE)


def parse_rpage(page_html: str) -> RPage:
    """Parse one R page. Columns come from the last header row made of dates
    (footnote header cells ignored). In data rows only value cells count:
    footnote cells ('[1]', class fn) and blank spacer cells (class th) are
    dropped, then a row with more cells than columns (leading blank column on
    old pages) is aligned from the right. Hidden '- Definition' rows skipped."""
    title, multiplier, columns = "", 1, []
    spans: list[int] = []
    rows: list[Row] = []
    for tr in re.findall(r"<tr.*?</tr>", page_html, re.DOTALL | re.IGNORECASE):
        cells3 = _cells3(tr)
        cells = [(c, t) for c, t, _ in cells3]
        if not any(t for _, t in cells):
            continue
        title_row = not title
        if title_row:
            title = cells[0][1]
            multiplier = money_multiplier(" ".join(t for _, t in cells))
        if not rows:
            for c, t, sp in cells3:
                d = _DURATION_HDR.match(t)
                if d:
                    spans += [int(d.group(1))] * sp
        # the second header row of a two-row header has NO title cell (rowspan=2),
        # so its first cell is already a date: keep it
        first_is_title = title_row or cells[0][0] == "tl"
        tail = [
            t
            for _, t in (cells[1:] if first_is_title else cells)
            if t and not _FOOT.match(t)
        ]
        if not rows and tail and all(parse_date(c) for c in tail):
            columns = [parse_date(c) for c in tail]  # type: ignore[misc]
            continue
        label = re.sub(r"\s*\[\d+\]", "", cells[0][1]).strip()
        if not columns or not label or label.startswith("- ") or _POPUP.match(label):
            continue  # header rows ("12 Months Ended"), spacers, popup definitions
        texts = [
            t
            for c, t in cells[1:]
            if c not in ("fn", "th") and not (t and _FOOT.match(t))
        ]
        vals = [parse_number(t) for t in texts]
        decs = [_decimals(t) for t in texts]
        if len(vals) > len(columns):
            vals, decs = vals[-len(columns) :], decs[-len(columns) :]
        elif len(vals) < len(columns):
            pad = len(columns) - len(vals)
            vals, decs = vals + [None] * pad, decs + [None] * pad
        rows.append(Row(label, vals, decs))
    months: list[int | None] = (
        list(spans) if len(spans) == len(columns) else [None] * len(columns)
    )
    return RPage(title, multiplier, columns, rows, months)  # type: ignore[arg-type]


_IS_NAME = re.compile(r"income|operations|earnings|loss|profit", re.IGNORECASE)
_IS_NOT = re.compile(
    r"details|tables?\b|policies|taxes|segment|discontinued|"
    r"stockholders|shareholders|equity|cash flow|balance sheet|financial position",
    re.IGNORECASE,
)


def _reports(filing_summary_xml: str) -> list[tuple[str, str, str]]:
    """(ShortName, HtmlFileName, MenuCategory) per <Report> block."""
    out = []
    for block in re.findall(r"<Report\b.*?</Report>", filing_summary_xml, re.DOTALL):
        sn = re.search(r"<ShortName>(.*?)</ShortName>", block, re.DOTALL)
        fn = re.search(r"<HtmlFileName>(.*?)</HtmlFileName>", block, re.DOTALL)
        mc = re.search(r"<MenuCategory>(.*?)</MenuCategory>", block, re.DOTALL)
        if sn and fn:
            out.append(
                (
                    html.unescape(sn.group(1)),
                    fn.group(1).strip(),
                    mc.group(1).strip() if mc else "",
                )
            )
    return out


def select_income_statement(filing_summary_xml: str) -> tuple[str, str, bool] | None:
    """(ShortName, file, combined) of the real income statement, or None.
    Only 'Statements' menu pages when the summary has categories (never notes such
    as 'Income Taxes' or 'Net Income Per Share'); parenthetical and per-share pages
    excluded. Rank: pure income/operations statement, then combined 'Operations and
    Comprehensive Income', then a comprehensive-income page (combined=True: its first
    block is net income, the filer has no separate statement, e.g. VRSN)."""
    reps = _reports(filing_summary_xml)
    if any(mc == "Statements" for _, _, mc in reps):
        reps = [r for r in reps if r[2] == "Statements"]
    best: tuple[int, int, tuple[str, str, bool]] | None = None
    categorised = any(mc == "Statements" for _, _, mc in _reports(filing_summary_xml))
    for pos, (n, fn, _) in enumerate(reps):
        if (
            re.search(r"par[ae]nthetical", n, re.IGNORECASE)
            or not _IS_NAME.search(n)
            or _IS_NOT.search(n)
        ):
            continue
        if not categorised and not re.search(r"statements?\b", n, re.IGNORECASE):
            continue  # no menu categories: a name must say 'statement(s)', never a note title
        if re.search(r"comprehensive", n, re.IGNORECASE):
            combined = bool(
                re.search(
                    r"(income|operations|earnings|loss)\s*(\(loss\)\s*)?and\s+comprehensive",
                    n,
                    re.IGNORECASE,
                )
            )
            rank = 1 if combined else 2
        else:
            combined, rank = False, 0
        if best is None or (rank, pos) < best[:2]:
            best = (rank, pos, (n, fn, rank > 0))
    return best[2] if best else None


def find_report_files(filing_summary_xml: str) -> dict[str, tuple[str, str]]:
    """First matching (ShortName, HtmlFileName) per statement kind BS/IS/CF.
    Each <Report> block is read on its own (HtmlFileName precedes ShortName).
    IS uses :func:`select_income_statement`."""
    out: dict[str, tuple[str, str]] = {}
    for n, fn, _ in _reports(filing_summary_xml):
        if _EXCLUDED_NAMES.search(n):
            continue
        for kind in ("BS", "CF"):
            if kind not in out and re.search(
                STATEMENT_PATTERNS[kind], n, re.IGNORECASE
            ):
                out[kind] = (n, fn)
                break
    sel = select_income_statement(filing_summary_xml)
    if sel:
        out["IS"] = (sel[0], sel[1])
    return out


# ---- income statement lines ---------------------------------------------------

_NET = re.compile(r"\bnet (income|loss|earnings|\(loss\)|profit)", re.IGNORECASE)
_STOP = re.compile(
    r"per (common )?share|comprehensive", re.IGNORECASE
)  # header rows that end the income block
_NCI = re.compile(r"non-?controlling|minority", re.IGNORECASE)
_ATTR = re.compile(
    r"attributable to|available to|applicable to|to common", re.IGNORECASE
)
_PER_SHARE = re.compile(
    r"per (common )?share|per unit|basic|diluted|weighted", re.IGNORECASE
)


def net_income_lines(page: RPage) -> list[tuple[str, Row]]:
    """Net-income-like rows with their kind. 'attributable' = to the parent or
    common holders; 'nci' = attributable to noncontrolling interests; 'consolidated'
    = net income including NCI (or the only bottom line). Pre-tax lines ('before
    income taxes'), per-share and share-count lines are skipped. Labels are kept so
    the caller never merges NCI-inclusive and attributable figures."""
    out = []
    for r in page.rows:
        lab = r.label
        if all(v is None for v in r.values) and _STOP.search(lab):
            break  # EPS block and the comprehensive-income block repeat 'Net income'
        if (
            not _NET.search(lab)
            or _PER_SHARE.search(lab)
            or re.search(r"before|comprehensive", lab, re.IGNORECASE)
        ):
            continue
        if re.search(r"discontinued|continuing operations", lab, re.IGNORECASE):
            continue  # a component, not the bottom line
        if re.search(r"including (the )?(portion )?attributable to", lab, re.IGNORECASE):
            kind = "consolidated"  # NCI-INCLUSIVE total, not the NCI line (Ambac)
        elif _NCI.search(lab):
            kind = "nci"
        elif _ATTR.search(lab):
            kind = "attributable"
        else:
            kind = "consolidated"
        out.append((kind, r))
    return out


def fetch_statements(
    client: Client, folder_url: str, kinds: Iterable[str] = ("BS", "IS", "CF")
) -> dict[str, RPage]:
    """Fetch FilingSummary.xml then each wanted R page (1 + len(kinds) requests)."""
    fs = client.get(folder_url + "FilingSummary.xml").decode("utf8", "ignore")
    files = find_report_files(fs)
    return {
        k: parse_rpage(client.get(folder_url + files[k][1]).decode("utf8", "ignore"))
        for k in kinds
        if k in files
    }


# ---- face-derived liabilities -------------------------------------------------

_MEZZ = re.compile(
    r"redeemable|mezzanine|temporary equity|operating partnership|puttable|"
    r"subject to (possible )?redemption|convertible preferred (units|stock|shares)",
    re.IGNORECASE,
)
_NOT_MEZZ = re.compile(
    r"non-?redeemable|^total|attributable|long-term debt|debt", re.IGNORECASE
)
_TOTAL_LIAB = re.compile(r"^total liabilities$", re.IGNORECASE)
_TOTAL_LE = re.compile(
    r"^total (capitalization and )?liabilities\b.*(\band\b|&).*(equity|deficit|capital|investment|shareholders|stockholders)"
    r"|^total capitalization and liabilities$|^liabilities and .*(equity|deficit|capital),? total$",
    re.IGNORECASE,
)
_BARE_TOTAL = re.compile(
    r"^total$", re.IGNORECASE
)  # accepted as L&E only as the last row
_TOTAL_EQ = re.compile(
    r"^total .*(equity|deficit|capital|investment)\b|^total (stockholders|shareholders)"
    r"|(stockholders|shareholders)'? equity,? including (the )?portion attributable to non-?controlling",
    re.IGNORECASE,
)
_EQ_INCL = re.compile(
    r"^total (equity|deficit|capital|\(deficit\) equity|equity \(deficit\))$"
    r"|including (the )?portion attributable to non-?controlling",
    re.IGNORECASE,
)


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
    if (
        not le_idx
    ):  # bare 'Total' (IDACORP): the first one AFTER a total-equity line; the
        # earlier bare 'Total' is total assets
        eq_seen = [i for i, lab, v in rows if v is not None and _TOTAL_EQ.search(lab)]
        le_idx = [
            i
            for i, lab, v in rows
            if v is not None and _BARE_TOTAL.match(lab) and eq_seen and i > eq_seen[0]
        ]
    combined = len(le_idx) > 1
    end = le_idx[0] + 1 if le_idx else len(rows)
    blk = [(i, lab, v) for i, lab, v in rows[:end] if v is not None]
    tl = [x for x in blk if _TOTAL_LIAB.match(x[1])]
    if tl:
        return FaceLiabilities(
            tl[0][2], "printed_total", {tl[0][1]: tl[0][2]}, combined=combined
        )
    if not le_idx:
        return FaceLiabilities(None, "unavailable", {}, "no total L&E line")
    le = next(x for x in blk if x[0] == le_idx[0])
    if not any(
        _TOTAL_EQ.search(x[1]) and not _TOTAL_LE.search(x[1]) for x in blk
    ):  # L&E printed BEFORE equity (LDOS)
        stop = le_idx[1] if len(le_idx) > 1 else len(rows)
        blk = blk + [x for x in rows[end:stop] if x[2] is not None]  # type: ignore[misc]
    eq = [x for x in blk if _TOTAL_EQ.search(x[1]) and not _TOTAL_LE.search(x[1])]
    foot = False
    if (
        not eq
    ):  # XEL: equity total printed on a 'Common stock' line; accept only if it foots
        eq = _common_stock_footing(blk)
        foot = bool(eq)
    if not eq:
        return FaceLiabilities(None, "unavailable", {}, "no total equity line")
    incl = [x for x in eq if _EQ_INCL.search(x[1])]
    equity = (incl or eq)[-1]
    # mezzanine: by position, before the first equity-section line, never inside debt
    eq_rows = [
        x[0]
        for x in blk
        if re.search(
            r"equity|deficit|capital|stockholders|shareholders|common stock",
            x[1],
            re.IGNORECASE,
        )
        and not _MEZZ.search(x[1])
        and x[0] <= equity[0]
    ]
    first_eq = min(eq_rows, default=equity[0])
    mezz = [
        x
        for x in blk
        if x[0] < first_eq
        and _MEZZ.search(x[1])
        and not _NOT_MEZZ.search(x[1])
        and not _is_inside_debt(page, x[0])
    ]
    parts = {le[1]: le[2], equity[1]: equity[2], **{x[1]: x[2] for x in mezz}}
    value = le[2] - equity[2] - sum((x[2] for x in mezz), Decimal(0))
    return FaceLiabilities(
        value,
        "derived",
        parts,
        "L&E - equity - mezzanine"
        + (" (equity footed from components)" if foot else ""),
        combined,
    )


def _common_stock_footing(blk: list) -> list:
    """A 'Common stock...' line whose value equals the sum of the consecutive
    rows right before it (APIC, retained earnings, AOCI ...): a printed equity total."""
    for k, x in enumerate(blk):
        if re.match(r"common stock", x[1], re.IGNORECASE):
            acc, n = Decimal(0), 0
            for y in reversed(blk[max(0, k - 6) : k]):
                acc, n = acc + y[2], n + 1
                if n >= 2 and acc == x[2]:
                    return [x]
    return []


def _is_inside_debt(page: RPage, idx: int) -> bool:
    """True when a later 'Total ... debt' line closes a section containing row idx
    with no other 'Total' line in between (redeemable preferred inside debt)."""
    for r in page.rows[idx + 1 :]:
        if re.match(r"^total\b", r.label, re.IGNORECASE):
            return bool(re.search(r"debt|borrowings", r.label, re.IGNORECASE))
    return False


def cell_matches(
    shown: Decimal, face: Decimal, multiplier: int, rounding_unit: int | None = None
) -> bool:
    """shown is in full units; face in the page's printed unit. Tolerance is
    half the printed rounding unit (default: one printed unit / 2)."""
    tol = Decimal(rounding_unit if rounding_unit is not None else multiplier) / 2
    return abs(shown - face * multiplier) <= tol


# ---- sampling -----------------------------------------------------------------


def seeded_sample(
    manifest: list[dict], seed: int, extra_per_company: int = 2
) -> list[dict]:
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

VERDICT_SECTIONS = (
    "Result",
    "Method",
    "Sample",
    "Cell table",
    "Withheld cells (avoidable holds)",
    "False holds",
    "Findings for the builder",
    "Requests and disk",
    "Untested scope",
)


def verdict_skeleton(
    name: str,
    day: str,
    branch: str,
    commit: str,
    seed: int,
    claimed: dict[str, int],
    files: list[str],
) -> str:
    claims = ", ".join(f"{k}={v}" for k, v in claimed.items()) or "none"
    head = (
        f"# Verify: {name} ({branch} {commit}), {day}\n\n"
        f"Seed {seed}. Files: {', '.join(files)}. Claimed counts: {claims}. Evidence class: FILING-CHECKED.\n\n"
    )
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

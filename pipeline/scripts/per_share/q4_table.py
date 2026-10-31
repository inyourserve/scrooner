"""Read a 10-K's printed 'Selected quarterly financial data' table (main HTML document) and return the Q4 basic and
diluted EPS of a fiscal year. Read-only; sec.gov only via the caller's client.

A table qualifies when its text names quarters (Fourth / 4th / Q4) and carries per-share rows. The header rows give the
column order of the quarters (and, when present, the fiscal year of each block); a value row is a row whose label says
basic or diluted (per share). Only an unambiguous reading is returned: exactly one Q4 column for the year, numbers that
parse, parentheses = negative."""

from __future__ import annotations

import html
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

_TABLE = re.compile(r"<table\b.*?</table>", re.S | re.I)
_ROW = re.compile(r"<tr\b.*?</tr>", re.S | re.I)
_CELL = re.compile(r"<t[dh]\b([^>]*)>(.*?)</t[dh]>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")
Q4 = re.compile(r"\b(fourth|4th|q4)\b", re.I)
QLABEL = re.compile(r"\b(first|second|third|fourth|1st|2nd|3rd|4th|q[1-4])\b", re.I)
YEAR = re.compile(r"\b(20[0-2]\d)\b")
_MON = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
DATE = re.compile(rf"\b({_MON})[a-z]*\.?\s+(\d{{1,2}}),?\s+(20[0-2]\d)\b", re.I)


def _date(c: str) -> date | None:
    m = DATE.search(c)
    if not m:
        return None
    try:
        return datetime.strptime(
            f"{m.group(1)[:3]} {m.group(2)} {m.group(3)}", "%b %d %Y"
        ).date()
    except ValueError:
        return None


def _text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", s))).strip()


def _grid(table_html: str) -> list[list[str]]:
    rows = []
    for tr in _ROW.findall(table_html):
        cells = []
        for attrs, body in _CELL.findall(tr):
            span = re.search(r"colspan\s*=\s*['\"]?(\d+)", attrs, re.I)
            t = _text(body)
            cells.extend([t] * (int(span.group(1)) if span else 1))
        rows.append(cells)
    return rows


def _number(s: str) -> Decimal | None:
    t = s.replace("$", "").replace(",", "").replace("—", "").strip()
    neg = t.startswith("(") or t.endswith(")")
    t = t.strip("() ")
    if not t or t in ("-", "–"):
        return None
    try:
        v = Decimal(t)
    except InvalidOperation:
        return None
    return -v if neg else v


def _value_cells(row: list[str]) -> list[Decimal]:
    """Numbers of a value row in order, merging '$' / ')' fragments the filer split across cells."""
    out, buf = [], ""
    for c in row[1:]:
        if c in ("$", ")", "(", "") and not buf:
            if c == "(":
                buf = "("
            continue
        v = _number(buf + c)
        buf = ""
        if v is not None:
            out.append(v)
    return out


def _date_columns(grid: list[list[str]], end: date) -> tuple[int, int] | None:
    """Date-headed quarter tables ("Three months ended ... Dec. 31, 2015"): (position of the column ending within 10
    days of ``end`` among the header's distinct date columns, number of date columns), or None."""
    for r in grid:
        dates = []
        for c in r[1:]:
            d = _date(c)
            if d is not None and (not dates or dates[-1] != d):
                dates.append(d)
        if len(dates) >= 3:
            hit = [i for i, d in enumerate(dates) if abs((d - end).days) <= 10]
            return (hit[0], len(dates)) if len(hit) == 1 else None
    return None


def q4_eps(doc_html: str, end: date) -> dict[str, object]:
    """{'basic': Decimal | None, 'diluted': Decimal | None, 'tables': n, 'why': str} for the fiscal quarter ending
    ``end`` (Q4 of the fiscal year)."""
    fiscal_year = end.year
    found: dict[str, set[Decimal]] = {"basic": set(), "diluted": set()}
    candidates = 0
    for t in _TABLE.findall(doc_html):
        txt = _text(t)
        if not re.search(r"per (common )?share|earnings per|eps", txt, re.I):
            continue
        grid = _grid(t)
        dated = _date_columns(grid, end) if not Q4.search(txt) else None
        if dated is not None:
            candidates += 1
            pos, ncols = dated
            for r in grid:
                label = r[0] if r else ""
                kind = (
                    "diluted"
                    if re.search(r"dilut", label, re.I)
                    else "basic"
                    if re.search(r"basic", label, re.I)
                    else None
                )
                vals = _value_cells(r) if kind else []
                if kind and len(vals) == ncols:
                    found[kind].add(vals[pos])
            continue
        if not Q4.search(txt):
            continue
        # header: the first row whose cells name >= 3 quarters; quarter order across that row
        header = next(
            (r for r in grid if sum(1 for c in r if QLABEL.search(c)) >= 3), None
        )
        if header is None:
            continue
        candidates += 1
        quarters = []
        for c in header[1:]:
            m = QLABEL.search(c)
            if m and (not quarters or quarters[-1] != c):
                quarters.append(c)
        q4_pos = [i for i, c in enumerate(quarters) if Q4.search(c)]
        if len(q4_pos) != 1 or len(quarters) not in (4, 5):
            continue
        # year blocks: rows naming one year (e.g. "2019" / "Fiscal 2019") start a block
        year = None
        for r in grid:
            label = r[0] if r else ""
            ys = YEAR.findall(" ".join(r))
            if ys and len(set(ys)) == 1 and not _value_cells(r):
                year = int(ys[0])
                continue
            kind = (
                "diluted"
                if re.search(r"dilut", label, re.I)
                else "basic"
                if re.search(r"basic", label, re.I)
                else None
            )
            if kind is None:
                continue
            vals = _value_cells(r)
            if len(vals) < len(quarters):
                continue
            if year is not None and year != fiscal_year:
                continue
            found[kind].add(vals[q4_pos[0]])
    out: dict[str, object] = {"tables": candidates}
    for kind, vals in found.items():
        out[kind] = next(iter(vals)) if len(vals) == 1 else None
    out["why"] = (
        "ok"
        if out["basic"] is not None or out["diluted"] is not None
        else ("no_quarterly_table" if candidates == 0 else "ambiguous_or_unread")
    )
    return out

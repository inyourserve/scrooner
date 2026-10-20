"""I5 period integrity.

  duration_vs_label   a quarter-labelled value whose period is longer than a
                      quarter (a full-year value under a quarter label: LGND,
                      UP, RTB), or a year-labelled value whose period is a
                      quarter. Lengths: quarter 61..121 days (91 +/- 30), year
                      350..380 (364 and 371 are both real, ledger 2026-10-18).
                      YTD periods (fiscal_period null) are not labelled and skip.
  quarters_vs_year    for an additive flow, the four discrete quarters that
                      tile a fiscal year must sum to the year (AMT Q2 revenue
                      211M for 2,749M; GE quarterly revenue from GE Capital).
                      Period matching is by dates, never by fiscal labels.
  label_shift         a quarter value exactly equal to the value of a longer
                      window (FY or YTD) of the same concept that contains it,
                      or equal to the adjacent quarter's value (>= 1e6 only)
  duplicate_window    two stored rows for one concept and one start/end window

One value per company/concept/period is enforced by the table's unique key, so
the duplicate check is on the date window, which core.period can repeat under
different fiscal labels.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from .model import ADDITIVE_FLOWS, REVIEW, WRONG_VALUE, Cell, CompanyData, Finding, finding

QUARTER_MIN, QUARTER_MAX = 61, 121
YEAR_MIN, YEAR_MAX = 350, 380
SUM_REVIEW = Decimal("0.02")
SUM_WRONG = Decimal("0.10")
MIN_EQUAL_VALUE = Decimal(1_000_000)
# Concepts whose quarterly value moves. Dividends, interest on fixed debt, D&A,
# SBC and similar steady lines repeat to the million (NVDA pays 99M a quarter for
# years), so equality between adjacent quarters says nothing about them.
VARYING_FLOWS = frozenset(
    {"revenue", "cost_of_revenue", "gross_profit", "operating_income", "net_income",
     "income_before_tax", "cfo", "operating_expenses"}
)
TILE_GAP_DAYS = 7  # quarters may start a few days off the previous end (calendar slack)


def _duration_vs_label(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    for c in data.cells:
        d, fp = c.days, c.fiscal_period
        if d is None or fp is None:
            continue
        if fp.startswith("Q"):
            if d > QUARTER_MAX:
                out.append(
                    finding(data, "I5", WRONG_VALUE, "quarter_label_on_long_period", c,
                            days=d, label=fp, start=str(c.start))
                )
            elif d < QUARTER_MIN:
                out.append(finding(data, "I5", REVIEW, "quarter_label_on_short_period", c, days=d, label=fp))
        elif fp == "FY":
            if d <= QUARTER_MAX:
                out.append(
                    finding(data, "I5", WRONG_VALUE, "year_label_on_quarter_period", c,
                            days=d, label=fp, start=str(c.start))
                )
            elif not (YEAR_MIN <= d <= YEAR_MAX):
                out.append(finding(data, "I5", REVIEW, "year_label_on_odd_period", c, days=d, label=fp))
    return out


def _tiling_quarters(year: Cell, quarters: list[Cell]) -> list[Cell] | None:
    inside = sorted(
        (q for q in quarters
         if q.start is not None and year.start is not None
         and q.start >= year.start - timedelta(days=TILE_GAP_DAYS)
         and q.end <= year.end + timedelta(days=TILE_GAP_DAYS)),
        key=lambda q: q.end,
    )
    if len(inside) != 4:
        return None
    for prev, nxt in zip(inside, inside[1:]):
        gap = (nxt.start - prev.end).days
        if not (-TILE_GAP_DAYS <= gap <= TILE_GAP_DAYS):
            return None
    return inside


def _quarters_vs_year(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    by = data.display_by_concept()
    for base in ADDITIVE_FLOWS:
        cells = by.get(base, [])
        years = [c for c in cells if c.days is not None and YEAR_MIN <= c.days <= YEAR_MAX]
        quarters = [c for c in cells if c.days is not None and QUARTER_MIN <= c.days <= QUARTER_MAX]
        for y in years:
            tile = _tiling_quarters(y, quarters)
            if not tile or y.value == 0:
                continue
            total = sum((q.value for q in tile), Decimal(0))
            rel = abs(total - y.value) / abs(y.value)
            if rel <= SUM_REVIEW:
                continue
            median_q = sorted(abs(q.value) for q in tile)[1:3]
            centre = (median_q[0] + median_q[1]) / 2
            suspect = max(tile, key=lambda q: abs(abs(q.value) - centre))
            out.append(
                finding(
                    data, "I5", WRONG_VALUE if rel > SUM_WRONG else REVIEW, "quarters_do_not_sum_to_year", y,
                    other=total, rel_gap=str(rel),
                    quarters=[{"end": str(q.end), "value": str(q.value), "derived": any(
                        s.derived for s in data.source_facts(q))} for q in tile],
                    suspect_quarter_end=str(suspect.end), suspect_quarter_value=str(suspect.value),
                    source_ids=sorted({i for q in tile for i in q.source_ids} | set(y.source_ids)),
                )
            )
    return out


def _label_shift(data: CompanyData) -> list[Finding]:
    """A quarter equal to a longer window that contains it is a label shift only
    if the window's OTHER quarters are non-zero (then the window cannot equal the
    quarter). When the other quarters are zero the value is real (GOOG's first
    dividend was paid in Q2 2024, so Q2 = 6M YTD); when they are absent it is a
    `review`."""
    out: list[Finding] = []
    by = data.display_by_concept()
    for base in ADDITIVE_FLOWS:
        cells = by.get(base, [])
        quarters = [c for c in cells if c.days is not None and QUARTER_MIN <= c.days <= QUARTER_MAX]
        longer = [c for c in cells if c.days is not None and c.days > QUARTER_MAX]
        for q in quarters:
            if abs(q.value) < MIN_EQUAL_VALUE:
                continue
            for w in longer:
                if not (w.start is not None and q.start is not None
                        and w.start <= q.start + timedelta(days=TILE_GAP_DAYS)
                        and w.end >= q.end - timedelta(days=TILE_GAP_DAYS)
                        and w.period_id != q.period_id and w.value == q.value):
                    continue
                others = [
                    o for o in quarters
                    if o.period_id != q.period_id and o.start is not None
                    and o.start >= w.start - timedelta(days=TILE_GAP_DAYS)
                    and o.end <= w.end + timedelta(days=TILE_GAP_DAYS)
                ]
                if others and all(o.value == 0 for o in others):
                    break  # the window's other quarters are zero: the value is real
                out.append(
                    finding(data, "I5", WRONG_VALUE if any(o.value != 0 for o in others) else REVIEW,
                            "quarter_equals_longer_window", q,
                            other=w.value, window_start=str(w.start), window_end=str(w.end),
                            window_days=w.days, other_quarters_in_window=len(others),
                            source_ids=sorted(set(q.source_ids) | set(w.source_ids)))
                )
                break
        quarters.sort(key=lambda c: c.end)
        for a, b in zip(quarters, quarters[1:] if base in VARYING_FLOWS else []):
            if a.value == b.value and abs(a.value) >= MIN_EQUAL_VALUE and abs((b.start - a.end).days) <= TILE_GAP_DAYS:
                out.append(
                    finding(data, "I5", REVIEW, "quarter_equals_adjacent_quarter", b,
                            other=a.value, other_period_end=str(a.end),
                            source_ids=sorted(set(a.source_ids) | set(b.source_ids)))
                )
    return out


def _duplicate_windows(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    seen: dict[tuple, Cell] = {}
    for c in data.cells:
        k = (c.concept, c.start, c.end)
        if k in seen and seen[k].period_id != c.period_id:
            out.append(
                finding(data, "I5", REVIEW, "duplicate_date_window", c, other=seen[k].value,
                        other_period_id=seen[k].period_id, period_id=c.period_id)
            )
        else:
            seen[k] = c
    return out


def check(data: CompanyData) -> list[Finding]:
    return _duration_vs_label(data) + _quarters_vs_year(data) + _label_shift(data) + _duplicate_windows(data)

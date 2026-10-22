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

from .thresholds import (
    FACE_MAX_PRIORITY,
    VINTAGE_LATE_FILING_DAYS,
    QUARTER_MIN,
    QUARTER_MAX,
    YEAR_MIN,
    YEAR_MAX,
    SUM_REVIEW,
    SUM_WRONG,
    MIN_EQUAL_VALUE,
    TILE_GAP_DAYS,
)
from .model import (
    ADDITIVE_FLOWS,
    REVIEW,
    WRONG_VALUE,
    Cell,
    CompanyData,
    Finding,
    finding,
)

# Concepts whose quarterly value moves. Dividends, interest on fixed debt, D&A,
# SBC and similar steady lines repeat to the million (NVDA pays 99M a quarter for
# years), so equality between adjacent quarters says nothing about them.
VARYING_FLOWS = frozenset(
    {
        "revenue",
        "cost_of_revenue",
        "gross_profit",
        "operating_income",
        "net_income",
        "income_before_tax",
        "cfo",
        "operating_expenses",
    }
)


def _duration_vs_label(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    for c in data.cells:
        d, fp = c.days, c.fiscal_period
        if d is None or fp is None:
            continue
        if fp.startswith("Q"):
            if d > QUARTER_MAX:
                out.append(
                    finding(
                        data,
                        "I5",
                        WRONG_VALUE,
                        "quarter_label_on_long_period",
                        c,
                        days=d,
                        label=fp,
                        start=str(c.start),
                    )
                )
            elif d < QUARTER_MIN:
                out.append(
                    finding(
                        data,
                        "I5",
                        REVIEW,
                        "quarter_label_on_short_period",
                        c,
                        days=d,
                        label=fp,
                    )
                )
        elif fp == "FY":
            if d <= QUARTER_MAX:
                out.append(
                    finding(
                        data,
                        "I5",
                        WRONG_VALUE,
                        "year_label_on_quarter_period",
                        c,
                        days=d,
                        label=fp,
                        start=str(c.start),
                    )
                )
            elif not (YEAR_MIN <= d <= YEAR_MAX):
                out.append(
                    finding(
                        data,
                        "I5",
                        REVIEW,
                        "year_label_on_odd_period",
                        c,
                        days=d,
                        label=fp,
                    )
                )
    return out


def _tiling_quarters(year: Cell, quarters: list[Cell]) -> list[Cell] | None:
    inside = sorted(
        (
            q
            for q in quarters
            if q.start is not None
            and year.start is not None
            and q.start >= year.start - timedelta(days=TILE_GAP_DAYS)
            and q.end <= year.end + timedelta(days=TILE_GAP_DAYS)
        ),
        key=lambda q: q.end,
    )
    if len(inside) != 4:
        return None
    for prev, nxt in zip(inside, inside[1:]):
        assert nxt.start is not None  # `inside` only holds cells with a start
        gap = (nxt.start - prev.end).days
        if not (-TILE_GAP_DAYS <= gap <= TILE_GAP_DAYS):
            return None
    return inside


def _filed_late(data: CompanyData, cell) -> bool | None:
    """True when the cell's source filing came more than 200 days after the period
    end (a later 10-K / 8-K re-presenting it), False when it came from the original
    filing window, None when no filing date is known."""
    dates = [s.filing_date for s in data.source_facts(cell) if s.filing_date]
    if not dates:
        return None
    return max(dates) > cell.end + timedelta(days=VINTAGE_LATE_FILING_DAYS)


def _same_filing_pair(data: CompanyData, a, b) -> bool:
    """A source of `a` and a source of `b` (same unit) come from the SAME filing on
    different contexts: the shape of a label error (the AMD Q2 10-Q equity statement
    prints the 6-month repurchase in its 3-month block), not coincidence. Tags may
    differ: the quarter can sit on the equity statement and the window on the cash flow."""
    for sa in data.source_facts(a):
        for sb in data.source_facts(b):
            if (
                sa.id != sb.id
                and not sa.derived
                and not sb.derived
                and sa.unit == sb.unit
                and sa.accession
                and sa.accession == sb.accession
            ):
                return True
    return False


def _face_tag(data: CompanyData, base: str, tag: str) -> bool:
    role = data.tag_roles.get((base, tag))
    return role is not None and role[0] <= FACE_MAX_PRIORITY and role[1] == "approved"


def _perimeter_mix(data: CompanyData, year, tile) -> bool:
    """The year and at least one quarter come from different tags, and every tag
    involved is an approved priority 1-2 mapping of the concept (a face line, the
    registry's proxy for 'a line on the statement of its own filing')."""
    fy_tags = {s.tag for s in data.source_facts(year) if not s.derived}
    q_tags = {s.tag for q in tile for s in data.source_facts(q) if not s.derived}
    if not fy_tags or not q_tags or fy_tags == q_tags:
        return False
    return all(_face_tag(data, year.base, t) for t in fy_tags | q_tags)


def _stale_quarter(data: CompanyData, year, tile, total: Decimal) -> Finding | None:
    ytd9 = next(
        (
            c
            for c in data.display_by_concept().get(year.base, [])
            if c.days is not None
            and 240 <= c.days <= 290
            and c.start is not None
            and year.start is not None
            and abs((c.start - year.start).days) <= TILE_GAP_DAYS
            and abs((c.end - tile[2].end).days) <= TILE_GAP_DAYS
        ),
        None,
    )
    if ytd9 is None or not any(s.derived for s in data.source_facts(tile[3])):
        return None
    gap9 = sum((q.value for q in tile[:3]), Decimal(0)) - ytd9.value
    if abs(gap9) <= SUM_REVIEW * abs(year.value):
        return None
    if abs(gap9 - (total - year.value)) > SUM_REVIEW * abs(year.value):
        return None
    dated = [
        (min(s.filing_date for s in data.source_facts(q) if s.filing_date), q)
        for q in tile[:3]
        if any(s.filing_date for s in data.source_facts(q))
    ]
    if len(dated) < 3:
        return None
    filed, quarter = min(dated, key=lambda t: (t[0], t[1].end))
    return finding(
        data,
        "I5",
        WRONG_VALUE,
        "stale_quarter_basis",
        quarter,
        other=ytd9.value,
        year_end=str(year.end),
        year_value=str(year.value),
        nine_month_value=str(ytd9.value),
        quarters_to_q3=str(total - tile[3].value),
        oldest_quarter_filed=str(filed),
        note="the year equals its own 9M plus a derived Q4; this quarter is the oldest copy "
        "(never re-presented) and the three quarters do not add up to the 9M figure",
        source_ids=sorted(
            {i for q in tile for i in q.source_ids} | set(ytd9.source_ids)
        ),
    )


def _quarters_vs_year(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    by = data.display_by_concept()
    for base in ADDITIVE_FLOWS:
        cells = by.get(base, [])
        years = [
            c for c in cells if c.days is not None and YEAR_MIN <= c.days <= YEAR_MAX
        ]
        quarters = [
            c
            for c in cells
            if c.days is not None and QUARTER_MIN <= c.days <= QUARTER_MAX
        ]
        for y in years:
            tile = _tiling_quarters(y, quarters)
            if not tile or y.value == 0:
                continue
            total = sum((q.value for q in tile), Decimal(0))
            rel = abs(total - y.value) / abs(y.value)
            if rel <= SUM_REVIEW:
                continue
            # Same-vintage rule (data-team/36 item 1): a year re-presented in a later
            # filing (ASC 606 recast, Kenvue, discontinued ops) next to quarters from the
            # original 10-Qs is a basis mix between two defensible readings: `review`.
            fy_late = _filed_late(data, y)
            originals = [q for q in tile if _filed_late(data, q) is False]
            basis_mix = bool(fy_late) and bool(originals)
            # (4) FY = the same filing's 9M + a derived Q4: the year is consistent with its
            # own vintage, the inconsistency sits in Q1-Q3 against the 9M figure, and
            # the wrong cell is the quarter never re-presented (JNJ interest FY2023:
            # Q2 346M exists only in the pre-separation 10-Q).
            stale = _stale_quarter(data, y, tile, total)
            if stale is not None:
                out.append(stale)
                continue
            # (6) a year and quarters on two DIFFERENT but equally legitimate face tags
            # (AMD pretax: after / before the equity-method loss, both approved
            # priority 1-2 tags) are a perimeter mix. A component tag (TSLA
            # CostOfGoodsSold, provisional priority 3) is not a face line and stays wrong.
            perimeter = _perimeter_mix(data, y, tile)
            median_q = sorted(abs(q.value) for q in tile)[1:3]
            centre = (median_q[0] + median_q[1]) / 2
            suspect = max(tile, key=lambda q: abs(abs(q.value) - centre))
            out.append(
                finding(
                    data,
                    "I5",
                    REVIEW
                    if basis_mix or perimeter or rel <= SUM_WRONG
                    else WRONG_VALUE,
                    "quarters_vs_year_basis_mix"
                    if basis_mix
                    else "quarters_vs_year_perimeter_mix"
                    if perimeter
                    else "quarters_do_not_sum_to_year",
                    y,
                    other=total,
                    rel_gap=str(rel),
                    quarters=[
                        {
                            "end": str(q.end),
                            "value": str(q.value),
                            "derived": any(s.derived for s in data.source_facts(q)),
                        }
                        for q in tile
                    ],
                    suspect_quarter_end=str(suspect.end),
                    suspect_quarter_value=str(suspect.value),
                    source_ids=sorted(
                        {i for q in tile for i in q.source_ids} | set(y.source_ids)
                    ),
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
        quarters = [
            c
            for c in cells
            if c.days is not None and QUARTER_MIN <= c.days <= QUARTER_MAX
        ]
        longer = [c for c in cells if c.days is not None and c.days > QUARTER_MAX]
        for q in quarters:
            if abs(q.value) < MIN_EQUAL_VALUE:
                continue
            for w in longer:
                if not (
                    w.start is not None
                    and q.start is not None
                    and w.start <= q.start + timedelta(days=TILE_GAP_DAYS)
                    and w.end >= q.end - timedelta(days=TILE_GAP_DAYS)
                    and w.period_id != q.period_id
                    and w.value == q.value
                ):
                    continue
                others = [
                    o
                    for o in quarters
                    if o.period_id != q.period_id
                    and o.start is not None
                    and o.start >= w.start - timedelta(days=TILE_GAP_DAYS)
                    and o.end <= w.end + timedelta(days=TILE_GAP_DAYS)
                ]
                if others and all(o.value == 0 for o in others):
                    break  # the window's other quarters are zero: the value is real
                if not _same_filing_pair(data, q, w):
                    continue  # equal by coincidence across two filings (NVDA tax 64M, AMD CFF 28M)
                out.append(
                    finding(
                        data,
                        "I5",
                        WRONG_VALUE if any(o.value != 0 for o in others) else REVIEW,
                        "quarter_equals_longer_window",
                        q,
                        other=w.value,
                        window_start=str(w.start),
                        window_end=str(w.end),
                        window_days=w.days,
                        other_quarters_in_window=len(others),
                        source_ids=sorted(set(q.source_ids) | set(w.source_ids)),
                    )
                )
                break
        quarters.sort(key=lambda c: c.end)
        for a, b in zip(quarters, quarters[1:] if base in VARYING_FLOWS else []):
            if b.start is not None and (
                a.value == b.value
                and abs(a.value) >= MIN_EQUAL_VALUE
                and abs((b.start - a.end).days) <= TILE_GAP_DAYS
            ):
                out.append(
                    finding(
                        data,
                        "I5",
                        REVIEW,
                        "quarter_equals_adjacent_quarter",
                        b,
                        other=a.value,
                        other_period_end=str(a.end),
                        source_ids=sorted(set(a.source_ids) | set(b.source_ids)),
                    )
                )
    return out


def _duplicate_windows(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    seen: dict[tuple, Cell] = {}
    for c in data.cells:
        k = (c.concept, c.start, c.end)
        if k in seen and seen[k].period_id != c.period_id:
            out.append(
                finding(
                    data,
                    "I5",
                    REVIEW,
                    "duplicate_date_window",
                    c,
                    other=seen[k].value,
                    other_period_id=seen[k].period_id,
                    period_id=c.period_id,
                )
            )
        else:
            seen[k] = c
    return out


def check(data: CompanyData) -> list[Finding]:
    return (
        _duration_vs_label(data)
        + _quarters_vs_year(data)
        + _label_shift(data)
        + _duplicate_windows(data)
    )

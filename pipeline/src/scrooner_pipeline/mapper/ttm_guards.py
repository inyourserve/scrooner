"""TTM window guards: RF-01 `ttm.consecutive_window@1` and RF-02 `ttm.age_guard@1`.

Pure functions (no database) plus one small dated loader. The wiring is in
`expanded_metrics.py`; both rules default OFF (see `rule_flags.py`).

W1 (RF-01). `expanded_metrics._ebitda_ttm` / `_fcf_ttm` summed the four most
recent NON-NULL quarterly metric rows. A null quarter is skipped and an older
one is pulled in, so the "trailing twelve months" can span two years.
MasTec (company 225, DATA-INFERRED from `analytics.metric_value`, read
2026-10-22): TTM EBITDA 1,019,295,000 = Q2'26 349,802,000 + Q1'26 263,702,000
+ Q2'25 260,702,000 + Q1'25 145,089,000; Q3'25 and Q4'25 are null
(`incomplete:add`). The reason code `missing:4_consecutive_quarters` claimed a
check the code never made. The fix tests the DATES: the four rows must tile
one year, each starting the day after the previous one ends. Fiscal labels are
not used (W5 repairs them), so the same function is right for 12/12/12/16
retail calendars and 52/53-week years.

W2 (RF-02). Buyback and dividend TTM sums are anchored on the concept's OWN
latest quarter, so a company that stopped reporting the line keeps a years-old
TTM that looks current (AAL buybacks from FY2021; APD from FY2014, before the
2015 history gate). The fix compares the anchor's end date with the company's
current quarter end (the latest revenue quarter, interim definition until the
shared `current_quarter()` of F6 lands) and hides the TTM when it trails by
more than two quarters (S5: "more than 2 quarters behind").

Parameters are ASSUMED values chosen from the filings-domain notes (data-team/21
section 2) and the certification thresholds; the dry-run reports the
distribution so the Verifier can challenge them:
  * quarter duration 61-121 days (12-week = 84, 13-week = 91, 14-week = 98,
    16-week Q4 = 111 at COST; same as certification QUARTER_MIN/MAX),
  * adjacent quarters: next.start - prev.end within 1 +/- 7 days,
  * four quarters span 350-385 days (52-week 364, 53-week 371),
  * anchor lag: stale when more than 200 days behind the current quarter end
    (two quarters = 182 days plus 18 days of calendar slack).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

QUARTER_MIN_DAYS, QUARTER_MAX_DAYS = 61, 121
ADJACENT_SLACK_DAYS = 7
WINDOW_MIN_DAYS, WINDOW_MAX_DAYS = 350, 385
MAX_ANCHOR_LAG_DAYS = 200

# Reason codes (is_null_reason is "guard:<code>[:<data point>]").
NON_CONTIGUOUS = "non_contiguous_ttm_window"
STALE_INPUT = "stale_ttm_input"

# Window failure classes, reported separately by the dry-run.
WINDOW_TOO_FEW = "too_few_quarters"
WINDOW_GAP = "gap_between_quarters"
WINDOW_OVERLAP = "overlapping_quarters"
WINDOW_DURATION = "quarter_duration_out_of_range"
WINDOW_SPAN = "window_span_out_of_range"
WINDOW_DUPLICATE = "conflicting_duplicate_period"


@dataclass(frozen=True)
class QuarterRow:
    value: Decimal
    start: date
    end: date
    label: str = ""


@dataclass(frozen=True)
class WindowDecision:
    ok: bool
    total: Decimal | None
    window: tuple[QuarterRow, ...]
    failure: str | None = None
    detail: str = ""


def legacy_total(rows: list[QuarterRow]) -> Decimal | None:
    """The pre-RF-01 behaviour: sum of the 4 most recent non-null rows."""
    ordered = sorted(rows, key=lambda r: r.end, reverse=True)[:4]
    if len(ordered) < 4:
        return None
    return sum((r.value for r in ordered), Decimal(0))


def contiguous_ttm_window(rows: list[QuarterRow]) -> WindowDecision:
    """Four date-contiguous quarters ending at the most recent row, or why not.

    Walks backwards from the newest row. A row with the same period as one
    already taken is a duplicate: equal values are collapsed, different values
    make the window ambiguous (never pick one).
    """
    ordered = sorted(rows, key=lambda r: (r.end, r.start), reverse=True)
    if not ordered:
        return WindowDecision(False, None, (), WINDOW_TOO_FEW, "no quarterly rows")
    window: list[QuarterRow] = []
    for row in ordered:
        if window:
            prev = window[-1]
            if row.start == prev.start and row.end == prev.end:
                if row.value != prev.value:
                    return WindowDecision(
                        False,
                        None,
                        tuple(window),
                        WINDOW_DUPLICATE,
                        f"{row.start}..{row.end} has values {prev.value} and {row.value}",
                    )
                continue
        duration = (row.end - row.start).days + 1
        if not QUARTER_MIN_DAYS <= duration <= QUARTER_MAX_DAYS:
            return WindowDecision(
                False,
                None,
                tuple(window + [row]),
                WINDOW_DURATION,
                f"{row.label or 'row'} {row.start}..{row.end} is {duration} days",
            )
        if window:
            prev = window[-1]
            gap = (prev.start - row.end).days  # 1 when it ends the day before
            if gap > 1 + ADJACENT_SLACK_DAYS:
                return WindowDecision(
                    False,
                    None,
                    tuple(window),
                    WINDOW_GAP,
                    f"no quarter between {row.end} and {prev.start} ({gap - 1} days missing)",
                )
            if gap < 1 - ADJACENT_SLACK_DAYS:
                return WindowDecision(
                    False,
                    None,
                    tuple(window + [row]),
                    WINDOW_OVERLAP,
                    f"{row.start}..{row.end} overlaps {prev.start}..{prev.end}",
                )
        window.append(row)
        if len(window) == 4:
            break
    if len(window) < 4:
        return WindowDecision(
            False,
            None,
            tuple(window),
            WINDOW_TOO_FEW,
            f"{len(window)} contiguous quarters",
        )
    span = (window[0].end - window[-1].start).days + 1
    if not WINDOW_MIN_DAYS <= span <= WINDOW_MAX_DAYS:
        return WindowDecision(
            False, None, tuple(window), WINDOW_SPAN, f"four quarters span {span} days"
        )
    total = sum((r.value for r in window), Decimal(0))
    return WindowDecision(True, total, tuple(window))


def rows_from_tuples(raw: list[tuple[Any, ...]]) -> list[QuarterRow]:
    """(value, period_start, period_end, period_label) tuples -> QuarterRow."""
    return [QuarterRow(Decimal(v), s, e, label) for v, s, e, label in raw]


@dataclass(frozen=True)
class AgeDecision:
    stale: bool
    lag_days: int | None
    reference_end: date | None
    anchor_end: date | None


def ttm_age_decision(
    anchor_end: date | None,
    reference_end: date | None,
    max_lag_days: int = MAX_ANCHOR_LAG_DAYS,
) -> AgeDecision:
    """Stale when the TTM anchor trails the company's current quarter by more
    than `max_lag_days`. With no anchor or no reference it cannot judge and
    returns stale=False (a missing reference is never a reason to hide)."""
    if anchor_end is None or reference_end is None:
        return AgeDecision(False, None, reference_end, anchor_end)
    lag = (reference_end - anchor_end).days
    return AgeDecision(lag > max_lag_days, lag, reference_end, anchor_end)


def current_quarter_end(
    bounds: dict[tuple[int, str], tuple[date, date]],
) -> date | None:
    """Interim "current quarter" = latest end date among the revenue quarters.

    Replace with the shared `current_quarter()` (F6) when the Period Engineer's
    lands; every rule should read one definition."""
    if not bounds:
        return None
    return max(end for _start, end in bounds.values())


def load_quarter_bounds(
    conn: Any, company_id: int, concept_ids: list[int]
) -> dict[int, dict[tuple[int, str], tuple[date, date]]]:
    """concept_id -> {(fiscal_year, fiscal_period): (start, latest end)} for Q1-Q4.

    One read-only query. When several periods share a label (W5 label defects)
    the latest end wins, which can only make a TTM look fresher, never hide one.
    """
    out: dict[int, dict[tuple[int, str], tuple[date, date]]] = {
        c: {} for c in concept_ids
    }
    if not concept_ids:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.canonical_concept_id, p.fiscal_year, p.fiscal_period,
                   p.start_date, p.end_date
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = any(%s)
              and p.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4')
            """,
            (company_id, list(concept_ids)),
        )
        for concept_id, fy, fp, start, end in cur.fetchall():
            by_key = out.setdefault(concept_id, {})
            key = (fy, fp)
            if key not in by_key or end > by_key[key][1]:
                by_key[key] = (start, end)
    return out

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

W2 (RF-02 v2, `ttm.age_guard@2`). Buyback and dividend TTM sums are anchored
on the concept's OWN latest quarter, so a company that stopped reporting the
line keeps a years-old TTM that looks current (AAL buybacks from FY2021; APD
from FY2014, before the 2015 history gate). v1 compared the anchor with the
latest revenue quarter and a 200-day lag; v2 (Chief ruling 2026-10-22) compares
it with the EXPECTED period: the period_of_report of the company's latest
periodic filing (`common/staleness.latest_filed_period_sql`).
  * the anchor end must equal the expected period end within 7 days, in either
    direction; a missing reference (no periodic filing) hides the value;
  * a composite needs all its components on the same window end (within 7 days
    of each other) as well as on the expected end;
  * a missing component is counted as 0 in a composite only with a current TTM
    (a reported zero) or a filing-evidenced zero (`ZeroEvidence`; none exists
    until lane 1's cell_evidence does, so today an absent component hides the
    composite with reason `unevidenced_zero`).

Parameters are ASSUMED values chosen from the filings-domain notes (data-team/21
section 2) and the certification thresholds; the dry-run reports the
distribution so the Verifier can challenge them:
  * quarter duration 61-121 days (12-week = 84, 13-week = 91, 14-week = 98,
    16-week Q4 = 111 at COST; same as certification QUARTER_MIN/MAX),
  * adjacent quarters: next.start - prev.end within 1 +/- 7 days,
  * four quarters span 350-385 days (52-week 364, 53-week 371),
  * expected-period tolerance: 7 days (the certification TOLERANCE_DAYS: 52/53-week
    years and amendments differ from a month end by days).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Protocol

QUARTER_MIN_DAYS, QUARTER_MAX_DAYS = 61, 121
ADJACENT_SLACK_DAYS = 7
WINDOW_MIN_DAYS, WINDOW_MAX_DAYS = 350, 385
EXPECTED_PERIOD_TOLERANCE_DAYS = 7

# Reason codes (is_null_reason is "guard:<code>[:<data point>]").
NON_CONTIGUOUS = "non_contiguous_ttm_window"
STALE_INPUT = "stale_ttm_input"
UNEVIDENCED_ZERO = "unevidenced_zero"
MISALIGNED = "misaligned_ttm_windows"

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


CURRENT = "current"
STALE = "stale"
ABSENT = "absent"
NO_REFERENCE = "no_expected_period"


@dataclass(frozen=True)
class AgeDecision:
    stale: bool
    lag_days: (
        int | None
    )  # expected_end - anchor_end; positive = behind, negative = ahead
    reference_end: date | None
    anchor_end: date | None
    status: str = CURRENT


def ttm_age_decision(
    anchor_end: date | None,
    expected_end: date | None,
    tolerance_days: int = EXPECTED_PERIOD_TOLERANCE_DAYS,
) -> AgeDecision:
    """RF-02 v2: the TTM anchor must END at the expected period end (+/- tolerance).

    No anchor -> ABSENT (nothing to age; the caller decides what absence means).
    No expected period -> hidden (NO_REFERENCE): a value that cannot be tied to
    a filing period is never shown as current."""
    if anchor_end is None:
        return AgeDecision(False, None, expected_end, None, ABSENT)
    if expected_end is None:
        return AgeDecision(True, None, None, anchor_end, NO_REFERENCE)
    lag = (expected_end - anchor_end).days
    if abs(lag) > tolerance_days:
        return AgeDecision(True, lag, expected_end, anchor_end, STALE)
    return AgeDecision(False, lag, expected_end, anchor_end, CURRENT)


class ZeroEvidence(Protocol):
    def has_evidenced_zero(self, company_id: int, component: str) -> bool: ...


class NoZeroEvidence:
    """Default until cell_evidence exists: no zero is ever evidenced."""

    def has_evidenced_zero(self, company_id: int, component: str) -> bool:
        return False


@dataclass(frozen=True)
class Component:
    name: str  # share_buybacks | dividends_paid
    status: str  # CURRENT | STALE | NO_REFERENCE | ABSENT
    anchor_end: date | None
    lag_days: int | None = None


def component(
    name: str,
    ttm_value: Decimal | None,
    anchor_end: date | None,
    expected_end: date | None,
    tolerance_days: int = EXPECTED_PERIOD_TOLERANCE_DAYS,
) -> Component:
    if ttm_value is None:
        return Component(name, ABSENT, None)
    age = ttm_age_decision(anchor_end, expected_end, tolerance_days)
    return Component(name, age.status, anchor_end, age.lag_days)


@dataclass(frozen=True)
class CompositeDecision:
    """Two independent verdicts (two rules, two flags):
    `stale_reason`  tsy.stale_component@1: a component is stale or the current
                    windows do not end together;
    `unevidenced_reason` tsy.unevidenced_zero@1: a component has no TTM at all and
                    no filing-evidenced zero (priced as 0 today; dry-run only)."""

    stale_reason: str | None
    unevidenced_reason: str | None
    stale: tuple[str, ...] = ()
    unevidenced: tuple[str, ...] = ()
    misaligned: bool = False

    @property
    def hidden(self) -> bool:
        return bool(self.stale_reason or self.unevidenced_reason)

    @property
    def reason(self) -> str | None:
        parts = [r for r in (self.stale_reason, self.unevidenced_reason) if r]
        return ";".join(parts) or None


def composite_decision(
    company_id: int,
    components: list[Component],
    evidence: ZeroEvidence | None = None,
    tolerance_days: int = EXPECTED_PERIOD_TOLERANCE_DAYS,
) -> CompositeDecision:
    """A composite (total shareholder yield) is fully supported only when every
    component is either a CURRENT TTM or a filing-evidenced zero, and the current
    windows end together. Every offending component is named in the reason."""
    evidence = evidence or NoZeroEvidence()
    stale = tuple(c.name for c in components if c.status in (STALE, NO_REFERENCE))
    unevidenced = tuple(
        c.name
        for c in components
        if c.status == ABSENT and not evidence.has_evidenced_zero(company_id, c.name)
    )
    current_ends = [
        c.anchor_end for c in components if c.status == CURRENT and c.anchor_end
    ]
    misaligned = bool(
        len(current_ends) > 1
        and (max(current_ends) - min(current_ends)).days > tolerance_days
    )
    stale_parts = []
    if stale:
        stale_parts.append(f"{STALE_INPUT}:{','.join(stale)}")
    if misaligned:
        stale_parts.append(
            f"{MISALIGNED}:{','.join(c.name for c in components if c.status == CURRENT)}"
        )
    return CompositeDecision(
        ";".join(stale_parts) or None,
        f"{UNEVIDENCED_ZERO}:{','.join(unevidenced)}" if unevidenced else None,
        stale,
        unevidenced,
        misaligned,
    )


def windows_aligned(
    end_a: date | None,
    end_b: date | None,
    tolerance_days: int = EXPECTED_PERIOD_TOLERANCE_DAYS,
) -> bool:
    """Two TTM windows of one ratio end together (both must exist)."""
    return (
        end_a is not None
        and end_b is not None
        and abs((end_a - end_b).days) <= tolerance_days
    )


def expected_period_end(conn: Any, company_id: int) -> date | None:
    """The company's latest periodic filing period end (staleness.latest_filed_period_sql)."""
    from scrooner_pipeline.common.staleness import latest_filed_period_sql

    with conn.cursor() as cur:
        cur.execute(f"select {latest_filed_period_sql('%s')}", (company_id,))
        row = cur.fetchone()
    return row[0] if row else None


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

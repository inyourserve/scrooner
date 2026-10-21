"""I9 split consistency.

  share_jump_without_split   consecutive stored share counts (shares_outstanding,
                             display layer) change by 1.5x or more with no split
                             in analytics.company_stock_split between the two
                             dates (window: previous period end - 30 days to
                             current period end + 150 days). wrong_value when the
                             factor is within 5% of a whole number >= 2 (or its
                             inverse), the shape of an unrecorded n-for-1 split
                             (BKNG 25-for-1 in 2026: trailing P/E 1.23 vs ~18);
                             review otherwise (an offering, merger or class mix).
  per_share_basis_mix        a DERIVED quarterly EPS or dividend per share that
                             is more than 5x away from (or opposite in sign to)
                             the median of its neighbouring quarters: two share
                             bases subtracted from each other (KLAC 10-for-1:
                             derived Q4 diluted EPS -22.61, filed 1.04).

The per-share-vs-net-income level test (EPS x shares vs net income) lives in
scale.py (I4) so a mismatch is reported once.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from statistics import median

from .thresholds import (
    BASIS_RATIO,
    BREAK_TOLERANCE,
    CLEAN_RATIOS,
    DUPLICATE_SPLIT_DAYS,
    INTEGER_TOLERANCE,
    JUMP_FACTOR,
    QUARTER_MAX_DAYS,
    RUN_TOLERANCE,
    SPLIT_WINDOW_AFTER,
    SPLIT_WINDOW_BEFORE,
    YEAR_MAX,
    YEAR_MIN,
)
from .model import PER_SHARE, REVIEW, WRONG_VALUE, CompanyData, Finding, finding


def _integer_like(factor: Decimal) -> bool:
    for f in (factor, 1 / factor):
        if f >= 2:
            nearest = f.quantize(Decimal(1))
            if nearest >= 2 and abs(f - nearest) / nearest <= INTEGER_TOLERANCE:
                return True
    return False


def _matches_recorded_split(factor: Decimal, data: CompanyData) -> bool:
    return any(
        abs(factor - r) / r <= INTEGER_TOLERANCE for _d, r in data.splits if r and r > 1
    )


def _share_jumps(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    shares = sorted(
        (
            c
            for c in data.display_cells()
            if c.base == "shares_outstanding" and c.value > 0
        ),
        key=lambda c: c.end,
    )
    for prev, cur in zip(shares, shares[1:]):
        factor = cur.value / prev.value
        big = factor if factor >= 1 else 1 / factor
        if big < JUMP_FACTOR:
            continue
        lo, hi = prev.end - SPLIT_WINDOW_BEFORE, cur.end + SPLIT_WINDOW_AFTER
        if any(lo <= d <= hi for d, _ratio in data.splits):
            continue
        out.append(
            finding(
                data,
                "I9",
                WRONG_VALUE if _integer_like(factor) else REVIEW,
                "share_jump_without_split",
                # the OLDER cell is the one on the old basis (data-team/36: NVDA
                # 24.53B on 2024-08-23 is right, the 2.46B before it is not)
                prev,
                other=cur.value,
                factor=str(factor),
                newer_period_end=str(cur.end),
                splits_on_record=[(str(d), str(r)) for d, r in data.splits],
                source_ids=sorted(set(cur.source_ids) | set(prev.source_ids)),
            )
        )
    return out


def _basis_mix(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    by = data.display_by_concept()
    for base in PER_SHARE:
        quarters = [
            c
            for c in by.get(base, [])
            if c.days is not None and c.days <= QUARTER_MAX_DAYS
        ]
        quarters.sort(key=lambda c: c.end)
        for i, c in enumerate(quarters):
            if not any(s.derived for s in data.source_facts(c)) or c.value == 0:
                continue
            near = [
                n.value
                for j, n in enumerate(
                    quarters[max(0, i - 3) : i + 4], start=max(0, i - 3)
                )
                if j != i and n.value != 0
            ]
            if len(near) < 2:
                continue
            med = Decimal(str(median(near)))
            ratio = abs(c.value) / abs(med)
            flipped = (c.value > 0) != (med > 0)
            # A tiny but same-sign quarter is just a weak quarter (AMZN Q4 2022 EPS
            # 0.02 against 0.30): only a sign flip, a value >= 5x its neighbours or
            # a small ratio equal (within 5%) to a split recorded for the company signals a basis mix.
            if (
                flipped
                and ratio
                >= 1  # a flip to a SMALLER loss is a real loss quarter (WMT Q4 FY21)
                or ratio >= BASIS_RATIO
                or (
                    ratio <= 1 / BASIS_RATIO
                    and _matches_recorded_split(1 / ratio, data)
                )
            ):
                out.append(
                    finding(
                        data,
                        "I9",
                        WRONG_VALUE,
                        "per_share_basis_mix",
                        c,
                        other=med,
                        ratio=str(ratio),
                        sign_flipped=flipped,
                        neighbours=len(near),
                        derived_fact_ids=[
                            s.id for s in data.source_facts(c) if s.derived
                        ],
                        splits_on_record=[(str(d), str(r)) for d, r in data.splits],
                    )
                )
    return out


def clean_ratio(x: Decimal, tolerance: Decimal = BREAK_TOLERANCE) -> int | None:
    """The split ratio k (2, 3, 4, 5, ... 50) that `x` or 1/x is within `tolerance`
    of, else None."""
    if x <= 0:
        return None
    big = x if x >= 1 else 1 / x
    for k in CLEAN_RATIOS:
        if abs(big - k) / k <= tolerance:
            return k
    return None


def _series(data: CompanyData) -> list[tuple[str, list[tuple[Decimal, list]]]]:
    """Value series that must not step by a clean split ratio. Each point is
    (value, cells that sit on that point's basis):
      shares   display shares_outstanding, one cell per point
      eps_fy   net income / diluted EPS of each fiscal year (the implied share
               count, free of business growth); cells = diluted + basic EPS and
               dividends per share of that period
      eps_q    the same for discrete quarters
    """
    by = data.display_by_concept()
    out: list[tuple[str, list]] = []
    shares = sorted(
        (c for c in by.get("shares_outstanding", []) if c.value > 0),
        key=lambda c: c.end,
    )
    out.append(("shares", [(c.value, [c]) for c in shares]))
    ni = {c.period_id: c for c in by.get("net_income", [])}
    basic = {c.period_id: c for c in by.get("basic_eps", [])}
    dps = {c.period_id: c for c in by.get("dividends_per_share", [])}
    for name, lo, hi in (
        ("eps_fy", YEAR_MIN, YEAR_MAX),
        ("eps_q", 61, QUARTER_MAX_DAYS),
    ):
        points = []
        for e in sorted(by.get("diluted_eps", []), key=lambda c: c.end):
            n = ni.get(e.period_id)
            if (
                e.days is None
                or not (lo <= e.days <= hi)
                or n is None
                or e.value == 0
                or n.value == 0
            ):
                continue
            if (e.value > 0) != (n.value > 0):
                continue
            group = [e] + [
                x
                for x in (basic.get(e.period_id), dps.get(e.period_id))
                if x is not None
            ]
            points.append((n.value / e.value, group))
        out.append((name, points))
    return out


def _basis_runs(data: CompanyData) -> list[Finding]:
    """R-SPLIT-BASIS (data-team/36 items 3 and 8): the display layer must sit on ONE
    share basis. A series that steps by a clean split ratio (within 8% of 2, 3, 4,
    5 ... 50) between two consecutive points is split into runs; the LATEST run is
    the current basis, and every earlier run whose accumulated offset to it is
    itself a clean ratio (within 12%) is on a different basis: EVERY cell of that
    run is `wrong_value` (NVDA ~216 cells before the 2024 split; AAPL 45 share
    cells before 2020-08; AAPL FY2018 diluted EPS 11.91 against 2.98 filed, an
    isolated run between two steps). A step with no split on record is the same
    finding (the split table is missing the event); evidence says which."""
    out: list[Finding] = []
    for name, points in _series(data):
        if len(points) < 3:
            continue
        values = [v for v, _ in points]
        breaks = []  # (index after which the step happens, ratio)
        for i in range(len(values) - 1):
            r = values[i + 1] / values[i]
            if clean_ratio(r) is not None:
                breaks.append((i, r))
        if not breaks:
            continue
        # runs: [start_idx, end_idx]
        edges = [-1] + [i for i, _ in breaks] + [len(values) - 1]
        runs = [(edges[j] + 1, edges[j + 1]) for j in range(len(edges) - 1)]
        for j, (a, b) in enumerate(runs[:-1]):
            offset = Decimal(1)
            for _i, r in breaks[j:]:
                offset *= r
            k = clean_ratio(offset, RUN_TOLERANCE)
            if k is None:
                continue
            step_end = points[b][1][0].end
            recorded = any(
                abs((d - step_end).days) <= 400
                and abs(rr - Decimal(k)) / Decimal(k) <= Decimal("0.12")
                for d, rr in data.splits
                if rr and rr > 1
            )
            for _v, cells in points[a : b + 1]:
                for c in cells:
                    out.append(
                        finding(
                            data,
                            "I9",
                            WRONG_VALUE,
                            "share_basis_mismatch",
                            c,
                            series=name,
                            run_offset=str(offset),
                            clean_ratio=k,
                            step_after=str(step_end),
                            run_start=str(points[a][1][0].end),
                            run_end=str(step_end),
                            split_on_record_near_step=recorded,
                            note="cell sits on a share basis that differs from the latest run by a "
                            "clean split ratio; the display layer should be on one basis",
                        )
                    )
    return out


def _duplicate_splits(data: CompanyData) -> list[Finding]:
    """The same ratio recorded twice within 120 days: one split counted twice
    divides older per-share values by the ratio twice (NVDA 4-for-1 of 2021 rows
    46 days apart: history divided by 16 instead of 40)."""
    out: list[Finding] = []
    rows = sorted(data.splits)
    for (d1, r1), (d2, r2) in zip(rows, rows[1:]):
        if (
            r1
            and r2
            and abs(r1 - r2) / r1 <= Decimal("0.01")
            and 0 < (d2 - d1).days <= DUPLICATE_SPLIT_DAYS
        ):
            out.append(
                finding(
                    data,
                    "I9",
                    REVIEW,
                    "split_ratio_counted_twice",
                    "company_stock_split",
                    period_end=d2,
                    stored=r2,
                    other=r1,
                    first_date=str(d1),
                    second_date=str(d2),
                    days_apart=(d2 - d1).days,
                )
            )
    return out


def check(data: CompanyData) -> list[Finding]:
    return (
        _share_jumps(data)
        + _basis_mix(data)
        + _basis_runs(data)
        + _duplicate_splits(data)
    )

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

from .model import PER_SHARE, REVIEW, WRONG_VALUE, CompanyData, Finding, finding

JUMP_FACTOR = Decimal("1.5")
SPLIT_WINDOW_BEFORE = timedelta(days=30)
SPLIT_WINDOW_AFTER = timedelta(days=150)
INTEGER_TOLERANCE = Decimal("0.05")
BASIS_RATIO = Decimal(5)
QUARTER_MAX_DAYS = 121


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
                cur,
                other=prev.value,
                factor=str(factor),
                previous_period_end=str(prev.end),
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
                and ratio >= Decimal(1) / 2
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


def check(data: CompanyData) -> list[Finding]:
    return _share_jumps(data) + _basis_mix(data)

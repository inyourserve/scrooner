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
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from statistics import median

from .thresholds import (
    BASIS_RATIO,
    BREAK_TOLERANCE,
    CLEAN_RATIOS,
    NON_INTEGER_RATIOS,
    BASIS_CELL_TOLERANCE,
    DUPLICATE_STEP_WINDOW_DAYS,
    DUPLICATE_EVENT_DAYS,
    MIN_RESTATED_RATIO,
    INTEGER_TOLERANCE,
    JUMP_FACTOR,
    QUARTER_MAX_DAYS,
    SPLIT_WINDOW_AFTER,
    SPLIT_WINDOW_BEFORE,
    YEAR_MAX,
    YEAR_MIN,
)
from .model import (
    PER_SHARE,
    SHARE_COUNTS,
    Cell,
    REVIEW,
    WRONG_VALUE,
    CompanyData,
    Finding,
    finding,
)


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
            if med == 0:
                continue  # neighbours of opposite sign average to 0: no level to compare to
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


def clean_ratio(
    x: Decimal, tolerance: Decimal = BREAK_TOLERANCE
) -> int | Decimal | None:
    """The split ratio k that `x` or 1/x is within `tolerance` of: a whole ratio
    (2, 3, 4, 5 ... 50) or one of the non-integer ratios real splits use (3-for-2 =
    1.5, 5-for-4 = 1.25, 5-for-2 = 2.5), else None."""
    if x <= 0:
        return None
    big = x if x >= 1 else 1 / x
    for k in (*CLEAN_RATIOS, *NON_INTEGER_RATIOS):
        if abs(big - k) / Decimal(str(k)) <= tolerance:
            return k
    return None


def _restated_pairs(data: CompanyData) -> list[tuple[date, Decimal]]:
    """(filing date of the newer copy, older value / newer value) for every per-share
    cell that lists the SAME period's fact from two filings with different values.
    A split restates the comparative columns of every later filing, so the older copy
    is `ratio` times the newer one (TSLA Q3 2019: 0.80 in 2019, 0.16 in 2020). An
    acquisition or an offering restates nothing: the older copies are unchanged."""
    out: list[tuple[date, Decimal]] = []
    for c in data.display_cells():
        if c.base not in PER_SHARE:
            continue
        pool = {s.id: s for s in data.source_facts(c)}
        for s in list(pool.values()):
            for cp in data.pershare_copies.get(s.id, []):
                pool.setdefault(cp.id, cp)
        dated = sorted(
            (
                (s.filing_date, s)
                for s in pool.values()
                if "SplitConversionRatio" not in s.tag
                and not s.derived
                and s.filing_date is not None
                and s.value != 0
            ),
            key=lambda t: t[0],
        )
        for (d_old, older), (d_new, newer) in zip(dated, dated[1:]):
            if d_new > d_old and (older.value > 0) == (newer.value > 0):
                r = older.value / newer.value
                # an UNCHANGED value (r ~ 1) is no proof of anything: the comparative must
                # have moved by at least the smallest real split ratio
                if max(r, 1 / r) >= MIN_RESTATED_RATIO:
                    out.append((d_new, r))
    return out


def _corroborated(b: date, sr: Decimal, pairs: list[tuple[date, Decimal]]) -> bool:
    """A non-integer step in the cover counts is a split only if per-share comparatives
    were restated by about the same ratio in a filing within ~7 months of it: otherwise
    it is an offering or an acquisition (NEM/Newcrest, DOC/HCP and MPC/Andeavor all step
    the cover counts 1.25-1.5x with no restated EPS; ODFL's 3-for-2 does)."""
    for d2, r in pairs:
        if (
            abs((d2 - b).days) <= 200
            and (r > 1) == (sr > 1)
            and _same_ratio(
                r if r > 1 else 1 / r, sr if sr > 1 else 1 / sr, Decimal("0.15")
            )
        ):
            return True
    return False


@dataclass(frozen=True)
class SplitEvent:
    date: date  # the date from which filings are on the NEW basis
    ratio: Decimal  # 4 for a 4-for-1; below 1 for a reverse split
    kind: str  # 'recorded' (analytics.company_stock_split) | 'inferred' (a clean step in the share series)


def _main_source(data: CompanyData, cell: Cell):
    """The as-filed source fact whose filing date fixes the cell's basis: of the
    non-derived sources that carry a filing date (split-ratio adjustment inputs
    excluded), the LATEST filed. A resolved cell often lists the same fact from
    several filings (AAPL FY2018 EPS 11.91 in the 2018 and the 2019 10-K; TSLA Q3
    2019 0.8 in 2019 and 0.16 in the 2020 re-presentation): the newest copy is the
    version the cell took. None for calculated or undated cells."""
    sources = [
        s
        for s in data.source_facts(cell)
        if "SplitConversionRatio" not in s.tag
        and not s.derived
        and s.filing_date is not None
    ]
    if not sources:
        return None
    return max(sources, key=lambda s: (s.filing_date, -abs(s.value - cell.value)))


def _shares_by_filing(data: CompanyData) -> list[tuple[date, Decimal]]:
    """As-filed share counts ordered by the DATE OF THE FILING that reported them
    (median per filing date; every dated source of every share cell counts).
    Ordered by filing date, a split is one clean step: filings before it report the
    old basis, filings after it the new one."""
    by_date: dict[date, dict[int, Decimal]] = {}
    for c in data.display_cells():
        if c.base != "shares_outstanding" or c.value <= 0:
            continue
        for s in data.source_facts(c):
            if (
                s.derived
                or s.filing_date is None
                or s.value <= 0
                or "SplitConversionRatio" in s.tag
            ):
                continue
            by_date.setdefault(s.filing_date, {})[s.id] = s.value
    return [
        (d, Decimal(str(median(list(v.values()))))) for d, v in sorted(by_date.items())
    ]


def _steps(series: list[tuple[date, Decimal]]) -> list[tuple[date, date, Decimal]]:
    """(earlier filing date, later filing date, ratio) of every clean step."""
    out = []
    for (d0, v0), (d1, v1) in zip(series, series[1:]):
        r = v1 / v0
        if clean_ratio(r) is not None:
            out.append((d0, d1, r))
    return out


def _same_ratio(a: Decimal, b: Decimal, tol: Decimal = Decimal("0.15")) -> bool:
    return a > 0 and b > 0 and abs(a - b) / max(a, b) <= tol


def split_events(
    data: CompanyData,
) -> tuple[list[SplitEvent], list[tuple[date, date, Decimal, int]]]:
    """Events used to compute each cell's expected basis, and the duplicates found.

    Recorded rows are collapsed BY RATIO AND EVENT, not by a day window: two rows
    of the same ratio within DUPLICATE_EVENT_DAYS with at most one clean step of
    that ratio in the filing-dated share series between them are one split recorded
    twice (an announcement and an effective date: GOOG 20:1 on 2022-02-01 and
    2022-07-15, 164 days apart; NVDA 4:1 rows 46 days apart); the LATER date is the
    event (filings from then on carry the new basis). A clean step with no recorded
    split near it becomes an inferred event (NVDA 10:1 of 2024 is not in the table).
    Returns (events, duplicates as (first date, second date, ratio, steps seen))."""
    series = _shares_by_filing(data)
    steps = _steps(series)
    implied = None
    events: list[SplitEvent] = []
    dups: list[tuple[date, date, Decimal, int]] = []
    for d, r in sorted(data.splits):
        if not r or r <= 0:
            continue
        if (
            events
            and events[-1].kind == "recorded"
            and _same_ratio(events[-1].ratio, r, Decimal("0.01"))
        ):
            prev = events[-1]
            if 0 < (d - prev.date).days <= DUPLICATE_EVENT_DAYS:
                lo, hi = (
                    prev.date - timedelta(days=60),
                    d + timedelta(days=DUPLICATE_STEP_WINDOW_DAYS),
                )
                seen = sum(
                    1
                    for _a, b, sr in steps
                    if lo <= b <= hi
                    and _same_ratio(sr if sr > 1 else 1 / sr, r if r > 1 else 1 / r)
                )
                if seen <= 1:
                    dups.append((prev.date, d, r, seen))
                    events[-1] = SplitEvent(d, r, "recorded")
                    continue
        events.append(SplitEvent(d, r, "recorded"))
    for a, b, sr in steps:
        near = any(
            _same_ratio(
                e.ratio if e.ratio > 1 else 1 / e.ratio, sr if sr > 1 else 1 / sr
            )
            and a - timedelta(days=90) <= e.date <= b + timedelta(days=90)
            for e in events
        )
        if not near:
            k = clean_ratio(sr)
            if k is None:  # _steps only yields clean steps
                continue
            # EVERY inferred split, integer or not, needs the restated-comparative proof: a
            # step in the cover counts alone is also an IPO preferred conversion (DOCU 4x),
            # a self-tender (INCY 0.8x), acquisition shares (STE) or nothing (TER 2x), and
            # none of those restates a single per-share comparative.
            if implied is None:
                implied = _restated_pairs(data)
            if not _corroborated(b, sr, implied):
                continue
            kd = Decimal(str(k))
            events.append(SplitEvent(b, kd if sr > 1 else 1 / kd, "inferred"))
    return sorted(events, key=lambda e: e.date), dups


def _share_basis(data: CompanyData) -> list[Finding]:
    """R-SPLIT-BASIS by SOURCE FILING DATE (data-team/36, round 2). Every per-share
    and share-count cell has a source filing dated F. A value filed after a split
    already sits on the new basis; a value filed before it sits on the old basis.
    With m = the product of the ratios of the events dated after F:
      per-share cell  (EPS, DPS)  stored / as-filed must be 1 / m
      share count                 stored / as-filed must be m (it is never re-based,
                                  so every share cell filed before a split is flagged)
    A cell off by more than 10% is `wrong_value`: unadjusted (GOOG FY2020 EPS 59.15
    vs 2.96), adjusted by the wrong factor (TSLA Q3 2019 0.16 vs 0.053: /5 not /15),
    divided twice (GOOG Q1 2015 0.0129 vs 0.258) or divided though filed after the
    split (WMT FY2024 EPS 0.64 vs 1.92). Cells that equal the as-filed value divided
    by the right factor are not flagged, whatever their neighbours look like."""
    events, _dups = split_events(data)
    out: list[Finding] = []
    for cell in data.display_cells():
        if cell.base not in PER_SHARE and cell.base not in SHARE_COUNTS:
            continue
        s = _main_source(data, cell)
        if (
            s is None
            or s.derived
            or s.filing_date is None
            or s.value == 0
            or cell.value == 0
        ):
            continue
        m = Decimal(1)
        for e in events:
            if e.date > s.filing_date:
                m *= e.ratio
        want = m if cell.base in SHARE_COUNTS else 1 / m
        observed = cell.value / s.value
        if observed <= 0 or abs(observed / want - 1) <= BASIS_CELL_TOLERANCE:
            continue
        double = (
            m == 1
            and cell.base in PER_SHARE
            and any(
                e.date <= s.filing_date and _same_ratio(1 / observed, e.ratio)
                for e in events
            )
        )
        out.append(
            finding(
                data,
                "I9",
                WRONG_VALUE,
                "share_basis_mismatch",
                cell,
                other=s.value * (m if cell.base in SHARE_COUNTS else 1 / m),
                as_filed=str(s.value),
                filed=str(s.filing_date),
                accession=s.accession,
                observed_factor=str(observed),
                expected_factor=str(want),
                events=[(str(e.date), str(e.ratio), e.kind) for e in events],
                adjusted_though_filed_after_split=double,
                note="stored value is not the as-filed value on the basis implied by its filing date",
            )
        )
    return out


def _duplicate_splits(data: CompanyData) -> list[Finding]:
    """A split recorded twice (see `split_events`): the table divides older
    per-share values by the ratio twice (GOOG: 2015-2021 EPS divided by 400)."""
    _events, dups = split_events(data)
    return [
        finding(
            data,
            "I9",
            WRONG_VALUE,
            "split_ratio_counted_twice",
            "company_stock_split",
            period_end=d2,
            stored=r,
            other=r,
            first_date=str(d1),
            second_date=str(d2),
            days_apart=(d2 - d1).days,
            steps_in_share_series=seen,
        )
        for d1, d2, r, seen in dups
    ]


def check(data: CompanyData) -> list[Finding]:
    return (
        _share_jumps(data)
        + _basis_mix(data)
        + _share_basis(data)
        + _duplicate_splits(data)
    )

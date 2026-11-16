"""Filer-scale guard for per-share data points (STX FY2022 dividends_per_share served as 2,770,000, expected 2.77: the
FY2024 10-K 0001137789-24-000068 stores a per-share figure at the filer's monetary scale).

ONE rule shared by the serving layer (mapper/structural_direct.py, mapper/company_tag_map.py: a flagged value is never
written, the cell is HELD) and the coverage export (mapper/top100_coverage.py: an already-served flagged value is OPEN,
never SHOWN, never hidden). Pure: no database access; the other columns are read by mapper/per_share_scale.py.

A per-share value (basic_eps, diluted_eps, dividends_per_share; tags EPS*, CommonStockDividendsPerShare*) is a
filer_scale_error when |v| >= PER_SHARE_FLOOR AND the SAME filing's other columns of that tag hold a value below the
floor that sits about 10^3 or 10^6 times below it (within half a decade: a real dividend grows by percents, not by
factors of 1,000). A genuinely large per-share figure (BRK-A) has large other columns and is never flagged. A value with
no other column to compare is not judged here (listed by the sweep). The hold ends when a filer_xbrl_errors correction
row replaces the value (the corrected value is below the floor).
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

PER_SHARE_FLOOR = Decimal(1000)
SCALE_DECADES = (3, 6)
SCALE_TOLERANCE = Decimal("0.5")  # decades
PER_SHARE_DATA_POINTS = frozenset({"basic_eps", "diluted_eps", "dividends_per_share"})
FILER_SCALE_REASON = "filer_scale_error"
PER_SHARE_TAG_PREFIXES = ("EarningsPerShare", "CommonStockDividendsPerShare")


def base_name(name: str | None) -> str:
    n = name or ""
    return n[: -len("_resolved")] if n.endswith("_resolved") else n


def is_per_share(name: str | None) -> bool:
    return base_name(name) in PER_SHARE_DATA_POINTS


def is_per_share_tag(tag: str | None) -> bool:
    return (tag or "").startswith(PER_SHARE_TAG_PREFIXES)


def at_or_above_floor(name: str | None, value: Any) -> bool:
    """A per-share data point whose |value| >= PER_SHARE_FLOOR (worth a comparison with the filing's other columns)."""
    if not is_per_share(name) or value is None or value == "":
        return False
    try:
        return abs(Decimal(str(value))) >= PER_SHARE_FLOOR
    except InvalidOperation:
        return False


def filer_scale_error(name: str | None, value: Any, others: Iterable[Any]) -> bool:
    """True when `name` is per-share, |value| >= PER_SHARE_FLOOR and an other column of the same filing and tag is
    nonzero, below the floor and 10^3 or 10^6 (within SCALE_TOLERANCE decades) below |value|. Pure."""
    if not at_or_above_floor(name, value):
        return False
    v = abs(Decimal(str(value)))
    for o in others:
        try:
            a = abs(Decimal(str(o)))
        except InvalidOperation:
            continue
        if a == 0 or a >= PER_SHARE_FLOOR:
            continue
        decades = (v / a).log10()
        if any(abs(decades - k) <= SCALE_TOLERANCE for k in SCALE_DECADES):
            return True
    return False

"""I4 scale and plausibility.

Catches the 1,000x and 1,000,000x errors (a figure stored in dollars that was
filed in thousands or millions, or the reverse) and impossible displayed
metrics. Five tests, all on stored data only:

  neighbour_magnitude   a value >= 1000x (or <= 1/1000) the median of its own
                        nearest same-length periods of the same concept
  cross_concept_scale   net income / operating income / CFO / gross profit
                        vanishingly small next to revenue of the same period
  layer_disagreement    the base row and the `_resolved` row of one concept and
                        period differ by >= 100x
  eps_vs_shares         diluted EPS x shares outstanding vs net income
  metric_plausibility   margins above 100%, market cap above $10T or far from
                        price x shares, trailing P/E near zero or 5x away from
                        market cap / annual net income

`wrong_value` when the ratio has the shape of a unit-scale error (a power-of-ten
signature, `model.power_of_ten_signature`), `review` otherwise.
"""

from __future__ import annotations

from decimal import Decimal
from statistics import median

from .model import (
    NON_MONETARY,
    PER_SHARE,
    SHARE_COUNTS,
    REVIEW,
    WRONG_VALUE,
    CompanyData,
    Cell,
    Finding,
    Metric,
    finding,
    power_of_ten_signature,
)

NEIGHBOUR_RATIO = Decimal(1000)
NEIGHBOURS_EACH_SIDE = 2
MIN_NEIGHBOURS = 2
CROSS_CONCEPT_REVIEW = Decimal("0.00001")  # 1e-5 of revenue
CROSS_CONCEPT_WRONG = Decimal("0.000001")  # 1e-6 of revenue
LAYER_RATIO = Decimal(100)
EPS_SHARES_RATIO = Decimal(3)
MARKET_CAP_MAX = Decimal("10000000000000")  # $10T: above any listed company
MARKET_CAP_PRICE_RATIO = Decimal(2)
PE_FLOOR = Decimal(2)
PE_BASIS_RATIO = Decimal(5)
MARGIN_METRICS = (
    "gross_margin",
    "operating_margin",
    "net_margin",
    "pretax_margin",
    "ebitda_margin",
)
CROSS_CONCEPTS = ("net_income", "operating_income", "cfo", "gross_profit")
FY_MIN_DAYS, FY_MAX_DAYS = 350, 380
SHARES_LOOKAROUND_DAYS = 120


def _class(cell: Cell) -> str | None:
    d = cell.days
    if d is None:
        return "instant"
    if FY_MIN_DAYS <= d <= FY_MAX_DAYS:
        return "FY"
    if d <= 121:
        return "Q"
    return None  # YTD windows


def _neighbour_magnitude(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    for base, cells in data.display_by_concept().items():
        if base in NON_MONETARY:
            continue
        groups: dict[str, list[Cell]] = {}
        for c in cells:
            k = _class(c)
            if k:
                groups.setdefault(k, []).append(c)
        for series in groups.values():
            for i, c in enumerate(series):
                if c.value == 0:
                    continue
                lo, hi = max(0, i - NEIGHBOURS_EACH_SIDE), i + NEIGHBOURS_EACH_SIDE + 1
                near = [
                    abs(n.value)
                    for j, n in enumerate(series[lo:hi], start=lo)
                    if j != i and n.value != 0
                ]
                if len(near) < MIN_NEIGHBOURS:
                    continue
                med = Decimal(str(median(near)))
                ratio = abs(c.value) / med
                if ratio >= NEIGHBOUR_RATIO or ratio <= 1 / NEIGHBOUR_RATIO:
                    sig = power_of_ten_signature(ratio)
                    out.append(
                        finding(
                            data,
                            "I4",
                            WRONG_VALUE if sig else REVIEW,
                            "neighbour_magnitude",
                            c,
                            other=med,
                            ratio=str(ratio),
                            power_of_ten_signature=sig,
                            neighbours=len(near),
                        )
                    )
    return out


def _cross_concept(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    by = data.display_by_concept()
    revenue = {c.period_id: c for c in by.get("revenue", [])}
    for name in CROSS_CONCEPTS:
        for c in by.get(name, []):
            rev = revenue.get(c.period_id)
            if rev is None or rev.value <= 0 or c.value == 0:
                continue
            share = abs(c.value) / rev.value
            if share <= CROSS_CONCEPT_REVIEW:
                out.append(
                    finding(
                        data,
                        "I4",
                        WRONG_VALUE if share <= CROSS_CONCEPT_WRONG else REVIEW,
                        "cross_concept_scale",
                        c,
                        other=rev.value,
                        share_of_revenue=str(share),
                        against="revenue",
                    )
                )
    return out


def _layer_disagreement(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    base = {(c.base, c.period_id): c for c in data.cells if not c.resolved}
    for c in data.cells:
        if not c.resolved:
            continue
        b = base.get((c.base, c.period_id))
        if b is None or b.value == 0 or c.value == 0:
            continue
        if c.base in PER_SHARE or c.base in SHARE_COUNTS:
            # the resolved layer re-bases per-share and share-count history for
            # splits (Apple basic EPS 5.16 vs 0.0129): a ratio is expected there
            continue
        ratio = abs(b.value) / abs(c.value)
        big, small = (ratio, 1 / ratio) if ratio >= 1 else (1 / ratio, ratio)
        if big >= LAYER_RATIO:
            sig = power_of_ten_signature(big)
            out.append(
                finding(
                    data,
                    "I4",
                    WRONG_VALUE if sig else REVIEW,
                    "layer_disagreement",
                    b,
                    other=c.value,
                    resolved_concept=c.concept,
                    ratio=str(big),
                    power_of_ten_signature=sig,
                    source_ids=sorted(set(b.source_ids) | set(c.source_ids)),
                )
            )
    return out


def _eps_vs_shares(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    by = data.display_by_concept()
    eps = [c for c in by.get("diluted_eps", []) if (_class(c) == "FY")]
    ni = {c.period_id: c for c in by.get("net_income", [])}
    shares = by.get("shares_outstanding", [])
    for e in eps:
        n = ni.get(e.period_id)
        if n is None or e.value == 0 or n.value == 0:
            continue
        s = min(shares, key=lambda x: abs((x.end - e.end).days), default=None)
        if (
            s is None
            or abs((s.end - e.end).days) > SHARES_LOOKAROUND_DAYS
            or s.value <= 0
        ):
            continue
        implied = e.value * s.value
        ratio = abs(implied / n.value)
        big = ratio if ratio >= 1 else 1 / ratio
        if big >= EPS_SHARES_RATIO:
            sig = power_of_ten_signature(big)
            out.append(
                finding(
                    data,
                    "I4",
                    WRONG_VALUE if sig else REVIEW,
                    "eps_vs_net_income_over_shares",
                    e,
                    other=n.value,
                    implied_net_income=str(implied),
                    shares=str(s.value),
                    ratio=str(big),
                    power_of_ten_signature=sig,
                    source_ids=sorted(set(e.source_ids) | set(n.source_ids)),
                )
            )
    return out


def _metric_plausibility(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    latest: dict[str, Metric] = {}
    for metric in data.metrics:
        k = metric.name
        if k not in latest or metric.period_end > latest[k].period_end:
            latest[k] = metric
    for name in MARGIN_METRICS:
        x = latest.get(name)
        if x is not None and x.value > 1:
            out.append(
                finding(
                    data,
                    "I4",
                    REVIEW,
                    "margin_above_100_percent",
                    name,
                    stored=x.value,
                    period_end=x.period_end,
                    label=x.label,
                    source_ids=x.source_ids,
                )
            )
    mc = latest.get("market_cap")
    if mc is not None:
        if mc.value > MARKET_CAP_MAX:
            out.append(
                finding(
                    data,
                    "I4",
                    WRONG_VALUE,
                    "market_cap_above_10T",
                    "market_cap",
                    stored=mc.value,
                    period_end=mc.period_end,
                    source_ids=mc.source_ids,
                )
            )
        shares = data.display_by_concept().get("shares_outstanding", [])
        if data.price and shares:
            s = max(shares, key=lambda c: c.end)
            implied = data.price[1] * s.value
            if implied > 0:
                ratio = mc.value / implied
                big = ratio if ratio >= 1 else 1 / ratio
                if big >= MARKET_CAP_PRICE_RATIO:
                    sig = power_of_ten_signature(big)
                    out.append(
                        finding(
                            data,
                            "I4",
                            WRONG_VALUE if sig else REVIEW,
                            "market_cap_vs_price_x_shares",
                            "market_cap",
                            stored=mc.value,
                            other=implied,
                            period_end=mc.period_end,
                            price=str(data.price[1]),
                            price_date=str(data.price[0]),
                            shares=str(s.value),
                            shares_period_end=str(s.end),
                            ratio=str(big),
                            source_ids=mc.source_ids,
                        )
                    )
    pe = latest.get("trailing_pe")
    if pe is not None:
        if 0 < pe.value < PE_FLOOR:
            out.append(
                finding(
                    data,
                    "I4",
                    REVIEW,
                    "trailing_pe_below_floor",
                    "trailing_pe",
                    stored=pe.value,
                    period_end=pe.period_end,
                    floor=str(PE_FLOOR),
                    source_ids=pe.source_ids,
                )
            )
        ni = [
            c
            for c in data.display_by_concept().get("net_income", [])
            if _class(c) == "FY"
        ]
        if mc is not None and ni and pe.value > 0:
            n = max(ni, key=lambda c: c.end)
            if n.value > 0:
                basis_pe = mc.value / n.value
                ratio = pe.value / basis_pe
                big = ratio if ratio >= 1 else 1 / ratio
                if big >= PE_BASIS_RATIO:
                    out.append(
                        finding(
                            data,
                            "I4",
                            REVIEW,
                            "trailing_pe_vs_market_cap_over_net_income",
                            "trailing_pe",
                            stored=pe.value,
                            other=basis_pe,
                            period_end=pe.period_end,
                            net_income_fy=str(n.value),
                            net_income_period_end=str(n.end),
                            ratio=str(big),
                            note="price/EPS and market cap/net income disagree: a split or share-basis mismatch",
                            source_ids=pe.source_ids,
                        )
                    )
    return out


def check(data: CompanyData) -> list[Finding]:
    return (
        _neighbour_magnitude(data)
        + _cross_concept(data)
        + _layer_disagreement(data)
        + _eps_vs_shares(data)
        + _metric_plausibility(data)
    )

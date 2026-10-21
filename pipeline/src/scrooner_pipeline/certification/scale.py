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

from .thresholds import (
    MIN_SIGN_CONFLICT,
    ROLE_LAYER_CONFLICT,
    ROLE_MIN_NEIGHBOURS,
    ROLE_RATIO,
    ROLE_SIGNALS_WRONG,
    SUM_WRONG,
    NEIGHBOUR_RATIO,
    NEIGHBOURS_EACH_SIDE,
    MIN_NEIGHBOURS,
    CROSS_CONCEPT_REVIEW,
    CROSS_CONCEPT_WRONG,
    LAYER_RATIO,
    EPS_SHARES_RATIO,
    MARKET_CAP_MAX,
    MARKET_CAP_PRICE_RATIO,
    PE_FLOOR,
    PE_BASIS_RATIO,
    FY_MIN_DAYS,
    FY_MAX_DAYS,
    SHARES_LOOKAROUND_DAYS,
)
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

MARGIN_METRICS = (
    "gross_margin",
    "operating_margin",
    "net_margin",
    "pretax_margin",
    "ebitda_margin",
)
CROSS_CONCEPTS = ("net_income", "operating_income", "cfo", "gross_profit")


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
        if (b.value > 0) != (c.value > 0) and min(
            abs(b.value), abs(c.value)
        ) >= MIN_SIGN_CONFLICT:
            # the two layers disagree on the SIGN of a material flow: one is an
            # arithmetic fallback on a component (TSLA operating income FY2017
            # +1,179M against -1,632M on the face)
            out.append(
                finding(
                    data,
                    "I4",
                    WRONG_VALUE,
                    "layer_sign_conflict",
                    c,
                    other=b.value,
                    base_concept=b.concept,
                    source_ids=sorted(set(b.source_ids) | set(c.source_ids)),
                )
            )
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


ROLE_CONCEPTS = (
    "revenue",
    "research_and_development",
    "operating_expenses",
    "sga_expense",
    "cost_of_revenue",
)


def _ratio_off(value: Decimal, reference: Decimal) -> bool:
    """value is >= ROLE_RATIO times, or <= 1/ROLE_RATIO of, a positive reference
    (a zero value against a positive reference counts)."""
    if reference <= 0:
        return False
    v = abs(value)
    return v >= reference * ROLE_RATIO or v <= reference / ROLE_RATIO


def _statement_role(data: CompanyData) -> list[Finding]:
    """R-STATEMENT-ROLE (data-team/36 items 5 and the EMR/NTAP check): a revenue or
    expense value taken from a different statement line or perimeter under the same
    tag (JNJ R&D = the cash-flow add-back of acquired IPR&D, 1,841 vs 17,232;
    EMR FY2022 revenue = the acquiree's 1,660 vs 13,804; NTAP FY2026 = a segment
    total, 6,237 vs 6,925). Five independent signals per annual cell:
      neighbours  >= 5x away from the median of its nearest annual values
      intensity   value / revenue >= 5x away from the concept's own median intensity
      layer       the resolved row and the base row of the concept differ by > 5%
      quarters    the four quarters of the year do not sum to it (> 10%, same vintage)
      margins     revenue below net income or operating income of the same year
    Two or more signals: `wrong_value`; a layer conflict alone: `review`."""
    from .period_integrity import _filed_late, _tiling_quarters

    out: list[Finding] = []
    by = data.display_by_concept()
    revenue = {c.period_id: c for c in by.get("revenue", [])}
    base_cells = {(c.base, c.period_id): c for c in data.cells if not c.resolved}
    for base in ROLE_CONCEPTS:
        cells = by.get(base, [])
        years = sorted(
            (
                c
                for c in cells
                if c.days is not None and FY_MIN_DAYS <= c.days <= FY_MAX_DAYS
            ),
            key=lambda c: c.end,
        )
        quarters = [c for c in cells if c.days is not None and 61 <= c.days <= 121]
        if len(years) < ROLE_MIN_NEIGHBOURS + 1:
            continue
        intensity = {
            c.period_id: (abs(c.value) / revenue[c.period_id].value)
            for c in years
            if base != "revenue"
            and c.period_id in revenue
            and revenue[c.period_id].value > 0
        }
        for i, c in enumerate(years):
            signals: list[str] = []
            near = [
                abs(n.value)
                for j, n in enumerate(years[max(0, i - 2) : i + 3], start=max(0, i - 2))
                if j != i and n.value != 0
            ]
            if len(near) >= 2 and _ratio_off(c.value, Decimal(str(median(near)))):
                signals.append("neighbours")
            if c.period_id in intensity:
                others = [
                    v for pid, v in intensity.items() if pid != c.period_id and v > 0
                ]
                if len(others) >= ROLE_MIN_NEIGHBOURS:
                    ref = Decimal(str(median(others)))
                    if _ratio_off(intensity[c.period_id], ref):
                        signals.append("intensity")
            b = base_cells.get((base, c.period_id))
            layer = False
            if c.resolved and b is not None and b.value != 0 and c.value != 0:
                layer = (
                    abs(c.value - b.value) / max(abs(c.value), abs(b.value))
                    > ROLE_LAYER_CONFLICT
                )
                if layer:
                    signals.append("layer")
            tile = _tiling_quarters(c, quarters)
            if tile and c.value != 0:
                rel = abs(sum((q.value for q in tile), Decimal(0)) - c.value) / abs(
                    c.value
                )
                originals = [q for q in tile if _filed_late(data, q) is False]
                if rel > SUM_WRONG and not (_filed_late(data, c) and originals):
                    signals.append("quarters")
            if base == "revenue":
                for other in ("net_income", "operating_income"):
                    o = next(
                        (x for x in by.get(other, []) if x.period_id == c.period_id),
                        None,
                    )
                    if o is not None and c.value > 0 and abs(o.value) > c.value:
                        signals.append("margins")
                        break
            if len(signals) >= ROLE_SIGNALS_WRONG or layer:
                out.append(
                    finding(
                        data,
                        "I4",
                        WRONG_VALUE if len(signals) >= ROLE_SIGNALS_WRONG else REVIEW,
                        "statement_role_suspect",
                        c,
                        other=b.value if b is not None else None,
                        signals=signals,
                        concept=base,
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
        + _statement_role(data)
    )

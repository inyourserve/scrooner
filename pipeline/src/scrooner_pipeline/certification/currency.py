"""I7 currency of values and of metric inputs.

stale_displayed_value   the latest stored value of a concept or metric, per
                        label class (FY / quarter / TTM), older than the
                        company's own latest filing by the staleness rule
                        (common/staleness.py: annual > 400 days, quarterly and
                        TTM > 230 days behind its own latest filed period).
                        The serve-time guard hides such a value with a reason,
                        so this is `review` ("a cell that must stay marked"),
                        never `wrong_value`.
stale_metric_input      an input fact of a price-dependent metric (market cap,
                        P/E, ...) whose period end is more than 15 months
                        before the metric's price date. A stale SHARE COUNT
                        is `wrong_value` (CME: 66.6M shares from 2010 inside a
                        market cap of a company with 359.6M); other inputs are
                        `review`.
market_cap_no_fresh_shares
                        market cap with no recorded source fact and no share
                        count (canonical or cover-page fallback) within 15 months.
"""

from __future__ import annotations

from datetime import date, timedelta

from scrooner_pipeline.common.staleness import staleness_reason

from .model import REVIEW, WRONG_VALUE, Cell, CompanyData, Finding, finding

INPUT_MAX_AGE_DAYS = 456  # 15 months
SHARE_TAG_HINTS = (
    "SharesOutstanding",
    "SharesIssued",
    "WeightedAverage",
    "SharesBasic",
    "SharesDiluted",
)
_QUARTER_LABELS = ("Q1", "Q2", "Q3", "Q4")


def _is_share_fact(tag: str) -> bool:
    return any(h in tag for h in SHARE_TAG_HINTS)


def _label_class(label: str | None) -> str:
    if label in ("FY", "TTM"):
        return label
    return "Q"


def _stale_cells(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    if data.latest_filed is None:
        return out
    latest: dict[tuple[str, str], Cell] = {}
    for c in data.display_cells():
        if c.fiscal_period is None:
            continue
        k = (c.base, _label_class(c.fiscal_period))
        if k not in latest or c.end > latest[k].end:
            latest[k] = c
    for (base, _cls), c in latest.items():
        reason = staleness_reason(
            c.end, c.fiscal_period, data.latest_filed, fiscal_year=c.fiscal_year
        )
        if reason:
            out.append(
                finding(
                    data,
                    "I7",
                    REVIEW,
                    "stale_displayed_value",
                    c,
                    other=None,
                    latest_filed_period=str(data.latest_filed),
                    reason_shown=reason,
                    gap_days=(data.latest_filed - c.end).days,
                )
            )
    return out


def _stale_metrics(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    if data.latest_filed is None:
        return out
    for m in data.metrics:
        reason = staleness_reason(m.period_end, m.label, data.latest_filed)
        if reason:
            out.append(
                finding(
                    data,
                    "I7",
                    REVIEW,
                    "stale_displayed_value",
                    m.name,
                    stored=m.value,
                    period_end=m.period_end,
                    label=m.label,
                    reason_shown=reason,
                    latest_filed_period=str(data.latest_filed),
                    source_ids=m.source_ids,
                )
            )
    return out


def _stale_inputs(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    shares_cells = [c for c in data.display_cells() if c.base == "shares_outstanding"]
    for m in data.metrics:
        if not m.requires_price:
            continue
        limit = m.period_end - timedelta(days=INPUT_MAX_AGE_DAYS)
        old = []
        for sid in m.source_ids:
            s = data.sources.get(sid)
            if s is not None and s.end is not None and s.end < limit:
                old.append(s)
        for s in old:
            assert s.end is not None  # `old` only holds sources with an end date
            out.append(
                finding(
                    data,
                    "I7",
                    WRONG_VALUE if _is_share_fact(s.tag) else REVIEW,
                    "stale_metric_input",
                    m.name,
                    stored=m.value,
                    other=s.value,
                    period_end=m.period_end,
                    input_tag=s.tag,
                    input_period_end=str(s.end),
                    input_age_days=(m.period_end - s.end).days,
                    max_age_days=INPUT_MAX_AGE_DAYS,
                    source_ids=[s.id],
                )
            )
        if m.name == "market_cap" and not m.source_ids:
            freshest: date | None = max((c.end for c in shares_cells), default=None)
            if data.shares_fallback_filed and (
                freshest is None or data.shares_fallback_filed > freshest
            ):
                freshest = data.shares_fallback_filed
            if freshest is None or freshest < limit:
                out.append(
                    finding(
                        data,
                        "I7",
                        WRONG_VALUE,
                        "market_cap_no_fresh_shares",
                        m.name,
                        stored=m.value,
                        period_end=m.period_end,
                        freshest_share_count=str(freshest) if freshest else None,
                        max_age_days=INPUT_MAX_AGE_DAYS,
                    )
                )
    return out


def check(data: CompanyData) -> list[Finding]:
    return _stale_cells(data) + _stale_metrics(data) + _stale_inputs(data)

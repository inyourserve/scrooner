"""I8 composition.

total debt (display layer = `total_debt_resolved` else `total_debt`):

  debt_below_component   the stored total is smaller than a single authoritative
                         debt component recorded for the same period. A total
                         can never be below one of its parts. Covers ABBV (0
                         while debt tags exist), WFC (resolved = short-term only,
                         25.2B vs 207.3B) and every "resolved equals one tag"
                         failure. Components are read from the registry
                         (analytics.concept_mapping rows of total_debt and
                         total_debt_split, minus 'rejected'), not assumed.
  debt_zero_with_components
                         subtype of the above, reported under its own rule name
                         when the stored total is 0.
  debt_double_count      the sources of the stored total include two tags where
                         one by definition contains the other (OVERLAPPING_TAGS,
                         from the us-gaap element definitions: DATA-INFERRED).

per-share by subtraction:

  per_share_derived      a per-share or share-count value whose source is a
                         DERIVED fact (Q4 = FY - 9M). Never valid: EPS and
                         weighted shares are not additive (KLAC Q4 EPS -22.61,
                         filed 1.04).
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from .thresholds import (
    DEBT_DIP_RATIO,
    Q4_EPS_TOLERANCE,
    Q4_RATE_TOLERANCE,
    LEASE_INCLUSIVE_DEBT_TAGS,
    LEASE_TOTAL_TOLERANCE,
    DPS_PAID_RATE_MAX,
    DPS_PAID_RATE_MIN,
    DPS_PAID_MAX_RATIO,
    SHARES_LOOKAROUND_DAYS,
    TOTAL_TOLERANCE,
    DPS_RATE_MIN_QUARTERS,
    DPS_RATE_TOLERANCE,
    QUARTER_MIN,
    QUARTER_MAX,
    TILE_GAP_DAYS,
    YEAR_MIN,
    YEAR_MAX,
)
from .model import (
    NON_ADDITIVE_DERIVED,
    REVIEW,
    WRONG_VALUE,
    CompanyData,
    Finding,
    finding,
)


# (container tag, contained tag): the first by its taxonomy definition includes
# the second, so summing both counts the second twice.
OVERLAPPING_TAGS = (
    ("LongTermDebt", "LongTermDebtCurrent"),
    ("LongTermDebt", "LongTermDebtNoncurrent"),
    ("DebtCurrent", "ShortTermBorrowings"),
    ("DebtCurrent", "LongTermDebtCurrent"),
    ("DebtCurrent", "SecuredDebtCurrent"),
)
# Partial overlap (LongTermDebt includes current maturities that DebtCurrent
# also holds): a review, not a certain double count.
PARTIAL_OVERLAPS = (("LongTermDebt", "DebtCurrent"),)


def _debt_cells(data: CompanyData):
    return [c for c in data.display_cells() if c.base == "total_debt"]


def _debt_below_component(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    by_period: dict[int, list] = {}
    for f in data.debt_facts:
        by_period.setdefault(f.period_id, []).append(f)
    for cell in _debt_cells(data):
        facts = by_period.get(cell.period_id, [])
        positives = [f for f in facts if f.value > 0]
        if not positives:
            continue
        violating = [
            f
            for f in positives
            if cell.value
            < f.value
            * (
                LEASE_TOTAL_TOLERANCE
                if f.tag in LEASE_INCLUSIVE_DEBT_TAGS
                else TOTAL_TOLERANCE
            )
        ]
        if not violating:
            continue
        biggest = max(violating, key=lambda f: f.value)
        rule = (
            "debt_zero_with_components" if cell.value == 0 else "debt_below_component"
        )
        out.append(
            finding(
                data,
                "I8",
                WRONG_VALUE,
                rule,
                cell,
                other=biggest.value,
                largest_component_tag=biggest.tag,
                largest_component_id=biggest.id,
                components=[
                    {"id": f.id, "tag": f.tag, "value": str(f.value)} for f in positives
                ],
                source_ids=sorted(set(cell.source_ids) | {biggest.id}),
            )
        )
    return out


def _debt_isolated_dip(data: CompanyData) -> list[Finding]:
    """A total debt that falls to a fraction of a balance sheet within two periods BEFORE
    and another within two periods AFTER it is a missing component, not a repayment (BAX 2020-06-30 total debt 319M
    against about 6.4B in the quarters either side: the 6,055M long-term line was not
    picked up). Fires when both neighbours (within 130 days) are at least DEBT_DIP_RATIO
    times the value. A real full repayment and re-borrowing inside two quarters is rare
    and stays visible in the evidence."""
    out: list[Finding] = []
    cells = sorted((c for c in _debt_cells(data) if c.value > 0), key=lambda c: c.end)
    for i, cur in enumerate(cells):
        before = [c for c in cells[max(0, i - 2) : i] if (cur.end - c.end).days <= 260]
        after = [c for c in cells[i + 1 : i + 3] if (c.end - cur.end).days <= 260]
        if not before or not after:
            continue
        hi_b, hi_a = max(before, key=lambda c: c.value), max(after, key=lambda c: c.value)
        if hi_b.value >= cur.value * DEBT_DIP_RATIO and hi_a.value >= cur.value * DEBT_DIP_RATIO:
            out.append(
                finding(
                    data, "I8", WRONG_VALUE, "debt_isolated_dip", cur, other=min(hi_b.value, hi_a.value),
                    previous_end=str(hi_b.end), previous_value=str(hi_b.value),
                    next_end=str(hi_a.end), next_value=str(hi_a.value),
                    note="total debt is a fraction of a balance sheet before AND after it: a component line is missing",
                    source_ids=sorted(set(cur.source_ids)),
                )
            )
    return out


def _debt_double_count(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    for cell in _debt_cells(data):
        tags = {s.tag for s in data.source_facts(cell)}
        for container, contained in OVERLAPPING_TAGS:
            if container in tags and contained in tags:
                out.append(
                    finding(
                        data,
                        "I8",
                        WRONG_VALUE,
                        "debt_double_count",
                        cell,
                        container=container,
                        contained=contained,
                        tags=sorted(tags),
                    )
                )
        for a, b in PARTIAL_OVERLAPS:
            if a in tags and b in tags:
                out.append(
                    finding(
                        data,
                        "I8",
                        REVIEW,
                        "debt_partial_overlap",
                        cell,
                        tags=sorted(tags),
                        note=f"{a} includes current maturities also held in {b}",
                    )
                )
    return out


def _window_cells(cells, start, end):
    return [
        c
        for c in cells
        if c.start is not None
        and start is not None
        and c.start >= start - timedelta(days=TILE_GAP_DAYS)
        and c.end <= end + timedelta(days=TILE_GAP_DAYS)
    ]


def _paid_ratio(data: CompanyData, year) -> Decimal | None:
    """Full-year DPS x shares over the full-year dividends paid. About 1 when the
    year's DPS is a full-year total, about 0.25 when it is one quarterly rate. The
    share count is net income / diluted EPS of the SAME year (it is on the DPS's own
    split basis: WMT's DPS is adjusted for the 2024 3-for-1 while its stored share
    counts are not), falling back to the stored share count. None when the cash
    dividends or both share sources are missing."""
    by = data.display_by_concept()
    paid = next(
        (c for c in by.get("dividends_paid", []) if c.period_id == year.period_id), None
    )
    if paid is None or paid.value <= 0:
        return None
    ni = next(
        (c for c in by.get("net_income", []) if c.period_id == year.period_id), None
    )
    eps = next(
        (c for c in by.get("diluted_eps", []) if c.period_id == year.period_id), None
    )
    if ni is not None and eps is not None and eps.value > 0 and ni.value > 0:
        return year.value * (ni.value / eps.value) / paid.value
    shares = [c for c in by.get("shares_outstanding", []) if c.value > 0]
    if not shares:
        return None
    s = min(shares, key=lambda c: abs((c.end - year.end).days))
    if abs((s.end - year.end).days) > SHARES_LOOKAROUND_DAYS:
        return None
    return year.value * s.value / paid.value


def dps_rate_on_ytd(data: CompanyData) -> dict[int, dict]:
    """R-RATE-ON-YTD (data-team/36 item 4): a filer tags its QUARTERLY dividend rate
    on every year-to-date and full-year context (Visa 0.59 on the 12-month context;
    NVDA 0.0975 on 6M and 12M). Detected per fiscal year from the FILED values
    inside it (3-month and year-to-date cells that are not derived): two or more
    positive values within 2% of each other are one quarterly rate, and then
      * the full-year cell equals that rate (it should be about 4x), or
      * a year-to-date (6M/9M) cell equals that rate (should be 2x/3x), or
      * a DERIVED quarter is <= 0 (rate - 3 x rate is negative, rate - rate is 0).
    Returns period_id -> evidence for every flagged cell."""
    cells = [
        c
        for c in data.display_cells()
        if c.base == "dividends_per_share" and c.days is not None
    ]
    years = [c for c in cells if c.days is not None and YEAR_MIN <= c.days <= YEAR_MAX]
    quarters = [
        c for c in cells if c.days is not None and QUARTER_MIN <= c.days <= QUARTER_MAX
    ]
    ytd = [c for c in cells if c.days is not None and QUARTER_MAX < c.days < YEAR_MIN]
    flagged: dict[int, dict] = {}
    for y in years:
        inside_q = _window_cells(quarters, y.start, y.end)
        inside_ytd = _window_cells(ytd, y.start, y.end)
        filed = [
            c
            for c in inside_q + inside_ytd
            if not any(s.derived for s in data.source_facts(c)) and c.value > 0
        ]
        values = sorted(c.value for c in filed)
        rate = None
        best = 0
        for v in values:
            n = sum(1 for w in values if abs(w - v) <= DPS_RATE_TOLERANCE * v)
            if n > best:
                rate, best = v, n
        paid = _paid_ratio(data, y)
        if (
            (rate is None or best < DPS_RATE_MIN_QUARTERS)
            and paid is not None
            and DPS_PAID_RATE_MIN <= paid <= DPS_PAID_RATE_MAX
        ):
            # no quarters to compare with (Visa FY2017 0.165, FY2021 0.32), but the
            # year's DPS x shares is about a QUARTER of the cash dividends paid
            flagged[y.period_id] = {
                "reason": "year DPS x shares is about a quarter of the dividends paid",
                "paid_ratio": str(paid),
                "fiscal_year_end": str(y.end),
            }
            continue
        if rate is None or best < DPS_RATE_MIN_QUARTERS:
            continue  # no single repeated rate to compare with
        if paid is not None and paid > DPS_PAID_MAX_RATIO:
            continue  # DPS x shares is a full year of cash dividends: declared once, not a rate (WMT)
        for c in [y, *inside_ytd]:
            if abs(c.value - rate) <= DPS_RATE_TOLERANCE * rate:
                flagged[c.period_id] = {
                    "reason": "year or year-to-date value equals one quarterly rate",
                    "rate": str(rate),
                    "fiscal_year_end": str(y.end),
                }
        for q in inside_q:
            if q.value <= 0 and any(s.derived for s in data.source_facts(q)):
                flagged[q.period_id] = {
                    "reason": "derived quarter <= 0 while filed values repeat a positive rate",
                    "rate": str(rate),
                    "fiscal_year_end": str(y.end),
                }
    return flagged


def _dps_rate_findings(data: CompanyData, flagged: dict[int, dict]) -> list[Finding]:
    out: list[Finding] = []
    for c in data.display_cells():
        if c.base == "dividends_per_share" and c.period_id in flagged:
            out.append(
                finding(
                    data,
                    "I8",
                    WRONG_VALUE,
                    "dps_rate_on_ytd",
                    c,
                    **flagged[c.period_id],
                )
            )
    return out


def _q4_value_status(data: CompanyData, cell) -> dict:
    """Separate 'wrong number' from 'unsourced' for a derived Q4 value (held-out
    validation: derived Q4 tax rates were wrong 7/7, derived Q4 EPS 6/11, the other
    five equal to the release but not publishable). Both stay gating (`wrong_value`);
    the evidence says which, from an independent recompute on stored data only:
      effective tax rate  Q4 income tax / Q4 pretax income (both additive, derived
                          from the same year-minus-nine-months)
      EPS                 Q4 net income / the share count implied by the filed
                          quarters of the year (net income / EPS of Q1-Q3)
    `differs_from_recompute` = the stored value is off by more than the tolerance;
    `consistent_with_recompute` = it matches (still unsourced: no filed Q4 figure)."""
    by = data.display_by_concept()
    same = lambda base: next((c for c in by.get(base, []) if c.period_id == cell.period_id), None)  # noqa: E731
    if cell.base == "effective_tax_rate_reported":
        tax, pre = same("income_tax_expense"), same("income_before_tax")
        if tax is None or pre is None or pre.value == 0:
            return {"value_status": "no_recompute_inputs"}
        est = tax.value / pre.value
        tol = Q4_RATE_TOLERANCE
        diff = abs(cell.value - est)
        return {
            "value_status": "differs_from_recompute" if diff > tol else "consistent_with_recompute",
            "recompute": str(est),
            "recompute_basis": "Q4 income tax / Q4 pretax income",
        }
    if cell.base in ("diluted_eps", "basic_eps"):
        ni = same("net_income")
        if ni is None or cell.days is None or ni.value == 0:
            return {"value_status": "no_recompute_inputs"}
        shares = []
        ni_by_pid = {c.period_id: c for c in by.get("net_income", [])}
        for e in by.get(cell.base, []):
            if (
                e.days is not None
                and QUARTER_MIN <= e.days <= QUARTER_MAX
                and e.period_id != cell.period_id
                and 0 < (cell.end - e.end).days <= 280
                and not any(s.derived for s in data.source_facts(e))
                and e.value != 0
            ):
                n = ni_by_pid.get(e.period_id)
                if n is not None and n.value != 0 and (n.value > 0) == (e.value > 0):
                    shares.append(n.value / e.value)
        if len(shares) < 2:
            return {"value_status": "no_recompute_inputs"}
        est = ni.value / (sum(shares, Decimal(0)) / len(shares))
        diff = abs(cell.value - est) / max(abs(est), Decimal("0.01"))
        return {
            "value_status": "differs_from_recompute" if diff > Q4_EPS_TOLERANCE else "consistent_with_recompute",
            "recompute": str(est),
            "recompute_basis": "Q4 net income / mean implied shares of the filed quarters",
        }
    return {}


def _per_share_derived(data: CompanyData, flagged: dict[int, dict]) -> list[Finding]:
    """A per-share, share-count or rate value built by subtraction (Q4 = FY - 9M).
    EPS and share counts: `wrong_value` (confirmed: AAPL Q4 FY21-23 1.23/1.29/1.47
    against 1.24/1.29/1.46 filed). Tax rate: `wrong_value` as a METHOD
    (`method_policy`: a 9M rate is not a base for a Q4 rate). Dividends per share:
    `review`, because declared dividends do add up across quarters on one share
    basis; `wrong_value` only when R-RATE-ON-YTD fires for the cell."""
    out: list[Finding] = []
    for (
        cell
    ) in data.display_cells():  # displayed layer only; base+resolved would double-count
        if cell.base not in NON_ADDITIVE_DERIVED:
            continue
        derived = [s for s in data.source_facts(cell) if s.derived]
        if not derived:
            continue
        if cell.base == "dividends_per_share":
            severity = WRONG_VALUE if cell.period_id in flagged else REVIEW
        else:
            severity = WRONG_VALUE
        out.append(
            finding(
                data,
                "I8",
                severity,
                "per_share_derived_by_subtraction",
                cell,
                derived_fact_ids=[s.id for s in derived],
                tags=sorted({s.tag for s in derived}),
                policy="never derive EPS, weighted shares or ratios by subtraction",
                value_checked=False,
                method_policy=cell.base == "effective_tax_rate_reported",
                rate_on_ytd=cell.period_id in flagged,
                note="gating: Q4 cannot be derived by subtraction; value_status separates a "
                "wrong number from an unsourced one (no filed Q4 figure is stored)",
                **_q4_value_status(data, cell),
            )
        )
    return out


def check(data: CompanyData) -> list[Finding]:
    flagged = dps_rate_on_ytd(data)
    return (
        _debt_below_component(data)
        + _debt_isolated_dip(data)
        + _debt_double_count(data)
        + _per_share_derived(data, flagged)
        + _dps_rate_findings(data, flagged)
    )

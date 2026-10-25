"""Shared rules for which facts may feed a derived period and for per-share
values (WO-2 RU-1, 2026-10-22). One home so the Normalizer deriver, the
Mapper TTM/price stages and the period-completeness classifier cannot drift.

PERIODIC_FORMS_DOMESTIC: only these forms carry the registrant's own
financial statements for a period. A fact from any other form must never be
an input to a derived quarter (FILING-CHECKED cases, ledger 2026-10-18 and
2026-10-22):
- JPM DEF 14A 0000019617-26-000096 R2 pay-versus-performance prints net
  income rounded to $0.1B; Q4 2025 was derived as 57,000 - 44,023 = 12,977M
  (core.fact 182608846) where the 10-K gives 13,025M.
- WTRG 8-K 0001193125-26-124163 furnishes American Water's statements under
  WTRG's CIK (R1, R7); a derived Q4 mixed the two entities.
20-F/40-F are left out on purpose: foreign private issuers are outside V1
scope (doc 02) and file no 10-Q, so they have no quarter chain to derive.
common/staleness.PERIODIC_FORMS (which includes them) answers a different
question ("latest filed period"), so it is not reused here.

Per-share values (EPS basic/diluted, dividends per share) are never derived
by subtraction and never summed from a derived quarter (fix register item
12; data-team/14 "No EPS or share subtraction"; doc 42). A cell that would
need one is shown as unavailable with PER_SHARE_NOT_DERIVED_REASON, and
period_completeness files it under PER_SHARE_GAP_CAUSE (data_limit).
"""

from datetime import date
from decimal import Decimal

PERIODIC_FORMS_DOMESTIC = frozenset(
    {
        "10-K",
        "10-K/A",
        "10-KT",
        "10-KT/A",
        "10-Q",
        "10-Q/A",
        "10-QT",
        "10-QT/A",
    }
)

# Exact text shown for a blank per-share cell or a metric blank because of
# one. Stored as metric_value.is_null_reason (the page renders it as is).
PER_SHARE_NOT_DERIVED_REASON = "not filed separately (per-share values are not derived)"

# analytics.period_gap.gap_cause value (migration 0098).
PER_SHARE_GAP_CAUSE = "per_share_not_filed_separately"

# Canonical per-share concepts (base and *_resolved display twins).
PER_SHARE_BASE_CONCEPTS = frozenset({"basic_eps", "diluted_eps", "dividends_per_share"})
PER_SHARE_CANONICAL_CONCEPTS = PER_SHARE_BASE_CONCEPTS | frozenset(
    f"{name}_resolved" for name in PER_SHARE_BASE_CONCEPTS
)


def is_periodic_form(form: str | None) -> bool:
    return form is not None and form.strip().upper() in PERIODIC_FORMS_DOMESTIC


# NA-1 state split (Dhairya ruling 2026-10-22). Regulation S-K Item 302(a)
# required selected quarterly data (incl. Q4 EPS) in the 10-K until Release
# 33-10890; compliance with its removal applies to fiscal years ending on or
# after 2021-08-09 (FILING-CHECKED rule text, R5). So:
# - fiscal year ending ON/AFTER the cutoff: Q4 per-share is genuinely not
#   filed separately -> PER_SHARE_NOT_DERIVED_REASON / PER_SHARE_GAP_CAUSE;
# - fiscal year ending BEFORE it: the 10-K was required to file the quarter,
#   so a blank is a capture gap of ours (q4_not_derived, pipeline_bug), shown
#   with PER_SHARE_NOT_CAPTURED_REASON, never "not filed". Early compliance
#   was allowed from 2021-02-10, so a fiscal year ending 2021-02-10..08-08
#   may legitimately omit it (ASSUMED rare; the conservative label stands).
ITEM_302A_CUTOFF = date(2021, 8, 9)
PER_SHARE_NOT_CAPTURED_REASON = "not captured yet (the 10-K quarterly note files it; per-share values are not derived)"


def q4_per_share_filed_separately_required(fiscal_year_end: date | None) -> bool:
    """True when the 10-K for this fiscal year had to file Q4 quarterly data."""
    return fiscal_year_end is not None and fiscal_year_end < ITEM_302A_CUTOFF


def q4_per_share_reason(fiscal_year_end: date | None) -> str:
    if q4_per_share_filed_separately_required(fiscal_year_end):
        return PER_SHARE_NOT_CAPTURED_REASON
    return PER_SHARE_NOT_DERIVED_REASON


# NA-3 guard (pershare.fy_rate_guard@1, ruling 2026-10-22 correcting ledger
# row 71): a filed FY dividends-per-share value is a quarterly RATE, not the
# year's total, unless it is at least the SUM of the filed Q1-Q3 values on the
# same split basis (minus rounding). The old "at least each quarter" test
# passes Visa (0.59 on the FY context vs quarters 0.59; 0001403161-25-000089
# R8). Hide-only: a failing FY DPS is never used as an annual figure.
FY_RATE_GUARD_ROUNDING = Decimal("0.005")


def fy_dps_is_annual_total(fy_value: Decimal, filed_q1_q3: list[Decimal]) -> bool:
    """False when the FY DPS cannot be the year's total (V, LEA pattern).
    With no filed Q1-Q3 there is nothing to compare: True."""
    if not filed_q1_q3:
        return True
    return fy_value >= sum(filed_q1_q3, Decimal(0)) - FY_RATE_GUARD_ROUNDING

"""Materiality floors, keyed by DENOMINATOR CONCEPT NAME -- shared by
every ratio-shaped formula module in this package (ratio.py,
sum_diff_ratio.py, days.py).

Refactored 2026-09-27 from an earlier per-metric-name-allowlist design
(three separate `{"operating_margin", "net_margin", ...}`-style sets
living directly in mapper/calculate.py) after a direct follow-up
question ("why so big? find the real root cause and fix at root level
so it never arises again"). The original design required a human to
notice a new violating metric and manually add its name to a list --
exactly the kind of per-symptom patching that let this gap accumulate
silently across months of Mapper builds in the first place (see
doc/learnings/2026-09-27-plausibility-gates-root-cause-fixes.md's "why
this was so big" analysis).

This table is keyed by CONCEPT instead: every ratio/sum_diff_ratio/
days-shaped metric automatically inherits the correct floor for
whatever concept it actually divides by, current AND future -- a
metric added next month with `revenue` as its denominator role needs
zero changes here to be protected.

A concept appears here ONLY when real data confirmed a near-zero value
is a shell/pass-through-entity signal, never a legitimate business
state -- concepts where near-zero is a real, meaningful state (equity,
for a leveraged/distressed company) are deliberately absent, so metrics
denominating on THEM (roe, price_to_book, debt_to_equity) are correctly
unaffected. Every floor value is sized from real company data for that
specific concept, not one universal number -- see each entry's own
evidence below.
"""

from decimal import Decimal

CONCEPT_MATERIALITY_FLOORS: dict[str, Decimal] = {
    # Confirmed on Inhibikase Therapeutics: real, authoritative $1 TTM
    # revenue (a genuine tiny licensing payment) against real ~$20M
    # operating losses produced a -2,006,393,700% operating_margin.
    "revenue": Decimal("1000000"),
    # Confirmed on Appsoft Technologies, Inc.: real, authoritative
    # FY2025 total_assets = $7 (a real near-defunct shell) against a
    # real -$93,642 net loss produced a -1,337,700% ROA. 142 of 175
    # roa critical violations were under this exact $1M threshold.
    "total_assets": Decimal("1000000"),
    # Confirmed on Invesco CurrencyShares Euro Trust: real, authoritative
    # current_liabilities of $155,864 (a pass-through currency trust's
    # genuine near-zero management-fee accrual) against $219.7M current
    # assets produced a 1,409x current_ratio -- one of several Invesco
    # CurrencyShares trusts (Swiss Franc/Yen/Pound/AUD) hitting the same
    # shape, all real commodity/currency pass-through structures with no
    # real operating liabilities, not a bug.
    "current_liabilities": Decimal("1000000"),
    # Confirmed on Dermata Therapeutics, Inc.: real, authoritative Q4
    # 2021 interest_expense = $4 (four dollars) produced a multi-
    # million-percent interest_coverage_ratio, despite that metric's
    # already-wide doc-47 bound of +/-5000 (500,000%). Floor set lower
    # than revenue/assets/current_liabilities -- a real early-stage
    # company's genuine interest expense can legitimately be a few
    # thousand dollars a quarter (Dermata's own real Q2 2021: $1,823,
    # Q1 2021: $43,135 -- both real, both correctly left uncapped by
    # this lower floor), unlike revenue/assets/liabilities where
    # anything under $1M for an operating company is itself already a
    # strong shell-company signal.
    "interest_expense": Decimal("10000"),
    # Deliberately NOT here, checked against real data before excluding,
    # not assumed: `stockholders_equity` (roe/price_to_book/debt_to_
    # equity's denominator) -- near-zero or negative equity is a real,
    # common, already-accepted leverage story for a distressed or heavy-
    # buyback company, not a shell-company signal; debt_to_equity (same
    # denominator) already shows ZERO critical findings in the live
    # data, confirming this concept genuinely doesn't need a floor.
    # cost_of_revenue (inventory_days/payables_days' denominator) and
    # current_assets/price were checked for evidence of the same pattern
    # and none was found this pass -- not added without evidence, same
    # "verify before trusting" discipline as every concept_mapping
    # addition in this project.
}


def materiality_floor_violation(
    denominator_concept_names: frozenset[str], denom_sum: Decimal
) -> str | None:
    """Checked by every ratio-shaped formula module (ratio.py,
    sum_diff_ratio.py, days.py) against CONCEPT_MATERIALITY_FLOORS
    above -- returns an explicit null reason naming whichever concept's
    floor was breached, or None if the denominator is material by every
    concept it's actually built from. A composite denominator role
    (e.g. roic's invested_capital, which sums total_debt AND
    stockholders_equity) checks each concept independently -- any one
    of them being genuinely immaterial is enough to null the metric."""
    for concept_name in denominator_concept_names:
        floor = CONCEPT_MATERIALITY_FLOORS.get(concept_name)
        if floor is not None and abs(denom_sum) < floor:
            return f"immaterial_{concept_name}_base"
    return None

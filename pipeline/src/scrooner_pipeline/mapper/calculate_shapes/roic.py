"""The "roic" formula shape -- the one genuinely custom formula in this
engine, per Stage 3c's pinned definition (doc 11):

    NOPAT = nopat_base x (1 - effective_tax_rate)
    effective_tax_rate = tax_rate_numerator / tax_rate_denominator
    invested_capital = sum(invested_capital_add) - sum(invested_capital_subtract)
    ROIC = NOPAT / invested_capital

FY-only (see calculate.py's FY_ONLY_METRICS) -- naively computing from
a bare quarter produces a badly misleading number (AAPL: 127.8% vs a
sane 31.95%, from a single strong quarter naively annualized).

Deliberately does NOT check invested_capital against a materiality
floor -- unlike total_assets, invested_capital (debt + equity) going
near-zero for a real, minimally-capitalized company hasn't been
evidenced as a shell-company signal the way total_assets was; only add
a floor here if real data confirms the same pattern (see
calculate_shapes/materiality.py's own "verify before trusting"
discipline).
"""

from decimal import Decimal


def compute(
    values_by_role: dict[str, list[Decimal]],
    denominator_concept_names: frozenset[str] = frozenset(),
) -> tuple[Decimal | None, str | None]:
    nopat_base = values_by_role.get("nopat_base")
    tax_num = values_by_role.get("tax_rate_numerator")
    tax_denom = values_by_role.get("tax_rate_denominator")
    ic_add = values_by_role.get("invested_capital_add")
    ic_sub = values_by_role.get("invested_capital_subtract")
    if nopat_base is None:
        return None, "missing:nopat_base"
    if tax_num is None:
        return None, "missing:tax_rate_numerator"
    if tax_denom is None:
        return None, "missing:tax_rate_denominator"
    if ic_add is None:
        return None, "missing:invested_capital_add"
    if ic_sub is None:
        return None, "missing:invested_capital_subtract"
    tax_denom_sum = sum(tax_denom)
    if tax_denom_sum == 0:
        return None, "zero_pretax_income"
    tax_rate = sum(tax_num) / tax_denom_sum
    nopat = sum(nopat_base) * (1 - tax_rate)
    invested_capital = sum(ic_add) - sum(ic_sub)
    if invested_capital == 0:
        return None, "zero_invested_capital"
    return nopat / invested_capital, None

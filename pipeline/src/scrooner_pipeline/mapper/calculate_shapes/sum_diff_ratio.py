"""The "sum_diff_ratio" formula shape: (sum(add) - sum(subtract)) /
sum(denominator) -- used by gross_margin (Revenue - CostOfRevenue) /
Revenue), fcf_margin, quick_ratio, eps_dilution_spread,
net_cash_per_share.
"""

from decimal import Decimal

from scrooner_pipeline.mapper.calculate_shapes.materiality import (
    materiality_floor_violation,
)


def compute(
    values_by_role: dict[str, list[Decimal]],
    denominator_concept_names: frozenset[str] = frozenset(),
) -> tuple[Decimal | None, str | None]:
    add = values_by_role.get("add")
    subtract = values_by_role.get("subtract")
    denom = values_by_role.get("denominator")
    if add is None:
        return None, "missing:add"
    if subtract is None:
        return None, "missing:subtract"
    if denom is None:
        return None, "missing:denominator"
    denom_sum = sum(denom)
    if denom_sum == 0:
        return None, "zero_denominator"
    floor_violation = materiality_floor_violation(denominator_concept_names, denom_sum)
    if floor_violation is not None:
        return None, floor_violation
    return (sum(add) - sum(subtract)) / denom_sum, None

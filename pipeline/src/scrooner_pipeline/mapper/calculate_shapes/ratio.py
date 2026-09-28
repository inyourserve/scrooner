"""The "ratio" formula shape: sum(numerator inputs) / sum(denominator
inputs). The single most common shape in calculate.py's generic engine
(operating_margin, net_margin, roe, roa, current_ratio, debt_to_equity,
interest_coverage_ratio, goodwill_pct_assets, rnd_intensity, ...).
"""

from decimal import Decimal

from scrooner_pipeline.mapper.calculate_shapes.materiality import (
    materiality_floor_violation,
)


def compute(
    values_by_role: dict[str, list[Decimal]],
    denominator_concept_names: frozenset[str] = frozenset(),
) -> tuple[Decimal | None, str | None]:
    num = values_by_role.get("numerator")
    denom = values_by_role.get("denominator")
    if num is None:
        return None, "missing:numerator"
    if denom is None:
        return None, "missing:denominator"
    denom_sum = sum(denom)
    if denom_sum == 0:
        return None, "zero_denominator"
    floor_violation = materiality_floor_violation(denominator_concept_names, denom_sum)
    if floor_violation is not None:
        return None, floor_violation
    return sum(num) / denom_sum, None

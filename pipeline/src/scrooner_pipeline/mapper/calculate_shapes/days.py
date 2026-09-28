"""The "days" formula shape: (numerator / denominator) x 365 --
Debtor/Inventory/Payables Days. FY-only (see calculate.py's
FY_ONLY_METRICS), same annualization reasoning as roic/roe: a quarterly
denominator would inflate the day-count ~4x for the same
balance-sheet snapshot. Added 2026-08-18.
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
    return (sum(num) / denom_sum) * 365, None

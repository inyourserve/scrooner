"""The "sum_diff" formula shape: sum(add inputs) - sum(subtract
inputs). No denominator, so no materiality-floor concern (see
materiality.py) -- used by fcf (cfo - capex), net_interest_income,
net_cash, working_capital.
"""

from decimal import Decimal


def compute(
    values_by_role: dict[str, list[Decimal]],
    denominator_concept_names: frozenset[str] = frozenset(),
) -> tuple[Decimal | None, str | None]:
    add = values_by_role.get("add")
    subtract = values_by_role.get("subtract")
    if add is None:
        return None, "missing:add"
    if subtract is None:
        return None, "missing:subtract"
    return sum(add) - sum(subtract), None

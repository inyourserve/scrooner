"""The "additive" formula shape: sum of all "add"-role inputs, no
subtraction, unlike sum_diff. Added 2026-08-18 for ebitda
(operating_income + depreciation_and_amortization): these are two
genuinely different concepts being added, not alternates for the same
thing (that's what depreciation_and_amortization's own first_match
resolution already handles, one layer down). Also used by
net_change_in_cash, cash_returned_to_shareholders.
"""

from decimal import Decimal


def compute(
    values_by_role: dict[str, list[Decimal]],
    denominator_concept_names: frozenset[str] = frozenset(),
) -> tuple[Decimal | None, str | None]:
    add = values_by_role.get("add")
    if add is None:
        return None, "missing:add"
    return sum(add), None

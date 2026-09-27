"""Stage 5c -- Predicate evaluation (doc 14 Sec 2, doc 02's 9 locked
operators). A null resolved value NEVER matches any comparison -- this
falls out of Python's own comparison semantics (None > x raises, not
"False"), so evaluation must check for None explicitly and treat it as
"excluded," not let a TypeError leak or, worse, silently coerce to a
number. This is the same "never guess, exclude instead" discipline as
core.fact.is_authoritative and analytics.metric_value.is_null_reason.

top_n/bottom_n is a ranking operator, not a per-company predicate -- it's
applied once, over the whole candidate set, after every other predicate
has already filtered it (see query.py). evaluate_comparison/evaluate_between
below are the per-company, per-predicate checks; rank_top_bottom is the
query-wide operation.
"""

from decimal import Decimal


def evaluate_comparison(value: Decimal | None, operator: str, target: Decimal) -> bool:
    if value is None:
        return False
    if operator == ">":
        return value > target
    if operator == "<":
        return value < target
    if operator == ">=":
        return value >= target
    if operator == "<=":
        return value <= target
    if operator == "=":
        return value == target
    if operator == "!=":
        return value != target
    raise ValueError(f"not a comparison operator: {operator!r}")


def evaluate_between(
    value: Decimal | None, value_range: tuple[Decimal, Decimal]
) -> bool:
    if value is None:
        return False
    low, high = value_range
    return low <= value <= high


def rank_top_bottom(
    candidates: list[tuple[str, Decimal | None]], operator: str, n: int
) -> list[str]:
    """candidates: list of (cik, value) for every company still in
    consideration after other predicates. Nulls are excluded from the
    ranking entirely -- a missing ROIC is not "the worst ROIC," it's
    unranked, same principle as every comparison operator above. Returns
    the top/bottom n ciks, in rank order."""
    non_null = [(cik, v) for cik, v in candidates if v is not None]
    # Value is primary; CIK ascending is the stable tiebreaker for both
    # directions. Database row order is not a deterministic ordering rule.
    if operator == "top_n":
        ranked = sorted(non_null, key=lambda cv: (-cv[1], cv[0]))
    elif operator == "bottom_n":
        ranked = sorted(non_null, key=lambda cv: (cv[1], cv[0]))
    else:
        raise ValueError(f"not a ranked operator: {operator!r}")
    return [cik for cik, _ in ranked[:n]]

"""WO-23 / RF-46 `dedupe.matching_copies@1`: two copies of one fact that
differ only by rounding are not a conflict.

XBRL rule (domain rule 8.4, data-team/03): duplicate numeric facts in a
filing are consistent when their decimals intervals overlap, and the copy
with the larger `decimals` (the more precise one) is preferred. Real cases
(data-team/36 T10; AT-23.1):
  TTWO  3,372,772,000 vs 3,372,800,000   (reported as 3,372,772K and 3,372.8M)
  ANET 14,043,921,000 vs 14,043,900,000

core.fact stores NO `decimals` (companyfacts entries carry none; CODE-READ
normalizer/facts.py insert and the companyfacts fixture), so the interval is
INFERRED from the value itself and the inference is deliberately conservative:
- both values must be integers (per-share and ratio values are never merged);
- the rounding unit of the coarser copy is 10 ** (its trailing zeros), capped
  at 10 ** MAX_ROUNDING_EXPONENT (millions: nothing coarser is trusted), and
  the two copies are consistent only if they differ by at most half of it;
- AND by at most MAX_RELATIVE_DIFF of the larger magnitude, which stops a
  round number such as 100,000,000 from "absorbing" a real 20% restatement;
- values of opposite sign or a zero are never consistent.
Evidence level of any group it resolves: DATA-INFERRED. The real fix is to
store `decimals` (instance or FSDS), which is an unblock request, not done.

Rule version: a change to either constant is rule dedupe.matching_copies@2.
"""

from collections.abc import Sequence
from decimal import Decimal

MAX_ROUNDING_EXPONENT = 6
MAX_RELATIVE_DIFF = Decimal("0.0005")
MAX_GROUP_SIZE = 50  # pairwise check; a larger group stays a conflict


def _is_integral(v: Decimal) -> bool:
    return v == v.to_integral_value()


def trailing_zeros(v: Decimal) -> int:
    """Trailing zero digits of an integral value (0 for 0)."""
    n = int(abs(v))
    if n == 0:
        return 0
    zeros = 0
    while n % 10 == 0:
        n //= 10
        zeros += 1
    return zeros


def consistent(a: Decimal, b: Decimal) -> bool:
    """True when a and b could be the same number reported at two roundings."""
    if a == b:
        return True
    if a == 0 or b == 0 or (a > 0) != (b > 0):
        return False
    if not (_is_integral(a) and _is_integral(b)):
        return False
    exponent = min(max(trailing_zeros(a), trailing_zeros(b)), MAX_ROUNDING_EXPONENT)
    half_unit = Decimal(10) ** exponent / 2
    diff = abs(a - b)
    if diff > half_unit:
        return False
    return diff / max(abs(a), abs(b)) <= MAX_RELATIVE_DIFF


def all_consistent(values: Sequence[Decimal]) -> bool:
    distinct = sorted(set(values))
    if len(distinct) == 1:
        return True
    if len(distinct) > MAX_GROUP_SIZE:
        return False
    return all(
        consistent(distinct[i], distinct[j])
        for i in range(len(distinct))
        for j in range(i + 1, len(distinct))
    )


def precision_rank(v: Decimal) -> int:
    """Smaller = more precise (fewer trailing zeros)."""
    return trailing_zeros(v) if _is_integral(v) else -1

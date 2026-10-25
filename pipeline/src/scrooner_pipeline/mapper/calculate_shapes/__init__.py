"""Formula-shape registry -- the "sub-tree node per calculation"
structure requested directly 2026-09-28 ("keep one main tree ->
calculate.py, create more sub tree node for each calculation, so it
will be scalable").

`mapper/calculate.py` stays the single entry point ("tree root") for
this engine's orchestration -- loading targets from the DB, loading a
company's canonical facts, matching duration/instant periods, and
writing analytics.metric_value. It does NOT contain per-shape math
logic anymore; that lives here, one module per formula shape (a peer of
`mapper/main_calculator.py`'s own module-level registry, doc 42, just
one layer further in -- that registry says WHICH MODULE computes a
metric; this one says WHICH SHAPE FUNCTION computes a formula inside
calculate.py's own module).

Adding a new formula shape in the future is: one new file here
exporting a `compute(values_by_role, denominator_concept_names)`
function with the same signature as every other shape module, plus one
line in SHAPE_REGISTRY below. calculate.py's own orchestration code
never needs to change, and no existing shape module needs touching --
the exact same "one place to look, zero per-symptom patching" property
`CONCEPT_MATERIALITY_FLOORS` (materiality.py) was refactored to have
the same day this package was built (see that module's own docstring).

Every shape module's `compute()` is a pure function (no DB access) --
unit-testable in isolation, which is the property that let this whole
refactor be verified purely against the existing unit-test suite while
the production database was unreachable.
"""

from decimal import Decimal

from scrooner_pipeline.mapper.calculate_shapes import (
    additive,
    days,
    ratio,
    roic,
    sum_diff,
    sum_diff_ratio,
)
from scrooner_pipeline.mapper.calculate_shapes.materiality import (
    CONCEPT_MATERIALITY_FLOORS,
    materiality_floor_violation,
)

SHAPE_REGISTRY: dict[str, callable] = {
    "ratio": ratio.compute,
    "sum_diff": sum_diff.compute,
    "sum_diff_ratio": sum_diff_ratio.compute,
    "additive": additive.compute,
    "days": days.compute,
    "roic": roic.compute,
}


def compute(
    shape: str,
    values_by_role: dict[str, list[Decimal]],
    denominator_concept_names: frozenset[str] = frozenset(),
) -> tuple[Decimal | None, str | None]:
    """Dispatches to the right shape module's own compute() -- the one
    function calculate.py's orchestration calls, same signature every
    shape module itself exposes."""
    fn = SHAPE_REGISTRY.get(shape)
    if fn is None:
        raise ValueError(f"unknown formula shape: {shape}")
    return fn(values_by_role, denominator_concept_names)


__all__ = [
    "SHAPE_REGISTRY",
    "compute",
    "CONCEPT_MATERIALITY_FLOORS",
    "materiality_floor_violation",
]

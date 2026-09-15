"""Stage 5a -- Query schema (doc 14). Pydantic here on purpose, unlike the
rest of this project's modules (Mapper/Company Master use plain dicts
throughout) -- this is a genuine external-input boundary, the same kind
Collector's config schema already uses Pydantic for, and it's deliberately
the schema the AI Query Engine (Part 6) will later need to produce and
validate against too.

Structural validation only (right fields for the right operator) -- this
module has no DB connection and doesn't know the live metric/SIC catalog.
Semantic validation (does this metric_name actually exist, is it one of
the 12 EDGAR-only ones) happens in query.py, against a catalog loaded from
analytics.metric_definition at query time -- kept separate so this schema
stays a pure, connectionless structural check, matching doc 04's boundary
discipline (a narrow, single-purpose stage, not a stage that reaches into
the database to validate itself).
"""

from decimal import Decimal
from typing import Literal, Union

from pydantic import BaseModel, Field, model_validator

COMPARISON_OPERATORS = {">", "<", ">=", "<=", "=", "!="}
RANKED_OPERATORS = {"top_n", "bottom_n"}
ALL_METRIC_OPERATORS = COMPARISON_OPERATORS | RANKED_OPERATORS | {"between"}


class MetricPredicate(BaseModel):
    metric_name: str
    operator: Literal[">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"]
    value: Decimal | None = None
    value_range: tuple[Decimal, Decimal] | None = None
    n: int | None = None

    @model_validator(mode="after")
    def _check_operator_fields(self) -> "MetricPredicate":
        if self.operator in COMPARISON_OPERATORS:
            if self.value is None:
                raise ValueError(f"operator {self.operator!r} requires 'value'")
            if self.value_range is not None or self.n is not None:
                raise ValueError(f"operator {self.operator!r} does not accept 'value_range' or 'n'")
        elif self.operator == "between":
            if self.value_range is None:
                raise ValueError("operator 'between' requires 'value_range'")
            if self.value_range[0] >= self.value_range[1]:
                raise ValueError("value_range must be (low, high) with low < high")
            if self.value is not None or self.n is not None:
                raise ValueError("operator 'between' does not accept 'value' or 'n'")
        elif self.operator in RANKED_OPERATORS:
            if self.n is None or self.n < 1:
                raise ValueError(f"operator {self.operator!r} requires a positive 'n'")
            if self.value is not None or self.value_range is not None:
                raise ValueError(f"operator {self.operator!r} does not accept 'value' or 'value_range'")
        return self


class PredicateGroup(BaseModel):
    """A boolean-tree filter node (doc/faster-loading/fast.md, 2026-09-10 --
    supersedes doc 14's original "AND-of-predicates only" boundary, see
    doc/adr/0001-screener-redis-cache-and-boolean-logic.md). Optional and
    additive: a ScreenQuery with no `where` behaves exactly as before
    (metric_predicates/categorical_predicates combined with AND), so every
    existing caller (ai_query, saved screens, doc 14b's golden-set tests)
    is unaffected.

    Ranked operators (top_n/bottom_n) do not belong inside a boolean tree
    -- they select a fixed-size slice of whatever the tree already
    filtered to, not a per-company true/false test -- so they stay in
    ScreenQuery.metric_predicates only; a leaf here rejects them.
    """

    op: Literal["and", "or", "not"]
    predicates: list[Union["MetricPredicate", "CategoricalPredicate", "PredicateGroup"]] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_shape(self) -> "PredicateGroup":
        if self.op == "not" and len(self.predicates) != 1:
            raise ValueError("'not' takes exactly one child predicate")
        for p in self.predicates:
            if isinstance(p, MetricPredicate) and p.operator in RANKED_OPERATORS:
                raise ValueError(f"operator {p.operator!r} is not valid inside a boolean-tree 'where' clause")
        return self


class CategoricalPredicate(BaseModel):
    # "sector" added 2026-08-21 (doc 10 Sec 12/doc 26 Sec 2.8/doc 28) --
    # core.company.sector, a curated SIC-range bucket
    # (company_master/sector_bucket.py), coarser than sic_code/
    # sic_description but the field an investor actually means by "tech
    # companies"/"financial companies" rather than an exact SIC match.
    field: Literal["sic_code", "sic_description", "sector"]
    operator: Literal["="]
    value: str


class ScreenQuery(BaseModel):
    metric_predicates: list[MetricPredicate] = []
    categorical_predicates: list[CategoricalPredicate] = []
    # Boolean-tree filter, additive alongside the two flat lists above
    # (2026-09-10, doc/adr/0001). When set, `where` is the ONLY thing that
    # determines which companies pass -- metric_predicates/
    # categorical_predicates are ignored for filtering in that case (a
    # non-ranked entry in metric_predicates alongside `where` would be
    # ambiguous: is it AND'd in, or dropped? Reject rather than guess --
    # see the validator below). Ranked ops (top_n/bottom_n) still work
    # alongside `where`: they rank whatever the tree already filtered to.
    where: PredicateGroup | None = None
    include_inactive: bool = False
    sort_by: str | None = None
    sort_desc: bool = True
    limit: int | None = Field(default=None, ge=1)
    # Metrics returned for comparison but never used to decide whether a
    # company matches. This keeps presentation concerns explicit without
    # weakening or silently changing the user's filter.
    display_metrics: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def _check_at_most_one_ranked_predicate(self) -> "ScreenQuery":
        # top_n/bottom_n determines the result size directly -- doc 14 scopes
        # this to simple AND-of-predicates, not a defined combination of two
        # independent rankings. Reject rather than guess which one wins.
        ranked = [p for p in self.metric_predicates if p.operator in RANKED_OPERATORS]
        if len(ranked) > 1:
            raise ValueError("at most one top_n/bottom_n predicate is supported per query")
        return self

    @model_validator(mode="after")
    def _check_where_not_mixed_with_flat_filters(self) -> "ScreenQuery":
        if self.where is not None:
            non_ranked = [p for p in self.metric_predicates if p.operator not in RANKED_OPERATORS]
            if non_ranked or self.categorical_predicates:
                raise ValueError(
                    "cannot combine 'where' with non-ranked metric_predicates or "
                    "categorical_predicates -- put every filter condition inside 'where' "
                    "(top_n/bottom_n predicates are still allowed alongside it)"
                )
        return self


PredicateGroup.model_rebuild()

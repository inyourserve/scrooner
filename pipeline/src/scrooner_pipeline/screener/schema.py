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
from typing import Literal

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
    include_inactive: bool = False
    sort_by: str | None = None
    sort_desc: bool = True
    limit: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _check_at_most_one_ranked_predicate(self) -> "ScreenQuery":
        # top_n/bottom_n determines the result size directly -- doc 14 scopes
        # this to simple AND-of-predicates, not a defined combination of two
        # independent rankings. Reject rather than guess which one wins.
        ranked = [p for p in self.metric_predicates if p.operator in RANKED_OPERATORS]
        if len(ranked) > 1:
            raise ValueError("at most one top_n/bottom_n predicate is supported per query")
        return self

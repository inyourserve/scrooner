"""Provider-neutral boundary for the optional LLM interpretation fallback.

The deterministic interpreter remains production behavior until a provider is
selected and this adapter is explicitly enabled. A placeholder key is treated
as not configured; it can never trigger a network call accidentally.
"""

import os
from dataclasses import dataclass
from typing import Literal, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from scrooner_pipeline.ai_query.interpreter import AmbiguityNote, InterpretationResult
from scrooner_pipeline.screener.schema import (
    CategoricalPredicate,
    MetricPredicate,
    PredicateGroup,
    ScreenQuery,
)


PLACEHOLDER_API_KEY = "replace_with_ai_provider_api_key"


class LLMNotConfiguredError(RuntimeError):
    pass


class InvalidLLMInterpretationError(ValueError):
    """The provider returned data that is unsafe or internally inconsistent."""


@dataclass(frozen=True)
class MetricCandidate:
    """The only metric information an LLM may use for one interpretation."""

    metric_name: str
    operators: frozenset[str]


class ModelAmbiguity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phrase: str = Field(min_length=1)
    candidates: list[str] = Field(min_length=2)


class ModelInterpretation(BaseModel):
    """Strict provider-neutral wire contract for an LLM response.

    This is deliberately separate from ``InterpretationResult``: a model
    response is untrusted external input and must not become executable merely
    because it resembles a ScreenQuery.
    """

    model_config = ConfigDict(extra="forbid")

    status: Literal["ready", "needs_clarification", "unsupported", "invalid"]
    query: dict | None
    explanation: str = Field(min_length=1)
    unrecognized: list[str]
    ambiguous: list[ModelAmbiguity]

    @model_validator(mode="after")
    def _enforce_status_gate(self) -> "ModelInterpretation":
        if self.status == "ready":
            if self.query is None or self.unrecognized or self.ambiguous:
                raise ValueError("ready interpretations require a complete query and no unresolved text")
        elif self.query is not None:
            raise ValueError("non-ready interpretations must not contain an executable query")
        return self


class StructuredLLMClient(Protocol):
    def interpret(
        self,
        text: str,
        *,
        candidates: list[MetricCandidate],
        current_query: dict | None = None,
    ) -> InterpretationResult: ...


@dataclass(frozen=True)
class LLMSettings:
    enabled: bool
    provider: str
    model: str
    api_key: str

    @property
    def configured(self) -> bool:
        return bool(
            self.enabled
            and self.provider
            and self.model
            and self.api_key
            and self.api_key != PLACEHOLDER_API_KEY
        )

    @classmethod
    def from_environment(cls) -> "LLMSettings":
        return cls(
            enabled=os.getenv("SCROONER_LLM_ENABLED", "false").lower() == "true",
            provider=os.getenv("SCROONER_LLM_PROVIDER", ""),
            model=os.getenv("SCROONER_LLM_MODEL", ""),
            api_key=os.getenv("SCROONER_LLM_API_KEY", PLACEHOLDER_API_KEY),
        )


class DisabledLLMInterpreter:
    """Explicit safe state until a concrete provider adapter is approved."""

    def __init__(self, settings: LLMSettings | None = None) -> None:
        self.settings = settings or LLMSettings.from_environment()

    def interpret(
        self,
        text: str,
        *,
        candidates: list[MetricCandidate] | None = None,
        current_query: dict | None = None,
    ) -> InterpretationResult:
        del text, candidates, current_query
        raise LLMNotConfiguredError(
            "LLM interpretation is disabled; deterministic interpretation remains available"
        )


def _metric_predicates(query: ScreenQuery) -> list[MetricPredicate]:
    predicates = list(query.metric_predicates)

    def visit(node: MetricPredicate | CategoricalPredicate | PredicateGroup) -> None:
        if isinstance(node, MetricPredicate):
            predicates.append(node)
        elif isinstance(node, PredicateGroup):
            for child in node.predicates:
                visit(child)

    if query.where is not None:
        visit(query.where)
    return predicates


def _reject_unknown_query_fields(raw_query: object) -> None:
    """Apply ``extra='forbid'`` semantics without changing ScreenQuery.

    ScreenQuery predates the LLM boundary and intentionally accepts additive
    fields from trusted callers. Model output has a stricter threat model, so
    reject unknown keys recursively before Pydantic can ignore them.
    """

    def require_mapping(value: object, location: str) -> Mapping:
        if not isinstance(value, Mapping):
            raise InvalidLLMInterpretationError(f"LLM returned a non-object at {location}")
        return value

    def reject_extra(value: Mapping, allowed: set[str], location: str) -> None:
        extra = sorted(set(value) - allowed)
        if extra:
            raise InvalidLLMInterpretationError(f"LLM returned unknown fields at {location}: {extra}")

    def visit_predicate(value: object, location: str) -> None:
        predicate = require_mapping(value, location)
        if "op" in predicate:
            reject_extra(predicate, {"op", "predicates"}, location)
            children = predicate.get("predicates")
            if not isinstance(children, list):
                raise InvalidLLMInterpretationError(f"LLM returned invalid predicates at {location}")
            for index, child in enumerate(children):
                visit_predicate(child, f"{location}.predicates[{index}]")
        elif "metric_name" in predicate:
            reject_extra(predicate, {"metric_name", "operator", "value", "value_range", "n"}, location)
        else:
            reject_extra(predicate, {"field", "operator", "value"}, location)

    query = require_mapping(raw_query, "query")
    reject_extra(
        query,
        {
            "metric_predicates",
            "categorical_predicates",
            "where",
            "include_inactive",
            "sort_by",
            "sort_desc",
            "limit",
            "display_metrics",
        },
        "query",
    )
    for field_name in ("metric_predicates", "categorical_predicates"):
        values = query.get(field_name, [])
        if not isinstance(values, list):
            raise InvalidLLMInterpretationError(f"LLM returned invalid {field_name}")
        for index, predicate in enumerate(values):
            visit_predicate(predicate, f"query.{field_name}[{index}]")
    if query.get("where") is not None:
        visit_predicate(query["where"], "query.where")


def validate_model_interpretation(
    payload: object,
    *,
    candidates: list[MetricCandidate],
) -> InterpretationResult:
    """Convert an untrusted provider payload into the executable contract.

    Structural Pydantic validation happens first. A second semantic pass then
    enforces the per-request candidate allow-list for filters, sorting and
    display metrics. Therefore neither a prompt injection nor a syntactically
    valid invented field can reach the Screener.
    """

    try:
        model_result = ModelInterpretation.model_validate(payload)
    except ValidationError as error:
        raise InvalidLLMInterpretationError("LLM response did not match the interpretation schema") from error

    ambiguities = [
        AmbiguityNote(phrase=item.phrase, candidates=item.candidates)
        for item in model_result.ambiguous
    ]
    if len({candidate.metric_name for candidate in candidates}) != len(candidates):
        raise InvalidLLMInterpretationError("candidate allow-list contains duplicate metric names")
    allowed = {candidate.metric_name: candidate.operators for candidate in candidates}
    for ambiguity in ambiguities:
        unknown_candidates = sorted(set(ambiguity.candidates) - allowed.keys())
        if unknown_candidates:
            raise InvalidLLMInterpretationError(
                f"LLM returned ambiguity candidates outside the candidate allow-list: {unknown_candidates}"
            )
    if model_result.status != "ready":
        return InterpretationResult(
            query=None,
            explanation=model_result.explanation,
            unrecognized=model_result.unrecognized,
            ambiguous=ambiguities,
        )

    _reject_unknown_query_fields(model_result.query)
    try:
        query = ScreenQuery.model_validate(model_result.query)
    except ValidationError as error:
        raise InvalidLLMInterpretationError("LLM query did not match ScreenQuery") from error
    if not query.metric_predicates and not query.categorical_predicates and query.where is None:
        raise InvalidLLMInterpretationError("LLM returned a ready query with no filtering or ranking criteria")

    for predicate in _metric_predicates(query):
        if predicate.metric_name not in allowed:
            raise InvalidLLMInterpretationError(
                f"LLM returned metric outside the candidate allow-list: {predicate.metric_name!r}"
            )
        if predicate.operator not in allowed[predicate.metric_name]:
            raise InvalidLLMInterpretationError(
                f"LLM returned unsupported operator {predicate.operator!r} for {predicate.metric_name!r}"
            )

    referenced = set(query.display_metrics)
    if query.sort_by is not None:
        referenced.add(query.sort_by)
    unknown_references = sorted(referenced - allowed.keys())
    if unknown_references:
        raise InvalidLLMInterpretationError(
            f"LLM returned metric references outside the candidate allow-list: {unknown_references}"
        )

    return InterpretationResult(
        query=query,
        recognized_query=query,
        explanation=model_result.explanation,
    )

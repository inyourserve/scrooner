"""Zero-token edits to an existing ScreenQuery using stored templates.

These templates cover the common conversational action "change only this
number". They always return a complete ScreenQuery, never a patch, so the same
structural and semantic validation used for a newly-created screen still runs.
Unknown or ambiguous edits return ``None`` for a later interpreter to handle.
"""

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from importlib.resources import files

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from scrooner_pipeline.ai_query.aliases import METRIC_ALIASES
from scrooner_pipeline.ai_query.interpreter import InterpretationResult
from scrooner_pipeline.ai_query.normalizer import normalize_query_text
from scrooner_pipeline.screener.schema import MetricPredicate, PredicateGroup, ScreenQuery


_MAGNITUDES = {
    "k": Decimal("1000"),
    "thousand": Decimal("1000"),
    "m": Decimal("1000000"),
    "mn": Decimal("1000000"),
    "million": Decimal("1000000"),
    "b": Decimal("1000000000"),
    "bn": Decimal("1000000000"),
    "billion": Decimal("1000000000"),
    "t": Decimal("1000000000000"),
    "tn": Decimal("1000000000000"),
    "trillion": Decimal("1000000000000"),
}
_VALUE_RE = re.compile(
    r"^\$?(?P<number>[\d,]*\.?\d+)\s*"
    r"(?P<magnitude>thousand|million|billion|trillion|k|m|mn|b|bn|t|tn)?"
    r"(?P<percent>%)?$",
    re.IGNORECASE,
)


class StoredEditTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    pattern: str


@dataclass(frozen=True)
class CompiledEditTemplate:
    id: str
    pattern: re.Pattern[str]


@lru_cache(maxsize=1)
def load_edit_templates() -> tuple[CompiledEditTemplate, ...]:
    resource = files("scrooner_pipeline.ai_query").joinpath("edit_templates.json")
    try:
        raw_templates = json.loads(resource.read_text(encoding="utf-8"))
        templates = [StoredEditTemplate.model_validate(item) for item in raw_templates]
    except (OSError, json.JSONDecodeError, ValidationError, TypeError) as error:
        raise RuntimeError("stored natural-language edit templates are invalid") from error

    ids = [template.id for template in templates]
    if len(ids) != len(set(ids)):
        raise RuntimeError("stored natural-language edit template IDs must be unique")
    try:
        return tuple(
            CompiledEditTemplate(template.id, re.compile(template.pattern, re.IGNORECASE))
            for template in templates
        )
    except re.error as error:
        raise RuntimeError("stored natural-language edit template regex is invalid") from error


def _parse_value(text: str) -> Decimal | None:
    match = _VALUE_RE.fullmatch(text.strip())
    if match is None:
        return None
    try:
        value = Decimal(match.group("number").replace(",", ""))
    except InvalidOperation:
        return None
    magnitude = match.group("magnitude")
    if magnitude:
        value *= _MAGNITUDES[magnitude.lower()]
    if match.group("percent"):
        value /= Decimal("100")
    return value


def _editable_predicates(query: ScreenQuery) -> list[MetricPredicate]:
    predicates = [
        predicate
        for predicate in query.metric_predicates
        if predicate.operator in {">", ">=", "<", "<=", "=", "!="}
    ]

    def visit(node: MetricPredicate | PredicateGroup | object) -> None:
        if isinstance(node, MetricPredicate) and node.operator in {">", ">=", "<", "<=", "=", "!="}:
            predicates.append(node)
        elif isinstance(node, PredicateGroup):
            for child in node.predicates:
                visit(child)

    if query.where is not None:
        visit(query.where)
    return predicates


def _replace_metric_value(value: object, metric_name: str, replacement: Decimal) -> int:
    """Mutate a model-dumped query tree and return the replacement count."""
    if isinstance(value, dict):
        if value.get("metric_name") == metric_name and value.get("operator") in {">", ">=", "<", "<=", "=", "!="}:
            value["value"] = replacement
            return 1
        return sum(_replace_metric_value(child, metric_name, replacement) for child in value.values())
    if isinstance(value, list):
        return sum(_replace_metric_value(child, metric_name, replacement) for child in value)
    return 0


def interpret_edit(text: str, current_query: ScreenQuery) -> InterpretationResult | None:
    """Apply a stored number-change template, or return ``None`` safely."""
    normalized = normalize_query_text(text)
    matched: re.Match[str] | None = None
    template_id: str | None = None
    for template in load_edit_templates():
        candidate = template.pattern.fullmatch(normalized.text)
        if candidate is not None:
            matched = candidate
            template_id = template.id
            break
    if matched is None:
        return None

    replacement = _parse_value(matched.group("value"))
    if replacement is None:
        return None

    editable = _editable_predicates(current_query)
    metric_phrase = matched.groupdict().get("metric")
    if metric_phrase is None or metric_phrase.lower() in {"it", "that", "the value"}:
        if len(editable) != 1:
            return None
        metric_name = editable[0].metric_name
    else:
        metric_name = METRIC_ALIASES.get(metric_phrase.strip().lower())
        if metric_name is None:
            return None
        matching = [predicate for predicate in editable if predicate.metric_name == metric_name]
        if len(matching) != 1:
            return None

    dumped = current_query.model_dump(mode="python")
    if _replace_metric_value(dumped, metric_name, replacement) != 1:
        return None
    updated = ScreenQuery.model_validate(dumped)
    return InterpretationResult(
        query=updated,
        recognized_query=updated,
        explanation=f"Updated {metric_name} to {replacement} using stored template {template_id}.",
        corrections=list(normalized.corrections),
    )

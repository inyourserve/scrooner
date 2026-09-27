"""Stored, reviewed screen templates and their popular cache-warm variants."""

import json
from decimal import Decimal
from functools import lru_cache
from importlib.resources import files
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery


class StoredScreenTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1)
    metric_name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    operator: Literal[">", ">=", "<", "<=", "=", "!="]
    value_type: Literal["decimal", "percentage", "currency"]
    prewarm_values: list[Decimal] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def _unique_positive_values(self) -> "StoredScreenTemplate":
        if len(self.prewarm_values) != len(set(self.prewarm_values)):
            raise ValueError("prewarm_values must be unique")
        if any(value < 0 for value in self.prewarm_values):
            raise ValueError("prewarm_values must not be negative")
        return self

    def instantiate(self, value: Decimal | str | int) -> ScreenQuery:
        return ScreenQuery(
            metric_predicates=[
                MetricPredicate(
                    metric_name=self.metric_name,
                    operator=self.operator,
                    value=Decimal(value),
                )
            ]
        )


@lru_cache(maxsize=1)
def load_screen_templates() -> tuple[StoredScreenTemplate, ...]:
    resource = files("scrooner_pipeline.ai_query").joinpath("screen_templates.json")
    try:
        raw = json.loads(resource.read_text(encoding="utf-8"))
        templates = tuple(StoredScreenTemplate.model_validate(item) for item in raw)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError) as error:
        raise RuntimeError("stored screen templates are invalid") from error
    ids = [template.id for template in templates]
    if len(ids) != len(set(ids)):
        raise RuntimeError("stored screen template IDs must be unique")
    return templates


def prewarm_queries() -> tuple[tuple[str, ScreenQuery], ...]:
    return tuple(
        (template.id, template.instantiate(value))
        for template in load_screen_templates()
        for value in template.prewarm_values
    )

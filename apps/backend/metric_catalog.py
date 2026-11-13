"""Human-facing metadata for the Screener's validated metric catalog.

The database remains authoritative for which metrics are currently
screenable and for their formula/version. Presentation fields now come from
the metric registry; a metric absent from the registry still gets an honest
generated label and neutral number formatting, and the registry agreement
test fails if any registry metric were ever to fall back.
"""

from dataclasses import dataclass

from scrooner_pipeline.metrics.generate import presentation as registry_presentation


@dataclass(frozen=True)
class MetricPresentation:
    display_name: str
    short_definition: str
    category: str
    value_type: str


# GENERATED from the metric registry (pipeline/src/scrooner_pipeline/metrics/registry/*.csv).
# Edit the registry row (label, short_definition, family, value_type), never this module.
METRIC_PRESENTATION: dict[str, MetricPresentation] = {
    metric_id: MetricPresentation(*fields)
    for metric_id, fields in registry_presentation().items()
}

OPERATOR_ORDER = [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"]


def presentation_for(metric_name: str) -> MetricPresentation:
    return METRIC_PRESENTATION.get(
        metric_name,
        MetricPresentation(
            metric_name.replace("_", " ").title(),
            "Defined Scrooner metric.",
            "Other",
            "number",
        ),
    )

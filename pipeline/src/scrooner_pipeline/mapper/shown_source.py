"""The one switch for calculators that read inputs with their own SQL (one-display-path plan step 5, M3).

Flag `serve.shown_cell_path@1` off (default): `analytics.canonical_fact`, no extra filter: byte-identical SQL to before.
Flag on: `analytics.shown_cell` (draft 0135) restricted to cell_state = 'value', i.e. cells the page shows whose latest
proof is PROVEN; an unproven cell is absent so the metric gets a null with a reason, never a fallback. The view has the
same column names the callers use (company_id, canonical_concept_id, period_id, value, source_fact_ids). It has FY and
instant grain only, so quarter inputs are absent with the flag on (PIPELINE.md section 7 M3 hard gate)."""

from __future__ import annotations

from scrooner_pipeline.common.rule_flags import rule_enabled

SHOWN_CELL_PATH_RULE = "serve.shown_cell_path@1"


def fact_relation() -> str:
    return (
        "analytics.shown_cell"
        if rule_enabled(SHOWN_CELL_PATH_RULE)
        else "analytics.canonical_fact"
    )


def value_filter() -> str:
    """An `and ...` fragment (leading space) to add to the where clause; empty with the flag off."""
    return " and cf.cell_state = 'value'" if rule_enabled(SHOWN_CELL_PATH_RULE) else ""

"""Stage 3c -- Metric formula definitions (doc 11). Seeds
analytics.metric_definition + metric_definition_input for doc 02's 18
locked V1 metrics (20 DB rows -- Revenue Growth and EPS Growth each split
into separate YoY / 3Y-CAGR metric_definition rows, since they produce
distinct values needing independent storage/versioning; still 18 product-
facing metrics per doc 02's guardrail, not a scope expansion).

ROIC's formula (left open in doc 02, explicitly assigned to this stage to
pin down "with a version number") is resolved here:

    NOPAT = Operating Income x (1 - Income Tax Expense / Income Before Tax)
    Invested Capital = Total Debt + Stockholders' Equity - Cash & Equivalents
    ROIC = NOPAT / Invested Capital

Verified live 2026-08-16 against AAPL Q1 FY2026 (the only period on hand
with all six inputs simultaneously authoritative) before locking this in:
tax_rate=17.46%, invested_capital=$131.4B, single-quarter NOPAT/invested
capital = 31.95%. Also checked -- and rejected -- naive x4 quarterly
annualization: it gives 127.8% ROIC, implausible, because AAPL's Q1 (the
holiday quarter) is its seasonally strongest by far, so scaling one
quarter's operating income by 4 badly overstates the year. Same structural
problem exists for ROE (net income, a flow, over stockholders' equity, a
point-in-time stock) -- Interest Coverage Ratio does NOT have this issue
(operating income and interest expense are both flows over the same
period, no stock/flow mismatch), nor do the margin ratios (all flow/flow)
or Debt/Equity and Current Ratio (both point-in-time/point-in-time).

Consequence for Stage 3d: ROIC and ROE compute directly on FY periods
(where the income-statement figure already naturally represents a full
year, no distortion) but are deliberately NOT computed from a bare
quarterly period until Stage 3e's TTM windows exist to do it properly.
Every other metric in this list is fine on any period basis its inputs
resolve for.
"""

import psycopg
import structlog

from scrooner_pipeline.metrics.generate import v1_definition_rows

logger = structlog.get_logger()

# GENERATED from the metric registry (pipeline/src/scrooner_pipeline/metrics/registry/*.csv) since
# 2026-11-13: edit the registry row, never this list. Row shape:
# (metric_name, formula_description, requires_price, quarterly_needs_ttm, inputs)
# inputs: list of (canonical_concept_name, role). For the expanded list, an empty inputs list marks a
# composite or externally sourced metric computed in its own mapper module (see main_calculator.py).
# tests/unit/test_metric_registry_agreement.py holds this output equal to the frozen pre-registry copy.
METRIC_DEFINITIONS: list[tuple[str, str, bool, bool, list[tuple[str, str]]]] = (
    v1_definition_rows()
)


def seed(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("select id, name from analytics.canonical_concept")
        concept_id_by_name = {name: cid for cid, name in cur.fetchall()}

    stats = {"considered": len(METRIC_DEFINITIONS), "defined": 0, "inputs_linked": 0}
    with conn.cursor() as cur:
        for (
            metric_name,
            formula_description,
            requires_price,
            _quarterly_needs_ttm,
            inputs,
        ) in METRIC_DEFINITIONS:
            cur.execute(
                """
                insert into analytics.metric_definition
                    (metric_name, formula_version, formula_description, requires_price, status)
                values (%s, 1, %s, %s, 'active')
                on conflict (metric_name, formula_version) do update
                    set formula_description = excluded.formula_description,
                        requires_price = excluded.requires_price
                returning id
                """,
                (metric_name, formula_description, requires_price),
            )
            metric_definition_id = cur.fetchone()[0]
            stats["defined"] += 1

            cur.execute(
                "delete from analytics.metric_definition_input where metric_definition_id = %s",
                (metric_definition_id,),
            )
            for canonical_concept_name, role in inputs:
                cur.execute(
                    """
                    insert into analytics.metric_definition_input (metric_definition_id, canonical_concept_id, role)
                    values (%s, %s, %s)
                    """,
                    (
                        metric_definition_id,
                        concept_id_by_name[canonical_concept_name],
                        role,
                    ),
                )
                stats["inputs_linked"] += 1
    conn.commit()
    logger.info("definitions.seeded", **stats)
    return stats

"""Expanded metric definitions (doc 18 Tier A / doc 26, built 2026-08-18
to raise data-point coverage). Same additive pattern as
expanded_concepts.py -- new rows only, doc 02's locked 18-metric list
(mapper/definitions.py) is not touched or reordered.

Seven definitions (roa, quick_ratio, sbc_pct_revenue, ebitda, debtor_days,
inventory_days, and payables_days) provide inputs to calculate.py's generic
per-role engine (FORMULA_SHAPES is widened additively there too). Definitions
with no inputs are composite or externally sourced metrics whose calculation
lives in mapper/expanded_metrics.py or mapper/quality_score.py; their inputs
cannot be represented by the generic engine's single-period canonical-concept
model.

net_debt_ebitda does NOT require price (Net Debt and EBITDA are both
price-independent) -- doc 18 already named this distinction; don't
conflate it with the metrics that genuinely need price.

Five more definitions added 2026-08-21, acting on
doc/learnings/core-fact-utilization-study.md's ranked recommendations
(expanded_concepts.py's own docstring has the full concept-level detail,
including why total_debt's alternate widening was reversed rather than
implemented):

- goodwill_pct_assets: real calculate.py-engine input (ratio shape),
  same as roa/quick_ratio.
- eps_dilution_spread: (basic_eps - diluted_eps) / basic_eps, a real
  calculate.py-engine input too -- basic_eps appears TWICE in its own
  inputs list, once as "add" and once as "denominator". Checked before
  relying on this: analytics.metric_definition_input has no unique
  constraint beyond its own surrogate primary key (verified live against
  pg_constraint), and calculate.py's per-period loop iterates each
  (concept, role) input row independently rather than deduping by
  concept_id -- so one concept feeding two different roles for the same
  metric is already safe with zero engine changes, not a new capability
  being assumed.
- ar_change_reconciliation_gap / inventory_change_reconciliation_gap /
  ap_change_reconciliation_gap: documentation-only, computed in the new
  mapper/reconciliation.py (FY-vs-prior-FY balance-sheet delta compared
  against the company's own reported cash-flow-statement change) --
  doesn't fit this engine's single-period model, same reasoning as
  cash_conversion_cycle needing expanded_metrics.py instead.

Two more added same day, acting on doc 28 (Trendlyne gap analysis)
items #1/#4:
- rnd_intensity: R&D / Revenue, real calculate.py-engine input (ratio shape).
- net_interest_income: Interest Income - Interest Expense, real
  calculate.py-engine input (sum_diff shape) -- same shape fcf already uses.

Six more added 2026-08-22 (a P0/coverage execution pass, doc 18 Tier A's
2 still-unbuilt items plus 4 new ones from the utilization-study
backlog):
- capex_pct_revenue, sga_pct_revenue: both real calculate.py-engine
  ratio inputs, zero new logic.
- effective_tax_rate_gap: documentation-only -- compares the company's
  own reported effective_tax_rate_reported against the rate ROIC
  already derives internally (income_tax_expense/income_before_tax), a
  cross-validation signal (doc 18's own #5 ranked idea). Computed in the
  new mapper/tax_reconciliation.py -- needs a metric's own separate
  per-period division that doesn't fit a single canonical-concept role.
- fcf_growth_3y_cagr, fcf_growth_5y_cagr: documentation-only -- FCF is
  itself a computed metric_value (sum_diff of cfo-capex), not a raw
  canonical_fact, so ttm.py's GROWTH_METRICS (which reads canonical_fact
  by concept) can't reach it directly. Computed in the new
  mapper/fcf_growth.py, reusing ttm.py's own _growth_value() function
  unchanged.
- dividend_growth_streak_years: documentation-only -- consecutive most-
  recent FY years with dividends_per_share strictly increasing, same
  "as of latest FY" single-value shape as profitable_streak_years.
  Computed in the new mapper/dividend_streak.py.

Six more added 2026-08-29 (zero-new-fetch coverage pass -- payout ratio,
pretax margin, net cash, dividend growth):
- payout_ratio: Dividends per Share / Diluted EPS, real calculate.py-engine
  ratio input. dividends_per_share and diluted_eps are both already
  canonical concepts (concepts.py, Stage 3a) -- no new concept curation.
- pretax_margin: Income Before Tax / Revenue, real ratio input.
  income_before_tax was already a canonical concept but only ever
  consumed as ROIC's tax_rate_denominator role -- reused here unchanged,
  not recreated.
- net_cash / net_cash_per_share: cash_and_equivalents - total_debt, and
  that same figure / shares_outstanding. All three inputs are already
  canonical concepts, all balance_sheet (instant) -- fits the EXISTING
  sum_diff / sum_diff_ratio shapes exactly (same shapes current_ratio's
  sibling metrics quick_ratio/fcf_margin already use for all-instant or
  mixed instant inputs), so no new formula shape and no expanded_metrics.py
  hardcoded function needed -- checked before assuming either was required.
- dps_growth_yoy / dps_growth_3y_cagr: documentation-only -- computed in
  mapper/ttm.py's GROWTH_METRICS, same purely-additive dict-entry pattern
  as the 5Y/10Y revenue/EPS CAGR additions (2026-08-19). "dps" abbreviation
  matches this file's existing "eps" convention (eps_growth_yoy uses
  concept diluted_eps but is named eps_*, not diluted_eps_*).
"""

import psycopg
import structlog

from scrooner_pipeline.metrics.generate import expanded_definition_rows

logger = structlog.get_logger()

# GENERATED from the metric registry (pipeline/src/scrooner_pipeline/metrics/registry/*.csv) since
# 2026-11-13: edit the registry row, never this list. Row shape:
# (metric_name, formula_description, requires_price, inputs)
# inputs: list of (canonical_concept_name, role). For the expanded list, an empty inputs list marks a
# composite or externally sourced metric computed in its own mapper module (see main_calculator.py).
# tests/unit/test_metric_registry_agreement.py holds this output equal to the frozen pre-registry copy.
METRIC_DEFINITIONS: list[tuple[str, str, bool, list[tuple[str, str]]]] = (
    expanded_definition_rows()
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
    logger.info("expanded_definitions.seeded", **stats)
    return stats

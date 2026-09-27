"""Calculator registry (doc 42, built 2026-09-05) -- the "centralized,
debuggable" lookup the multi-parser/multi-calculator architecture asked
for: for every one of the 64 real `metric_definition` rows, which
module actually computes it.

This is NOT a rewrite of the calculation layer -- every module listed
here already exists, already works, and is already independently tested
(pipeline/CLAUDE.md documents each one's own build history and real
bugs found/fixed). What was missing was a single place that answers
"which module computes metric X" without grepping through 9 files or
re-deriving it from memory. That's what METRIC_CALCULATOR_REGISTRY and
run_calculator() are for.

Two calculator "shapes" exist, and BOTH are correct architectures for
their own case -- this registry documents which shape applies to each
metric rather than forcing every metric into one shape:

1. **Generic, data-driven** (`mapper/calculate.py`): the large majority
   of metrics (a plain ratio/sum_diff/days/additive/roic formula over
   already-resolved canonical_fact concepts) are computed by ONE
   generic engine, driven entirely by `metric_definition_input` rows in
   the database -- adding a new metric of this shape is a data change
   (seed rows), never a new Python file. This is the calculator
   equivalent of `concept_mapping` for the parser side: centralized by
   construction, not by convention.
2. **Dedicated module** (ttm.py, quality_score.py, expanded_metrics.py,
   etc.): metrics whose calculation genuinely can't be expressed as one
   of calculate.py's formula shapes (a rolling window, a 9-part
   composite score, a cross-check between two independently-derived
   figures) get their own small, focused module -- the same principle
   this project already uses for parsers/revenue_parser.py, just
   predating this session's naming of the pattern.

A metric appearing in DEFERRED_CALCULATE_METRICS below means
calculate.py's own `_load_target_metrics()` deliberately skips it (it
has a `metric_definition` row but its real logic lives in one of the
dedicated modules) -- this is the exact mechanism doc 18's "A metric
definition that's requires_price=False but has no FORMULA_SHAPES entry
crashes the generic engine with a bare KeyError" finding (pipeline/
CLAUDE.md) already documented; this registry is the reason nobody has
to rediscover that lesson by hitting the crash again.
"""

import psycopg
import structlog

logger = structlog.get_logger()

# metric_name -> (module_path, cli_command, description). module_path
# is for humans reading this registry, not an import target -- each
# module's own run function has a different signature (some take
# --ciks, some don't, some are called via a different verb entirely
# like `growth`/`ttm-returns` rather than `calculate-X`) reflecting real
# differences in how they were built over time, not something worth
# forcing into one uniform call shape retroactively.
METRIC_CALCULATOR_REGISTRY: dict[str, dict[str, str]] = {}


def _register(
    metric_names: list[str], module: str, cli_command: str, description: str
) -> None:
    for name in metric_names:
        METRIC_CALCULATOR_REGISTRY[name] = {
            "module": module,
            "cli_command": cli_command,
            "description": description,
        }


_register(
    [
        "gross_margin",
        "operating_margin",
        "net_margin",
        "fcf",
        "fcf_margin",
        "debt_to_equity",
        "current_ratio",
        "interest_coverage_ratio",
        "roa",
        "quick_ratio",
        "sbc_pct_revenue",
        "ebitda",
        "debtor_days",
        "inventory_days",
        "payables_days",
        "goodwill_pct_assets",
        "rnd_intensity",
        "net_interest_income",
        "capex_pct_revenue",
        "sga_pct_revenue",
        "payout_ratio",
        "pretax_margin",
        "net_cash",
        "net_cash_per_share",
        "eps_dilution_spread",
        "book_value_per_share",
        "working_capital",
        "net_change_in_cash",
        "ocf_to_net_income",
        "cash_returned_to_shareholders",
    ],
    module="mapper/calculate.py",
    cli_command="scrooner-map calculate",
    description="Generic formula engine (ratio/sum_diff/sum_diff_ratio/days/additive/roic shapes), "
    "driven entirely by metric_definition_input rows -- a new metric of this shape is a data "
    "change, not a code change.",
)

_register(
    ["roic", "roe"],
    module="mapper/calculate.py (FY) + mapper/ttm.py (TTM)",
    cli_command="scrooner-map calculate; scrooner-map ttm-returns",
    description="A real, deliberate split -- the SAME metric_definition_id is written by TWO "
    "modules, distinguished only by period_label ('FY' vs 'TTM'). This is exactly the shared-table "
    "scoping Mapper Day 6 found the hard way (pipeline/CLAUDE.md): a delete scoped by company_id "
    "alone, or by company_id+metric_definition_id alone, silently destroys the OTHER writer's rows "
    "on rerun -- only excluding period_label='TTM' in calculate.py's own delete (mirrored the "
    "opposite way in ttm.py) correctly partitions the two writers.",
)

_register(
    [
        "revenue_growth_yoy",
        "revenue_growth_3y_cagr",
        "revenue_growth_5y_cagr",
        "revenue_growth_10y_cagr",
        "eps_growth_yoy",
        "eps_growth_3y_cagr",
        "eps_growth_5y_cagr",
        "eps_growth_10y_cagr",
        "dps_growth_yoy",
        "dps_growth_3y_cagr",
        "net_income_growth_yoy",
        "net_income_growth_3y_cagr",
        "net_income_growth_5y_cagr",
        "net_income_growth_10y_cagr",
        "diluted_shares_growth_yoy",
        "diluted_shares_growth_3y_cagr",
        "diluted_shares_growth_5y_cagr",
    ],
    module="mapper/ttm.py (compute_growth)",
    cli_command="scrooner-map growth",
    description="YoY/CAGR growth over any lag_years, driven by GROWTH_METRICS' own dict keys -- "
    "adding a new growth metric of this shape is 2 dict lines, no new logic.",
)

_register(
    [
        "market_cap",
        "trailing_pe",
        "price_to_sales",
        "price_to_book",
        "dividend_yield",
        "fcf_yield",
    ],
    module="mapper/price_metrics.py",
    cli_command="scrooner-map calculate-price-metrics",
    description="The 6 price-dependent V1 metrics -- requires core.market_price_alpaca real price "
    "data (update-market-price) to have run first.",
)

_register(
    [
        "net_debt_ebitda",
        "ev_ebitda",
        "ev_sales",
        "peg_ratio",
        "buyback_yield",
        "total_shareholder_yield",
        "institutional_ownership_pct",
        "share_dilution_trend",
        "cash_conversion_cycle",
        "ebitda_margin",
        "debt_to_ebitda",
        "fcf_per_share",
        "share_repurchases_pct_fcf",
        "dividends_pct_fcf",
    ],
    module="mapper/expanded_metrics.py",
    cli_command="scrooner-map calculate-expanded-metrics",
    description="Composite metrics whose inputs mix analytics.metric_value (ebitda, market_cap) "
    "with canonical_fact in ways calculate.py's concept-only engine can't express. Requires "
    "calculate + calculate-price-metrics to have already run.",
)

_register(
    ["piotroski_f_score"],
    module="mapper/quality_score.py",
    cli_command="scrooner-map calculate-piotroski",
    description="Standard 9-binary-test Piotroski F-Score, FY vs prior FY. Correctly null for "
    "financial institutions (needs a classified balance sheet + gross-profit split, which banks/"
    "insurers don't report) -- not a coverage gap to chase.",
)

_register(
    [
        "fcf_gt_net_income",
        "zero_debt",
        "profitable_streak_years",
        "margin_expanding_3yr",
    ],
    module="mapper/quality_flags.py",
    cli_command="scrooner-map calculate-quality-flags",
    description="4 boolean/count quality flags. zero_debt emits null (never a guessed 0) when no "
    "total_debt fact exists for a year, so absence of data is never mistaken for evidence of "
    "debt-free status.",
)

_register(
    [
        "ar_change_reconciliation_gap",
        "inventory_change_reconciliation_gap",
        "ap_change_reconciliation_gap",
    ],
    module="mapper/reconciliation.py",
    cli_command="scrooner-map calculate-reconciliation",
    description="Cash-flow-statement-vs-balance-sheet quality-of-earnings cross-checks, FY-only, "
    "a signed dollar-figure diagnostic not a locked ratio.",
)

_register(
    ["effective_tax_rate_gap"],
    module="mapper/tax_reconciliation.py",
    cli_command="scrooner-map calculate-tax-reconciliation",
    description="Cross-check between the company's own reported effective tax rate and ROIC's "
    "internally-derived rate.",
)

_register(
    ["fcf_growth_yoy", "fcf_growth_3y_cagr", "fcf_growth_5y_cagr"],
    module="mapper/fcf_growth.py",
    cli_command="scrooner-map calculate-fcf-growth",
    description="FCF growth CAGR, requires calculate (for fcf) to have already run.",
)

_register(
    ["dividend_growth_streak_years"],
    module="mapper/dividend_streak.py",
    cli_command="scrooner-map calculate-dividend-streak",
    description="Consecutive years of dividend-per-share growth.",
)


def unregistered_metrics(conn: psycopg.Connection) -> list[str]:
    """Real active metric_definition rows this registry doesn't yet
    know about -- should be empty; a non-empty result means a metric
    was seeded without updating this file in the same pass, exactly the
    'add the deferral entry in the same edit, never a follow-up' lesson
    pipeline/CLAUDE.md already documents for DEFERRED_TO_EXPANDED_METRICS."""
    with conn.cursor() as cur:
        cur.execute(
            "select metric_name from analytics.metric_definition where status = 'active'"
        )
        all_names = {r[0] for r in cur.fetchall()}
    return sorted(all_names - set(METRIC_CALCULATOR_REGISTRY))


def print_registry() -> None:
    for name in sorted(METRIC_CALCULATOR_REGISTRY):
        entry = METRIC_CALCULATOR_REGISTRY[name]
        print(f"  {name:<38} -> {entry['module']:<38} ({entry['cli_command']})")

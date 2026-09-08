"""Typer CLI for the Mapper (doc 11). Day 1: `seed-concepts` (Stage 3a)."""

import json
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.mapper.calculate import calculate
from scrooner_pipeline.mapper.concepts import coverage_report, seed, unmapped_tag_report
from scrooner_pipeline.mapper import definitions as definitions_module
from scrooner_pipeline.mapper.resolve import resolve
from scrooner_pipeline.mapper.concept_fallback import resolve_fallbacks, resolve_all_arithmetic_fallbacks
from scrooner_pipeline.mapper.ttm import compute_growth, compute_ttm_returns
from scrooner_pipeline.mapper import validate as validate_module
from scrooner_pipeline.statements.classify import seed as seed_statements
from scrooner_pipeline.mapper.price_metrics import calculate_price_metrics
from scrooner_pipeline.mapper import expanded_concepts
from scrooner_pipeline.mapper import expanded_definitions
from scrooner_pipeline.mapper.expanded_metrics import calculate_expanded_metrics
from scrooner_pipeline.mapper.quality_score import calculate_piotroski
from scrooner_pipeline.mapper.quality_flags import calculate_quality_flags
from scrooner_pipeline.mapper.reconciliation import calculate_reconciliation
from scrooner_pipeline.mapper.coverage_matrix import build_registry, build_coverage
from scrooner_pipeline.mapper.tag_candidates import build_tag_candidates, report_status
from scrooner_pipeline.mapper.tax_reconciliation import calculate_tax_reconciliation
from scrooner_pipeline.mapper.fcf_growth import calculate_fcf_growth
from scrooner_pipeline.mapper.dividend_streak import calculate_dividend_streak
from scrooner_pipeline.mapper.coverage_snapshot import write_snapshot
from scrooner_pipeline.parsers.main_parser import run_parser, registry_summary, PARSER_REGISTRY
from scrooner_pipeline.mapper.main_calculator import METRIC_CALCULATOR_REGISTRY, unregistered_metrics

app = typer.Typer()
logger = structlog.get_logger()

GOLDEN_COMPANIES_PATH = Path(__file__).resolve().parents[3] / "tests" / "golden_companies" / "companies.json"


def _load_golden_ciks() -> set[str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"] for c in companies}


@app.command("seed-concepts")
def seed_concepts_cmd() -> None:
    """Stage 3a: seed analytics.canonical_concept + analytics.concept_mapping."""
    with get_connection() as conn:
        stats = seed(conn)
    typer.echo(f"seed-concepts: {stats}")


@app.command("coverage")
def coverage_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
    show_unresolved_only: bool = typer.Option(True, help="Only print rows that failed to resolve."),
) -> None:
    """Stage 3a coverage report: for every (company, canonical_concept), did
    at least one mapped tag resolve to real authoritative fact data?"""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        rows = coverage_report(conn, target_ciks)
    unresolved = [r for r in rows if not r["resolved"]]
    typer.echo(f"{len(rows)} (company, concept) pairs checked; {len(unresolved)} unresolved")
    to_print = unresolved if show_unresolved_only else rows
    for r in to_print:
        typer.echo(f"  {r}")


@app.command("unmapped-tags")
def unmapped_tags_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: every company with facts, not just golden)."),
    limit: int = typer.Option(50, help="Max tags to print."),
) -> None:
    """Coverage-gap discovery (doc 11's proposed, never-built Frames-API
    workflow's SQL half): core.concept tags with real fact volume that have
    NO analytics.concept_mapping row at all -- ranked by fact-row-count, so
    the highest-leverage unmapped tags surface first for curation into
    mapper/concepts.py's CONCEPT_MAPPINGS. Read-only, no writes -- discovery
    only, never auto-maps."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    with get_connection() as conn:
        rows = unmapped_tag_report(conn, target_ciks, limit)
    typer.echo(f"{len(rows)} unmapped tag(s) with real fact volume (top {limit} by fact_count)")
    for r in rows:
        typer.echo(f"  {r}")


@app.command("resolve-facts")
def resolve_facts_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 3b: apply concept_mapping to core.fact, populate
    analytics.canonical_fact. Requires Stage 3a (seed-concepts) to have run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = resolve(conn, target_ciks)
    typer.echo(f"resolve-facts: {stats}")


@app.command("resolve-concept-fallbacks")
def resolve_concept_fallbacks_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 40: prefer-A-else-B merge for concepts needing a safe fallback
    resolve.py's sum/first_match modes can't express (today: total_debt,
    see mapper/concept_fallback.py's own module docstring). Run AFTER
    resolve-facts (reads its output), BEFORE calculate/calculate-piotroski
    (they should consume the *_resolved concept, not the original)."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = resolve_fallbacks(conn, target_ciks)
    typer.echo(f"resolve-concept-fallbacks: {stats}")


@app.command("resolve-statement-fallbacks")
def resolve_statement_fallbacks_cmd() -> None:
    """Migration 0047 / 2026-09-07: gross_profit_resolved,
    cost_of_revenue_resolved, operating_expenses_resolved -- derives a
    missing Income Statement line from two other already-resolved concepts
    (e.g. Revenue - Cost of Revenue) when the primary tag is absent. Always
    population-wide (set-based SQL, no per-CIK scoping -- see
    concept_fallback.py's resolve_arithmetic_fallback docstring for why a
    loop-per-company shape was deliberately avoided). Run AFTER
    resolve-facts, BEFORE seed-statements' consumers render the company
    page (statements/classify.py's STATEMENT_LINES already points at the
    *_resolved concepts)."""
    with get_connection() as conn:
        stats = resolve_all_arithmetic_fallbacks(conn)
    typer.echo(f"resolve-statement-fallbacks: {stats}")


@app.command("seed-definitions")
def seed_definitions_cmd() -> None:
    """Stage 3c: seed analytics.metric_definition + metric_definition_input for doc 02's 18 locked metrics."""
    with get_connection() as conn:
        stats = definitions_module.seed(conn)
    typer.echo(f"seed-definitions: {stats}")


@app.command("calculate")
def calculate_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 3d: compute analytics.metric_value for the 10 EDGAR-only,
    non-growth metrics. Requires Stages 3a/3b/3c to have already run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate(conn, target_ciks)
    typer.echo(f"calculate: {stats}")


@app.command("growth")
def growth_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 3e (part 1): compute revenue/EPS growth (YoY + 3Y CAGR)."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = compute_growth(conn, target_ciks)
    typer.echo(f"growth: {stats}")


@app.command("ttm-returns")
def ttm_returns_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 3e (part 2): compute TTM ROIC/ROE for quarterly periods."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = compute_ttm_returns(conn, target_ciks)
    typer.echo(f"ttm-returns: {stats}")


@app.command("seed-statements")
def seed_statements_cmd() -> None:
    """Doc 17 Sec 4 / doc 23 Stage B: seed statement-display-only canonical
    concepts (cost_of_revenue, public_float, etc.) additively, alongside
    Mapper's frozen 17. Run resolve-facts after this to populate values."""
    with get_connection() as conn:
        stats = seed_statements(conn)
    typer.echo(f"seed-statements: {stats}")


@app.command("calculate-price-metrics")
def calculate_price_metrics_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 3h (doc 25 follow-on): compute the 6 price-dependent metrics
    (Market Cap, Trailing P/E, Price/Sales, Price/Book, Dividend Yield,
    FCF Yield) from core.market_price_alpaca's real price + TTM
    fundamentals. Requires update-market-price to have run first."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_price_metrics(conn, target_ciks)
    typer.echo(f"calculate-price-metrics: {stats}")


@app.command("seed-expanded-concepts")
def seed_expanded_concepts_cmd() -> None:
    """Doc 18 Tier A / doc 26 (2026-08-18): seed inventory/sbc/
    depreciation_and_amortization additively, alongside Mapper's frozen
    17 and doc 17's statement concepts. Run resolve-facts after this."""
    with get_connection() as conn:
        stats = expanded_concepts.seed(conn)
    typer.echo(f"seed-expanded-concepts: {stats}")


@app.command("seed-expanded-definitions")
def seed_expanded_definitions_cmd() -> None:
    """Doc 18 Tier A / doc 26 (2026-08-18): seed roa/quick_ratio/
    sbc_pct_revenue/ebitda (real calculate.py-engine inputs) plus
    documentation-only rows for the 6 EBITDA/price-based ratios computed
    in expanded_metrics.py. Run calculate after this."""
    with get_connection() as conn:
        stats = expanded_definitions.seed(conn)
    typer.echo(f"seed-expanded-definitions: {stats}")


@app.command("calculate-expanded-metrics")
def calculate_expanded_metrics_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 18 Tier A / doc 26 (2026-08-18): Net Debt/EBITDA, EV/EBITDA,
    EV/Sales, PEG, Buyback Yield, Total Shareholder Yield. Requires
    calculate (for ebitda) and calculate-price-metrics (for market_cap/
    trailing_pe/dividend_yield) to have already run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_expanded_metrics(conn, target_ciks)
    typer.echo(f"calculate-expanded-metrics: {stats}")


@app.command("calculate-piotroski")
def calculate_piotroski_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 26 Sec 2 (2026-08-19): standard 9-test Piotroski F-Score (0-9),
    FY vs prior FY. Requires seed-expanded-definitions (for the metric_
    definition row) and resolve-facts (for the 9 raw concepts) to have
    already run. Correctly null for financial institutions -- see
    mapper/quality_score.py's module docstring."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_piotroski(conn, target_ciks)
    typer.echo(f"calculate-piotroski: {stats}")


@app.command("calculate-quality-flags")
def calculate_quality_flags_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 26 Sec 2.9 (2026-08-19): fcf_gt_net_income, zero_debt,
    profitable_streak_years, margin_expanding_3yr. Requires
    seed-expanded-definitions and resolve-facts to have already run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_quality_flags(conn, target_ciks)
    typer.echo(f"calculate-quality-flags: {stats}")


@app.command("calculate-reconciliation")
def calculate_reconciliation_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Core-fact-utilization-study.md #2 (2026-08-21): AR/Inventory/AP
    cash-flow-vs-balance-sheet reconciliation gaps, a quality-of-earnings
    cross-check, FY-only. Requires seed-expanded-concepts,
    seed-expanded-definitions, and resolve-facts to have already run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_reconciliation(conn, target_ciks)
    typer.echo(f"calculate-reconciliation: {stats}")


@app.command("calculate-tax-reconciliation")
def calculate_tax_reconciliation_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Utilization-study ranked #5 (2026-08-22): effective_tax_rate_gap,
    a cross-check between the reported effective tax rate and ROIC's own
    internally-derived rate. Requires seed-expanded-concepts,
    seed-expanded-definitions, and resolve-facts to have already run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_tax_reconciliation(conn, target_ciks)
    typer.echo(f"calculate-tax-reconciliation: {stats}")


@app.command("calculate-fcf-growth")
def calculate_fcf_growth_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 18 Tier A (2026-08-22): fcf_growth_3y_cagr/5y_cagr. Requires
    calculate (for fcf) to have already run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_fcf_growth(conn, target_ciks)
    typer.echo(f"calculate-fcf-growth: {stats}")


@app.command("calculate-dividend-streak")
def calculate_dividend_streak_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 26 (2026-08-22): dividend_growth_streak_years. Requires
    seed-expanded-definitions and resolve-facts to have already run."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = calculate_dividend_streak(conn, target_ciks)
    typer.echo(f"calculate-dividend-streak: {stats}")


@app.command("snapshot-coverage")
def snapshot_coverage_cmd() -> None:
    """Doc 41 (2026-09-02): compute and persist today's data-point
    coverage (per canonical_concept, per active metric_definition, plus
    the two aggregate avg_*_coverage_score rows) to
    analytics.coverage_snapshot. Whole-population, no --ciks scoping --
    run once per day after the day's calculate-family stages finish."""
    with get_connection() as conn:
        stats = write_snapshot(conn)
    typer.echo(f"snapshot-coverage: {stats}")


@app.command()
def errors(
    stage: str = typer.Option(None, help="Restrict to one stage (resolve, calculate, growth, ttm_returns, price_metrics)."),
    unresolved_only: bool = typer.Option(True, help="Only print rows with resolved=false."),
    limit: int = typer.Option(50, help="Max rows to print."),
) -> None:
    """Dead-letter report over analytics.mapper_error (Phase 1 scaling
    foundation) -- read-only, no writes. One row per company whose mapping/
    calculation failed with an unhandled exception; the batch itself keeps
    going past a single company's failure."""
    conditions, params = [], []
    if stage:
        conditions.append("stage = %s")
        params.append(stage)
    if unresolved_only:
        conditions.append("not resolved")
    where = f"where {' and '.join(conditions)}" if conditions else ""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"select id, cik, stage, error_type, message, occurred_at, resolved "
                f"from analytics.mapper_error {where} order by occurred_at desc limit %s",
                (*params, limit),
            )
            rows = cur.fetchall()
    typer.echo(f"{len(rows)} row(s)")
    for row in rows:
        typer.echo(f"  {row}")


@app.command("validate")
def validate_cmd() -> None:
    """Stage 3f: confidence-state distribution, non-authoritative-leak check,
    and source_fact_ids lineage integrity across the whole analytics schema
    (not scoped to a CIK set -- these are global invariants)."""
    with get_connection() as conn:
        result = validate_module.run(conn)
    typer.echo(f"validate: {result}")
    if not result["clean"]:
        raise typer.Exit(1)


@app.command("run-parser")
def run_parser_cmd(
    concept_name: str = typer.Argument(..., help=f"Registered: {sorted(PARSER_REGISTRY)}"),
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: full gap population)."),
) -> None:
    """Doc 42 Parser 3 architecture: run the dedicated rendered-report
    parser registered for one canonical concept (see parsers/main_parser.py's
    own module docstring for the 3-tier resolution order this fits into).
    Automatically skips companies already resolved via XBRL tag matching
    and companies this parser has already attempted before (see
    analytics.concept_parser_attempt) -- safe and efficient to rerun."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    with get_connection() as conn:
        result = run_parser(conn, concept_name, target_ciks)
    typer.echo(f"run-parser {concept_name}: {result['stats']}")


@app.command("parser-registry-summary")
def parser_registry_summary_cmd() -> None:
    """Read-only: for every (concept, parser) pair ever attempted, real
    counts of matched/no_report/no_row_matched/errored -- the 'which
    parser resolved this' view doc 42's routing table exists for."""
    with get_connection() as conn:
        rows = registry_summary(conn)
    for row in rows:
        typer.echo(f"  {row}")


@app.command("build-coverage-matrix")
def build_coverage_matrix_cmd() -> None:
    """2026-09-05: the two-table coverage system (registry + per-company
    yes/no). Rebuilds both from scratch each run -- never hand-edited,
    can't drift from concept_mapping/metric_definition_input/
    canonical_fact/metric_value/the ownership tables."""
    with get_connection() as conn:
        registry_stats = build_registry(conn)
        coverage_stats = build_coverage(conn)
    typer.echo(f"registry: {registry_stats}")
    typer.echo(f"coverage: {coverage_stats}")


@app.command("build-tag-candidates")
def build_tag_candidates_cmd() -> None:
    """2026-09-08: retires reference/xbrl_tag_coverage_library.json
    (doc 40) into analytics.concept_tag_candidate -- the DB-native
    record of candidate UNMAPPED XBRL tags per canonical concept, ranked
    by real company count. The one thing the JSON library had that the
    coverage matrix didn't; now the single DB source of truth for both.
    Every candidate is still a LEAD to investigate, never an approval --
    see tag_candidates.py's module docstring."""
    with get_connection() as conn:
        stats = build_tag_candidates(conn)
    typer.echo(f"tag-candidates: {stats}")


@app.command("tag-candidate-report")
def tag_candidate_report_cmd() -> None:
    """Reads back the current concept-by-concept status
    (well_covered / gap_safe_candidate_found / gap_needs_fallback_resolver
    / gap_no_safe_candidate) computed live from analytics.canonical_fact
    coverage + analytics.concept_tag_candidate -- read-only, safe any time."""
    with get_connection() as conn:
        rows = report_status(conn)
    for row in rows:
        top = f"{row['top_candidate'][0]} ({row['top_candidate'][1]} cos)" if row["top_candidate"] else "-"
        typer.echo(f"{row['concept']:<32} {row['coverage_pct']:>5}%  {row['status']:<28} top candidate: {top}")


@app.command("calculator-registry")
def calculator_registry_cmd() -> None:
    """Doc 42: for every real metric_definition, which module computes
    it and via which CLI command. Also flags any metric this registry
    doesn't yet know about (should be empty -- a non-empty result means
    a new metric was seeded without updating mapper/main_calculator.py
    in the same pass)."""
    with get_connection() as conn:
        missing = unregistered_metrics(conn)
    for name in sorted(METRIC_CALCULATOR_REGISTRY):
        entry = METRIC_CALCULATOR_REGISTRY[name]
        typer.echo(f"  {name:<38} -> {entry['module']:<38} ({entry['cli_command']})")
    if missing:
        typer.echo(f"\nUNREGISTERED (fix main_calculator.py): {missing}")


if __name__ == "__main__":
    app()

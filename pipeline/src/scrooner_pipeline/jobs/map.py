"""Typer CLI for the Mapper (doc 11). Day 1: `seed-concepts` (Stage 3a)."""

import json
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.mapper.calculate import calculate
from scrooner_pipeline.mapper.concepts import coverage_report, seed
from scrooner_pipeline.mapper import definitions as definitions_module
from scrooner_pipeline.mapper.resolve import resolve
from scrooner_pipeline.mapper.ttm import compute_growth, compute_ttm_returns
from scrooner_pipeline.mapper import validate as validate_module
from scrooner_pipeline.statements.classify import seed as seed_statements

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


if __name__ == "__main__":
    app()

"""Typer CLI for the Normalizer (doc 09). Day 1: `identity` (Stage 2a) and
`golden` (Stage 2a restricted to the golden-company set -- doc 09's
reconciliation set, reused as-is from the Collector)."""

import json
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.normalizer.dedupe import conflict_summary, resolve_authoritative
from scrooner_pipeline.normalizer.derived import derive_interim_quarters, derive_q4
from scrooner_pipeline.normalizer.facts import FACT_EXTRACTION_EXCLUDED_CIKS, normalize_facts
from scrooner_pipeline.normalizer.identity import normalize_identity
from scrooner_pipeline.normalizer.periods import normalize_periods
from scrooner_pipeline.normalizer.restatements import resolve_restatements
from scrooner_pipeline.normalizer.units import normalize_units

app = typer.Typer()
logger = structlog.get_logger()

GOLDEN_COMPANIES_PATH = Path(__file__).resolve().parents[3] / "tests" / "golden_companies" / "companies.json"


def _load_golden_ciks() -> set[str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"] for c in companies}


def _parse_ciks(ciks: str | None) -> set[str] | None:
    if not ciks:
        return None
    return {c.strip().zfill(10) for c in ciks.split(",") if c.strip()}


@app.command()
def identity(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2a: normalize raw.sec_submissions into core.company/listing/filing."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        stats = normalize_identity(conn, target_ciks)
    typer.echo(f"identity: {stats}")


@app.command()
def periods(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2b: resolve every distinct period in raw.sec_companyfacts into
    core.period. Requires Stage 2a (identity) to have already run for these
    CIKs -- core.period.company_id is a hard FK to core.company."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        stats = normalize_periods(conn, target_ciks)
    typer.echo(f"periods: {stats}")


@app.command()
def units(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2c: resolve every distinct unit string in raw.sec_companyfacts
    into core.unit. Independent of identity/periods -- core.unit is a
    global lookup, not scoped per company."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        stats = normalize_units(conn, target_ciks)
    typer.echo(f"units: {stats}")


@app.command()
def facts(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2d: extract every XBRL fact into core.fact. Requires Stages
    2a/2b/2c (identity/periods/units) to have already run for these CIKs.
    CIKs in FACT_EXTRACTION_EXCLUDED_CIKS (TSM, ENB) are silently dropped
    from the target set -- see doc 09's Day-7 scope note."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        result = normalize_facts(conn, target_ciks)
    typer.echo(f"facts: excluded={result['excluded']} totals={result['totals']}")


@app.command()
def dedupe(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2e: resolve core.fact.is_authoritative for every duplicate
    (company, concept, unit, period) group. Requires Stage 2d (facts) to
    have already run for these CIKs."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        stats = resolve_authoritative(conn, target_ciks)
    typer.echo(f"dedupe: {stats}")


@app.command()
def conflicts(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
    limit: int = typer.Option(20, help="Max conflicts to print."),
) -> None:
    """Print unresolved conflict groups (Stage 2e) for manual review --
    read-only, no writes."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        rows = conflict_summary(conn, target_ciks)
    typer.echo(f"{len(rows)} unresolved conflict groups")
    for row in rows[:limit]:
        typer.echo(f"  {row}")


@app.command()
def restatements(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2f: link amendments to what they amend (core.filing.amends_filing_id)
    and supersede the matching core.fact rows. Runs over core.filing for
    every requested CIK (including TSM/ENB -- this is filing-structure
    linkage, not fact interpretation) but only touches core.fact where
    facts actually exist."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        stats = resolve_restatements(conn, target_ciks)
    typer.echo(f"restatements: {stats}")


@app.command("derive-interim-quarters")
def derive_interim_quarters_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2g follow-on (doc 24/25): derive discrete Q2/Q3 from
    cumulative half-year/three-quarter YTD spans (common on cash-flow
    lines) via successive subtraction. Run BEFORE derive-q4 -- once Q2/Q3
    exist as authoritative facts, derive-q4's own existing logic picks
    them up automatically, no code change needed there."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        stats = derive_interim_quarters(conn, target_ciks)
    typer.echo(f"derive-interim-quarters: {stats}")


@app.command("derive-q4")
def derive_q4_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2g: derive Q4 = FY - Q1 - Q2 - Q3 for every duration concept
    that has all three authoritative quarters plus an authoritative FY
    value. Requires Stages 2d/2e (and ideally 2f) to have already run."""
    target_ciks = _parse_ciks(ciks) or _load_golden_ciks()
    with get_connection() as conn:
        stats = derive_q4(conn, target_ciks)
    typer.echo(f"derive-q4: {stats}")


@app.command()
def golden() -> None:
    """Stages 2a+2b+2c+2d+2e+2f+2g over the fixed golden-company set
    (tests/golden_companies/companies.json). Fact extraction (2d), dedupe
    (2e) and Q4 derivation (2g) skip TSM/ENB per doc 09's Day-7 scope note
    -- identity/periods/units/restatement-linking still run for them."""
    golden_ciks = _load_golden_ciks()
    typer.echo(f"golden set: {len(golden_ciks)} companies ({len(golden_ciks - FACT_EXTRACTION_EXCLUDED_CIKS)} get fact extraction)")
    with get_connection() as conn:
        identity_stats = normalize_identity(conn, golden_ciks)
        typer.echo(f"identity: {identity_stats}")
        period_stats = normalize_periods(conn, golden_ciks)
        typer.echo(f"periods: {period_stats}")
        unit_stats = normalize_units(conn, golden_ciks)
        typer.echo(f"units: {unit_stats}")
        fact_result = normalize_facts(conn, golden_ciks)
        typer.echo(f"facts: excluded={fact_result['excluded']} totals={fact_result['totals']}")
        dedupe_stats = resolve_authoritative(conn, golden_ciks)
        typer.echo(f"dedupe: {dedupe_stats}")
        restatement_stats = resolve_restatements(conn, golden_ciks)
        typer.echo(f"restatements: {restatement_stats}")
        interim_stats = derive_interim_quarters(conn, golden_ciks)
        typer.echo(f"derive-interim-quarters: {interim_stats}")
        q4_stats = derive_q4(conn, golden_ciks)
        typer.echo(f"derive-q4: {q4_stats}")


if __name__ == "__main__":
    app()

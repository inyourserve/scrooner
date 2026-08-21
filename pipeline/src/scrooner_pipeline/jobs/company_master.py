"""Typer CLI for Company Master (doc 13). Day 1: `update-identity` (Stage 4a-1)."""

import json
from datetime import date
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.company_master.identity import update_identity
from scrooner_pipeline.company_master.sector_bucket import update_sector
from scrooner_pipeline.company_master.history import update_history
from scrooner_pipeline.company_master.status import update_status
from scrooner_pipeline.company_master.market_price import load_mock_prices
from scrooner_pipeline.company_master.market_price_alpaca import update_market_price
from scrooner_pipeline.company_master.security_type import resolve_primary_tickers, update_security_types
from scrooner_pipeline.company_master.shares_outstanding_fallback import update_shares_outstanding_fallback
from scrooner_pipeline.company_master.universe import build_current_universe
from scrooner_pipeline.db.connection import get_connection

app = typer.Typer()
logger = structlog.get_logger()

GOLDEN_COMPANIES_PATH = Path(__file__).resolve().parents[3] / "tests" / "golden_companies" / "companies.json"


def _load_golden_ciks() -> set[str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"] for c in companies}


def _load_golden_tickers() -> dict[str, str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"]: c["ticker"] for c in companies}


@app.command("update-identity")
def update_identity_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 4a-1: parse sic/stateOfIncorporation/entityType/category out of
    each company's already-stored raw.sec_submissions payload into
    core.company. No new SEC fetch."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_identity(conn, target_ciks)
    typer.echo(f"update-identity: {stats}")


@app.command("update-history")
def update_history_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 4a-2: populate core.company_name_history and date
    core.listing's effective_from/effective_to/source."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_history(conn, target_ciks)
    typer.echo(f"update-history: {stats}")


@app.command("update-status")
def update_status_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 4a-3: infer core.company.status (active/stale/unknown) from
    core.filing's own filing-recency."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_status(conn, target_ciks)
    typer.echo(f"update-status: {stats}")


@app.command("update-sector")
def update_sector_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 10 Sec 12 / doc 26 Sec 2.8 / doc 28 (2026-08-21): derive
    core.company.sector from the already-captured sic_code via a curated
    SIC-range mapping (company_master/sector_bucket.py) -- zero new fetch."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_sector(conn, target_ciks)
    typer.echo(f"update-sector: {stats}")


@app.command("load-mock-prices")
def load_mock_prices_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 4b: load MOCK end-of-day prices into core.market_price
    (is_mock=true, source='mock'). Not real market data -- built to unblock
    the pipeline's shape ahead of doc 02's still-open vendor decision. See
    company_master/market_price.py's module docstring before swapping in a
    real vendor."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = load_mock_prices(conn, target_ciks)
    typer.echo(f"load-mock-prices: {stats}")


@app.command("update-security-types")
def update_security_types_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Classifies each current listing's real security type via OpenFIGI
    (free, NOT Alpaca -- see security_type.py's module docstring) --
    replaces the golden_companies.json ticker stopgap update-market-price
    originally used to find a company's primary common-stock/ADR ticker."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_security_types(conn, target_ciks)
    typer.echo(f"update-security-types: {stats}")


@app.command("update-shares-outstanding-fallback")
def update_shares_outstanding_fallback_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Real fallback for multi-class share-structure companies (Block,
    Reddit) whose shares outstanding is dimensionally XBRL-tagged and
    stripped by the standard Company Facts API -- parses the 10-K cover
    page instead. See shares_outstanding_fallback.py's module docstring.
    Only fill this gap where the primary XBRL path genuinely has
    nothing; never a replacement for it."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_shares_outstanding_fallback(conn, target_ciks)
    typer.echo(f"update-shares-outstanding-fallback: {stats}")


@app.command("update-market-price")
def update_market_price_cmd() -> None:
    """Stage 4b real-data follow-on (doc 25): fetch REAL current prices
    from Alpaca (delayed_sip feed, ~15min delay, full consolidated tape)
    into core.market_price_alpaca -- a table separate from
    core.market_price's mock data, by explicit design. Run once daily or
    on demand (no scheduler wired up yet -- see doc 25's open cadence
    question, answered as 'daily/on-demand for now' during dev).
    Primary ticker per company comes from real OpenFIGI-sourced
    classification (run update-security-types first) -- see
    security_type.py's resolve_primary_tickers(), NOT Alpaca itself, kept
    deliberately separate from the price vendor. golden_companies.json's
    curated ticker is only the tie-break for a company with more than one
    legitimately valid Common-Stock/ADR listing (e.g. Alphabet's two
    share classes), not the primary source of truth anymore."""
    golden_ciks = _load_golden_ciks()
    with get_connection() as conn:
        ticker_by_cik = resolve_primary_tickers(conn, golden_ciks, fallback_ticker_by_cik=_load_golden_tickers())
        stats = update_market_price(conn, ticker_by_cik)
    typer.echo(f"update-market-price: {stats}")


@app.command("build-universe")
def build_universe_cmd(
    as_of: str = typer.Option(
        None,
        help="Snapshot date in YYYY-MM-DD form; must be today (default: today).",
    ),
) -> None:
    """Build the deterministic, reason-coded production-universe snapshot."""
    snapshot_date = date.fromisoformat(as_of) if as_of else date.today()
    if snapshot_date != date.today():
        raise typer.BadParameter(
            "retroactive builds would use future-known identity data; choose today's date"
        )
    with get_connection() as conn:
        stats = build_current_universe(conn, snapshot_date)
    typer.echo(f"build-universe: {stats}")


if __name__ == "__main__":
    app()

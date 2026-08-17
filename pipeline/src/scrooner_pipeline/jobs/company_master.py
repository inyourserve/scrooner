"""Typer CLI for Company Master (doc 13). Day 1: `update-identity` (Stage 4a-1)."""

import json
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.company_master.identity import update_identity
from scrooner_pipeline.company_master.history import update_history
from scrooner_pipeline.company_master.status import update_status
from scrooner_pipeline.company_master.market_price import load_mock_prices
from scrooner_pipeline.company_master.market_price_alpaca import update_market_price
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


@app.command("update-market-price")
def update_market_price_cmd() -> None:
    """Stage 4b real-data follow-on (doc 25): fetch REAL current prices
    from Alpaca (delayed_sip feed, ~15min delay, full consolidated tape)
    into core.market_price_alpaca -- a table separate from
    core.market_price's mock data, by explicit design. Run once daily or
    on demand (no scheduler wired up yet -- see doc 25's open cadence
    question, answered as 'daily/on-demand for now' during dev). No
    --ciks override, unlike the other commands here -- ticker resolution
    currently depends on golden_companies.json's own curated primary
    ticker (see market_price_alpaca.py's module docstring for why), so
    this is golden-10-only until a real "primary listing" design exists."""
    with get_connection() as conn:
        stats = update_market_price(conn, _load_golden_tickers())
    typer.echo(f"update-market-price: {stats}")


if __name__ == "__main__":
    app()

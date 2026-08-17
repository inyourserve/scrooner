"""Typer CLI for Ownership & Insider Activity (doc 19)."""

import json
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.ownership.insider import update_insider_transactions
from scrooner_pipeline.ownership.beneficial_ownership import update_beneficial_ownership
from scrooner_pipeline.ownership.institutional import update_institutional_ownership

app = typer.Typer()
logger = structlog.get_logger()

GOLDEN_COMPANIES_PATH = Path(__file__).resolve().parents[3] / "tests" / "golden_companies" / "companies.json"


def _load_golden_ciks() -> set[str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"] for c in companies}


@app.command("update-insider-transactions")
def update_insider_transactions_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 2: download/parse each company's Form 4 filings (list already
    in raw.sec_submissions, bodies fetched here) into core.insider_transaction."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_insider_transactions(conn, target_ciks)
    typer.echo(f"update-insider-transactions: {stats}")


@app.command("update-beneficial-ownership")
def update_beneficial_ownership_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 3: download/parse each company's Schedule 13D/13G full-submission
    headers into core.beneficial_ownership, with the issuer-vs-filer check."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_beneficial_ownership(conn, target_ciks)
    typer.echo(f"update-beneficial-ownership: {stats}")


@app.command("update-institutional-ownership")
def update_institutional_ownership_cmd() -> None:
    """Stage 4: download SEC's bulk Form 13F data set (all managers), match
    INFOTABLE rows by CUSIP against golden companies' own CUSIPs (captured
    by Stage 3), write into core.institutional_ownership. Not restricted
    by --ciks like the other two commands -- matching is CUSIP-driven
    against whatever golden companies already have a CUSIP on file."""
    with get_connection() as conn:
        stats = update_institutional_ownership(conn)
    typer.echo(f"update-institutional-ownership: {stats}")


if __name__ == "__main__":
    app()

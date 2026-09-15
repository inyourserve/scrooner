"""Typer CLI for Ownership & Insider Activity (doc 19)."""

import json
from pathlib import Path

import psycopg
import structlog
import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.ownership.insider import update_insider_transactions
from scrooner_pipeline.ownership.insider_summary import update_insider_summary
from scrooner_pipeline.ownership.beneficial_ownership import update_beneficial_ownership
from scrooner_pipeline.ownership.institutional import correct_value_scale_anomalies, update_institutional_ownership
from scrooner_pipeline.ownership.institutional_summary import compute_institutional_ownership_summary
from scrooner_pipeline.ownership.mutual_fund import update_mutual_fund_ownership
from scrooner_pipeline.ownership.mutual_fund_summary import compute_mutual_fund_ownership_summary

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


@app.command("update-insider-summary")
def update_insider_summary_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: ALL companies already in core.insider_transaction -- not the golden set, since Stage 2's data is already fully populated across ~5,160 companies)."),
) -> None:
    """doc/scoping/insider_info.md's "Insider Ownership & Transactions"
    aggregate summary: current insider ownership %, and 3/6/12-month
    rolling summaries (buy/sell shares + $ volume, distinct buyer/seller
    counts, largest single purchase/sale), computed purely from the
    already-fully-populated core.insider_transaction -- zero new SEC
    fetches. Writes core.insider_ownership_summary / core.insider_window_summary."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else None
    with get_connection() as conn:
        stats = update_insider_summary(conn, target_ciks)
    typer.echo(f"update-insider-summary: {stats}")


@app.command("update-beneficial-ownership")
def update_beneficial_ownership_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Stage 3: download/parse each company's Schedule 13D/13G full-submission
    headers into core.beneficial_ownership, with the issuer-vs-filer check."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    stats = None
    try:
        with get_connection() as conn:
            stats = update_beneficial_ownership(conn, target_ciks)
    except psycopg.OperationalError:
        # Found live 2026-09-16: this outer conn is only touched at the
        # very start (the company lookup) and, if a per-company error
        # occurs, inside update_beneficial_ownership()'s own rollback/
        # reconnect handler -- otherwise it sits idle for the entire
        # multi-hour run. A dead Supabase pooler connection surfaces here
        # when the `with` block exits and psycopg tries its own implicit
        # commit/close on a socket that's already gone -- AFTER stats has
        # already been set correctly and every company's own work already
        # committed via its own per-company connection. Swallow it rather
        # than let a fully-successful run exit non-zero with a scary
        # traceback that looks like the whole batch failed.
        logger.warning("update_beneficial_ownership_cmd.exit_commit_failed", stats=stats)
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


@app.command("correct-institutional-value-scale")
def correct_institutional_value_scale_cmd() -> None:
    """Standalone re-run of the value-scale correction update-institutional-ownership
    now runs automatically after every fetch (found 2026-09-06: some Form 13F
    filers -- T. Rowe Price among them -- still submit VALUE in thousands
    despite SEC's 2023 actual-dollars rule; see this module's own doc and
    migration 0043). Use this to apply the fix to already-stored data
    immediately, without re-downloading and re-matching the ~400MB bulk zips."""
    with get_connection() as conn:
        stats = correct_value_scale_anomalies(conn)
    typer.echo(f"correct-institutional-value-scale: {stats}")


@app.command("compute-institutional-ownership-summary")
def compute_institutional_ownership_summary_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """QoQ summary over the two most recent Form 13F report_periods
    already stored by update-institutional-ownership (total institutional
    %, holder counts, new/increased/decreased/exited positions, Top 10
    holders) -- writes core.institutional_ownership_summary. Run
    update-institutional-ownership first so both report_periods exist."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = compute_institutional_ownership_summary(conn, target_ciks)
    typer.echo(f"compute-institutional-ownership-summary: {stats}")


@app.command("update-mutual-fund-ownership")
def update_mutual_fund_ownership_cmd() -> None:
    """doc 21 Sec 1 / insider_info.md Mutual Fund Ownership MVP: download
    SEC's bulk Form N-PORT data sets for the two most recent consecutive
    quarterly windows (all registered funds/ETFs), match
    FUND_REPORTED_HOLDING rows by CUSIP against golden companies' own
    CUSIPs (captured by Stage 3), write into core.fund_ownership. Not
    restricted by --ciks, same reasoning as update-institutional-ownership
    -- matching is CUSIP-driven against whatever golden companies already
    have a CUSIP on file."""
    with get_connection() as conn:
        stats = update_mutual_fund_ownership(conn)
    typer.echo(f"update-mutual-fund-ownership: {stats}")


@app.command("compute-mutual-fund-ownership-summary")
def compute_mutual_fund_ownership_summary_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """QoQ summary over the two most recent Form N-PORT report_periods
    already stored by update-mutual-fund-ownership (total mutual fund
    ownership %, fund counts, new/increased/decreased/exited positions,
    Top 10 holders) -- writes core.fund_ownership_summary. Run
    update-mutual-fund-ownership first so both report_periods exist.
    Never combined with institutional ownership's own % anywhere --
    doc `insider_info.md`'s explicit non-additive rule."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = compute_mutual_fund_ownership_summary(conn, target_ciks)
    typer.echo(f"compute-mutual-fund-ownership-summary: {stats}")


if __name__ == "__main__":
    app()

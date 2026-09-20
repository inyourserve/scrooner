"""Typer CLI for Company Master (doc 13). Day 1: `update-identity` (Stage 4a-1)."""

import json
from datetime import date
from pathlib import Path

import structlog
import typer

from scrooner_pipeline.company_master.identity import update_identity
from scrooner_pipeline.company_master.contact_details import update_contact_details
from scrooner_pipeline.company_master.display_name import update_display_names
from scrooner_pipeline.company_master.employee_headcount import process_companies as process_employee_headcount
from scrooner_pipeline.company_master.sector_bucket import update_sector
from scrooner_pipeline.company_master.history import update_history
from scrooner_pipeline.company_master.status import update_status
from scrooner_pipeline.company_master.market_price import load_mock_prices
from scrooner_pipeline.company_master.market_price_alpaca import update_market_price
from scrooner_pipeline.company_master.security_type import persist_primary_tickers, resolve_primary_tickers, update_security_types
from scrooner_pipeline.company_master.shares_outstanding_fallback import update_shares_outstanding_fallback
from scrooner_pipeline.company_master.universe import build_current_universe
from scrooner_pipeline.company_master.yfinance_industry import update_yfinance_industry
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


@app.command("update-contact-details")
def update_contact_details_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Zero-new-fetch coverage pass (2026-08-29): parse ein/business address/
    phone out of each company's already-stored raw.sec_submissions payload
    into core.company -- NOT from XBRL/core.fact, which was checked live and
    confirmed to not carry these unitless dei text fields at all."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_contact_details(conn, target_ciks)
    typer.echo(f"update-contact-details: {stats}")


@app.command("update-employee-headcount")
def update_employee_headcount_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
) -> None:
    """Doc 39: fetch the 4 most recent 10-Ks per company (annual-only
    disclosure -- confirmed no 10-Q repeats it), extract employee
    headcount via regex over cleaned visible text, store latest 10-K's
    About text. Genuinely new fetch (10-K primary document bodies aren't
    currently stored anywhere) -- NOT zero-fetch like update-contact-details."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = process_employee_headcount(conn, target_ciks)
    typer.echo(f"update-employee-headcount: {stats}")


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


@app.command("update-yfinance-industry")
def update_yfinance_industry_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
    all_active: bool = typer.Option(
        False, "--all-active", help="Target every active company, not just --ciks/golden set."
    ),
    force: bool = typer.Option(
        False, "--force", help="Re-fetch companies already resolved ok/no_data, not just error/unattempted."
    ),
    no_pacing: bool = typer.Option(
        False,
        "--no-pacing",
        help="Skip the shared rate limiter and retry-on-rate-limit entirely -- an explicit "
        "'try fast first' pass. Always follow with a plain (paced) rerun to clean up "
        "whatever landed in STATUS_ERROR from being rate-limited.",
    ),
) -> None:
    """Explicit user direction 2026-09-06 (see CLAUDE.md, doc 02): backfill
    core.company.y_sector/y_industry from yfinance. Default mode is paced
    and resumable, safe to run as several parallel `--ciks <shard>`
    processes -- they coordinate through one shared cross-process rate
    limiter (common/rate_limiter.py) rather than each pacing independently,
    which would multiply Yahoo's own aggregate rate the same way the SEC
    in-process limiter broke under multiprocessing (see pipeline/CLAUDE.md).
    --no-pacing drops that limiter entirely for a fast first pass, by
    explicit user direction -- run it, then run again without --no-pacing
    (still resumable: only STATUS_ERROR/unattempted rows get retried) to
    safely clean up whatever the fast pass got rate-limited on."""
    with get_connection() as conn:
        if all_active:
            with conn.cursor() as cur:
                cur.execute("select cik from core.company where status = 'active'")
                target_ciks = {row[0] for row in cur.fetchall()}
        else:
            target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
        stats = update_yfinance_industry(conn, target_ciks, force=force, paced=not no_pacing)
    typer.echo(f"update-yfinance-industry: {stats}")


@app.command("update-display-names")
def update_display_names_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
    edgar_suffix_only: bool = typer.Option(
        True,
        "--edgar-suffix-only/--all",
        help="Only target companies whose company_name matches the EDGAR /XX/ suffix pattern "
        "(the default, and the actual reported problem). --all targets every given CIK.",
    ),
    no_pacing: bool = typer.Option(
        False, "--no-pacing", help="Skip yfinance's shared rate limiter for a fast first pass."
    ),
    force: bool = typer.Option(False, "--force", help="Re-resolve companies that already have a display_name."),
) -> None:
    """Explicit user direction 2026-09-07: clean up company_name's raw EDGAR
    disambiguation suffix (e.g. 'COSTCO WHOLESALE CORP /NEW', 'TUCOWS INC
    /PA/') into core.company.display_name -- yfinance longName/shortName
    first, OpenFIGI name second, a deterministic suffix-strip always as the
    guaranteed fallback. Never overwrites company_name itself."""
    with get_connection() as conn:
        if ciks:
            target_ciks = {c.strip().zfill(10) for c in ciks.split(",")}
        elif edgar_suffix_only:
            with conn.cursor() as cur:
                cur.execute(
                    r"select cik from core.company where status = 'active' "
                    r"and company_name ~ '/[A-Za-z]{2,4}/?\s*$'"
                )
                target_ciks = {row[0] for row in cur.fetchall()}
        else:
            target_ciks = _load_golden_ciks()
        stats = update_display_names(conn, target_ciks, paced=not no_pacing, force=force)
    typer.echo(f"update-display-names: {stats}")


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
    force: bool = typer.Option(
        False, "--force", help="Re-classify listings that already have a security_type, not just null ones."
    ),
) -> None:
    """Classifies each current listing's real security type via OpenFIGI
    (free, NOT Alpaca -- see security_type.py's module docstring) --
    replaces the golden_companies.json ticker stopgap update-market-price
    originally used to find a company's primary common-stock/ADR ticker.
    Resumable: skips already-classified listings and commits incrementally
    unless --force."""
    target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    with get_connection() as conn:
        stats = update_security_types(conn, target_ciks, force=force)
    typer.echo(f"update-security-types: {stats}")


@app.command("update-primary-ticker")
def update_primary_ticker_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
    all_active: bool = typer.Option(
        False, "--all-active", help="Target every active company, not just --ciks/golden set."
    ),
) -> None:
    """Persists resolve_primary_tickers()'s output onto core.company
    (migration 0069: primary_ticker/primary_ticker_status/
    primary_ticker_updated_at) -- a real, queryable "does this company
    have a ticker" marker instead of every consumer recomputing the same
    core.listing query. Pure local computation (no external fetch), so
    always run this AFTER update-security-types in the same pass -- a
    stale run here just reflects yesterday's classification state, same
    as concept_fallback.py's own "run right after resolve-facts"
    ordering dependency."""
    with get_connection() as conn:
        if all_active:
            with conn.cursor() as cur:
                cur.execute("select cik from core.company where status = 'active'")
                target_ciks = {row[0] for row in cur.fetchall()}
        else:
            target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
        stats = persist_primary_tickers(conn, target_ciks)
    typer.echo(f"update-primary-ticker: {stats}")


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
def update_market_price_cmd(
    ciks: str = typer.Option(None, help="Comma-separated CIKs to restrict to (default: golden set)."),
    all_active: bool = typer.Option(
        False, "--all-active", help="Target every active company, not just --ciks/golden set."
    ),
) -> None:
    """Stage 4b real-data follow-on (doc 25): fetch REAL current prices
    from Alpaca (delayed_sip feed, ~15min delay, full consolidated tape)
    into core.market_price_alpaca -- a table separate from
    core.market_price's mock data, by explicit design. Run once daily or
    on demand (no scheduler wired up yet -- see doc 25's open cadence
    question, answered as 'daily/on-demand for now' during dev).
    Primary ticker per company comes from resolve_primary_tickers() --
    security_type.py's OpenFIGI classification where available, plus
    (2026-08-24, full-population extension) an unclassified single-
    active-listing fallback for the 83% of the full universe OpenFIGI
    was never run for. golden_companies.json's curated ticker is only
    the tie-break for a company with more than one legitimately valid
    Common-Stock/ADR listing (e.g. Alphabet's two share classes), not
    the primary source of truth."""
    with get_connection() as conn:
        if all_active:
            with conn.cursor() as cur:
                cur.execute("select cik from core.company where status = 'active'")
                target_ciks = {row[0] for row in cur.fetchall()}
        else:
            target_ciks = {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
        ticker_by_cik = resolve_primary_tickers(conn, target_ciks, fallback_ticker_by_cik=_load_golden_tickers())
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

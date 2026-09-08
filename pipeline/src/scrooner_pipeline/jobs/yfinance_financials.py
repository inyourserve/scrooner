"""Typer CLI for the yfinance Full Financial Statements system (2026-09-08)
-- a SEPARATE system from `scrooner-sanity` (which only checks `.info()`'s
aggregate ratios for the latest period). This one fetches and compares
every available quarter's individual income-statement/balance-sheet/
cash-flow LINE ITEMS. See yfinance_financials/fetch.py's module docstring
for the full design and doc/learnings/2026-09-08-yfinance-financials-system.md
for how it was scoped and what it found."""

import json
from pathlib import Path

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.yfinance_financials.fetch import fetch_and_store_statements, pick_rotation_batch
from scrooner_pipeline.yfinance_financials.line_item_map import seed_line_item_mapping
from scrooner_pipeline.yfinance_financials.compare import compare_statements, investigate_major_findings
from scrooner_pipeline.yfinance_financials.report import summarize, render_markdown

app = typer.Typer()

GOLDEN_COMPANIES_PATH = Path(__file__).resolve().parents[3] / "tests" / "golden_companies" / "companies.json"


def _load_golden_company_ids(conn) -> list[int]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    ciks = [c["cik"].zfill(10) for c in companies]
    with conn.cursor() as cur:
        cur.execute("select id from core.company where cik = any(%s)", (ciks,))
        return [r[0] for r in cur.fetchall()]


@app.command("seed-line-item-mapping")
def seed_line_item_mapping_cmd() -> None:
    """Seeds analytics.yfinance_line_item_mapping from line_item_map.py's
    curated LINE_ITEM_MAP -- the "tag db" for yfinance's own row labels."""
    with get_connection() as conn:
        stats = seed_line_item_mapping(conn)
    typer.echo(f"seed-line-item-mapping: {stats}")


@app.command("fetch-statements")
def fetch_statements_cmd(
    company_ids: str = typer.Option(None, help="Comma-separated company_ids to restrict to (default: golden-10)."),
    no_pacing: bool = typer.Option(
        False, "--no-pacing",
        help="Skip yfinance's shared rate limiter and the rate-limit retry entirely for a fast 'try fast first' "
             "pass. Always follow with a plain (paced) rerun over whatever's left un-fetched to clean up.",
    ),
) -> None:
    """Fetches yfinance's quarterly income statement/balance sheet/cash
    flow for each company, stores raw line items in
    analytics.yfinance_statement_line. 3 paced yfinance requests per
    company by default -- deliberately run on a bounded batch, not
    blindly at full-population scale, unless --no-pacing is given for a
    deliberate fast first pass (see fetch.py's module docstring)."""
    with get_connection() as conn:
        target_ids = [int(c.strip()) for c in company_ids.split(",")] if company_ids else _load_golden_company_ids(conn)
        stats = fetch_and_store_statements(conn, target_ids, paced=not no_pacing)
    typer.echo(f"fetch-statements: {stats}")


@app.command("compare")
def compare_cmd(
    company_ids: str = typer.Option(None, help="Comma-separated company_ids to restrict to (default: golden-10)."),
) -> None:
    """Compares stored yfinance statement lines against our own
    canonical_fact values (preferring a *_resolved concept where one
    exists), every available quarter, not just the latest."""
    with get_connection() as conn:
        target_ids = [int(c.strip()) for c in company_ids.split(",")] if company_ids else _load_golden_company_ids(conn)
        stats = compare_statements(conn, target_ids)
    typer.echo(f"compare: {stats}")


@app.command("daily-rotation")
def daily_rotation_cmd(
    limit: int = typer.Option(200, help="Companies to fetch+compare this run (rotates coldest-fetched-first)."),
) -> None:
    """Added 2026-09-08 for the daily cron -- fetch-statements/compare
    previously had no rotation of their own (only an explicit
    --company-ids list or the golden-10 default), so this system could
    never actually run against the full population unattended. Picks a
    coldest-fetched-first batch (pick_rotation_batch(), mirroring
    sanity/yfinance_check.py's own rotation), fetches it (paced -- this
    is a shared daily cron slot, not a one-off fast pass), then compares
    that SAME batch immediately so a run's findings are never stale
    relative to its own fetch. limit=200 (vs the ratio checker's 750) --
    3 yfinance requests/company here vs 1 there, same shared rate
    budget, kept lower so this doesn't starve the ratio checker's own
    daily rotation of the budget both share."""
    with get_connection() as conn:
        target_ids = pick_rotation_batch(conn, limit)
        fetch_stats = fetch_and_store_statements(conn, target_ids, paced=True)
        compare_stats = compare_statements(conn, target_ids)
    typer.echo(f"fetch: {fetch_stats}")
    typer.echo(f"compare: {compare_stats}")


@app.command("investigate")
def investigate_cmd() -> None:
    """Hands every current 'major' finding without an already-understood
    note to sanity/tag_investigator.py's investigate() -- reuses that
    fix pipeline (real SEC tag only, yfinance for detection/matching
    only) rather than duplicating it."""
    with get_connection() as conn:
        stats = investigate_major_findings(conn)
    typer.echo(f"investigate: {stats}")


@app.command("report")
def report_cmd() -> None:
    with get_connection() as conn:
        summary = summarize(conn)
    typer.echo(render_markdown(summary))

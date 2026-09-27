"""Typer CLI for revenue-by-segment (doc 37/38, built 2026-08-31)."""

import json
from pathlib import Path

import typer

from scrooner_pipeline.db.connection import get_connection
from scrooner_pipeline.segments.segment_revenue import update_segment_revenue

app = typer.Typer()

GOLDEN_COMPANIES_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "golden_companies"
    / "companies.json"
)


def _load_golden_ciks() -> set[str]:
    companies = json.loads(GOLDEN_COMPANIES_PATH.read_text())
    return {c["cik"] for c in companies}


@app.command("update-segment-revenue")
def update_segment_revenue_cmd(
    ciks: str = typer.Option(
        None, help="Comma-separated CIKs to restrict to (default: golden set)."
    ),
) -> None:
    """Fetch each company's latest 10-Q/10-K, find its segment/
    disaggregated-revenue "Details" report, parse it into
    core.segment_revenue. Genuinely new fetch (not zero-fetch) -- each
    company's report is parsed live, not read from any existing storage."""
    target_ciks = (
        {c.strip().zfill(10) for c in ciks.split(",")} if ciks else _load_golden_ciks()
    )
    with get_connection() as conn:
        stats = update_segment_revenue(conn, target_ciks)
    typer.echo(f"update-segment-revenue: {stats}")


if __name__ == "__main__":
    app()

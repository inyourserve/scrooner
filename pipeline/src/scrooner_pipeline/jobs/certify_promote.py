"""Typer CLI `scrooner-certify-promote`: the FSN-era certification ladder above checks_clean
(reconciled, verified, certified; certification/promote.py). Run after `scrooner-certify`.
Dry run by default; --apply writes analytics.company_certification states only and needs the
founder's typed words for production."""

from __future__ import annotations

import psycopg
import typer

from scrooner_pipeline.certification.promote import (
    MigrationNotAppliedError,
    promote,
    render,
)
from scrooner_pipeline.certification.loader import resolve_company_ids
from scrooner_pipeline.certification.runner import SHARDS_CSV, load_shard_company_ids
from scrooner_pipeline.common.config import settings

app = typer.Typer(help=__doc__)


@app.command()
def main(
    ciks: str = typer.Option("", help="Comma-separated CIKs."),
    top1000_shard: str = typer.Option(
        "", "--top1000-shard", help="Campaign shard id, e.g. S001."
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--apply",
        help="Dry run (default): decide and print, write nothing.",
    ),
    statement_timeout: int = typer.Option(15, help="Seconds, set before every query."),
) -> None:
    """Decide each company's highest rung and print why the next one does not hold."""
    if not ciks and not top1000_shard:
        raise typer.BadParameter("give --ciks or --top1000-shard")
    conn = psycopg.connect(settings.database_url)
    try:
        conn.read_only = dry_run
        ids: list[int] = []
        if top1000_shard:
            ids += load_shard_company_ids(top1000_shard, SHARDS_CSV)
        if ciks:
            with conn.cursor() as cur:
                ids += resolve_company_ids(cur, ciks.split(","), statement_timeout)
            conn.rollback()
        ids = list(dict.fromkeys(ids))
        typer.echo(
            f"mode: {'DRY RUN (nothing written)' if dry_run else 'APPLY'}; companies: {len(ids)}"
        )
        try:
            decisions = promote(
                conn, ids, apply=not dry_run, timeout_s=statement_timeout
            )
        except MigrationNotAppliedError as exc:
            typer.echo(f"REFUSED: {exc}")
            raise typer.Exit(code=2)
        typer.echo(render(decisions))
        skipped = len(ids) - len(decisions)
        if skipped:
            typer.echo(
                f"{skipped} compan{'y' if skipped == 1 else 'ies'} without a certification row (run scrooner-certify first)"
            )
    finally:
        conn.close()
